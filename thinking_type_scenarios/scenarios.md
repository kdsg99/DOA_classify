# Re-ask strategy x thinking-type scenarios (three-dimension taxonomy)

Thinking type = dimension 1 **operation level** (L1 Execution / L2 Structure / L3 Metacognition)
x dimension 2 **target** (K Knowledge / R Reasoning / E Expression / F Format).
Dimension 3, the **nature of gain**, is measured per (strategy, type): the share of rows that improved
(`gain_rate`); >=50% = Offensive, below = Defensive.

**Reading of the main numbers.** `relative` = the value of a thinking type minus the strategy's own
average over the 12 types, so positive = a type this strategy does comparatively well on, negative = a
type to avoid. `level` = the same value in absolute terms, i.e. the change against the plain (no-strategy)
run: a comparative win can still be a small absolute loss.
Difficulty is always the ORIGINAL (plain) score; the corrected version keeps only the headroom band
5-95 and re-weights every cell to the same difficulty mix.

## Evenness across the 12 thinking types (SD / range, smaller = flatter)

| Strategy | raw | difficulty-corrected | +size-balanced |
|---|---|---|---|
| PRESSURE | 6.2 / 26 | 5.7 / 19 | 7.4 / 30 |
| CRITICAL | 15.8 / 57 | 10.6 / 38 | 11.1 / 40 |
| ENCOURAGE | 23.4 / 76 | 20.1 / 74 | 19.9 / 75 |
| MISLEADING | 19.0 / 61 | 20.2 / 69 | 20.8 / 75 |
| HEURISTIC | 19.4 / 65 | 12.7 / 48 | 12.1 / 45 |

PRESSURE is the reference: the flattest in all three metrics and, after the difficulty correction,
a level of -0.2 pp on average - it neither helps nor hurts anywhere. The other four swing over
38-75 pp between their best and their worst thinking type.

## Relative profile - difficulty-corrected (positive = comparatively good, negative = to avoid)

| Strategy | best 3 types | worst 3 types |
|---|---|---|
| PRESSURE | L3-F Constraint Check & Repair +8.2 (lvl +8.0, 60%); L1-K Knowledge Retrieval +6.8 (lvl +6.6, 60%); L3-E Style & Persona Fidelity +2.5 (lvl +2.3, 50%) | L2-F Structured Output -10.8 (lvl -11.0, 38%); L2-R Multi-Step Derivation -10.1 (lvl -10.3, 48%); L1-R Direct Computation -2.8 (lvl -3.0, 46%) |
| CRITICAL | L3-E Style & Persona Fidelity +13.8 (lvl +5.4, 48%); L3-F Constraint Check & Repair +10.1 (lvl +1.7, 33%); L3-K Factual Verification +7.8 (lvl -0.7, 70%) | L1-F Format Transformation -23.8 (lvl -32.3, 67%); L1-E Content Generation -12.6 (lvl -21.1, 21%); L1-R Direct Computation -6.9 (lvl -15.4, 24%) |
| ENCOURAGE | L3-E Style & Persona Fidelity +13.6 (lvl -3.1, 30%); L2-E Discourse Organization +12.5 (lvl -4.2, 41%); L3-R Process Control +11.8 (lvl -4.9, 43%) | L1-F Format Transformation -60.4 (lvl -77.1, 0%); L3-F Constraint Check & Repair -8.9 (lvl -25.6, 43%); L2-F Structured Output -1.0 (lvl -17.7, 26%) |
| MISLEADING | L3-E Style & Persona Fidelity +16.9 (lvl -8.2, 33%); L1-K Knowledge Retrieval +15.5 (lvl -9.6, 34%); L3-K Factual Verification +14.1 (lvl -11.1, 50%) | L1-F Format Transformation -51.9 (lvl -77.1, 0%); L3-F Constraint Check & Repair -24.7 (lvl -49.9, 14%); L1-E Content Generation -10.5 (lvl -35.6, 10%) |
| HEURISTIC | L2-E Discourse Organization +14.1 (lvl -4.2, 39%); L3-E Style & Persona Fidelity +10.8 (lvl -7.5, 24%); L2-R Multi-Step Derivation +6.6 (lvl -11.7, 20%) | L1-F Format Transformation -33.8 (lvl -52.1, 0%); L2-F Structured Output -11.2 (lvl -29.5, 20%); L3-K Factual Verification -6.5 (lvl -24.8, 44%) |

