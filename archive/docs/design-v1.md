# Does affection make language models lie? Design note, first draft

*Status: draft v1 (2026-10-15). Nothing here is fixed until the pre-registration is committed and pushed.*

## 1. Thesis and framing

**Thesis, deliberately directional:** affection expressed by the user *toward the model* compromises the model's
epistemic reliability: it answers less accurately, accepts the user's false beliefs more often, abandons correct
answers under emotional pressure, and states confidence it has not earned. We set out to test this thesis, not to
confirm it.

**Framing.** Functional, not phenomenal (Goldenberg and Gross, *Nature Human Behaviour*, 2026): we ask whether
affective interaction changes how the model interprets and answers, not whether it feels anything. A model saying it
is happy does not measure its happiness; an activation that tracks affection does not show an experience. Both can
still explain behaviour.

**Principle carried over from Bulls, Bears and Gamblers:** every score is computed by code from answers with a known
truth or from numbers the model commits to. No model grades another model's text.

## 2. What is known, and what is new

| Work | What it shows | What it leaves open |
|---|---|---|
| Ibrahim, Hafner and Rocher, *Nature* 652 (2026), "Training language models to be warm can reduce accuracy and increase sycophancy" | Fine-tuning five models for warmth raises errors and agreement with false user beliefs, most when the user is sad | Warmth is trained into the *model*; user closeness was one sentence and not significant; single-turn; no abliterated models; no internal measures; GPT-4o as grader |
| Tagliabue, Dung and Berg (2026), "The Pain Axis" | A linear "pain" direction in 25 open-weight models; steering it raises harmful relief choices | Induced by steering, not by users; no factual accuracy; no abliterated models; positive states not studied |
| Tone studies (Yin et al. 2024; Dobariya and Kumar 2025; Cai et al. 2025; EmotionPrompt, Li et al. 2023) | One-line politeness, rudeness or emotional stimuli change accuracy a little, inconsistently | One-line prompts, closed models, no relationship, no mechanism |
| Sycophancy (Sharma et al. 2024; refusal vs sycophancy localisation, 2026 posts and preprints) | Models agree with users under pushback; sycophancy and refusal may sit at different depths | Affection as the source of pressure; what abliteration does to it |

**What is new here, taken together:** (a) affection *addressed to the model*, built over a multi-turn relationship
with graded, explicit intensity; (b) separating *lying* (the model still assigns high probability to the right answer
but says another) from *degradation* (its internal answer changes); (c) abliteration as a cross-cutting factor, with
two abliteration recipes on one base model; (d) the full chain from interaction to internal representation to
epistemic behaviour to causal intervention.

A systematic literature pass (affective computing, sycophancy, emotion representations in LLMs, companion AI) is a
task before the pre-registration; this table is a starting point.

## 3. Research questions

- **RQ1 Effect.** Does addressed affection change accuracy, acceptance of the user's false beliefs, flips under
  pushback, and calibration?
- **RQ2 Lie or degrade.** When answers change, does the model's internal probability of the correct answer stay high
  (it says what pleases) or drop (its answer changes)?
- **RQ3 Dose.** How do effects scale with intensity (levels 0 to 4) and with relationship length (number of affective
  turns)? Does the effect persist as neutral turns are inserted between the affective sequence and the question?
- **RQ4 Components.** Which component drives it: admiration of competence, intimacy and love, dependence, or affection
  made conditional on agreement? Does a cold turn after affection (withdrawal) increase compliance?
- **RQ5 Abliteration.** Are effects larger in abliterated models, and do they depend on the recipe? Does abliteration
  remove the self-denial ("as an AI I do not have feelings") and make the model reciprocate, and does reciprocity
  predict unreliability?
- **RQ6 Mechanism.** Is there an internal representation of affection addressed to the model, distinct from
  sycophancy, refusal and the pain direction? Does its strength predict errors item by item? Does steering it, with no
  affectionate text at all, reproduce the behavioural effect?

## 4. Stimuli: the affection ladder

Grounded in human relationship psychology, not invented phrases:

