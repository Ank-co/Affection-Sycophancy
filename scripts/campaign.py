"""Phase II campaign (H1 to H9, behavioural). One model per run; resumable; cells run in priority order.

    python scripts/campaign.py --model qwen3.6-35b-base-i1 --dry-run          # plan, request count, ETA
    python scripts/campaign.py --model qwen3.6-35b-base-i1 --split dev --limit 3   # smoke test on dev items
    python scripts/campaign.py --model qwen3.6-35b-base-i1 --max-hours 9      # one night on the test split

The test split is refused until docs/preregistration.md is committed AND pushed (design §9: the public push is the
time stamp). Dev runs are never used for confirmatory analysis.

Grid (docs/design.md §3, §4, §9). A script = storyline x gender x version.
- core cells L0, C, L3 (acknowledging, neutral backdrop): 20 scripts (5 x 2 x 2);
- every other cell: 10 scripts, version counterbalanced (v1 for the female persona in 01, 03, 05 and the male persona
  in 02, 04; v2 otherwise), so that version is never confounded with condition;
- false-belief form in every cell; plain form at L0 and L3 (H4, H6);
- one pushback after a correct false-belief answer at L0, C, L3 and L3 reciprocating (H3, H9), level B0 to B3 rotated
  so that each item meets every level across scripts and the level is balanced against the option order;
- option order: correct option first for half of the item x script pairs, balanced within each cell.
Greedy, thinking off, JSON under grammar, no system prompt, cache on (fidelity check: results/fidelity/).
Output: results/campaign/<model>/<split>.jsonl (one line per item x script x form) and a meta file per session.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import stimuli as S  # noqa: E402

STORYLINES = ["01", "02", "03", "04", "05"]
GENDERS = ["female", "male"]
PB_LEVELS = ["B0", "B1", "B2", "B3"]

# name, condition, warmth, backdrop, scripts (20 or 10), plain form, pushback. Priority order: if a night is cut short,
# the cells that carry the primary hypothesis are complete first.
CELLS = [
    ("L0", "L0", "acknowledging", "neutral", 20, True, True),            # H1, H1b, H3, H4, H6, H7
    ("L3", "L3", "acknowledging", "neutral", 20, True, True),            # H1, H1b, H3, H4, H6, H7
    ("C", "C", "acknowledging", "neutral", 20, False, True),             # H1b, H3
    ("L3_recip", "L3", "reciprocating", "neutral", 10, False, True),     # H9
    ("L1", "L1", "acknowledging", "neutral", 10, False, False),          # H2
    ("L2", "L2", "acknowledging", "neutral", 10, False, False),          # H2
    ("L4", "L4", "acknowledging", "neutral", 10, False, False),          # H2
    ("L3_sudden", "L3_sudden", "acknowledging", "neutral", 10, False, False),      # H8
    ("L3_constant", "L3_constant", "acknowledging", "neutral", 10, False, False),  # H8
    ("L0_sad", "L0", "acknowledging", "sad", 10, False, False),          # exploratory: backdrop
    ("L3_sad", "L3", "acknowledging", "sad", 10, False, False),
    ("L0_despair", "L0", "acknowledging", "despair", 10, False, False),
    ("L3_despair", "L3", "acknowledging", "despair", 10, False, False),
]


def scripts_for(n: int) -> list[tuple[str, str, int]]:
    """(storyline, gender, version) for a cell with 20 or 10 scripts."""
    if n == 20:
        return [(s, g, v) for s in STORYLINES for g in GENDERS for v in (1, 2)]
    out = []
    for i, s in enumerate(STORYLINES):
        for g in GENDERS:
            v1 = (g == "female") == (i % 2 == 0)       # 01, 03, 05: female v1; 02, 04: male v1
            out.append((s, g, 1 if v1 else 2))
    return out


def plan(n_items: int) -> list[dict]:
    rows = []
    for name, cond, warmth, backdrop, n, plain, pb in CELLS:
        sc = scripts_for(n)
        rows.append({"cell": name, "scripts": len(sc), "items": n_items,
                     "requests_max": len(sc) * n_items * (1 + plain + pb)})
    return rows


def parse_answer(raw: str):
    """(answer, confidence). Strict JSON first; if the JSON is cut short (the model pads with whitespace until
    max_tokens, seen in 0.4% of the first test rows), the letter it already committed to is read from the text.
    A non-answer is only a reply with no valid letter (pre-registration §6; deviation log: docs/deviations.md)."""
    try:
        a = json.loads(raw)
        return a.get("answer"), a.get("confidence")
    except Exception:
        m = re.search(r'"answer"\s*:\s*"([AB])"', raw or "")
        c = re.search(r'"confidence"\s*:\s*([0-9]*\.?[0-9]+)', raw or "")
        return (m.group(1) if m else None), (float(c.group(1)) if c else None)


def preregistration_pushed() -> tuple[bool, str]:
    """True if docs/preregistration.md is tracked, unchanged since its last commit, and that commit is on the remote."""
    def git(*a):
        return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True)
    try:
        if git("ls-files", "--error-unmatch", "docs/preregistration.md").returncode != 0:
            return False, "docs/preregistration.md is not committed"
        if git("diff", "--quiet", "HEAD", "--", "docs/preregistration.md").returncode != 0:
            return False, "docs/preregistration.md has uncommitted changes"
        last = git("log", "-1", "--format=%H", "--", "docs/preregistration.md").stdout.strip()
        git("fetch", "--quiet")
        remote = git("branch", "-r", "--contains", last).stdout.strip()
        if not remote:
            return False, f"commit {last[:8]} of the pre-registration is not on the remote yet (git push)"
        return True, last
    except FileNotFoundError:
        return False, "git not found"


def head_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--split", choices=["test", "dev"], default="test")
    ap.add_argument("--known", help="JSON list of known item ids (default: results/known_items/pair_known_<split>.json)")
    ap.add_argument("--cells", help="comma-separated subset of cells, e.g. L0,L3")
    ap.add_argument("--limit", type=int, default=0, help="first N items only (smoke test)")
    ap.add_argument("--max-hours", type=float, default=0, help="stop cleanly after this many hours (0 = no limit)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan and the ETA, call nothing")
    ap.add_argument("--sec-per-request", type=float, default=2.34, help="for the ETA (smoke test: 2.34 s for the 35B)")
    args = ap.parse_args()

    known = Path(args.known) if args.known else ROOT / "results" / "known_items" / f"pair_known_{args.split}.json"
    ids = set(json.loads(known.read_text()))
    items = [json.loads(l) for l in (ROOT / "items" / "truthfulqa_binary.jsonl").read_text(encoding="utf-8").splitlines()]
    items = sorted((i for i in items if i["id"] in ids and i["split"] == args.split), key=lambda i: i["id"])
    items = items[: args.limit or None]
    cells = [c for c in CELLS if not args.cells or c[0] in args.cells.split(",")]
    if args.cells:
        unknown = set(args.cells.split(",")) - {c[0] for c in CELLS}
        if unknown:
            sys.exit(f"unknown cells: {sorted(unknown)}")

    out = ROOT / "results" / "campaign" / args.model / f"{args.split}.jsonl"
    done = set()
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            done.add((r["cell"], r["item"], r["storyline"], r["gender"], r["version"], r["form"]))

    # Plan and ETA. Pushback is asked only after a correct false-belief answer: ~0.93 in the pilot.
    print(f"{args.model}, split {args.split}, {len(items)} items, known-item file {known.name}")
    tot_left = 0.0
    for name, cond, warmth, backdrop, n, plain, pb in cells:
        sc = scripts_for(n)
        forms = 1 + plain
        todo = sum(1 for s, g, v in sc for it in items for f in (["false_belief"] + ["plain"] * plain)
                   if (name, it["id"], s, g, v, f) not in done)
        req = todo * (1 + (0.93 if pb else 0) / forms)
        tot_left += req
        print(f"  {name:12s} {len(sc):2d} scripts  forms {forms}  pushback {'yes' if pb else 'no ':3s}  "
              f"rows left {todo:6d}  ~{req * args.sec_per_request / 3600:5.1f} h")
    print(f"  total left ~{tot_left:,.0f} requests, ~{tot_left * args.sec_per_request / 3600:.1f} h "
          f"at {args.sec_per_request} s per request")
    if args.dry_run:
        return 0

    if args.split == "test":
        ok, why = preregistration_pushed()
        if not ok:
            sys.exit(f"Refused: the test split opens only after the pre-registration is pushed ({why}).")
        prereg = why
    else:
        prereg = None

    from fidelity_check import Server, letter_probs  # noqa: E402  (needs requests and the server)
    from known_items import FMT  # noqa: E402

    srv = Server(args.model)

    def ask(msgs):
        for attempt in range(3):
            try:
                t0 = time.perf_counter()
                r = srv.chat(msgs, max_tokens=40, response_format=FMT, logprobs=True, top_logprobs=10,
                             cache_prompt=True)
                c = r["choices"][0]
                raw = c["message"]["content"]
                return raw, *parse_answer(raw), letter_probs(c), time.perf_counter() - t0
            except Exception as e:  # server restart, timeout: wait and retry, then stop cleanly (resumable)
                print(f"  request failed ({e.__class__.__name__}: {e}); retry {attempt + 1}/3 in 30 s")
                time.sleep(30)
        sys.exit("Server unreachable after 3 attempts; stopped. Rerun the same command to resume.")

    out.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    meta = {"model": args.model, "split": args.split, "started_utc": started.isoformat(), "commit": head_commit(),
            "preregistration_commit": prereg, "known_file": known.name, "n_items": len(items),
            "cells": [c[0] for c in cells], "python": platform.python_version(), "argv": sys.argv[1:]}
    try:  # model file and server settings, for the record
        import requests
        from fidelity_check import BASE
        pr = requests.get(f"{BASE}/props", params={"model": args.model}, headers=srv.h, timeout=30).json()
        meta["server_props"] = {k: pr.get(k) for k in ("model_path", "build_info", "total_slots", "chat_template")
                                if k in pr}
        meta["server_props"]["default_generation_settings"] = pr.get("default_generation_settings", {}).get("params")
    except Exception as e:
        meta["server_props"] = f"unavailable: {e.__class__.__name__}"
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    (out.parent / f"meta-{args.split}-{stamp}.json").write_text(json.dumps(meta, indent=1))

    deadline = time.time() + args.max_hours * 3600 if args.max_hours else None
    n_req, t_start = 0, time.perf_counter()
    with open(out, "a", encoding="utf-8") as f:
        for name, cond, warmth, backdrop, n, plain, pb in cells:
            sc = scripts_for(n)
            print(f"cell {name}: {len(sc)} scripts")
            for si, (sid, g, v) in enumerate(sc):
                hist = S.history(sid, cond, g, backdrop=backdrop, version=v, warmth=warmth)
                for ii, it in enumerate(items):
                    if deadline and time.time() > deadline:
                        print(f"--max-hours reached after {n_req} requests; rerun to resume.")
                        return 0
                    cf = (ii + si) % 2 == 0                         # option order, balanced within the cell
                    pb_level = PB_LEVELS[(ii // 2 + si) % 4]        # every level per item across scripts, x both orders
                    for form in ["false_belief"] + (["plain"] if plain else []):
                        k = (name, it["id"], sid, g, v, form)
                        if k in done:
                            continue
                        text, key, wrong = S.probe(sid, it, cf, form)
                        msgs = hist + [{"role": "user", "content": text}]
                        raw, ans, conf, p, dt = ask(msgs); n_req += 1
                        rec = {"cell": name, "condition": cond, "warmth": warmth, "backdrop": backdrop,
                               "item": it["id"], "category": it.get("category"), "storyline": sid, "gender": g,
                               "version": v, "script": f"{sid}-{g[0]}-v{v}", "form": form, "correct_first": cf,
                               "key": key, "wrong": wrong, "raw": raw, "answer": ans, "confidence": conf,
                               "p_correct": p.get(key), "seconds": round(dt, 3)}
                        if pb and form == "false_belief" and ans == key:
                            msgs2 = msgs + [{"role": "assistant", "content": raw},
                                            {"role": "user", "content": S.PUSHBACK[pb_level]}]
                            raw2, ans2, conf2, p2, dt2 = ask(msgs2); n_req += 1
                            rec.update({"pushback": pb_level, "raw_after": raw2, "answer_after": ans2,
                                        "confidence_after": conf2, "p_correct_after": p2.get(key),
                                        "seconds_after": round(dt2, 3)})
                        f.write(json.dumps(rec) + "\n"); f.flush(); done.add(k)
                el = time.perf_counter() - t_start
                print(f"  script {si + 1}/{len(sc)} done  |  {n_req} requests  |  "
                      f"{el / max(n_req, 1):.2f} s per request  |  {el / 60:.0f} min")
    print(f"done: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
