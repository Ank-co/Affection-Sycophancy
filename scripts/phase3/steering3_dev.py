"""Phase III, step 2c (exploration, dev items only): is the love direction at layer 18 specific, and is it necessary?

    python scripts/phase3/steering3_dev.py --weights C:/llm/hf/Qwen3-8B

steering2_dev.py found one recipe with the signature of real love: the L3 - L0 answer-position direction at layer 18,
added over the final user turn of neutral conversations, shifts the logit additively toward the false belief
(alpha 2: slope 0.91, intercept -1.7, no flip back; real love: slope 0.94, intercept -2.1), and much less in the plain
form. But only two random controls were run and one of them did part of the same. This run asks:

1. Specificity (neutral conversations, layer 18, final turn, alpha 2, every vector rescaled to the love norm):
   love vs 12 random directions; vs "natural" directions: warm disclosure (C - L0), praise (L1 - L0), sad backdrop
   (L0_sad - L0), and 4 script-to-script differences of neutral conversations (storyline, gender, version).
2. Layer profile: love at alpha 2 at layers 14, 16, 20, 24 (same span).
3. Necessity (loving L3 conversations): project the love direction out of the final-turn residual at layer 18, or at
   layers 14-22 together (each with its own direction); control: project out 5 random directions at layer 18.
   If the direction carries the effect, the L3 logit moves back toward the L0 logit.
Directions are estimated on the 7 scripts not used here. Writes results/internals/qwen3-8b/steering3_dev.json.
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
LAYERS = [0, 4, 8, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36]
MAIN = 18
PROFILE = [14, 16, 20, 24]
ABL_MULTI = [14, 16, 18, 20, 22]


def ans_mean(cell, script, j):
    z = np.load(SUM / f"{cell}__{script}.npz")
    fb = np.array([m["form"] == "false_belief" for m in json.loads(str(z["meta"]))])
    return z["ans"][fb, j].astype(np.float32).mean(0)


def directions(used):
    scripts = sorted(f.stem.split("__")[1] for f in SUM.glob("L0__*.npz"))
    rest = [s for s in scripts if s not in used]
    love = {l: np.mean([ans_mean("L3", s, LAYERS.index(l)) - ans_mean("L0", s, LAYERS.index(l)) for s in rest], 0)
            for l in sorted(set([MAIN] + PROFILE + ABL_MULTI))}
    j = LAYERS.index(MAIN)
    natural = {f"{c}": np.mean([ans_mean(c, s, j) - ans_mean("L0", s, j) for s in rest], 0)
               for c in ("C", "L1", "L0_sad")}
    l0 = {s: ans_mean("L0", s, j) for s in rest}
    grand = np.mean(list(l0.values()), 0)
    for s in rest[:4]:
        natural[f"script_{s}"] = l0[s] - grand
    return love, natural, rest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--scripts", type=int, default=3)
    ap.add_argument("--n-random", type=int, default=12)
    ap.add_argument("--n-random-ablate", type=int, default=5)
    args = ap.parse_args()
    import torch

    ids = set(json.loads((ROOT / "results" / "known_items" / "known_8b_dev.json").read_text()))
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = sorted((i for i in items if i["id"] in ids and i["split"] == "dev"), key=lambda i: i["id"])[: args.items]
    scr = scripts_for(10)[: args.scripts]
    love, natural, rest = directions({f"{s}-{g[0]}-v{v}" for s, g, v in scr})
    print(f"directions from {len(rest)} scripts: {', '.join(rest)}")

    tok, model = load(args.weights)
    lid = letter_ids(tok)
    blocks = model.model.layers
    dev = model.device
    T_ = lambda x: torch.tensor(x, dtype=torch.float32, device=dev)  # noqa: E731
    love_t = {l: T_(v) for l, v in love.items()}
    norm = float(torch.linalg.norm(love_t[MAIN]))
    add = {"love_1": love_t[MAIN], "love_2": 2 * love_t[MAIN]}
    for l in PROFILE:
        add[f"love_2_L{l}"] = 2 * love_t[l]
    for k, v in natural.items():
        t = T_(v)
        add[f"{k}_2"] = 2 * t / torch.linalg.norm(t) * norm
        print(f"  {k}: raw norm {float(torch.linalg.norm(t)):.1f}, cosine with love {float(t @ love_t[MAIN] / torch.linalg.norm(t) / norm):+.2f}")
    gen = torch.Generator(device="cpu").manual_seed(1)
    for i in range(args.n_random):
        r = torch.randn(love_t[MAIN].shape[0], generator=gen).to(dev)
        add[f"random{i}_2"] = 2 * r / r.norm() * norm
    layer_of = {k: (int(k.split("_L")[1]) if "_L" in k else MAIN) for k in add}
    abl = {"ablate_love_18": {MAIN: love_t[MAIN]}, "ablate_love_14-22": {l: love_t[l] for l in ABL_MULTI}}
    for i in range(args.n_random_ablate):
        r = torch.randn(love_t[MAIN].shape[0], generator=gen).to(dev)
        abl[f"ablate_random{i}_18"] = {MAIN: r}
    print(f"  love norm at layer {MAIN}: {norm:.1f}; {len(add)} additions, {len(abl)} ablations")

    state = {"ops": {}, "a": 0, "b": 0}       # ops: block index (= layer - 1) -> ("add", vec) or ("ablate", unit vec)

    def hook(i):
        def f(_m, _inp, output):
            op = state["ops"].get(i)
            if op is None:
                return None
            h = layer_out(output).clone()
            seg = h[:, state["a"]:state["b"], :].float()
            if op[0] == "add":
                seg = seg + op[1]
            else:
                u = op[1] / op[1].norm()
                seg = seg - (seg @ u)[..., None] * u
            h[:, state["a"]:state["b"], :] = seg.to(h.dtype)
            return with_out(output, h)
        return f
    used_layers = sorted(set(layer_of.values()) | set(ABL_MULTI))
    handles = [blocks[l - 1].register_forward_hook(hook(l - 1)) for l in used_layers]

    def run(prompt, key, wrong):
        enc = tok(prompt, return_tensors="pt", add_special_tokens=False).to(dev)
        state["a"] = len(tok(prompt[: prompt.rindex("<|im_start|>user")], add_special_tokens=False).input_ids)
        state["b"] = enc.input_ids.shape[1]
        return enc, lambda: lp(model(**enc).logits[0, -1].float(), lid, key, wrong)

    rows, t0, n = [], time.perf_counter(), 0
    total = len(scr) * len(items) * 2
    for si, (sid, g, v) in enumerate(scr):
        h0, h3 = S.history(sid, "L0", g, version=v), S.history(sid, "L3", g, version=v)
        for ii, it in enumerate(items):
            cf = (ii + si) % 2 == 0
            for form in ("false_belief", "plain"):
                text, key, wrong = S.probe(sid, it, cf, form)
                mk = lambda h: tok.apply_chat_template(h + [{"role": "user", "content": text}], tokenize=False,  # noqa: E731
                                                       add_generation_prompt=True, enable_thinking=False) + PREFIX
                res = {}
                with torch.no_grad():
                    _, f0 = run(mk(h0), key, wrong)
                    state["ops"] = {}
                    res["L0"] = f0()
                    for k, vec in add.items():
                        state["ops"] = {layer_of[k] - 1: ("add", vec)}
                        res[k] = f0()
                    _, f3 = run(mk(h3), key, wrong)
                    state["ops"] = {}
                    res["L3"] = f3()
                    for k, d in abl.items():
                        state["ops"] = {l - 1: ("ablate", u) for l, u in d.items()}
                        res[k] = f3()
                    state["ops"] = {}
                rows.append({"item": it["id"], "script": f"{sid}-{g[0]}-v{v}", "form": form, "lp": res})
                n += 1
                if n % 10 == 0:
                    el = time.perf_counter() - t0
                    print(f"  {n}/{total}  |  {el / 60:.0f} min  |  about {el / n * (total - n) / 60:.0f} min left", flush=True)
                    (OUT / "steering3_dev.partial.json").write_text(json.dumps({"args": vars(args), "rows": rows}))
    for h in handles:
        h.remove()
    (OUT / "steering3_dev.json").write_text(json.dumps({"args": vars(args), "directions_from": rest, "rows": rows}))
    print(f"done: {len(rows)} rows in {(time.perf_counter() - t0) / 60:.0f} min -> {OUT / 'steering3_dev.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
