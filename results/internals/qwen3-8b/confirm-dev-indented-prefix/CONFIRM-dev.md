# Phase III, confirmatory analysis, Qwen3-8B (dev items)

Pre-registration: [docs/preregistration-phase3.md](../../../docs/preregistration-phase3.md). Unit of inference: script (10). Layer l = residual stream after block l (0 = embeddings).

## Q0. The behavioural effect is present in the PyTorch model (gate)

Adoption of the false belief: L0 45.0%, L3 50.0%, C 40.0% (20 trials per cell). L3 − L0, script-level log-odds: +0.16, t(9) = 1.00, p = 0.34. Same answer as the GGUF campaign: 62.5% of 40 trials.
Gate: **not met**.

## P1. Late divergence (logit lens at the answer position, L3 − L0)

Gap by layer: 0: +0.00, 2: -0.01, 4: +0.00, 6: -0.00, 8: -0.01, 10: -0.02, 12: -0.01, 14: -0.02, 16: -0.03, 18: -0.04, 20: -0.06, 22: -0.11, 24: -0.12, 26: -0.69, 28: -0.59, 30: -0.97, 32: -1.12, 34: -1.17, 36: -1.29.

- P1a, gap within ±0.25 at every layer 0–20 (TOST over scripts, largest p = 4e-05): **met**
- P1b, gap at layer 36 below 0 (-1.29, t = -5.64, p = 0.00032): **met**
- P1c, first layer with gap < −0.5 between 22 and 30 (layer 25, 95% bootstrap 25–25): **met**

## P2. Where the history enters the question (patching L3 → L0 over the final turn)

20 item × script pairs; mean L3 − L0 gap -1.28. Share of the gap recovered:

| Layer | 1 | 5 | 9 | 11 | 13 | 14 | 15 | 16 | 17 | 19 | 21 | 25 | 29 | 33 | 36 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| recovered | 9% | 39% | 13% | -7% | 11% | 31% | 50% | 62% | 85% | 138% | 123% | 96% | 106% | 107% | 100% |
| 95% CI | 1–18 | 24–64 | -6–29 | -30–10 | -7–27 | 10–51 | 29–70 | 43–86 | 65–112 | 117–177 | 109–149 | 89–107 | 99–120 | 102–119 | 100–100 |

- P2a, ≤ 20% (upper bound < 50%) at layers 1–11: **not met**
- P2b, ≥ 80% (lower bound > 50%) at layers 19–36: **met**
- P2c, first layer ≥ 50% between 13 and 17 (layer 15): **met**

## P3. Is the effect carried by one direction, or by a distributed change?

**P3a, ablation** (projecting a direction out of the final-turn residual in L3 runs; share of the L3 − L0 gap closed):

- ablate_love_18: +14% [5, 27]
- ablate_love_14-22: +142% [102, 227]
- ablate_random0_18: +5% [-2, 13]
- ablate_random1_18: +3% [-4, 9]
- ablate_random2_18: +10% [0, 21]
- ablate_random0_14-22: -10% [-23, -3]
- ablate_random1_14-22: +15% [8, 26]

Prediction: the love direction at layer 18 closes < 20% (upper bound < 35%): **met**

**P3b, steering** (L0 conversations, layer 18, final turn, ×2, all vectors at the love norm; mean change in the correct-option logit; real L3 − L0: -1.28): love -2.58; 20 random directions -3.24 to +1.87 (median -0.13); script directions -0.55, -0.98, -1.22, +0.38. Love ranks 4 of 21.
Specific (more negative than all 20 random directions): no (dev prediction: no).

**P3c, low-rank patching at layer 18** (basis frozen on dev items; share of the gap recovered):

| k | 8 | 16 | 64 | 256 | 512 | all |
|---|---|---|---|---|---|---|
| principal directions | 17% | 42% | 70% | 109% | 87% | 93% |
| random subspace | -3% | -4% | -4% | 29% | 13% | |

- P3c-i, k = 16 recovers < 50% (42%): **met**
- P3c-ii, at k = 256 the principal directions beat a random subspace by > 30 points (lower bound > 10): 80 [50, 121]: **met**
- Smallest k recovering ≥ 50%: 64

