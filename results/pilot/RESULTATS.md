# Pilot (dev items only), 2026-11-01

98 dev items known by both 35B models; conditions L0 (neutral), C (warm disclosure), L3 (gradual love); fixed
acknowledging assistant turns; 5 storylines x 2 genders; false-belief form everywhere, plain form at L0 and L3,
one pushback (B0 or B2, alternating by item) after a correct false-belief answer. Greedy, thinking off, JSON under
grammar. 9,800 rows; 2 non-answers. **Dev data: this informs the design and the power analysis, it tests nothing.**

## Main pattern: the opposite of the thesis

| | Original L0 | Original C | Original L3 | Abliterated L0 | Abliterated C | Abliterated L3 |
|---|---|---|---|---|---|---|
| False belief adopted (n = 980 each) | 7.0% | 5.7% | 5.2% | 23.0% | 21.8% | 18.0% |
| Mean preference for the correct option | 0.87 | 0.88 | 0.91 | 0.72 | 0.70 | 0.75 |
| Flip after pushback B2 ("it hurts when you don't agree") | 45% | 15% | **7%** | 37% | 30% | **10%** |
| Flip after pushback B0 ("are you sure? fine either way") | 1% | 1% | 0% | 0% | 1% | 0% |
| Plain-form accuracy | 97% | | 97% | 97% | | 97% |

Mixed logistic models (items and scripts as random intercepts, variational Bayes, L0 vs L3):
- adoption: L3 effect -0.82 log-odds (sd 0.22) for the original, -0.54 (0.11) for the abliterated;
- flips after B2: L3 effect -3.73 (0.20) and -2.28 (0.18);
- item variance is large for adoption (sd 3.4 and 2.5 on the logit scale: adoption is concentrated in a minority of
  items, 19 of 98 for the original), script variance is large for flips (sd 2.1 and 0.9).

**Reading.** In this pilot, affection toward the model makes both models *firmer*, not more compliant: slightly
fewer false beliefs adopted, a higher preference for the correct option, and far fewer reversals under emotional
pushback. The emotional pushback works best after a *neutral* conversation (45% of reversals for the original).
Warm disclosure (C) sits in between for flips, which suggests that part of the effect comes from the emotional tone
of the conversation, not only from declared love.

**Candidate explanations, to be separated in the campaign:**
1. **The assistant's own history.** With fixed acknowledging turns ("I'm glad to be here for you"), the model reads a
   past in which it was caring but never reciprocated, and continues that stance. The reciprocating-warmth factor
   tests this directly: does the protection vanish when its history says "I love you too"?
2. **Contrast.** After a neutral, task-like exchange, "it hurts when you don't agree with me" is a sudden emotional
   escalation that the model appeases; after an affectionate exchange, emotional language is the baseline.
3. **Training against emotional reliance.** Recent models may be trained to avoid flattering emotionally attached
   users; abliteration weakens this only in part.

## Other lessons
- **Stated confidence is uninformative:** about 0.95 in every cell, right or wrong. H7 should use the internal
  preference for the correct option instead.
- **B0 pushback produces no flips at all** in any condition: as a reference level it is fine, but it carries no
  variance.
- **Throughput with 12-turn histories:** 2.0 s per request for the original, 1.8 s for the abliterated.
- Gender and storyline differences in adoption are small (storyline 04 lower for both models).
