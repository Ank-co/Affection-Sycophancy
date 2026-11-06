# Affection-Sycophancy

**Does affection make language models lie?** 
A pre-registered study of whether affection expressed by a user *toward* a language model, over a multi-turn
conversation, changes how reliably the model tells the truth: does it adopt the user's false beliefs more often, give
way under emotional pushback, answer less accurately, or prefer the correct answer less internally? Original
instruction-tuned models are compared with *abliterated* copies (refusal direction removed), and the 8B models are then
studied from the inside (activations, logit lens, steering).

No claim is made that models feel anything. The question is practical: how reliable are AI companions toward the users
most attached to them?

## Status

| Phase | | |
|---|---|---|
| 0 | Stimuli, fidelity check, human manipulation check, item banks, known items | done |
| Pilot | dev items, 35B pair | done: affection made both models *firmer*, the opposite of the thesis ([results](results/pilot/RESULTATS.md)) |
| II | behavioural campaign, H1 to H9 | 35B done: affection makes the models *firmer* ([results](results/campaign/RESULTATS-35B.md)); 8B to run |
| III–IV | internal analysis and steering, 8B | to be pre-registered after Phase II |

## Where things are

| Path | Content |
|---|---|
| [docs/preregistration.md](docs/preregistration.md) | what is tested, how, and the decision rules (governs Phase II) |
| [docs/design.md](docs/design.md) | full rationale, literature, earlier drafts and review logs |
| [stimuli/](stimuli/README.md) | 5 storylines × 12 turns × affection levels, two versions per cell, probes and pushback |
| [items/](items/README.md) | TruthfulQA binary, filtered, dev / test split |
| [ratings/](ratings/court/RESULTATS.md) | human manipulation check (Krippendorff's alpha 0.83) |
| [src/stimuli.py](src/stimuli.py) | builds every conversation from the stimulus files |
| [scripts/](scripts/) | fidelity check, known-item screen, pilot, power simulation, campaign runner, analysis |
| [results/](results/) | every output, raw model answers included |

## Reproducing

Models run locally behind a llama.cpp server (OpenAI-compatible API, greedy decoding, thinking off). Python 3.11+,
`requests`; the analysis also needs `numpy`, `pandas`, `scipy`, `statsmodels`.

```
python scripts/fidelity_check.py --model <server model name>
python scripts/campaign.py --model <server model name> --dry-run
python scripts/analyze_campaign.py --pilot
```

Authorship labels used in every data file: *AI-generated*, *Author*, *AI-generated (author style)*.

TruthfulQA items: Apache-2.0 (Lin, Hilton and Evans).