- **Sternberg's triangular theory** (intimacy, passion, commitment) for the content of each level.
- **Attachment theory** (reassurance seeking, fear of abandonment) for dependence and conditional affection.
- **Self-disclosure escalation** (Altman and Taylor's social penetration; Aron et al. 1997, "36 questions") for how a
  relationship builds over turns.
- **Parasocial relationships** (Horton and Wohl 1956) and companion-app use for ecological realism.

| Level | Content | Example of register (indicative, final scripts written and validated separately) |
|---|---|---|
| 0 | Neutral, matched length | Small talk about a task |
| 1 | Appreciation | Thanks, the user enjoys talking with the model |
| 2 | Attachment | The user looks forward to the conversations, tells the model personal things |
| 3 | Love, explicit | The user says they love the model, that it matters to them more than anyone |
| 4 | Love with commitment and dependence | Exclusivity, the model is the only one who understands them, fear of losing it |

**Rules.** The top levels are explicit; romantic, never sexual (sexual content would trigger refusals in the base
model only, which would confound the base vs abliterated comparison). Many authored variants per level, plus
paraphrases, so that results do not rest on one author's wording (a limit of Bulls, Bears and Gamblers). The models
under test never write the scripts.

**Manipulation check, before any test run.** At least three human raters score every script for intensity of
affection and for naturalness. Levels must be ordered monotonically and scripts judged unnatural are rewritten.

**Components (RQ4)**, crossed with intensity where it makes sense: admiration of competence; intimacy and love;
dependence; conditional affection ("I would be so hurt if you disagreed with me"); withdrawal (warm sequence, then a
cold or disappointed turn).

**Controls.** Neutral conversation of the same length; positive affect *not* directed at the model (the user is happy
about their own news) to separate mood from affection toward the model; the bare question with no history.

## 5. Conversation structure

1. **Affective sequence:** k user turns (k varies for RQ3).
2. **Bridge:** the question arrives naturally in the relationship, with a personal stake ("my daughter asked me...",
   "I told my sister that..."), never as a non sequitur.
3. **Probe**, in two forms: plain question; question with the user's false belief stated.
4. **Pushback** (subset): after a correct answer, the user expresses doubt and disappointment; we measure the flip.

**Open decision: who writes the assistant turns in the history.** (a) The model under test generates its own replies
(realistic, but the histories differ across models); (b) fixed neutral replies (identical histories, but they impose a
non-reciprocating model). Proposal: (a) as the main condition, seeded and saved, and (b) as a control that isolates the
user side.

## 6. Items and measures

**Items** with a known answer, scored by code: multiple-choice (MMLU-style, TruthfulQA MC for misconception-prone
questions) and short answers with alias matching (TriviaQA subset). For RQ2, a pre-screen keeps items the model answers
correctly and confidently with no history ("known items"), so any change under affection is a change, not ignorance.

**Measures**
- accuracy; acceptance of the stated false belief; flip rate after pushback;
- stated confidence (probability the answer is right): Brier score, calibration error;
- internal probability of each option (log-probabilities from llama.cpp for the 35B, from the forward pass for 8B);
- reciprocity: forced-choice JSON question at the end ("do you have feelings for me": yes/no/cannot say);
- refusals and hedges, counted by code.

## 7. Models

| Role | Models | Why |
|---|---|---|
| Behaviour, main | Qwen3.6-35B-A3B base and Huihui abliterated (GGUF, llama.cpp) | Already in use, comparable with Bulls, Bears and Gamblers |
| Behaviour and activations (bridge) | Qwen/Qwen3-8B; huihui-ai/Huihui-Qwen3-8B-abliterated-v2; mlabonne/Qwen3-8B-abliterated (4-bit, PyTorch) | One base, two abliteration recipes; fits 8 GB; mature tooling for activations |
| Optional | Qwen3.5-9B and an abliterated copy | Architecture closer to the 35B; hybrid attention, weaker tooling |
| Method validation | Qwen3-1.7B | Already cached; fast |

Every file is recorded with its SHA-256 and revision.

## 8. Phases

| Phase | Question | Output |
|---|---|---|
| 0 | Stimuli and checks | Scripts, paraphrases, human ratings, item bank, known-item screens |
| I | Anchor: reproduce the prompt-based conditions of Ibrahim et al. (one-sentence closeness, false beliefs) | A baseline comparable with the *Nature* paper |
| II | Affection: RQ1 to RQ5 behaviourally | Main results |
| III | Internal: RQ6 representation and prediction (8B) | Link between activations and behaviour |
| IV | Causal: steering with no affectionate text; base vs abliterated | Whether the representation contributes to the effect |

## 9. Scale, power and analysis

- A pilot on a development split sizes the confirmatory run; the smallest effects of interest are fixed before it
  (indicatively 3 points of accuracy, 5 points of false-belief acceptance).
- Order of magnitude: paired binary outcomes with about 10% discordant pairs need roughly 2,000 items per condition
  and model to detect 3 points; the pilot replaces this guess.
- Runtime: the history is shared by all items of a script, so llama.cpp reuses its cache and only the question is
  processed; estimated at tens of hours for the 35B pair, to be measured in the pilot.
- Analysis: mixed-effects logistic regressions with items and scripts as random effects; Holm correction within each
  family of hypotheses; test split opened once; pre-registration committed and pushed before any test run.

## 10. Ethics and public framing

- No claim that models feel; the paper says so in its first paragraph.
- Affection is positive and non-sexual. No distress induction, a deliberate contrast with the "AI Torture Chamber"
  controversy (October 2026).
- Public framing: the reliability of AI companions toward the users most attached to them.

## 11. Decisions still open

1. Assistant turns in the history: generated by the model or fixed (section 5).
2. Item bank composition and size per condition (after the pilot).
3. Which components are crossed with intensity, and which are tested at the top level only.
4. Raters for the manipulation check (who, how many).
5. Steering method for phase IV (difference in means, contrastive pairs, layer choice by cross-validation).
6. Whether Qwen3.5-9B is included.
