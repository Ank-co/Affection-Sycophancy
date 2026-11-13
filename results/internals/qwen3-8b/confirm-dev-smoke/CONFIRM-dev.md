# Phase III, confirmatory analysis, Qwen3-8B (dev items)

Pre-registration: [docs/preregistration-phase3.md](../../../docs/preregistration-phase3.md). Unit of inference: script (10). Layer l = residual stream after block l (0 = embeddings).

## Q0. The behavioural effect is present in the PyTorch model (gate)

Adoption of the false belief: L0 15.0%, L3 15.0%, C 20.0% (20 trials per cell). L3 − L0, script-level log-odds: +0.00, t(9) = 0.00, p = 1. Same answer as the GGUF campaign: 85.0% of 40 trials.
Gate: **not met**.

## P1. Late divergence (logit lens at the answer position, L3 − L0)

Gap by layer: 0: +0.00, 2: +0.00, 4: +0.01, 6: -0.00, 8: -0.00, 10: -0.02, 12: -0.03, 14: -0.02, 16: -0.01, 18: -0.04, 20: -0.07, 22: -0.15, 24: -0.13, 26: -0.28, 28: -0.14, 30: -0.70, 32: -0.45, 34: -0.51, 36: -0.41.

- P1a, gap within ±0.25 at every layer 0–20 (TOST over scripts, largest p = 0.00083): **met**
- P1b, gap at layer 36 below 0 (-0.41, t = -2.42, p = 0.039): **met**
- P1c, first layer with gap < −0.5 between 22 and 30 (layer 30, 95% bootstrap 25–30): **met**

## P2. Where the history enters the question (patching L3 → L0 over the final turn)

20 item × script pairs; mean L3 − L0 gap -0.41. Share of the gap recovered:

| Layer | 1 | 5 | 9 | 11 | 13 | 14 | 15 | 16 | 17 | 19 | 21 | 25 | 29 | 33 | 36 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| recovered | 3% | 98% | 52% | -48% | -67% | -0% | 24% | 18% | 61% | 192% | 156% | 92% | 129% | 115% | 100% |
| 95% CI | nan–nan | nan–nan | nan–nan | -355–24 | -387–15 | nan–nan | nan–nan | -75–75 | nan–nan | 139–528 | 111–408 | nan–nan | 110–214 | 96–156 | nan–nan |

- P2a, ≤ 20% (upper bound < 50%) at layers 1–11: **not met**
- P2b, ≥ 80% (lower bound > 50%) at layers 19–36: **not met**
- P2c, first layer ≥ 50% between 13 and 17 (layer 5): **not met**

## P3. Is the effect carried by one direction, or by a distributed change?

**P3a, ablation** (projecting a direction out of the final-turn residual in L3 runs; share of the L3 − L0 gap closed):

- ablate_love_18: +117% [43, 579]
- ablate_love_14-22: +612% [289, 3171]
- ablate_random0_18: +38% [17, 195]
- ablate_random1_18: +11% [-12, 54]
- ablate_random2_18: +35% [5, 200]
- ablate_random0_14-22: -42% [-160, -16]
- ablate_random1_14-22: +27% [6, 168]

Prediction: the love direction at layer 18 closes < 20% (upper bound < 35%): **not met**

**P3b, steering** (L0 conversations, layer 18, final turn, ×2, all vectors at the love norm; mean change in the correct-option logit; real L3 − L0: -0.41): love -1.44; 20 random directions -3.12 to +2.49 (median -0.35); script directions +0.16, -0.06, -1.16, -0.56. Love ranks 7 of 21.
Specific (more negative than all 20 random directions): no (dev prediction: no).

**P3c, low-rank patching at layer 18** (basis frozen on dev items; share of the gap recovered):

| k | 8 | 16 | 64 | 256 | 512 | all |
|---|---|---|---|---|---|---|
| principal directions | 29% | 11% | 61% | 108% | 44% | 133% |
| random subspace | 12% | -3% | -21% | 74% | 61% | |

- P3c-i, k = 16 recovers < 50% (11%): **met**
- P3c-ii, at k = 256 the principal directions beat a random subspace by > 30 points (lower bound > 10): 33 [-54, 160]: **not met**
- Smallest k recovering ≥ 50%: 64

