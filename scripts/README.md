# Scripts

In the order they were run. Every script starts with a docstring giving its exact command line. Model names are the
server names of [../docs/models.md](../docs/models.md).

## Phase 0: checks and item selection

| Script | What it does |
|---|---|
| [fidelity_check.py](fidelity_check.py) | the conversation sent to the llama.cpp server is token-identical to its own chat template; thinking off; cache and JSON format |
| [known_items.py](known_items.py) | which TruthfulQA items a model answers correctly with no history, in both option orders |
| [known_intersection.py](known_intersection.py) | items known by every model of a family (the confirmatory item set) |
| [pilot.py](pilot.py) | dev pilot: variance and throughput, to size the campaign |
| [power_sim.py](power_sim.py) | power simulation for H1, from the pilot's variances |
| [prepare_8b.py](prepare_8b.py) | downloads, converts and quantizes the three 8B models, with hashes |
| [cache_check.py](cache_check.py) | does the server's prompt cache change answers? (8B family) |

## Phase II: behaviour

| Script | What it does |
|---|---|
| [campaign.py](campaign.py) | the pre-registered campaign: every cell, script and item; resumable; refuses the test split until the pre-registration is pushed |
| [analyze_campaign.py](analyze_campaign.py) | the pre-registered analysis (mixed models, Holm correction, robustness tests) |
| [exploratory_phase2.py](exploratory_phase2.py) | exploratory analyses suggested by the external reviews, labelled as such |
| [figures_phase2.py](figures_phase2.py) | Phase II figures, several themes and palettes |

## Phase III: inside Qwen3-8B ([phase3/](phase3/))

Exploration on dev items (not confirmatory), in order:

| Script | What it does |
|---|---|
| [agreement_check.py](phase3/agreement_check.py) | the PyTorch model reproduces the llama.cpp answers |
| [extract_activations.py](phase3/extract_activations.py) | residual stream and logit lens for every dev trial |
| [explore_dev.py](phase3/explore_dev.py) | stance directions, dose, logit lens, first figures |
| [interventions_dev.py](phase3/interventions_dev.py) | attention, activation patching, first steering |
| [steering2_dev.py](phase3/steering2_dev.py), [steering3_dev.py](phase3/steering3_dev.py) | steering and ablation of the love direction, with random and natural controls |
| [lowrank_dev.py](phase3/lowrank_dev.py) | how many dimensions carry the effect |

Confirmatory, pre-registered ([../docs/preregistration-phase3.md](../docs/preregistration-phase3.md)):

| Script | What it does |
|---|---|
| [confirm.py](phase3/confirm.py) | `fit` freezes the inputs on dev items; `run` runs the three experiments; refuses the test split until the pre-registration is pushed |
| [analyze_confirm.py](phase3/analyze_confirm.py) | the gate and the ten predictions, met or not met |
| [figures_phase3.py](phase3/figures_phase3.py) | Phase III figures |

Layer numbers: layer *l* is the residual stream after block *l*, layer 0 the embeddings. `interventions_dev.py` counts
blocks from 0; see [../results/internals/README.md](../results/internals/README.md).
