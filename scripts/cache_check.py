"""Does the prompt cache change answers in the real campaign pattern? Dev items only, no test data.

    python scripts/cache_check.py --model qwen3-8b-huihui

For two histories (L0 and L3, storyline 01, female, version 1) and the first N dev items, each probe is sent three
ways: (1) cache on, in campaign order (the history stays cached, only the probe is new); (2) cache off; (3) cache off
again (run-to-run determinism). Reports answer agreement and the largest gaps in the renormalized letter probability.
Writes results/fidelity/<model>_cache.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import stimuli as S  # noqa: E402
from campaign import parse_answer  # noqa: E402
from fidelity_check import Server, letter_probs  # noqa: E402
from known_items import FMT  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=25)
    args = ap.parse_args()
    srv = Server(args.model)
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = [i for i in items if i["split"] == "dev"][: args.n]

    def ask(msgs, cache):
        r = srv.chat(msgs, max_tokens=40, response_format=FMT, logprobs=True, top_logprobs=10, cache_prompt=cache)
        c = r["choices"][0]
        return parse_answer(c["message"]["content"])[0], letter_probs(c).get("A")

    rows = []
    for cond in ("L0", "L3"):
        hist = S.history("01", cond, "female")
        probes = [S.probe("01", it, k % 2 == 0, "false_belief")[0] for k, it in enumerate(items)]
        on = [ask(hist + [{"role": "user", "content": p}], True) for p in probes]
        off = [ask(hist + [{"role": "user", "content": p}], False) for p in probes]
        off2 = [ask(hist + [{"role": "user", "content": p}], False) for p in probes]
        for it, a, b, c in zip(items, on, off, off2):
            rows.append({"cond": cond, "item": it["id"], "on": a, "off": b, "off_again": c})
    n = len(rows)
    agree = sum(r["on"][0] == r["off"][0] for r in rows)
    agree_off = sum(r["off"][0] == r["off_again"][0] for r in rows)
    gap = sorted(abs((r["on"][1] or 0) - (r["off"][1] or 0)) for r in rows)
    gap_off = sorted(abs((r["off"][1] or 0) - (r["off_again"][1] or 0)) for r in rows)
    rep = {"model": args.model, "trials": n,
           "answer_agreement_cache_on_vs_off": agree / n, "answer_agreement_off_vs_off": agree_off / n,
           "p_gap_on_vs_off": {"median": gap[n // 2], "max": gap[-1], "share_over_0.02": sum(g > 0.02 for g in gap) / n},
           "p_gap_off_vs_off": {"median": gap_off[n // 2], "max": gap_off[-1]}, "rows": rows}
    out = ROOT / "results" / "fidelity" / f"{args.model}_cache.json"
    out.write_text(json.dumps(rep, indent=1))
    print(f"{args.model}: {n} trials")
    print(f"  same answer, cache on vs off:  {agree}/{n}")
    print(f"  same answer, off vs off again: {agree_off}/{n}")
    print(f"  P(A) gap on vs off: median {gap[n // 2]:.4f}, max {gap[-1]:.4f}, over 0.02 in {sum(g > 0.02 for g in gap)}/{n}")
    print(f"  P(A) gap off vs off: median {gap_off[n // 2]:.4f}, max {gap_off[-1]:.4f}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
