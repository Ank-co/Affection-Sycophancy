"""Phase III, step 0: does the PyTorch model reproduce the GGUF answers? Dev items only.

    python scripts/phase3/agreement_check.py --model qwen3-8b --weights C:/llm/hf/Qwen3-8B

Reads results/campaign/<model>/dev.jsonl (a small dev run of the campaign runner with the llama.cpp server), rebuilds
every trial exactly (same history, probe, chat template, thinking off), feeds it to the original Hugging Face weights in
PyTorch with the answer's JSON prefix up to the letter, and compares the renormalized probability of the correct letter
and the answer with the GGUF run. Design §7 and deviation list: the internal analysis is valid only if the PyTorch
setup gives the same behaviour on dev items. Writes results/internals/<model>/agreement_dev.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import stimuli as S  # noqa: E402


def load_model(weights: str, quant: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(weights)
    free, total = torch.cuda.mem_get_info()
    print(f"GPU memory free before loading: {free / 2**30:.1f} of {total / 2**30:.1f} GiB "
          "(stop llama-server first if this is low)", flush=True)
    # Everything on the GPU: "auto" plans with a safety margin and refuses a 4-bit model that does fit in 8 GiB.
    kw = {"device_map": {"": 0}, "dtype": torch.bfloat16}
    if quant == "4bit":
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16,
                                                       bnb_4bit_use_double_quant=True)
    elif quant == "8bit":
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    model = AutoModelForCausalLM.from_pretrained(weights, **kw).eval()
    return tok, model


def letter_ids(tok):
    ids = {}
    for L in ("A", "B"):
        t = tok.encode(L, add_special_tokens=False)
        assert len(t) == 1, f"letter {L} is not a single token: {t}"
        ids[L] = t[0]
    return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="server name of the GGUF run (results/campaign/<model>/dev.jsonl)")
    ap.add_argument("--weights", required=True, help="Hugging Face weights folder")
    ap.add_argument("--quant", choices=["4bit", "8bit", "none"], default="4bit")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    import torch

    rows = [json.loads(l) for l in (ROOT / "results" / "campaign" / args.model / "dev.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r.get("answer") in ("A", "B") and r.get("p_correct") is not None][: args.limit or None]
    items = {i["id"]: i for i in map(json.loads, (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines())}
    tok, model = load_model(args.weights, args.quant)
    ids = letter_ids(tok)
    out, t0 = [], time.perf_counter()
    for k, r in enumerate(rows):
        hist = S.history(r["storyline"], r["condition"], r["gender"], backdrop=r["backdrop"], version=r["version"],
                         warmth=r["warmth"])
        text, key, wrong = S.probe(r["storyline"], items[r["item"]], r["correct_first"], r["form"])
        assert key == r["key"]
        prompt = tok.apply_chat_template(hist + [{"role": "user", "content": text}], tokenize=False,
                                         add_generation_prompt=True, enable_thinking=False)
        raw = r["raw"]                       # e.g. '{\n  "answer": "A", ...': keep up to the quote before the letter
        i = raw.index('"answer"'); j = raw.index('"', raw.index(":", i))
        prefix = raw[: j + 1]
        enc = tok(prompt + prefix, return_tensors="pt", add_special_tokens=False).to(model.device)
        with torch.no_grad():
            logits = model(**enc).logits[0, -1].float()
        pa, pb = torch.softmax(logits[[ids["A"], ids["B"]]], 0).tolist()
        p = {"A": pa, "B": pb}
        out.append({"cell": r["cell"], "item": r["item"], "script": r["script"], "form": r["form"], "key": key,
                    "gguf_answer": r["answer"], "gguf_p_correct": r["p_correct"],
                    "torch_answer": max(p, key=p.get), "torch_p_correct": p[key]})
        if (k + 1) % 50 == 0:
            print(f"  {k + 1}/{len(rows)}  {(time.perf_counter() - t0) / (k + 1):.2f} s per trial", flush=True)
            part = ROOT / "results" / "internals" / args.model
            part.mkdir(parents=True, exist_ok=True)
            (part / "agreement_dev.partial.json").write_text(json.dumps(out))   # progress, overwritten at the end
    import numpy as np
    agree = np.mean([o["gguf_answer"] == o["torch_answer"] for o in out])
    lg = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))  # noqa: E731
    g = np.array([lg(o["gguf_p_correct"]) for o in out]); t = np.array([lg(o["torch_p_correct"]) for o in out])
    rep = {"model": args.model, "weights": args.weights, "quant": args.quant, "trials": len(out),
           "answer_agreement": float(agree), "logit_correlation": float(np.corrcoef(g, t)[0, 1]),
           "mean_abs_logit_gap": float(np.mean(np.abs(g - t))), "mean_logit_gap_torch_minus_gguf": float(np.mean(t - g)),
           "by_cell": {c: {"gguf_adopt": float(np.mean([o["gguf_answer"] != o["key"] for o in out if o["cell"] == c and o["form"] == "false_belief"] or [np.nan])),
                           "torch_adopt": float(np.mean([o["torch_answer"] != o["key"] for o in out if o["cell"] == c and o["form"] == "false_belief"] or [np.nan]))}
                       for c in sorted({o["cell"] for o in out})},
           "rows": out}
    dest = ROOT / "results" / "internals" / args.model
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "agreement_dev.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
