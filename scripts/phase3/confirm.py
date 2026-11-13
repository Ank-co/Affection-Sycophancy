"""Phase III, confirmatory runner: Qwen3-8B in PyTorch (NF4), test items. See docs/preregistration-phase3.md.

    python scripts/phase3/confirm.py fit --weights C:/llm/hf/Qwen3-8B                         # dev only, frozen input
    python scripts/phase3/confirm.py run --weights C:/llm/hf/Qwen3-8B --split dev --items 4    # smoke test
    python scripts/phase3/confirm.py run --weights C:/llm/hf/Qwen3-8B --split test             # confirmatory

Layer convention (all Phase III registered analyses): layer l = the residual stream after block l, l = 1..36;
layer 0 = the embeddings. (Some dev exploration scripts labelled block outputs from 0; see results/internals/README.md.)

fit   Low-rank basis for E2: top 512 principal directions of the per-token L3 - L0 differences at layer 18 over the
      final user turn and answer prefix, dev items, 10 scripts, false-belief form. Tokens whose neutral residual norm
      exceeds 10x the median norm of their turn are left out of the fit (a few tokens with very large activations
      otherwise dominate it). Writes results/internals/qwen3-8b/frozen/lowrank_basis_L18.npy (+ .json).
      Same pass: the love directions (answer position, mean L3 - L0 over the 10 dev scripts, layers 14-22) and the 4
      script-to-script directions (layer 18) are written into frozen/directions.npz, whose random vectors are kept.
run   E1 logit lens and answers: cells L0, L3, C, false-belief form, all items, 10 scripts.
      E2 on the patching subset (60 test items x 10 scripts), L3 -> L0 over the final turn:
         full patching at 15 layers; low-rank patching at layer 18 (k = 8, 16, 64, 256, 512; frozen basis vs a random
         subspace); ablation of the frozen love direction in L3 runs (layer 18; layers 14-22) and random controls.
      E4 on the steering subset (30 items x 10 scripts): frozen love direction x 2 added at layer 18 over the final
         turn of L0 conversations, against 20 random directions and 4 script-to-script directions of the same norm.
      One file per experiment x script in results/internals/qwen3-8b/confirm-<split>/; resumable (Ctrl+C, rerun).
      The test split is refused until docs/preregistration-phase3.md and the frozen inputs are committed and pushed.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "phase3"))
import stimuli as S  # noqa: E402
from campaign import scripts_for  # noqa: E402
from agreement_check import letter_ids  # noqa: E402
from interventions_dev import OUT, load, lp  # noqa: E402

# Answer prefix up to the letter: the format Qwen3-8B itself produced in 95% of the Phase II test trials (GGUF).
# The dev exploration used '{\n  "answer": "' (under 2% of the 8B's own outputs); see the pre-registration, section 3.
PREFIX = '{"answer": "'

FROZEN = OUT / "frozen"
PREREG = "docs/preregistration-phase3.md"
FROZEN_FILES = ["directions.npz", "test_subsets.json", "lowrank_basis_L18.npy", "lowrank_basis_L18.json"]
E1_CELLS = ["L0", "L3", "C"]
PATCH_LAYERS = [1, 5, 9, 11, 13, 14, 15, 16, 17, 19, 21, 25, 29, 33, 36]
LR_LAYER, KS, NB = 18, [8, 16, 64, 256, 512], 512
ABL_MULTI = [14, 16, 18, 20, 22]
ALPHA, N_RANDOM, MASSIVE = 2.0, 20, 10.0
SEED_SUBSPACE = 20261115


# ------------------------------------------------------------------ guards and inputs
def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True)


def registered() -> tuple[bool, str]:
    paths = [PREREG] + [str((FROZEN / f).relative_to(ROOT)).replace("\\", "/") for f in FROZEN_FILES]
    for p in paths:
        if git("ls-files", "--error-unmatch", p).returncode != 0:
            return False, f"{p} is not committed"
        if git("diff", "--quiet", "HEAD", "--", p).returncode != 0:
            return False, f"{p} has uncommitted changes"
    last = git("log", "-1", "--format=%H", "--", PREREG).stdout.strip()
    git("fetch", "--quiet")
    if not git("branch", "-r", "--contains", last).stdout.strip():
        return False, f"commit {last[:8]} of the pre-registration is not on the remote yet (git push)"
    return True, last


def items_for(split):
    ids = set(json.loads((ROOT / "results" / "known_items" / f"known_8b_{split}.json").read_text()))
    rows = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    return sorted((i for i in rows if i["id"] in ids and i["split"] == split), key=lambda i: i["id"])


def option_orders(split):
    """correct_first of the GGUF campaign trial with the same item and script (L0, false-belief), if any."""
    f = ROOT / "results" / "campaign" / "qwen3-8b" / f"{split}.jsonl"
    out = {}
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["cell"] == "L0" and r["form"] == "false_belief":
                out[(r["item"], r["script"])] = r["correct_first"]
    return out


def sid_of(s, g, v):
    return f"{s}-{g[0]}-v{v}"


# ------------------------------------------------------------------ model plumbing
class Hooks:
    """One hook per layer (0 = embeddings, l = after block l). Acts on the last k tokens (final turn + prefix)."""

    def __init__(self, model):
        import torch  # noqa: F401
        self.handles = [model.model.embed_tokens.register_forward_hook(self._f(0))]
        self.handles += [b.register_forward_hook(self._f(i + 1)) for i, b in enumerate(model.model.layers)]
        self.reset()

    def reset(self):
        self.k, self.capture, self.cap, self.ops, self.last, self.lastcap = 0, set(), {}, {}, False, {}

    def _f(self, l):
        def f(_m, _inp, output):
            h = output[0] if isinstance(output, tuple) else output
            if self.last:
                self.lastcap[l] = h[0, -1].detach().clone()      # clone: a view would keep the whole layer output alive
            if l in self.capture:
                self.cap[l] = h[0, -self.k:, :].detach().float().clone()
            op = self.ops.get(l)
            if op is None:
                return None
            kind, x = op
            h = h.clone()
            seg = h[0, -self.k:, :].float()
            if kind == "replace":
                seg = x
            elif kind == "add":
                seg = seg + x
            elif kind == "ablate":
                seg = seg - (seg @ x)[:, None] * x[None, :]
            h[0, -self.k:, :] = seg.to(h.dtype)
            return (h,) + tuple(output[1:]) if isinstance(output, tuple) else h
        return f


def build(tok, sid, g, v, cond, it, cf, form="false_belief"):
    text, key, wrong = S.probe(sid, it, cf, form)
    p = tok.apply_chat_template(S.history(sid, cond, g, version=v) + [{"role": "user", "content": text}],
                                tokenize=False, add_generation_prompt=True, enable_thinking=False) + PREFIX
    k = len(tok(p[p.rindex("<|im_start|>user"):], add_special_tokens=False).input_ids)
    return p, key, wrong, k


class Runner:
    def __init__(self, weights):
        import torch
        self.torch = torch
        self.tok, self.model = load(weights)
        self.lid = letter_ids(self.tok)
        self.hooks = Hooks(self.model)
        self.dev = self.model.device

    def fwd(self, prompt, k, capture=(), ops=None, last=False):
        h = self.hooks
        h.reset()
        h.k, h.capture, h.ops, h.last = k, set(capture), ops or {}, last
        enc = self.tok(prompt, return_tensors="pt", add_special_tokens=False).to(self.dev)
        with self.torch.no_grad():
            logits = self.model(**enc).logits[0, -1].float()
        cap, lastcap = h.cap, h.lastcap
        h.reset()
        return logits, cap, lastcap

    def lp(self, logits, key, wrong):
        return lp(logits, self.lid, key, wrong)

    def t(self, x):
        return self.torch.tensor(np.asarray(x), dtype=self.torch.float32, device=self.dev)


# ------------------------------------------------------------------ fit (dev only)
def cmd_fit(args):
    R = Runner(args.weights)
    torch = R.torch
    items, orders = items_for("dev"), option_orders("dev")
    C = torch.zeros(4096, 4096, dtype=torch.float64, device=R.dev)
    ntok, nexcl, t0 = 0, 0, time.perf_counter()
    ans = {}                                                  # script -> {cond: {layer: sum of answer states}}
    for si, (s, g, v) in enumerate(scripts_for(10)):
        sid = sid_of(s, g, v)
        ans[sid] = {c: {l: 0.0 for l in ABL_MULTI} for c in ("L0", "L3")}
        for ii, it in enumerate(items):
            cf = orders.get((it["id"], sid), (ii + si) % 2 == 0)
            p3, _, _, k = build(R.tok, s, g, v, "L3", it, cf)
            p0, _, _, k0 = build(R.tok, s, g, v, "L0", it, cf)
            assert k == k0
            _, c3, a3 = R.fwd(p3, k, capture=[LR_LAYER], last=True)
            _, c0, a0 = R.fwd(p0, k, capture=[LR_LAYER], last=True)
            for l in ABL_MULTI:
                ans[sid]["L3"][l] = ans[sid]["L3"][l] + a3[l].float().cpu().numpy() / len(items)
                ans[sid]["L0"][l] = ans[sid]["L0"][l] + a0[l].float().cpu().numpy() / len(items)
            n0 = c0[LR_LAYER].norm(dim=1)
            keep = n0 <= MASSIVE * n0.median()
            D = (c3[LR_LAYER] - c0[LR_LAYER])[keep].double()
            C += D.T @ D
            ntok += int(keep.sum()); nexcl += int((~keep).sum())
        print(f"  fit {si + 1}/10 scripts  |  {(time.perf_counter() - t0) / 60:.0f} min", flush=True)
    w, V = np.linalg.eigh((C / ntok).cpu().numpy())
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    FROZEN.mkdir(parents=True, exist_ok=True)
    np.save(FROZEN / "lowrank_basis_L18.npy", V[:, :NB].astype(np.float32))
    ex = np.cumsum(w) / w.sum()
    info = {"layer": LR_LAYER, "items": "dev, known by the three 8B models", "scripts": 10, "form": "false_belief",
            "tokens_used": ntok, "tokens_excluded_massive": nexcl, "massive_rule": f"norm > {MASSIVE} x median of the turn",
            "explained": {str(k): float(ex[k - 1]) for k in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]}}
    (FROZEN / "lowrank_basis_L18.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info, indent=1))
    old = dict(np.load(FROZEN / "directions.npz"))
    new = {k: v for k, v in old.items() if k.startswith(("random_", "ablate_"))}
    sids = list(ans)
    for l in ABL_MULTI:
        new[f"love_{l}"] = np.mean([ans[x]["L3"][l] - ans[x]["L0"][l] for x in sids], 0).astype(np.float32)
    grand = np.mean([ans[x]["L0"][18] for x in sids], 0)
    for x in sids[:4]:
        new[f"script_{x}_18"] = (ans[x]["L0"][18] - grand).astype(np.float32)
    cos = lambda a, b: float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))  # noqa: E731
    for l in ABL_MULTI:
        print(f"  love_{l}: norm {np.linalg.norm(new[f'love_{l}']):.2f}, cosine with the dev-exploration direction "
              f"{cos(new[f'love_{l}'], old[f'love_{l}']):+.2f}")
    np.savez(FROZEN / "directions.npz", **new)
    return 0


# ------------------------------------------------------------------ run
def cmd_run(args):
    if args.split == "test":
        ok, why = registered()
        if not ok:
            print(f"refused: {why}")
            return 1
    for f in FROZEN_FILES:
        if not (FROZEN / f).exists():
            print(f"missing frozen input {f} (run `confirm.py fit` first)")
            return 1
    items = items_for(args.split)
    orders = option_orders(args.split)
    if args.split == "test":
        sub = json.loads((FROZEN / "test_subsets.json").read_text())
        e2_ids, e4_ids = set(sub["patching_lowrank_ablation"]), set(sub["steering"])
    else:
        items = items[: args.items] if args.items else items
        e2_ids = e4_ids = {i["id"] for i in items}
    dest = OUT / f"confirm-{args.split}"
    dest.mkdir(parents=True, exist_ok=True)

    R = Runner(args.weights)
    torch = R.torch
    meta = {"started": datetime.now(timezone.utc).isoformat(), "git_head": git("rev-parse", "HEAD").stdout.strip(),
            "weights": args.weights, "split": args.split, "n_items": len(items), "python": platform.python_version(),
            "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
    try:
        import transformers, bitsandbytes  # noqa: E401
        meta.update(transformers=transformers.__version__, bitsandbytes=bitsandbytes.__version__)
    except Exception:  # noqa: BLE001
        pass
    (dest / f"meta-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json").write_text(json.dumps(meta, indent=1))

    d = np.load(FROZEN / "directions.npz")
    love = {l: R.t(d[f"love_{l}"]) for l in ABL_MULTI}
    unit = lambda x: x / x.norm()  # noqa: E731
    lnorm = float(love[18].norm())
    U = R.t(np.load(FROZEN / "lowrank_basis_L18.npy"))
    Rs = R.t(np.linalg.qr(np.random.default_rng(SEED_SUBSPACE).standard_normal((U.shape[0], NB)))[0])
    W, norm = R.model.lm_head.weight, R.model.model.norm
    scripts = [(si, s, g, v) for si, (s, g, v) in enumerate(scripts_for(10))]
    plan = [(e, ids) for e, ids in [("e1", None), ("e2", e2_ids), ("e4", e4_ids)] if e in args.exps.split(",")]
    n_pass = {"e1": len(E1_CELLS), "e2": 2 + len(PATCH_LAYERS) + 1 + 2 * len(KS) + 7, "e4": 3 + N_RANDOM + 4}
    total = sum(n_pass[e] * (len(items) if ids is None else len([i for i in items if i["id"] in ids])) * len(scripts)
                for e, ids in plan)
    done_passes, t0 = 0, time.perf_counter()
    print(f"{args.split}: {len(items)} items, about {total} forward passes in all", flush=True)

    for exp, ids in plan:
        its = [(ii, it) for ii, it in enumerate(items) if ids is None or it["id"] in ids]
        for si, s, g, v in scripts:
            sid = sid_of(s, g, v)
            shard = dest / f"{exp}__{sid}.json"
            if shard.exists():
                continue
            rows = []
            for ii, it in its:
                cf = orders.get((it["id"], sid), (ii + si) % 2 == 0)
                if exp == "e1":
                    for cell in E1_CELLS:
                        p, key, wrong, k = build(R.tok, s, g, v, cell, it, cf)
                        logits, _, lc = R.fwd(p, k, last=True)
                        H = torch.stack([lc[l] for l in range(len(R.model.model.layers) + 1)])
                        with torch.no_grad():
                            lens = (norm(H.to(W.dtype)) @ (W[R.lid[key]] - W[R.lid[wrong]])).float().cpu().tolist()
                        pk = torch.softmax(logits[[R.lid["A"], R.lid["B"]]], 0)[0 if key == "A" else 1].item()
                        rows.append({"cell": cell, "item": it["id"], "script": sid, "form": "false_belief",
                                     "correct_first": cf, "key": key, "p_correct": pk, "lp": R.lp(logits, key, wrong),
                                     "lens": lens})
                    continue
                p3, key, wrong, k = build(R.tok, s, g, v, "L3", it, cf)
                p0, _, _, k0 = build(R.tok, s, g, v, "L0", it, cf)
                assert k == k0, (it["id"], sid)
                res = {}
                if exp == "e2":
                    l3, C3, _ = R.fwd(p3, k, capture=set(PATCH_LAYERS) | {LR_LAYER})
                    l0, C0, _ = R.fwd(p0, k, capture=[LR_LAYER])
                    res["L0"], res["L3"] = R.lp(l0, key, wrong), R.lp(l3, key, wrong)
                    for l in PATCH_LAYERS:
                        res[f"patch_{l}"] = R.lp(R.fwd(p0, k, ops={l: ("replace", C3[l])})[0], key, wrong)
                    D = C3[LR_LAYER] - C0[LR_LAYER]
                    res["lowrank_full"] = R.lp(R.fwd(p0, k, ops={LR_LAYER: ("add", D)})[0], key, wrong)
                    for kk in KS:
                        for name, B in (("pc", U[:, :kk]), ("random", Rs[:, :kk])):
                            res[f"lowrank_{name}_{kk}"] = R.lp(R.fwd(p0, k, ops={LR_LAYER: ("add", (D @ B) @ B.T)})[0],
                                                               key, wrong)
                    abl = {"ablate_love_18": {18: unit(love[18])},
                           "ablate_love_14-22": {l: unit(love[l]) for l in ABL_MULTI}}
                    for j in range(3):
                        abl[f"ablate_random{j}_18"] = {18: R.t(d[f"ablate_random_{j}_18"])}
                    for j in range(2):
                        abl[f"ablate_random{j}_14-22"] = {l: R.t(d[f"ablate_multi_random_{j}_{l}"]) for l in ABL_MULTI}
                    for name, dirs in abl.items():
                        res[name] = R.lp(R.fwd(p3, k, ops={l: ("ablate", u) for l, u in dirs.items()})[0], key, wrong)
                else:  # e4
                    res["L0"] = R.lp(R.fwd(p0, k)[0], key, wrong)
                    res["love"] = R.lp(R.fwd(p0, k, ops={18: ("add", ALPHA * love[18])})[0], key, wrong)
                    for j in range(N_RANDOM):
                        x = R.t(d[f"random_{j}"]) * lnorm * ALPHA
                        res[f"random{j}"] = R.lp(R.fwd(p0, k, ops={18: ("add", x)})[0], key, wrong)
                    for name in sorted(n for n in d.files if n.startswith("script_")):
                        x = unit(R.t(d[name])) * lnorm * ALPHA
                        res[name.replace("_18", "")] = R.lp(R.fwd(p0, k, ops={18: ("add", x)})[0], key, wrong)
                    res["L3"] = R.lp(R.fwd(p3, k)[0], key, wrong)
                rows.append({"item": it["id"], "script": sid, "form": "false_belief", "correct_first": cf, "key": key,
                             "lp": res})
            shard.write_text(json.dumps({"exp": exp, "script": sid, "rows": rows}))
            done_passes += n_pass[exp] * len(its)
            el = time.perf_counter() - t0
            print(f"  {shard.name}: {len(rows)} rows  |  {el / 60:.0f} min  |  about "
                  f"{el / done_passes * max(total - done_passes, 0) / 60:.0f} min left (if nothing was resumed)", flush=True)
    print(f"done: {dest}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fit", "run"])
    ap.add_argument("--weights", required=True)
    ap.add_argument("--split", choices=["dev", "test"], default="dev")
    ap.add_argument("--items", type=int, default=0, help="dev smoke test: first n dev items")
    ap.add_argument("--exps", default="e1,e2,e4", help="subset of experiments to run (e.g. e1)")
    args = ap.parse_args()
    return cmd_fit(args) if args.cmd == "fit" else cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
