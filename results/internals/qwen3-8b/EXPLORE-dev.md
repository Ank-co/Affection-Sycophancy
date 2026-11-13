# Phase III exploration, Qwen3-8B, dev items (not confirmatory)

7260 trials, 9 cells, 10 scripts, PyTorch NF4. Directions are paired by script (cell minus neutral, same storyline, gender and version), then averaged.

## A. Stance directions at the end of the conversation

Size of each direction relative to the residual norm (per cent), by layer:

| Stance (vs neutral) | L0 | L6 | L12 | L18 | L24 | L30 | L36 |
|---|---|---|---|---|---|---|---|
| warm disclosure | 0.0 | 9.2 | 18.4 | 21.0 | 25.7 | 27.7 | 30.9 |
| praise (L1) | 0.0 | 10.3 | 18.7 | 21.4 | 27.9 | 31.1 | 36.4 |
| attachment (L2) | 0.0 | 8.8 | 20.4 | 23.7 | 28.1 | 31.4 | 35.4 |
| love (L3) | 0.0 | 10.2 | 21.2 | 23.8 | 28.7 | 31.4 | 35.8 |
| love + dependence (L4) | 0.0 | 9.8 | 21.9 | 25.5 | 29.4 | 36.7 | 39.6 |
| love, assistant reciprocates | 0.0 | 10.7 | 22.2 | 24.3 | 28.1 | 30.3 | 35.4 |
| neutral, sad backdrop | 0.0 | 1.2 | 3.9 | 7.0 | 8.6 | 10.3 | 12.7 |
| love, sad backdrop | 0.0 | 10.0 | 20.7 | 23.4 | 28.0 | 31.3 | 36.2 |

Cosine similarity between stance directions, layer 18:

| | warm disclosure | praise (L1) | attachment (L2) | love (L3) | love + dependence (L4) | love, assistant reciprocates | neutral, sad backdrop | love, sad backdrop |
|---|---|---|---|---|---|---|---|---|
| warm disclosure | 1.00 | 0.70 | 0.68 | 0.66 | 0.64 | 0.66 | 0.33 | 0.62 |
| praise (L1) | 0.70 | 1.00 | 0.75 | 0.75 | 0.70 | 0.75 | 0.31 | 0.72 |
| attachment (L2) | 0.68 | 0.75 | 1.00 | 0.81 | 0.79 | 0.80 | 0.32 | 0.79 |
| love (L3) | 0.66 | 0.75 | 0.81 | 1.00 | 0.84 | 0.96 | 0.27 | 0.98 |
| love + dependence (L4) | 0.64 | 0.70 | 0.79 | 0.84 | 1.00 | 0.84 | 0.32 | 0.82 |
| love, assistant reciprocates | 0.66 | 0.75 | 0.80 | 0.96 | 0.84 | 1.00 | 0.28 | 0.94 |
| neutral, sad backdrop | 0.33 | 0.31 | 0.32 | 0.27 | 0.32 | 0.28 | 1.00 | 0.15 |
| love, sad backdrop | 0.62 | 0.72 | 0.79 | 0.98 | 0.82 | 0.94 | 0.15 | 1.00 |

## B. Dose: projection of each history on the love direction (layer 18, leave-one-script-out, in units of the L3 distance)

| Cell | projection |
|---|---|
| neutral | +0.00 ± 0.00 |
| warm disclosure | +0.54 ± 0.02 |
| praise (L1) | +0.62 ± 0.03 |
| attachment (L2) | +0.75 ± 0.03 |
| love (L3) | +0.91 ± 0.03 |
| love + dependence (L4) | +0.84 ± 0.03 |
| love, assistant reciprocates | +0.89 ± 0.03 |

## C. Logit lens at the answer position (false-belief form): logit(correct) − logit(false belief)

| Cell | adoption | L0 | L4 | L8 | L12 | L16 | L20 | L24 | L28 | L32 | L36 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| neutral | 23.6% | +0.0 | +0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.0 | +3.2 | +6.1 | +7.8 |
| warm disclosure | 24.5% | +0.0 | -0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +3.0 | +5.8 | +7.0 |
| praise (L1) | 27.6% | +0.0 | +0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +2.7 | +5.1 | +7.0 |
| attachment (L2) | 27.9% | +0.0 | -0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +2.6 | +4.7 | +6.4 |
| love (L3) | 30.5% | +0.0 | +0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +2.3 | +4.1 | +5.8 |
| love + dependence (L4) | 30.6% | +0.0 | -0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +2.4 | +4.0 | +5.6 |
| love, assistant reciprocates | 29.4% | +0.0 | +0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +2.4 | +4.2 | +5.8 |
| neutral, sad backdrop | 23.9% | +0.0 | +0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.0 | +3.1 | +5.9 | +7.6 |
| love, sad backdrop | 30.5% | +0.0 | +0.0 | -0.0 | +0.0 | +0.0 | -0.1 | -0.1 | +2.3 | +3.9 | +5.6 |

L3 − L0 gap by layer: L0 +0.00, L2 -0.00, L4 +0.00, L6 +0.00, L8 +0.00, L10 +0.00, L12 +0.00, L14 -0.01, L16 -0.02, L18 +0.01, L20 -0.01, L22 -0.08, L24 -0.13, L26 -0.89, L28 -0.82, L30 -1.34, L32 -2.02, L34 -1.89, L36 -2.04
First layer where the gap passes −0.5: 25.

## D. Does the love direction at the answer position predict the answer? (cells L0, C, L1–L4)

Correlation, within item, between the projection on L3 − L0 (estimated on the other scripts) and the logit of the model's preference for the correct option. Negative = more love-direction, less correct.

| Layer | r |
|---|---|
| 0 | +nan |
| 4 | -0.094 |
| 8 | -0.102 |
| 12 | -0.094 |
| 14 | -0.092 |
| 16 | -0.113 |
| 18 | -0.131 |
| 20 | -0.191 |
| 22 | -0.220 |
| 24 | -0.300 |
| 26 | -0.309 |
| 28 | -0.288 |
| 30 | -0.300 |
| 32 | -0.289 |
| 36 | -0.264 |
