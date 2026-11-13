"""Phase III, step 2d (exploration, dev items only): how many dimensions carry the love effect at layer 18?

    python scripts/phase3/lowrank_dev.py --weights C:/llm/hf/Qwen3-8B

Background (dev): copying the whole final-turn residual of a loving (L3) conversation into the neutral (L0) one at
layer 18 transfers the full effect; but the mean L3 - L0 direction is not the carrier (adding it is no more effective
than random or script-to-script directions; projecting it out of L3 runs closes ~0% of the gap). So the effect lives in
the final-turn state, but not along the mean direction.

Here only part of the difference is copied: h0 + P_k (h3 - h0), where P_k projects onto the top-k principal directions
of the per-token L3 - L0 differences at layer 18 (final user turn + answer prefix), estimated on the 7 scripts not used
for testing. k = 1 ... 512; control: a random k-dimensional subspace. Reported: share of the L3 - L0 gap recovered.
If a few components recover most of the gap, the effect is low-rank and can be studied (and pre-registered) as such;
if it needs hundreds, it is distributed.
Writes results/internals/qwen3-8b/lowrank_dev.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "phase3"))
import stimuli as S  # noqa: E402
from campaign import scripts_for  # noqa: E402
from agreement_check import letter_ids  # noqa: E402
from interventions_dev import PREFIX, OUT, load, lp, layer_out, with_out  # noqa: E402

LAYER = 18                       # output of block 18 = model.model.layers[17]
KS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--scripts", type=int, default=3, help="test scripts (the first n); the other 7 fit the subspace")
    args = ap.parse_args()
    import torch

    ids = set(json.loads((ROOT / "results" / "known_items" / "known_8b_dev.json").read_text()))
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = sorted((i for i in items if i["id"] in ids and i["split"] == "dev"), key=lambda i: i["id"])[: args.items]
    allscr = list(enumerate(scripts_for(10)))
    test, fit = allscr[: args.scripts], allscr[args.scripts:]

    tok, model = load(args.weights)
    lid = letter_ids(tok)
    dev = model.device
    st = {"mode": None, "k": 0}

    def hook(_m, _inp, output):
        h = layer_out(output)
        if st["mode"] == "capture":
            st["cap"] = h[0, -st["k"]:, :].float().clone()
            return None
        if st["mode"] == "patch":
            h = h.clone()
            h[0, -st["k"]:, :] = (h[0, -st["k"]:, :].float() + st["delta"]).to(h.dtype)
            return with_out(output, h)
        return None
    hd = model.model.layers[LAYER - 1].register_forward_hook(hook)

    def prompts(si, sid, g, v, ii, it):
        cf = (ii + si) % 2 == 0
        text, key, wrong = S.probe(sid, it, cf, "false_belief")
        p = {c: tok.apply_chat_template(S.history(sid, c, g, version=v) + [{"role": "user", "content": text}],
                                        tokenize=False, add_generation_prompt=True, enable_thinking=False) + PREFIX
             for c in ("L0", "L3")}
        k = len(tok(p["L0"][p["L0"].rindex("<|im_start|>user"):], add_special_tokens=False).input_ids)
        return p, key, wrong, k

    def fwd(prompt, mode, k, delta=None):
        st.update(mode=mode, k=k, delta=delta)
        enc = tok(prompt, return_tensors="pt", add_special_tokens=False).to(dev)
        with torch.no_grad():
            out = model(**enc).logits[0, -1].float()
        st["mode"] = None
        return out

    # 1. fit: per-token L3 - L0 differences on the fit scripts
    t0, diffs = time.perf_counter(), []
    for n, (si, (sid, g, v)) in enumerate(fit):
        for ii, it in enumerate(items):
            p, key, wrong, k = prompts(si, sid, g, v, ii, it)
            fwd(p["L3"], "capture", k); c3 = st["cap"]
            fwd(p["L0"], "capture", k); c0 = st["cap"]
            diffs.append((c3 - c0).cpu())
        print(f"  fit {n + 1}/{len(fit)} scripts  |  {(time.perf_counter() - t0) / 60:.0f} min", flush=True)
    X = torch.cat(diffs).numpy().astype(np.float64)                   # (tokens, d), uncentered
    C = X.T @ X / len(X)
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    explained = np.cumsum(w) / w.sum()
    print("  variance of the differences explained by the top k: " +
          ", ".join(f"k={k}: {100 * explained[k - 1]:.0f}%" for k in KS), flush=True)
    U = torch.tensor(V[:, : max(KS)], dtype=torch.float32, device=dev)
    rng = np.random.default_rng(0)
    R = torch.tensor(np.linalg.qr(rng.standard_normal((V.shape[0], max(KS))))[0], dtype=torch.float32, device=dev)

    # 2. test: partial patching on the held-out scripts
    rows, n, total = [], 0, len(test) * len(items)
    for si, (sid, g, v) in test:
        for ii, it in enumerate(items):
            p, key, wrong, k = prompts(si, sid, g, v, ii, it)
            l3 = fwd(p["L3"], "capture", k); c3 = st["cap"]
            l0 = fwd(p["L0"], "capture", k); c0 = st["cap"]
            D = c3 - c0
            res = {"L0": lp(l0, lid, key, wrong), "L3": lp(l3, lid, key, wrong),
                   "full": lp(fwd(p["L0"], "patch", k, D), lid, key, wrong)}
            for kk in KS:
                for name, B in (("pc", U[:, :kk]), ("random", R[:, :kk])):
                    res[f"{name}_{kk}"] = lp(fwd(p["L0"], "patch", k, (D @ B) @ B.T), lid, key, wrong)
            rows.append({"item": it["id"], "script": f"{sid}-{g[0]}-v{v}", "lp": res,
                         "diff_share_in_top": {str(kk): float(((D @ U[:, :kk]).norm() / D.norm()) ** 2) for kk in KS}})
            n += 1
            if n % 10 == 0:
                el = time.perf_counter() - t0
                print(f"  test {n}/{total}  |  {el / 60:.0f} min", flush=True)
    hd.remove()
    (OUT / "lowrank_dev.json").write_text(json.dumps({"args": vars(args), "layer": LAYER, "ks": KS,
                                                     "explained": {str(k): float(explained[k - 1]) for k in KS},
                                                     "fit_scripts": [f"{s}-{g[0]}-v{v}" for _, (s, g, v) in fit],
                                                     "rows": rows}))
    print(f"done: {len(rows)} rows in {(time.perf_counter() - t0) / 60:.0f} min -> {OUT / 'lowrank_dev.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
