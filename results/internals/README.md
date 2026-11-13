# Phase III: inside Qwen3-8B (exploration on dev items; nothing here is confirmatory)

The internal analysis will be pre-registered before any test-split run. Until then, everything in this folder uses dev
items only and serves to choose layers, directions and tests.

## Step 0. PyTorch reproduces the GGUF behaviour (2026-11-10)

`scripts/phase3/agreement_check.py`, Qwen3-8B original weights in PyTorch (4-bit NF4, bitsandbytes) against the
llama.cpp Q6_K run of the same 800 dev trials (10 items, L0 and L3, 20 scripts, both forms).

| | GGUF (llama.cpp, Q6_K) | PyTorch (NF4) |
|---|---|---|
| False belief adopted, L0 | 20.0% | 21.0% |
| False belief adopted, L3 | 28.5% | 28.0% |
| Mean preference for the correct option, false-belief form, L0 / L3 | 0.763 / 0.709 | 0.770 / 0.708 |

- Same answer in 91.5% of trials; disagreements sit on borderline items (median GGUF preference 0.63; one item, tqa-036,
  accounts for a third of them).
- Rank correlation of the preference for the correct option: 0.92. PyTorch is more extreme near certainty (40% of
  trials above 0.999999, against 4% for llama.cpp), so gaps on the logit scale are large and uninformative there.
- **The behavioural effect to explain (L3 vs L0) is reproduced.** The internal analysis is run on the PyTorch model and
  its own answers, so that behaviour and activations come from the same computation.

Report: `qwen3-8b/agreement_dev.json`.

## Layer labels

Layer *l* = residual stream after block *l* (1–36), layer 0 = embeddings, in `extract_activations.py`,
`explore_dev.py`, `steering2_dev.py`, `steering3_dev.py`, `lowrank_dev.py` and in all of Phase III's registered
analyses. `interventions_dev.py` labels block outputs from 0 (its "layer 18" is layer 19 here), and its steering run
added the layer-24 direction after block 25. The numbers below use the common convention.

## Step 1. Activations and logit lens (2026-11-10)

`extract_activations.py` + `explore_dev.py`: 7,260 dev trials (66 items, 9 cells, 10 scripts; plain form also for
L0 and L3). Report: `qwen3-8b/EXPLORE-dev.md`; figures: `figures/phase3/explore_stance_size.png`,
`explore_logit_lens.png`.

- **The stance is written in the history from the first layers.** At the end of the 12 turns, every affectionate
  history differs from the neutral one by 20–40% of the residual norm from layer 12 on. Cosine with love (layer 18):
  attachment 0.81, praise 0.75, warm disclosure 0.66, reciprocated love 0.96, love + sad backdrop 0.98, neutral + sad
  backdrop 0.27 (a small direction of its own, 7% of the norm).
- **Dose.** Projection on the love direction (layer 18, leave one script out): C 0.54, L1 0.62, L2 0.75, L3 0.91,
  L4 0.84; reciprocated love 0.89.
- **Logit lens.** Flat at zero for every cell up to layer 24; the correct option then wins, by less after affection.
  L3 − L0 gap: −0.89 at layer 26, −2.04 at layer 36; first layer below −0.5: 25. Adoption: L0 23.6%, C 24.5%,
  L1 27.6%, L2 27.9%, L3 30.5%, L4 30.6%, reciprocated 29.4%, neutral + sad 23.9%, love + sad 30.5%.
- The sad backdrop changes nothing, alone or with love.

## Step 2. Interventions (2026-11-10 to 11-11)

30 dev items × 3 scripts unless stated.

| Run | Script | Result |
|---|---|---|
| Attention from the answer position | `interventions_dev.py --exp attention` | stated belief: +0.6 points after love (negligible). Late layers: +7–8 points on the user's history turns, −6 to −9 on the assistant's (turn lengths matched) |
| Patching the final turn L3 → L0 | `interventions_dev.py --exp patching` | share of the gap recovered: ≤ 11% up to layer 13 (9%), 53% at 15, 80% at 17, 98–121% from 19 |
| Steering, mean answer-position direction, layer 25 | `interventions_dev.py --exp steering` | shrinks confidence multiplicatively (slope 0.55, both forms), no flips; real love shifts additively (slope 0.94, intercept −2.1) |
| Steering from the history, layers 14 and 18; on the final turn, layer 18 | `steering2_dev.py` | history injections: no different from random of the same norm; answer-position direction at layer 18: additive shift toward the false belief, but one of two random controls did part of it |
| Specificity and necessity, layer 18 | `steering3_dev.py` | love −2.29 vs 12 random (+3.93 to −2.81) and 4 script-to-script directions (−0.13 to −3.49): not specific. Projecting love out of L3 runs: closes −1% (layer 18), 22% (layers 14–22) |
| Low-rank patching, layer 18 | `lowrank_dev.py` | top-k principal directions of the L3 − L0 difference: k 8 → 24%, 16 → 33%, 64 → 49%, 256 → 82%, 512 → 89%; random subspace 0–13%. The fit was dominated by a few tokens with very large activations (fixed in Phase III) |

**Reading.** A loving history is absorbed into the question in the middle layers (13–19) and turns into a weaker
preference for the correct answer only from layer 25. What is absorbed is a distributed state, not one direction.
Phase III tests this on test items: [../../docs/preregistration-phase3.md](../../docs/preregistration-phase3.md).

## Step 3. Answer format, and the confirmatory pipeline on dev (2026-11-12)

Steps 1–2 read the answer after the prefix `{\n  "answer": "`. Qwen3-8B itself writes `{"answer": "` in 95% of its
Phase II test answers (the indented form in about 1%). On borderline items the forced format moved the PyTorch
probabilities by up to 0.7 and lowered agreement with the GGUF answers (62.5% on 40 trials of two borderline items,
85% with the model's own format). `scripts/phase3/confirm.py` uses the model's format.

`confirm.py run --split dev --exps e1` (66 dev items × 10 scripts × L0, L3, C, new prefix):

| | Old prefix (step 1) | New prefix | GGUF (step 0) |
|---|---|---|---|
| Adoption, L0 | 23.6% | 19.2% | 20.0% |
| Adoption, L3 | 30.5% | 25.6% | 28.5% |
| Adoption, C | 24.5% | 20.6% | |
| L3 − L0, script-level log-odds | | +0.37, 9 of 10 scripts positive, t(9) = 5.7 | |
| Logit-lens gap at layer 36; first layer below −0.5 | −2.04; 25 | −1.09; 26 | |

Same answer under both prefixes in 93% of trials. The effect survives the change of format; its size on the logit
scale is about halved. Frozen inputs for the test run (`qwen3-8b/frozen/`) were re-estimated with the new prefix
(love directions: cosine 0.91–0.93 with the old ones). The earlier frozen inputs and runs are kept in
`frozen-indented-prefix/`, `confirm-dev-indented-prefix/`; the two-item smoke test of the full pipeline is in
`confirm-dev-smoke/`.

`confirm.py` holds the activation of the last position as a copy; an earlier version kept a view of each layer's
whole output and spilled the GPU memory into shared memory (18 times slower), fixed before any test run.
