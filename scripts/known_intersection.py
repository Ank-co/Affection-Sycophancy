"""Known items shared by every model of a family (pre-registration §4), from the summaries of known_items.py.

    python scripts/known_intersection.py --name 8b --split test --models qwen3-8b qwen3-8b-huihui qwen3-8b-mlabonne

Writes results/known_items/known_<name>_<split>.json (sorted item ids) and prints the counts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--split", choices=["dev", "test"], required=True)
    ap.add_argument("--models", nargs="+", required=True)
    args = ap.parse_args()
    sets = {}
    for m in args.models:
        s = json.loads((ROOT / "results" / "known_items" / m / f"{args.split}_summary.json").read_text())
        sets[m] = set(s["known_ids"])
        print(f"{m:24s} known {len(sets[m]):4d} of {s['items']}  (accuracy over both orders {s['accuracy_both_orders']:.3f})")
    shared = sorted(set.intersection(*sets.values()))
    out = ROOT / "results" / "known_items" / f"known_{args.name}_{args.split}.json"
    out.write_text(json.dumps(shared, indent=0))
    print(f"shared by all {len(args.models)}: {len(shared)}  ->  {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