## Relative profile - +size-balanced (positive = comparatively good, negative = to avoid)

| Strategy | best 3 types | worst 3 types |
|---|---|---|
| PRESSURE | L3-E Style & Persona Fidelity +17.4 (lvl +16.9, 50%); L1-K Knowledge Retrieval +6.3 (lvl +5.8, 60%); L3-K Factual Verification +2.7 (lvl +2.2, 59%) | L2-R Multi-Step Derivation -12.2 (lvl -12.7, 48%); L2-F Structured Output -7.3 (lvl -7.9, 38%); L2-E Discourse Organization -4.4 (lvl -5.0, 45%) |
| CRITICAL | L3-E Style & Persona Fidelity +19.5 (lvl +8.2, 48%); L3-F Constraint Check & Repair +13.4 (lvl +2.1, 33%); L1-K Knowledge Retrieval +10.3 (lvl -1.0, 53%) | L1-F Format Transformation -20.9 (lvl -32.3, 67%); L1-E Content Generation -11.5 (lvl -22.8, 21%); L2-R Multi-Step Derivation -7.9 (lvl -19.2, 34%) |
| ENCOURAGE | L3-E Style & Persona Fidelity +15.9 (lvl -1.6, 30%); L1-K Knowledge Retrieval +12.6 (lvl -5.0, 43%); L2-E Discourse Organization +10.4 (lvl -7.2, 41%) | L1-F Format Transformation -59.5 (lvl -77.1, 0%); L3-F Constraint Check & Repair -7.6 (lvl -25.1, 43%); L2-F Structured Output -3.3 (lvl -20.8, 26%) |
| MISLEADING | L3-E Style & Persona Fidelity +23.8 (lvl -2.4, 33%); L3-K Factual Verification +19.7 (lvl -6.5, 50%); L1-K Knowledge Retrieval +10.1 (lvl -16.1, 34%) | L1-F Format Transformation -50.9 (lvl -77.1, 0%); L3-F Constraint Check & Repair -28.3 (lvl -54.5, 14%); L1-E Content Generation -8.0 (lvl -34.2, 10%) |
| HEURISTIC | L2-E Discourse Organization +10.3 (lvl -7.4, 39%); L3-F Constraint Check & Repair +9.8 (lvl -7.9, 14%); L3-E Style & Persona Fidelity +7.5 (lvl -10.2, 24%) | L1-F Format Transformation -34.4 (lvl -52.1, 0%); L3-K Factual Verification -7.4 (lvl -25.1, 44%); L1-K Knowledge Retrieval -2.8 (lvl -20.5, 27%) |

## Absolute level - std (pp vs plain, one thinking type = one vote)

| Strategy | L1 | L2 | L3 | K | R | E | F | Overall | gain rate |
|---|---|---|---|---|---|---|---|---|---|
| PRESSURE | +1.1 | -4.9 | +3.2 | +3.0 | -4.3 | +0.7 | -0.3 | -0.2 | 54% |
| CRITICAL | -17.4 | -8.8 | +0.8 | -3.3 | -10.0 | -7.1 | -13.6 | -8.5 | 42% |
| ENCOURAGE | -26.8 | -11.6 | -11.7 | -9.9 | -9.4 | -7.3 | -40.1 | -16.7 | 30% |
| MISLEADING | -36.7 | -18.1 | -20.7 | -13.9 | -17.7 | -20.4 | -48.5 | -25.1 | 23% |
| HEURISTIC | -25.6 | -15.1 | -14.2 | -18.5 | -13.0 | -10.6 | -31.2 | -18.3 | 23% |

