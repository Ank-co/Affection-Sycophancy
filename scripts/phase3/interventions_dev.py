"""Phase III, step 2 (exploration, dev items only): attention, activation patching and steering in Qwen3-8B.

    python scripts/phase3/interventions_dev.py --exp attention --weights C:/llm/hf/Qwen3-8B
    python scripts/phase3/interventions_dev.py --exp patching  --weights C:/llm/hf/Qwen3-8B
    python scripts/phase3/interventions_dev.py --exp steering  --weights C:/llm/hf/Qwen3-8B

All three compare a neutral (L0) and a loving (L3) history for the same item and script. The final user turn (bridge,
question, stated belief) and the answer prefix are identical text in both, so their last k tokens are aligned.

attention  Share of attention from the answer position to: the stated belief ("I told her the answer is ..."), the
           question and options, the user turns of the history, the assistant turns of the history; per layer, mean
           over heads. Needs eager attention (slower).
patching   For each layer, the residual stream over the final user turn is copied from the L3 run into the L0 run.
           If the preference for the correct option moves toward its L3 value, that layer's final-turn state carries
           the effect. Reported as the share of the L3 - L0 gap recovered.
steering   The L3 - L0 direction at the answer position (from the dev activations, results/internals/.../directions.npz,
           written by explore_dev.py) is added at one layer over the final user turn of *neutral* conversations, at
           several strengths; control: random directions of the same norm. Measures: preference for the correct
           option in the false-belief form (compliance) and in the plain form (side effect on accuracy).
Writes results/internals/qwen3-8b/<exp>_dev.json. Resumable at the level of the whole experiment only (short runs).
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

PREFIX = '{\n  "answer": "'
OUT = ROOT / "results" / "internals" / "qwen3-8b"


def load(weights, eager=False):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    tok = AutoTokenizer.from_pretrained(weights)
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           bnb_4bit_use_double_quant=True)
    kw = {"device_map": {"": 0}, "dtype": torch.bfloat16, "quantization_config": q}
    if eager:
        kw["attn_implementation"] = "eager"
    return tok, AutoModelForCausalLM.from_pretrained(weights, **kw).eval()


def trials(n_items, n_scripts):
    ids = set(json.loads((ROOT / "results" / "known_items" / "known_8b_dev.json").read_text()))
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = sorted((i for i in items if i["id"] in ids and i["split"] == "dev"), key=lambda i: i["id"])[:n_items]
    for si, (sid, g, v) in enumerate(scripts_for(10)[:n_scripts]):
        for ii, it in enumerate(items):
            yield sid, g, v, it, (ii + si) % 2 == 0


def build(tok, sid, g, v, it, cf, cond, form="false_belief"):
    hist = S.history(sid, cond, g, version=v)
    text, key, wrong = S.probe(sid, it, cf, form)
    prompt = tok.apply_chat_template(hist + [{"role": "user", "content": text}], tokenize=False,
                                     add_generation_prompt=True, enable_thinking=False) + PREFIX
    start = prompt.rindex("<|im_start|>user")
    k = len(tok(prompt[start:], add_special_tokens=False).input_ids)       # final turn + answer prefix
    return prompt, key, wrong, k


def lp(logits, lid, key, wrong):
    return float(logits[lid[key]] - logits[lid[wrong]])                    # log-odds of the correct option


def layer_out(output):
    return output[0] if isinstance(output, tuple) else output


def with_out(output, h):
    return (h,) + tuple(output[1:]) if isinstance(output, tuple) else h


# ---------------------------------------------------------------- attention
def run_attention(tok, model, lid, args):
    import torch
    layers = model.model.layers
    rows, grab = [], {}

    def hook(i):
        def f(_m, _inp, output):
            if isinstance(output, tuple) and len(output) > 1 and output[1] is not None:
                grab[i] = output[1][0, :, -1, :].float().mean(0).cpu()          # mean over heads, last query
        return f
    hs = [layers[i].self_attn.register_forward_hook(hook(i)) for i in range(len(layers))]
    for sid, g, v, it, cf in trials(args.items, args.scripts):
        for cond in ("L0", "L3"):
            prompt, key, wrong, k = build(tok, sid, g, v, it, cf, cond)
            enc = tok(prompt, return_tensors="pt", add_special_tokens=False, return_offsets_mapping=True)
            offs = enc.pop("offset_mapping")[0].tolist()
            spans = {"stated_belief": (prompt.rindex("I told "), prompt.rindex("<|im_end|>")),
                     "question": (prompt.rindex("<|im_start|>user"), prompt.rindex("I told ")),
                     "history": (0, prompt.rindex("<|im_start|>user"))}
            masks = {n: torch.tensor([a <= s < b for s, _ in offs]) for n, (a, b) in spans.items()}
            u_starts = [i for i in range(len(prompt)) if prompt.startswith("<|im_start|>user", i)][:-1]
            a_starts = [i for i in range(len(prompt)) if prompt.startswith("<|im_start|>assistant", i)][:-1]
            role = np.zeros(len(offs), dtype=int)
            for i, (s, _) in enumerate(offs):
                prev_u = max([u for u in u_starts if u <= s], default=-1)
                prev_a = max([a for a in a_starts if a <= s], default=-1)
                role[i] = 1 if prev_u > prev_a else (2 if prev_a > prev_u else 0)
            hist_user = masks["history"] & torch.tensor(role == 1)
            hist_asst = masks["history"] & torch.tensor(role == 2)
            with torch.no_grad():
                logits = model(**enc.to(model.device)).logits[0, -1].float()   # weights come from the hooks
            row = {"cond": cond, "item": it["id"], "script": f"{sid}-{g[0]}-v{v}", "lp": lp(logits, lid, key, wrong),
                   "attn": {n: [float(grab[i][m].sum()) for i in range(len(layers))]
                            for n, m in (("stated_belief", masks["stated_belief"]), ("question", masks["question"]),
                                         ("history_user", hist_user), ("history_assistant", hist_asst))}}
            rows.append(row)
    for h in hs:
        h.remove()
    return rows


# ---------------------------------------------------------------- patching
def run_patching(tok, model, lid, args):
    import torch
    layers = model.model.layers
    L = len(layers)
    which = list(range(0, L, args.stride)) + ([L - 1] if (L - 1) % args.stride else [])
    rows, store = [], {}

    def capture(i):
        def f(_m, _inp, output):
            store[i] = layer_out(output)[:, -store["k"]:, :].detach().clone()
        return f

    def patch(i):
        def f(_m, _inp, output):
            if store.get("patch") != i:
                return None
            h = layer_out(output).clone()
            h[:, -store["k"]:, :] = store[i]
            return with_out(output, h)
        return f
    for sid, g, v, it, cf in trials(args.items, args.scripts):
        p3, key, wrong, k = build(tok, sid, g, v, it, cf, "L3")
        p0, _, _, k0 = build(tok, sid, g, v, it, cf, "L0")
        assert k == k0
        store["k"] = k
        hs = [layers[i].register_forward_hook(capture(i)) for i in which]
        with torch.no_grad():
            lp3 = lp(model(**tok(p3, return_tensors="pt", add_special_tokens=False).to(model.device)).logits[0, -1].float(), lid, key, wrong)
        for h in hs:
            h.remove()
        enc0 = tok(p0, return_tensors="pt", add_special_tokens=False).to(model.device)
        hs = [layers[i].register_forward_hook(patch(i)) for i in which]
        with torch.no_grad():
            store["patch"] = None
            lp0 = lp(model(**enc0).logits[0, -1].float(), lid, key, wrong)
            patched = {}
            for i in which:
                store["patch"] = i
                patched[i] = lp(model(**enc0).logits[0, -1].float(), lid, key, wrong)
        for h in hs:
            h.remove()
        rows.append({"item": it["id"], "script": f"{sid}-{g[0]}-v{v}", "lp_L0": lp0, "lp_L3": lp3,
                     "patched": {str(i): patched[i] for i in which}})
        print(f"  {it['id']} {sid}-{g[0]}-v{v}: L0 {lp0:+.2f}  L3 {lp3:+.2f}", flush=True)
    return rows


# ---------------------------------------------------------------- steering
def run_steering(tok, model, lid, args):
    import torch
    d = np.load(OUT / "directions.npz")
    layer = args.layer
    u = torch.tensor(d[f"L3_minus_L0_answer_{layer}"], dtype=torch.bfloat16, device=model.device)
    scale = float(torch.linalg.norm(u.float()))
    gen = torch.Generator(device="cpu").manual_seed(0)
    rand = [torch.randn(u.shape[0], generator=gen) for _ in range(args.n_random)]
    rand = [(r / r.norm() * scale).to(torch.bfloat16).to(model.device) for r in rand]
    state = {"vec": None, "k": 0}

    def hook(_m, _inp, output):
        if state["vec"] is None:
            return None
        h = layer_out(output).clone()
        h[:, -state["k"]:, :] += state["vec"]
        return with_out(output, h)
    hd = model.model.layers[layer].register_forward_hook(hook)
    rows = []
    for sid, g, v, it, cf in trials(args.items, args.scripts):
        for form in ("false_belief", "plain"):
            p0, key, wrong, k = build(tok, sid, g, v, it, cf, "L0", form)
            enc = tok(p0, return_tensors="pt", add_special_tokens=False).to(model.device)
            state["k"] = k
            res = {}
            with torch.no_grad():
                for a in args.alphas:
                    state["vec"] = None if a == 0 else a * u
                    res[f"love_{a}"] = lp(model(**enc).logits[0, -1].float(), lid, key, wrong)
                for j, r in enumerate(rand):
                    for a in args.alphas:
                        if a == 0:
                            continue
                        state["vec"] = a * r
                        res[f"random{j}_{a}"] = lp(model(**enc).logits[0, -1].float(), lid, key, wrong)
            state["vec"] = None
            rows.append({"item": it["id"], "script": f"{sid}-{g[0]}-v{v}", "form": form, "lp": res})
    hd.remove()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", choices=["attention", "patching", "steering"], required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--items", type=int, default=30)
    ap.add_argument("--scripts", type=int, default=3)
    ap.add_argument("--stride", type=int, default=2, help="patching: every n-th layer")
    ap.add_argument("--layer", type=int, default=24, help="steering layer (must be in directions.npz)")
    ap.add_argument("--alphas", type=float, nargs="+", default=[0, 1, 2, 4])
    ap.add_argument("--n-random", type=int, default=3)
    args = ap.parse_args()
    tok, model = load(args.weights, eager=args.exp == "attention")
    lid = letter_ids(tok)
    t0 = time.perf_counter()
    rows = {"attention": run_attention, "patching": run_patching, "steering": run_steering}[args.exp](tok, model, lid, args)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{args.exp}_dev.json").write_text(json.dumps({"args": vars(args), "rows": rows}))
    print(f"done: {len(rows)} rows in {(time.perf_counter() - t0) / 60:.0f} min -> {OUT / (args.exp + '_dev.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
