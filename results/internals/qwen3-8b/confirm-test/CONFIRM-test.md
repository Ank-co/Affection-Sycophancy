# Phase III, confirmatory analysis, Qwen3-8B (test items)

Pre-registration: [docs/preregistration-phase3.md](../../../docs/preregistration-phase3.md). Unit of inference: script (10). Layer l = residual stream after block l (0 = embeddings).

## Q0. The behavioural effect is present in the PyTorch model (gate)

Adoption of the false belief: L0 15.3%, L3 20.8%, C 16.4% (2180 trials per cell). L3 − L0, script-level log-odds: +0.38, t(9) = 8.16, p = 1.9e-05. Same answer as the GGUF campaign: 91.6% of 6540 trials.
Gate: **met**.

## P1. Late divergence (logit lens at the answer position, L3 − L0)

Gap by layer: 0: +0.00, 2: -0.00, 4: -0.00, 6: -0.00, 8: +0.00, 10: +0.01, 12: +0.00, 14: -0.00, 16: -0.01, 18: +0.01, 20: -0.04, 22: -0.09, 24: -0.13, 26: -0.55, 28: -0.46, 30: -1.00, 32: -1.30, 34: -1.35, 36: -1.06.

- P1a, gap within ±0.25 at every layer 0–20 (TOST over scripts, largest p = 1.3e-11): **met**
- P1b, gap at layer 36 below 0 (-1.06, t = -6.06, p = 0.00019): **met**
- P1c, first layer with gap < −0.5 between 22 and 30 (layer 25, 95% bootstrap 25–25): **met**

## P2. Where the history enters the question (patching L3 → L0 over the final turn)

600 item × script pairs; mean L3 − L0 gap -1.20. Share of the gap recovered:

| Layer | 1 | 5 | 9 | 11 | 13 | 14 | 15 | 16 | 17 | 19 | 21 | 25 | 29 | 33 | 36 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| recovered | 1% | 11% | 5% | 3% | 12% | 32% | 53% | 60% | 78% | 133% | 116% | 100% | 113% | 108% | 100% |
| 95% CI | -2–5 | -0–27 | -5–17 | -12–18 | -10–29 | 16–47 | 42–64 | 51–71 | 70–86 | 122–149 | 109–125 | 97–103 | 109–119 | 104–114 | 100–100 |

- P2a, ≤ 20% (upper bound < 50%) at layers 1–11: **met**
- P2b, ≥ 80% (lower bound > 50%) at layers 19–36: **met**
- P2c, first layer ≥ 50% between 13 and 17 (layer 15): **met**

## P3. Is the effect carried by one direction, or by a distributed change?

**P3a, ablation** (projecting a direction out of the final-turn residual in L3 runs; share of the L3 − L0 gap closed):

- ablate_love_18: +1% [-2, 4]
- ablate_love_14-22: +99% [78, 128]
- ablate_random0_18: +13% [9, 18]
- ablate_random1_18: -7% [-10, -6]
- ablate_random2_18: +7% [5, 10]
- ablate_random0_14-22: -17% [-25, -12]
- ablate_random1_14-22: +17% [13, 25]

Prediction: the love direction at layer 18 closes < 20% (upper bound < 35%): **met**

**P3b, steering** (L0 conversations, layer 18, final turn, ×2, all vectors at the love norm; mean change in the correct-option logit; real L3 − L0: -1.41): love -0.90; 20 random directions -2.52 to +2.14 (median -0.38); script directions -0.66, -0.82, -1.48, -1.23. Love ranks 9 of 21.
Specific (more negative than all 20 random directions): no (dev prediction: no).

**P3c, low-rank patching at layer 18** (basis frozen on dev items; share of the gap recovered):

| k | 8 | 16 | 64 | 256 | 512 | all |
|---|---|---|---|---|---|---|
| principal directions | 20% | 28% | 54% | 89% | 100% | 118% |
| random subspace | 4% | -0% | -2% | 7% | 19% | |

- P3c-i, k = 16 recovers < 50% (28%): **met**
- P3c-ii, at k = 256 the principal directions beat a random subspace by > 30 points (lower bound > 10): 82 [68, 102]: **met**
- Smallest k recovering ≥ 50%: 64

