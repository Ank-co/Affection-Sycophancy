# Results

Write-ups are the `RESULTATS*.md` files (in English despite the name, kept for the links of the pre-registrations).

| Folder | Phase | Write-up | Content |
|---|---|---|---|
| [fidelity/](fidelity/) | 0 | [RESULTATS.md](fidelity/RESULTATS.md) | template fidelity and cache checks, one JSON per model |
| [known_items/](known_items/) | 0 | [RESULTATS.md](known_items/RESULTATS.md) | items each model knows; confirmatory item sets |
| [pilot/](pilot/) | 0 | [RESULTATS.md](pilot/RESULTATS.md) | dev pilot of the 35B models |
| [campaign/](campaign/) | II | [35B](campaign/RESULTATS-35B.md), [8B](campaign/RESULTATS-8B.md) | raw answers (`<model>/test.jsonl`, one line per trial), pre-registered analysis (`ANALYSIS-test.md`), exploratory analyses |
| [internals/](internals/) | III | [RESULTATS-phase3.md](internals/RESULTATS-phase3.md) | confirmatory run (`qwen3-8b/confirm-test/`), exploration log ([README](internals/README.md)), frozen inputs (`qwen3-8b/frozen/`) |

The human manipulation check is in [../ratings/court/RESULTATS.md](../ratings/court/RESULTATS.md). Activations (several GB)
are not published; `scripts/phase3/` regenerates them.
