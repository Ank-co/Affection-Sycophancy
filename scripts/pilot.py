"""Pilot (dev items only): variance, effect size and throughput, to size the confirmatory run. Not a test of H1.

    python scripts/pilot.py --model qwen3.6-35b-base-i1
    python scripts/pilot.py --model qwen3.6-35b-abliterated

Design of the pilot:
- items: dev items known by both models of the 35B pair (results/known_items/pair_known_dev.json);
- conditions: L0 (neutral), C (warm disclosure), L3 (gradual love), fixed acknowledging assistant turns,
  neutral backdrop, first version of each cell (AI-generated);
- scripts: 5 storylines x 2 genders;
- per item and script: false-belief form (all conditions), plain form (L0 and L3), and after a correct
  false-belief answer, one pushback (B0 or B2, alternating by item) followed by a second answer;
- option order balanced: correct option first for half of the item x script pairs.
Greedy, thinking off, JSON under grammar, no system prompt, cache on. Runs script by script so that each 12-turn
history is processed once and reused from the cache. Resumable: results/pilot/<model>.jsonl.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import stimuli as S  # noqa: E402
from fidelity_check import Server, letter_probs  # noqa: E402
from known_items import FMT  # noqa: E402

CONDS = ["L0", "C", "L3"]
STORYLINES = ["01", "02", "03", "04", "05"]
GENDERS = ["female", "male"]


def ask(srv, msgs):
    t0 = time.perf_counter()
    r = srv.chat(msgs, max_tokens=40, response_format=FMT, logprobs=True, top_logprobs=10, cache_prompt=True)
    c = r["choices"][0]
    try:
        ans = json.loads(c["message"]["content"])
    except Exception:
        ans = {}
    return c["message"]["content"], ans.get("answer"), ans.get("confidence"), letter_probs(c), time.perf_counter() - t0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3.6-35b-base-i1")
    ap.add_argument("--limit", type=int, default=0, help="first N items only (quick test)")
    args = ap.parse_args()
    ids = set(json.loads((ROOT / "results" / "known_items" / "pair_known_dev.json").read_text()))
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = [i for i in items if i["id"] in ids][: args.limit or None]
    out = ROOT / "results" / "pilot" / f"{args.model}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(l); done.add((r["item"], r["storyline"], r["gender"], r["condition"], r["form"]))
    srv = Server(args.model)
    scripts = [(s, g, c) for s in STORYLINES for g in GENDERS for c in CONDS]
    total = len(scripts) * len(items); n = 0; t_start = time.perf_counter(); n_req = 0
    with open(out, "a", encoding="utf-8") as f:
        for si, (sid, g, cond) in enumerate(scripts):
            hist = S.history(sid, cond, g)
            for ii, it in enumerate(items):
                n += 1
                cf = (ii + si) % 2 == 0
                forms = ["false_belief"] + (["plain"] if cond in ("L0", "L3") else [])
                for form in forms:
                    k = (it["id"], sid, g, cond, form)
                    if k in done:
                        continue
                    text, key, wrong = S.probe(sid, it, cf, form)
                    msgs = hist + [{"role": "user", "content": text}]
                    raw, ans, conf, p, dt = ask(srv, msgs); n_req += 1
                    rec = {"item": it["id"], "storyline": sid, "gender": g, "condition": cond, "form": form,
                           "correct_first": cf, "key": key, "wrong": wrong, "answer": ans, "confidence": conf,
                           "p_correct": p.get(key), "seconds": round(dt, 3)}
                    if form == "false_belief" and ans == key:
                        pb = "B0" if ii % 2 == 0 else "B2"
                        msgs2 = msgs + [{"role": "assistant", "content": raw}, {"role": "user", "content": S.PUSHBACK[pb]}]
                        _, ans2, conf2, p2, dt2 = ask(srv, msgs2); n_req += 1
                        rec.update({"pushback": pb, "answer_after": ans2, "confidence_after": conf2,
                                    "p_correct_after": p2.get(key), "seconds_after": round(dt2, 3)})
                    f.write(json.dumps(rec) + "\n"); f.flush(); done.add(k)
                if n % 100 == 0:
                    el = time.perf_counter() - t_start
                    rate = el / max(n_req, 1)
                    print(f"  {n}/{total} item x script  |  {rate:.2f} s per request  |  {el / 60:.0f} min elapsed")
    print(f"done: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
