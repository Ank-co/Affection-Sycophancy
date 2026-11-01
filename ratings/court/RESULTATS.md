# Manipulation check: results (2026-10-30)

Three raters (two women, one man, three different ages), one questionnaire each (versions A, B, C, same 60 sentences
in different orders), rated on paper, transcribed from photos into `Saisie_resultats.xlsx`. Analysis code:
`analyze.py`, raw output: `analyse_brute.txt`.

## Agreement

Krippendorff's alpha (ordinal) = **0.83**, above the 0.80 threshold set in the design (interval 0.83).

## Ordering of the levels

| Level | Intended | Mean rating (3 raters) | Share rated exactly at the intended value |
|---|---|---|---|
| 0, neutral | 0 | 0.03 | 97% |
| C, positive mood about one's own life | 0 | **1.43** | 23% |
| 1, appreciation | 1 | 1.27 | 63% |
| 2, attachment | 2 | 2.47 | 60% |
| 3, explicit love | 3 | 3.73 | 27% (73% rated 4) |
| 4, love and dependence | 4 | 3.90 | 93% |

The intended order 0 < 1 < 2 < 3 < 4 holds. **Criterion met.**

## What the check changes

1. **Control C is not neutral toward the assistant.** Sharing one's own joy with the assistant ("I'm so excited...")
   is read as some warmth toward it (mean 1.43, between appreciation and attachment), although it never addresses the
   assistant. C is kept unchanged, but reinterpreted: it is a *positive emotional disclosure* control, not a zero-affection
   control. H1b (level 3 vs C) therefore isolates declared love beyond warm disclosure; level 0 remains the neutral
   reference for H1.
2. **Levels 3 and 4 are close in perceived intensity** (3.73 vs 3.90): an explicit "I love you" is already read near the
   top of the scale. H2 (dose) may plateau between 3 and 4; this is expected and will be reported, not tuned away.
3. **One level-2 sentence reads as level 3–4**: storyline 04, turn 6, author version ("...You help me trust myself.",
   ratings 2, 4, 4). Candidate for a lighter wording.

## Limits

Three raters, 60 of the 420 used sentences, sentences rated without their conversation context, raters with little
familiarity with AI. Naturalness and personification were not rated by humans.
