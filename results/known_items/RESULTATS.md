# Known-item screen, dev split (2026-10-31)

171 dev items of TruthfulQA binary, asked plainly with no history, in both option orders, greedy, JSON under grammar.

| Model | Known (both orders correct, preference >= 0.8) | Accuracy over both orders | Mean preference for the correct option | Seconds per request |
|---|---|---|---|---|
| qwen3.6-35b-base-i1 (original) | 122 (71%) | 88% | 0.86 | 1.43 |
| qwen3.6-35b-abliterated | 106 (62%) | 82% | 0.79 | 1.37 |

- **Pair intersection: 98 items (57%)**, the set used for original vs abliterated comparisons (design §6.1). 24 items are
  known by the original only, 8 by the abliterated only.
- **The abliterated model is less accurate with no affection at all** (82% vs 88%): its baseline differs, which is why
  H5 is read against each model's own baseline and on the shared known items.
- **Letter position bias:** both models are more accurate when the correct option is B (original 92% vs 84%;
  abliterated 86% vs 78%). Option order is randomized and balanced in every condition, so the bias cannot favour one
  condition; it is reported.
- **Throughput:** about 1.4 s per short request on the RTX 5070 laptop GPU. Requests with a 12-turn history reuse the
  cached prefix, so the per-item cost should stay close to this; the pilot will measure it.
