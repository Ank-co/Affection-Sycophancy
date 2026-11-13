"""Phase III, step 2b (exploration, dev items only): steering with the love direction *before* the model reads the question.

    python scripts/phase3/steering2_dev.py --weights C:/llm/hf/Qwen3-8B

Why: interventions_dev.py --exp steering added the L3 - L0 answer-position direction at layer 24. It shrank the model's
confidence multiplicatively (slope 0.55 on the neutral logit, in both the false-belief and the plain form, wrong answers
became less wrong too), whereas real love shifts the logit additively toward the user's stated answer (slope 0.94,
intercept -2.1). A fixed vector cannot point to "the user's letter" (the false letter is counterbalanced), so the real
effect must come from the love state *combining* with the stated belief. Patching located that combination: the
final-turn tokens hold the whole effect from layer 18 on, little before 12.

Here the direction is the love state itself, injected where the model would read it, and the model's own circuitry is
left to combine it with the question. Configurations (layer = index in the activation files: 0 = embeddings, l = output
of block l):
  hist-14-history   L3 - L0 at the end of the history, layer 14, added over every history token (user and assistant)
  hist-18-history   same, layer 18
  hist-18-final     same direction, layer 18, added over the final user turn and the answer prefix
  ans-18-final      L3 - L0 at the answer position, layer 18, over the final user turn (the earlier recipe, earlier layer)
Directions are estimated on the 7 scripts not used here (leave-out). Controls: random directions of the same norm.
Prediction if love acts through the stated belief: an additive shift toward the false belief in the false-belief form
(slope near 1, negative intercept) and little or no shift in the plain form.
Writes results/internals/qwen3-8b/steering2_dev.json.
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

SUM = OUT / "acts_dev_summary"
LAYERS = [0, 4, 8, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36]       # answer-position layers kept in the summaries
CONFIGS = [("hist", 14, "history"), ("hist", 18, "history"), ("hist", 18, "final"), ("ans", 18, "final")]


def directions(used):
    """L3 - L0, paired by script, on the scripts not used for steering."""
    out = {}
    scripts = sorted(f.stem.split("__")[1] for f in SUM.glob("L0__*.npz"))
    rest = [s for s in scripts if s not in used]
    hist = [np.load(SUM / f"L3__{s}.npz")["hist"] - np.load(SUM / f"L0__{s}.npz")["hist"] for s in rest]
    for src, l, _ in CONFIGS:
        if src == "hist":
            out[(src, l)] = np.mean([h[l] for h in hist], 0)
        else:
            j = LAYERS.index(l)
            diffs = []
            for s in rest:
                z3, z0 = np.load(SUM / f"L3__{s}.npz"), np.load(SUM / f"L0__{s}.npz")
                f3 = np.array([m["form"] == "false_belief" for m in json.loads(str(z3["meta"]))])
                f0 = np.array([m["form"] == "false_belief" for m in json.loads(str(z0["meta"]))])
                diffs.append(z3["ans"][f3, j].astype(np.float32).mean(0) - z0["ans"][f0, j].astype(np.float32).mean(0))
            out[(src, l)] = np.mean(diffs, 0)
    return out, rest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--scripts", type=int, default=3)
    ap.add_argument("--alphas", type=float, nargs="+", default=[1, 2, 4])
    ap.add_argument("--random-alphas", type=float, nargs="+", default=[2, 4])
    ap.add_argument("--n-random", type=int, default=2)
    args = ap.parse_args()
    import torch

    ids = set(json.loads((ROOT / "results" / "known_items" / "known_8b_dev.json").read_text()))
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = sorted((i for i in items if i["id"] in ids and i["split"] == "dev"), key=lambda i: i["id"])[: args.items]
    scr = scripts_for(10)[: args.scripts]
    dirs, rest = directions({f"{s}-{g[0]}-v{v}" for s, g, v in scr})
    print(f"directions from {len(rest)} scripts: {', '.join(rest)}")

    tok, model = load(args.weights)
    lid = letter_ids(tok)
    blocks = model.model.layers
    vec = {k: torch.tensor(d, dtype=torch.bfloat16, device=model.device) for k, d in dirs.items()}
    gen = torch.Generator(device="cpu").manual_seed(0)
    rand = {}
    for k, u in vec.items():
        n = float(torch.linalg.norm(u.float()))
        rand[k] = [(r / r.norm() * n).to(torch.bfloat16).to(model.device)
                   for r in (torch.randn(u.shape[0], generator=gen) for _ in range(args.n_random))]
        print(f"  {k[0]}-{k[1]}: norm {n:.1f}")
    state = {"block": None, "vec": None, "a": 0, "b": 0}

    def hook(i):
        def f(_m, _inp, output):
            if state["block"] != i or state["vec"] is None:
                return None
            h = layer_out(output).clone()
            h[:, state["a"]:state["b"], :] += state["vec"]
            return with_out(output, h)
        return f
    handles = [blocks[l - 1].register_forward_hook(hook(l - 1)) for l in sorted({c[1] for c in CONFIGS})]

    rows, t0, n = [], time.perf_counter(), 0
    total = len(scr) * len(items) * 2
    for si, (sid, g, v) in enumerate(scr):
        hist = S.history(sid, "L0", g, version=v)
        for ii, it in enumerate(items):
            cf = (ii + si) % 2 == 0
            for form in ("false_belief", "plain"):
                text, key, wrong = S.probe(sid, it, cf, form)
                prompt = tok.apply_chat_template(hist + [{"role": "user", "content": text}], tokenize=False,
                                                 add_generation_prompt=True, enable_thinking=False) + PREFIX
                enc = tok(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
                T = enc.input_ids.shape[1]
                h0 = len(tok(prompt[: prompt.index("<|im_start|>user")], add_special_tokens=False).input_ids)
                h1 = len(tok(prompt[: prompt.rindex("<|im_start|>user")], add_special_tokens=False).input_ids)
                span = {"history": (h0, h1), "final": (h1, T)}
                res = {}
                with torch.no_grad():
                    state["vec"] = None
                    res["base"] = lp(model(**enc).logits[0, -1].float(), lid, key, wrong)
                    for src, l, sp in CONFIGS:
                        name = f"{src}-{l}-{sp}"
                        state["block"], (state["a"], state["b"]) = l - 1, span[sp]
                        for a in args.alphas:
                            state["vec"] = a * vec[(src, l)]
                            res[f"{name}|love_{a:g}"] = lp(model(**enc).logits[0, -1].float(), lid, key, wrong)
                        for j, r in enumerate(rand[(src, l)]):
                            for a in args.random_alphas:
                                state["vec"] = a * r
                                res[f"{name}|random{j}_{a:g}"] = lp(model(**enc).logits[0, -1].float(), lid, key, wrong)
                    state["vec"] = None
                rows.append({"item": it["id"], "script": f"{sid}-{g[0]}-v{v}", "form": form, "lp": res})
                n += 1
                if n % 10 == 0:
                    el = time.perf_counter() - t0
                    print(f"  {n}/{total}  |  {el / 60:.0f} min  |  about {el / n * (total - n) / 60:.0f} min left", flush=True)
                    (OUT / "steering2_dev.partial.json").write_text(json.dumps({"args": vars(args), "rows": rows}))
    for h in handles:
        h.remove()
    (OUT / "steering2_dev.json").write_text(json.dumps({"args": vars(args), "directions_from": rest, "rows": rows}))
    print(f"done: {len(rows)} rows in {(time.perf_counter() - t0) / 60:.0f} min -> {OUT / 'steering2_dev.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