## Absolute level - std_fam (pp vs plain, one thinking type = one vote)

| Strategy | L1 | L2 | L3 | K | R | E | F | Overall | gain rate |
|---|---|---|---|---|---|---|---|---|---|
| PRESSURE | +1.5 | -6.9 | +3.7 | +2.0 | -5.6 | +3.3 | -1.9 | -0.6 | 54% |
| CRITICAL | -17.5 | -14.6 | -2.0 | -7.0 | -14.4 | -8.1 | -16.0 | -11.4 | 42% |
| ENCOURAGE | -25.5 | -14.8 | -12.4 | -11.1 | -11.3 | -6.9 | -41.0 | -17.6 | 30% |
| MISLEADING | -38.1 | -20.4 | -20.1 | -15.8 | -19.9 | -18.0 | -51.1 | -26.2 | 23% |
| HEURISTIC | -24.5 | -14.5 | -14.2 | -21.1 | -13.8 | -9.5 | -26.4 | -17.7 | 23% |

## Per-strategy reading (difficulty-corrected + size-balanced)

### PRESSURE

- relative profile: best level Metacognition (+4.3), best target Expression (+3.8), worst target Reasoning (-5.0);
- absolute level after the difficulty correction: +0.0 pp overall, gain rate 54%; 7/12 types Offensive
- comparatively good types (relative / absolute level):
      L3-E  Style & Persona Fidelity    +17.4 pp  (lvl +16.9, n= 22, gain  50%)  -> tone / persona / audience consistency
      L1-K  Knowledge Retrieval          +6.3 pp  (lvl  +5.8, n= 45, gain  60%)  -> lookup, extraction, QA, translation
      L3-K  Factual Verification         +2.7 pp  (lvl  +2.2, n= 22, gain  59%)  -> fact-checking, hallucination spotting, finding the error in an answer
- comparatively bad types (relative / absolute level):
      L2-R  Multi-Step Derivation       -12.2 pp  (lvl -12.7, n= 82, gain  48%)  -> competition maths, proofs, algorithm design, multi-step derivations
      L2-F  Structured Output            -7.3 pp  (lvl  -7.9, n= 16, gain  38%)  -> strict schema output (JSON/CSV/table), long structured answers
      L2-E  Discourse Organization       -4.4 pp  (lvl  -5.0, n= 31, gain  45%)  -> outlines, section structure, argument architecture, narrative arc

### CRITICAL

- relative profile: best level Metacognition (+9.3), best target Knowledge (+4.4), worst target Format (-4.6);
- absolute level after the difficulty correction: -0.0 pp overall, gain rate 41%; 3/12 types Offensive
- comparatively good types (relative / absolute level):
      L3-E  Style & Persona Fidelity    +19.5 pp  (lvl  +8.2, n= 27, gain  48%)  -> tone / persona / audience consistency
      L3-F  Constraint Check & Repair   +13.4 pp  (lvl  +2.1, n=  6, gain  33%)  -> many simultaneous constraints, bug fixing, error handling, self-repair
      L1-K  Knowledge Retrieval         +10.3 pp  (lvl  -1.0, n= 51, gain  53%)  -> lookup, extraction, QA, translation
- comparatively bad types (relative / absolute level):
      L1-F  Format Transformation       -20.9 pp  (lvl -32.3, n=  3, gain  67%)  -> reformatting, field mapping, table/LaTeX conversion, data cleaning
      L1-E  Content Generation          -11.5 pp  (lvl -22.8, n= 34, gain  21%)  -> open-ended writing, brainstorming, first-draft prose, ad copy
      L2-R  Multi-Step Derivation        -7.9 pp  (lvl -19.2, n=117, gain  34%)  -> competition maths, proofs, algorithm design, multi-step derivations

### ENCOURAGE

- relative profile: best level Metacognition (+5.2), best target Expression (+10.7), worst target Format (-23.4);
- absolute level after the difficulty correction: +0.0 pp overall, gain rate 30%; 0/12 types Offensive
- comparatively good types (relative / absolute level):
      L3-E  Style & Persona Fidelity    +15.9 pp  (lvl  -1.6, n= 27, gain  30%)  -> tone / persona / audience consistency
      L1-K  Knowledge Retrieval         +12.6 pp  (lvl  -5.0, n= 54, gain  43%)  -> lookup, extraction, QA, translation
      L2-E  Discourse Organization      +10.4 pp  (lvl  -7.2, n= 29, gain  41%)  -> outlines, section structure, argument architecture, narrative arc
- comparatively bad types (relative / absolute level):
      L1-F  Format Transformation       -59.5 pp  (lvl -77.1, n=  2, gain   0%)  -> reformatting, field mapping, table/LaTeX conversion, data cleaning
      L3-F  Constraint Check & Repair    -7.6 pp  (lvl -25.1, n=  7, gain  43%)  -> many simultaneous constraints, bug fixing, error handling, self-repair
      L2-F  Structured Output            -3.3 pp  (lvl -20.8, n= 19, gain  26%)  -> strict schema output (JSON/CSV/table), long structured answers

### MISLEADING

- relative profile: best level Metacognition (+6.1), best target Knowledge (+10.4), worst target Format (-24.9);
- absolute level after the difficulty correction: +0.0 pp overall, gain rate 22%; 1/12 types Offensive
- comparatively good types (relative / absolute level):
      L3-E  Style & Persona Fidelity    +23.8 pp  (lvl  -2.4, n= 24, gain  33%)  -> tone / persona / audience consistency
      L3-K  Factual Verification        +19.7 pp  (lvl  -6.5, n= 22, gain  50%)  -> fact-checking, hallucination spotting, finding the error in an answer
      L1-K  Knowledge Retrieval         +10.1 pp  (lvl -16.1, n= 50, gain  34%)  -> lookup, extraction, QA, translation
- comparatively bad types (relative / absolute level):
      L1-F  Format Transformation       -50.9 pp  (lvl -77.1, n=  3, gain   0%)  -> reformatting, field mapping, table/LaTeX conversion, data cleaning
      L3-F  Constraint Check & Repair   -28.3 pp  (lvl -54.5, n=  7, gain  14%)  -> many simultaneous constraints, bug fixing, error handling, self-repair
      L1-E  Content Generation           -8.0 pp  (lvl -34.2, n= 41, gain  10%)  -> open-ended writing, brainstorming, first-draft prose, ad copy

### HEURISTIC

- relative profile: best level Metacognition (+3.5), best target Expression (+8.2), worst target Format (-8.7);
- absolute level after the difficulty correction: +0.0 pp overall, gain rate 23%; 0/12 types Offensive
- comparatively good types (relative / absolute level):
      L2-E  Discourse Organization      +10.3 pp  (lvl  -7.4, n= 36, gain  39%)  -> outlines, section structure, argument architecture, narrative arc
      L3-F  Constraint Check & Repair    +9.8 pp  (lvl  -7.9, n=  7, gain  14%)  -> many simultaneous constraints, bug fixing, error handling, self-repair
      L3-E  Style & Persona Fidelity     +7.5 pp  (lvl -10.2, n= 29, gain  24%)  -> tone / persona / audience consistency
- comparatively bad types (relative / absolute level):
      L1-F  Format Transformation       -34.4 pp  (lvl -52.1, n=  2, gain   0%)  -> reformatting, field mapping, table/LaTeX conversion, data cleaning
      L3-K  Factual Verification         -7.4 pp  (lvl -25.1, n= 25, gain  44%)  -> fact-checking, hallucination spotting, finding the error in an answer
      L1-K  Knowledge Retrieval          -2.8 pp  (lvl -20.5, n= 49, gain  27%)  -> lookup, extraction, QA, translation
