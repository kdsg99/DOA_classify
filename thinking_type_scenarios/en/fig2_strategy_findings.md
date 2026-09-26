# Strategy Profiles in Figure 2: What Each Re-Ask Strategy Is Good At

*Paper-style account. Reading conventions are in §1; per-type values in `fig2_types_table.md`; the design
rationale for the three dimensions in `fig2_design.md`; the difficulty-correction method in
`difficulty_correction.md`.*

---

## 0 High-level synthesis: where each re-ask pushes the model's thinking

Each re-ask strategy can be read as a **thinking displacement** operation: it does not change the task,
it changes the model's mode of thinking about the task. The three dimensions give the direction of that
displacement — level (does the thinking get pushed one layer up), target (towards which kind of content),
and starting state (does it need an existing output as an anchor).

**Table 0.1 Thinking-displacement profiles of the five strategies**

| Strategy | Thinking mode it elicits | Displacement direction (three dimensions) | Source of gain | Price paid (where the losses come from) | One-line role |
|---|---|---|---|---|---|
| PRESSURE | Rehearsal / re-doing in place: walk the same solution path once more | level: none (+1.3 / −4.7 / +3.4); target: flat; starting state: none | introduces no new perspective and no new goal → smallest output variance (SD 5.7) | L2-R −10.3, L2-F −11.0: re-walking the same path amplifies earlier mistakes and makes it easier to drop constraints | **the zero-displacement rehearsal** (the "thinking frozen" control) |
| CRITICAL | Reviewer / proof-reader thinking: find the problem, align with the standard, repair | level: **strongest upward displacement** (−8.9 → +9.3, span 18.2); target: leans towards the "checkable" items in K / E / F; starting state: none (0.6) | metacognitive (L3) tasks genuinely need an external viewpoint | L1 −8.9: single-step tasks have no structure to review, so doubt only adds disturbance | **turns the model into a reviewer** (metacognition specialist) |
| ENCOURAGE | Divergent expansion: change the angle, add another layer, offer more solutions | level: pushes to L2/L3 (+5.1 / +5.0); target: **pushes to E (+9.3)**; starting state: **most anchor-dependent (gap 12.6, the largest)** | open-ended output has negotiated success criteria, so expansion converts directly into gain | F −23.5: expansion is over-shooting; L1 −10.1 | **pushes the model towards expressive divergence** (content expansion) |
| MISLEADING | Adversarial verification: "is this claim actually right?" | level: pushes to L2/L3 (+7.1 / +4.5); target: **pushes to K (+11.2, highest of the four)** then R (+7.4); starting state: gap 9.8 | tasks with a verifiable anchor activate a confirm/refute loop and the model resists from internal knowledge | E (especially L1-E −10.5): with no objective standard to fall back on, open generation gets dragged along; F −23.4 | **pushes the model towards evidence checking and position defence** (resists when anchored, collapses when not) |
| HEURISTIC | Cue-driven local repair: change one spot, add one step, leave the overall structure alone | level: positive on L2/L3 (+3.2 / +4.1); target: pushes to E (+7.7) and R (+5.3); starting state: **least sensitive (gap 3.6)** | point edits are cheap and need no anchor | only strategy negative on K (−0.2, L3-K −6.5): a cue substitutes for independent judgement and steers the model towards the hinted answer; F −12.9 | **pushes the model towards cue-driven local repair** (mildest, but replaces independent judgement) |

**Table 0.2 Three readable scales of displacement** (span of the `std_rel` marginals; `std` = absolute scale)

| Strategy | Level span L1→L3 | Strongest target | Weakest target | Starting-state gap | SD (relative profile) | Absolute mean |
|---|---|---|---|---|---|---|
| PRESSURE | 8.1 | K +3.2 | R −4.1 | 3.6 | 5.7 | −0.2 |
| CRITICAL | **18.2** | K +5.2 | F −5.1 | 0.6 | 10.6 | −8.5 |
| ENCOURAGE | 15.2 | E +9.3 | F −23.5 | **12.6** | 20.1 | −16.7 |
| MISLEADING | 18.6 | K +11.2 | F −23.4 | 9.8 | 20.2 | −25.1 |
| HEURISTIC | 11.4 | E +7.7 | F −12.9 | 3.6 | 12.7 | −18.3 |

**Three general laws across strategies** (what "re-asking" itself does):

1. **Level law: a re-ask is re-processing, not re-executing.** The four non-control strategies lose
   uniformly on the L1 execution level (−7.3 to −11.5) and gain uniformly on L2/L3 → any content-bearing
   re-ask pushes thinking from "direct production" towards "further processing of a product"; execution
   tasks offer no structure to process again, which makes them a built-in blind spot of re-asking.
2. **Target law: content expansion and constraint satisfaction trade off.** All three content-adding
   strategies (ENCOURAGE / MISLEADING / HEURISTIC) displace towards the content side (positive on E / K
   / R) and pay for it in constraint satisfaction (F: −12.9 to −23.5) → between "think outward" and
   "respect the boundary", a re-ask can only buy one.
3. **Starting-state law: revision beats re-construction, and the larger the displacement the more it
   needs an anchor.** Continuation tasks are uniformly better than from-scratch tasks, and the gap scales
   with how expansive the strategy is: ENCOURAGE (most expansive) 12.6 pp, MISLEADING 9.8 pp, HEURISTIC
   3.6 pp; CRITICAL barely depends on an anchor (0.6 pp) because the reviewing action it elicits is
   itself directed at an existing output. → Re-asking is a cheap incremental revision only when there is
   an existing output to continue; otherwise it is an expensive re-construction.

**One-paragraph summary (abstract-ready)**: the five re-ask strategies are not five levels of intensity
but five **modes of thinking displacement** — PRESSURE rehearses thinking in place (the zero-displacement
control), CRITICAL turns the model into a reviewer (metacognition specialist), ENCOURAGE pushes thinking
towards expressive divergence (content expansion), MISLEADING pushes it towards evidence checking and
position defence (resisting when an anchor exists, collapsing when not), and HEURISTIC pushes it towards
cue-driven local repair (mildest, at the price of replacing independent judgement). All five are
constrained by three laws: re-asking only works above the execution level (L2/L3); content expansion is
always paid for in constraint satisfaction; and re-asking is revision rather than re-construction only
when an existing output can be continued.

---

## 1 Data and reading conventions

- **Sample**: 2801 *(strategy, task)* observations, 5 strategies x 12 thinking types = 60 cells, with
  2–204 rows per cell (median 36.5).
- **Difficulty correction**: keep only rows with baseline 5 ≤ p ≤ 95 (1954 rows), bin into 20 pp bins and
  apply direct standardisation to a single reference mix `w = (0.093, 0.068, 0.108, 0.731)`;
  `std_fam` additionally re-averages with "one evaluation family, one vote".
- **Profile scale**: `std_rel` = the corrected cell value minus that strategy's own equally weighted mean
  over its 12 types (one type, one vote; pp). A value of 0 means "for this strategy, this type is at its
  own average"; positive = comparatively good, negative = comparatively bad. The absolute scale (`std`)
  is reported separately and used for the "who is best" comparison in §2.
- **Readability conventions**: `L1-F` (n = 2–3) and `L3-F` (n = 5–7) are thin on both scales and are
  treated as directional only; they enter no ranking. Cells with `n < 15` are marked in the figure with a
  red `n=` and a lighter bar.
- **Significance**: none of the stratified results here passes FDR < 0.05 (with only 6 types per
  strategy x type there is insufficient power), so every statement below is descriptive and suggestive:
  it is meant to generate mechanistic hypotheses, not to claim established effects.

## 2 Main result: judged by "not losing points", the strongest re-ask is the one that changes nothing

On the absolute scale (`std`, pp):

| Strategy | mean | SD | range |
|---|---|---|---|
| PRESSURE | −0.2 | 5.7 | 19 |
| CRITICAL | −8.5 | 10.6 | 38 |
| HEURISTIC | −18.3 | 12.7 | 48 |
| ENCOURAGE | −16.7 | 20.1 | 74 |
| MISLEADING | −25.1 | 20.2 | 69 |

Across the 12 types, **PRESSURE (re-asking the same question unchanged) achieves the best absolute level
in 10 of them**. The only two exceptions are **L2-F structured output** (PRESSURE −11.0 vs CRITICAL
−10.1) and **L3-E style fidelity** (PRESSURE +2.3 vs CRITICAL +5.4). In other words, strategies that ask
the model to do it again and explain itself lose points overall; the only occasions on which they beat
"just ask again" are **rearranging content into a given structure** and **holding a style over an
existing text**.

At the same time PRESSURE is not a zero effect: it still shows systematic losses on **L2-R multi-step
derivation (−10.3)** and **L2-F structured output (−11.0)**, and neither cell is thin (n = 82 / 16).
These two types are therefore **hostile to re-asking as such**: in multi-step derivation, redoing the
problem sends the model down the same path and replays the earlier mistake; in structured output, redoing
it means satisfying the whole set of hard constraints again.

## 3 Dimension 1 (operation level): gain rises monotonically with level

Marginals (`std_rel`, pp; one vote per type, 4 types per level):

| Strategy | L1 Execution | L2 Structure | L3 Metacognition | L1→L3 span |
|---|---|---|---|---|
| PRESSURE (control) | +1.3 | −4.7 | +3.4 | 8.1 |
| CRITICAL | −8.9 | −0.3 | **+9.3** | **18.2** |
| ENCOURAGE | −10.1 | +5.1 | +5.0 | 15.2 |
| MISLEADING | −11.5 | +7.1 | +4.5 | 18.6 |
| HEURISTIC | −7.3 | +3.2 | +4.1 | 11.4 |

**Reading**: the four non-control strategies are **uniformly negative on L1** (−7.3 to −11.5) and
**uniformly positive on L2/L3** (+3.2 to +9.3). Mechanistically, L1 is the single-step level: there is no
intermediate structure to review, so re-asking is just another attempt in the same single step, and
points are more easily lost; L2/L3 contain objects that can be re-organised or re-monitored, which is
where a re-ask has room to do work.

**Differences**: CRITICAL has the steepest level slope (span 18.2 pp) and the highest L3 marginal
(+9.3, against +4.1 to +5.0 for the others) — i.e. "ask for a critique / justification" specialises in
the metacognitive level. PRESSURE's level values (+1.3 / −4.7 / +3.4) show no monotonicity, as expected
of a negative control.

## 4 Dimension 2 (target): constrained output is the common weakness, expression and knowledge split the most

Marginals (`std_rel`, pp; one vote per type, 3 types per target):

| Strategy | K Knowledge | R Reasoning | E Expression | F Format |
|---|---|---|---|---|
| PRESSURE (control) | +3.2 | −4.1 | +0.9 | −0.1 |
| CRITICAL | +5.2 | −1.5 | +1.4 | −5.1 |
| ENCOURAGE | +6.8 | +7.3 | **+9.3** | **−23.5** |
| MISLEADING | **+11.2** | +7.4 | +4.8 | **−23.4** |
| HEURISTIC | −0.2 | +5.3 | +7.7 | −12.9 |

Three points:

1. **F (format constraints) is the common weakness of every content-adding strategy**: ENCOURAGE −23.5,
   MISLEADING −23.4, HEURISTIC −12.9, CRITICAL −5.1, against only −0.1 for the control. This is not an
   artefact of thin cells: `L2-F` (n = 16–21, not thin) is also negative on the absolute scale across the
   board (−10.1 to −29.5 pp). Mechanistically, a format task is decided by whether **all** hard
   constraints are satisfied; another attempt only enlarges the edit surface, and the more you edit, the
   easier it is to break another constraint.
2. **E (expression) is the sweet spot of the "add words" strategies**: ENCOURAGE +9.3, HEURISTIC +7.7,
   MISLEADING +4.8. The success criterion of open-ended output is negotiated, so additional requirements
   translate easily into gain.
3. **K (knowledge) and R (reasoning) split internally**: on K, MISLEADING is the highest of the four
   (+11.2, coming from `L1-K` +15.5 and `L3-K` +14.1), suggesting that tasks with a verifiable anchor
   resist misleading prompts; on R the marginals put the control strategy negative (−4.1) and all four
   strategies positive (+5.3 to +7.4), but within the axis the two types are poles apart: on `L2-R` the
   control loses heavily (−10.1) while the four are positive (+3.7 to +9.9), and on `L3-R` all five are
   positive (+5.3 to +11.8, control +0.7). "Reasoning" is thus not homogeneous: it depends on whether it
   lands in multi-step derivation (a from-scratch chain) or in process control (continuation-style
   review).

## 5 Dimension 3 (starting state): continuation wins, with the gap ordered by strategy

| Strategy | continuation (6 types) | from scratch (6 types) | gap | gap on `std_fam_rel` |
|---|---|---|---|---|
| ENCOURAGE | +6.3 | −6.3 | **12.6** | 12.0 |
| MISLEADING | +4.9 | −4.9 | 9.8 | 10.6 |
| HEURISTIC | +1.8 | −1.8 | 3.6 | 6.8 |
| PRESSURE | −1.8 | +1.8 | 3.6 | 1.4 |
| CRITICAL | −0.3 | +0.3 | 0.6 | 0.0 |

**Reading (with a warning)**: the split is 6 : 6 and the profile is centred over the 12 types, so the two
group means are necessarily mirror images; only the **gap** is readable. The readable conclusion is that
**the strategies that ask the model to change direction (ENCOURAGE / MISLEADING) are comparatively strong
on continuation tasks and comparatively weakest on from-scratch construction, whereas CRITICAL barely
differentiates** (its action — reviewing an existing output — has little to do with whether such an output
exists). Mechanistically, in a continuation task the existing output provides an anchor and reusable
material, so a new prompt only triggers a local edit on top of it; in a from-scratch task the same prompt
forces the whole construction to be redone, without the model knowing where the previous version went
wrong, so it has to start a new path.

## 6 Which dimension explains more (η² of the dimensions)

Share of the variance among each strategy's 12 profile values explained by each dimension:

| Strategy | level | target | starting state | dominant dimension |
|---|---|---|---|---|
| PRESSURE (control) | 0.40 | 0.23 | 0.10 | none (all low) |
| CRITICAL | **0.54** | 0.14 | 0.00 | **level** |
| ENCOURAGE | 0.14 | **0.50** | 0.11 | target |
| MISLEADING | 0.18 | **0.50** | 0.06 | target |
| HEURISTIC | 0.18 | **0.43** | 0.02 | target |

(`std_fam_rel` is the same in direction: CRITICAL 0.40 / 0.13 / 0.00; ENCOURAGE 0.09 / 0.52 / 0.10;
MISLEADING 0.18 / 0.52 / 0.07; HEURISTIC 0.17 / 0.32 / 0.09.)

**This is what explains the division of labour between dimensions**: CRITICAL's profile is dominated by
**level** (the only "L3 specialist"); ENCOURAGE / MISLEADING / HEURISTIC are dominated by **target** (all
of the form "expression benefits, format suffers"); and **the starting state is the smallest of the three
for all of them (0.00–0.11)** — it is not an axis for ranking types but an axis that explains the
**overall level shift** (continuation is 2 to 6 pp better overall). This is exactly the property an
independent third dimension should have: it does not compete for variance with the two dimensions that
are already being explained.

## 7 Main per-type table (12 types x 5 strategies, `std_rel`, pp)

⚠ = thin cell (n < 15), excluded from conclusions.

| type | Name | level | target | start | PRESSURE | CRITICAL | ENCOURAGE | MISLEADING | HEURISTIC | best |
|---|---|---|---|---|---|---|---|---|---|---|
| L1-K | Knowledge Retrieval | L1 | K | scratch | +6.8 | +7.5 | +11.6 | **+15.5** | +2.8 | MISLEADING |
| L1-R | Direct Computation | L1 | R | cont. | −2.8 | −6.9 | +6.5 | +0.7 | +3.5 | ENCOURAGE |
| L1-E | Content Generation | L1 | E | cont. | −1.0 | −12.6 | +2.0 | −10.5 | −1.7 | ENCOURAGE |
| L1-F ⚠ | Format Transformation | L1 | F | scratch | +2.3 | −23.8 | −60.4 | −51.9 | −33.8 | PRESSURE |
| L2-K | Knowledge Synthesis | L2 | K | cont. | +0.7 | +0.2 | +5.2 | +4.0 | +3.2 | ENCOURAGE |
| L2-R | Multi-Step Derivation | L2 | R | scratch | −10.1 | −2.9 | +3.7 | +9.9 | +6.6 | MISLEADING |
| L2-E | Discourse Organization | L2 | E | scratch | +1.2 | +3.0 | +12.5 | +7.8 | **+14.1** | HEURISTIC |
| L2-F | Structured Output | L2 | F | cont. | −10.8 | −1.7 | −1.0 | +6.6 | −11.2 | MISLEADING |
| L3-K | Factual Verification | L3 | K | scratch | +2.1 | +7.8 | +3.6 | **+14.1** | −6.5 | MISLEADING |
| L3-R | Process Control | L3 | R | cont. | +0.7 | +5.3 | +11.8 | +11.6 | +6.0 | ENCOURAGE |
| L3-E | Style & Persona Fidelity | L3 | E | cont. | +2.5 | **+13.8** | +13.6 | +16.9 | +10.8 | MISLEADING |
| L3-F ⚠ | Constraint Check & Repair | L3 | F | scratch | +8.2 | +10.1 | −8.9 | −24.7 | +6.2 | CRITICAL |

## 8 Strategy by strategy

**PRESSURE (re-ask unchanged; negative control)** — role: a flat baseline (SD 5.7, the smallest).
Comparatively strongest: `L3-F` ⚠ / `L1-K` +6.8 / `L3-E` +2.5; comparatively weakest: `L2-F` −10.8 /
`L2-R` −10.1. Its value is not in itself but in two things: (a) it supplies the lower-bound reference for
"just asking again"; (b) its systematic losses on `L2-R` and `L2-F` identify two types that are
**hostile to re-asking** (a reasoning chain must be rebuilt from scratch; constraints must all be
re-satisfied).

**CRITICAL (ask for a critique / justification)** — role: **the level specialist** (level η² 0.54), the
only strategy clearly positive on L3 (+9.3); comparatively strongest `L3-E` +13.8 / `L3-F` ⚠ +10.1 /
`L3-K` +7.8; comparatively weakest `L1-F` ⚠ / `L1-E` −12.6 / `L1-R` −6.9. It is the **only strategy that
achieves the best absolute level on any type** (`L2-F`, `L3-E`). Mechanism: a critical re-ask supplies
an external viewpoint, which is exactly the missing step in tasks that already demand monitoring and
checking; on single-step tasks there is no structure to check, so the same doubt only adds disturbance.

**ENCOURAGE (encourage another angle / more detail)** — role: **target-driven** (target η² 0.50), with
expression and reasoning benefiting and format suffering. Comparatively strongest `L3-E` +13.6 /
`L2-E` +12.5 / `L3-R` +11.8; comparatively weakest `L1-F` ⚠ −60.4 / `L3-F` ⚠ −8.9 / `L2-F` −1.0. It also
has the largest continuation gap of all strategies (12.6 pp).

**MISLEADING (supply biased information / a wrong direction)** — role: target-driven, and most resilient
on tasks with an anchor. Comparatively strongest `L3-E` +16.9 / `L1-K` +15.5 / `L3-K` +14.1 / `L2-R` +9.9;
comparatively weakest `L1-F` ⚠ −51.9 / `L3-F` ⚠ −24.7 / `L1-E` −10.5 (only better than CRITICAL's
−12.6 there). Two points deserve discussion: (a) it is the highest of the four on K (knowledge, factual
verification, +11.2), showing that a **verifiable anchor** lets the model resist misleading input; (b) it
is clearly negative on `L1-E` (content generation), showing that **open generation with no objective
standard to fall back on** is the first thing to collapse under misleading prompts.

**HEURISTIC (hint-style follow-up / give a clue)** — role: target-driven but the mildest (SD 12.7), with
expression benefiting and K and F suffering. Comparatively strongest `L2-E` +14.1 / `L3-E` +10.8 /
`L2-R` +6.6; comparatively weakest `L1-F` ⚠ −33.8 / `L2-F` −11.2 / `L3-K` −6.5. It is the only strategy
negative on K (−0.2, driven by `L3-K` −6.5): a clue does not help tasks that require an independent
anchor, and may instead steer the model towards the hinted direction.

## 9 Limitations

1. **No FDR control**: each strategy x type has only 6 types voting, so power is insufficient; all
   stratified statements here are descriptive and suggestive.
2. **Thin cells**: `L1-F` (n = 2–3) and `L3-F` (n = 5–7) are marked red in the figure and are excluded
   from rankings; the −50 to −77 pp values for `L1-F` are readable only as "this cell is extreme".
3. **Strategies overlap heavily**: pairwise Δ correlations between the five strategies are 0.66–0.93, so
   "specialisation" here means a **relative** advantage, not an exclusive capability.
4. **Scale depends on the reference frame**: absolute levels depend strongly on the reference mix (see
   the sensitivity table in `difficulty_correction.md` §6); only comparisons within the same frame are
   meaningful, which is why the main table uses the relative profile.
5. **Construct validity of dimension 3**: the starting state is currently measured (continuation-item
   share), not annotated (see `fig2_design.md` §3.3); switching `L3-K` / `L3-F` / `L1-F` to a
   definition-based assignment would require one 12-item annotation pass.

## 10 Conclusion paragraph (ready for the paper)

Under a single difficulty frame, the 12-type profiles of the five re-ask strategies exhibit three stable
stratifications. **Along the operation level**, the four non-control strategies are uniformly negative on
the L1 execution level and uniformly positive on L2/L3, with CRITICAL showing the steepest slope and the
only clear gain at L3. **Along the target of intervention**, constrained-format tasks are the common
weakness of the four strategies (ENCOURAGE −23.5, MISLEADING −23.4, HEURISTIC −12.9, CRITICAL −5.1 pp,
and the non-thin `L2-F` is negative on the absolute scale for all of them), while expression tasks are
the sweet spot of the content-adding strategies (ENCOURAGE +9.3, HEURISTIC +7.7, MISLEADING +4.8 pp), and
knowledge tasks reveal a "verifiable anchor resists misleading" pattern (MISLEADING is the highest of the
four on K, +11.2). **Along the starting state**, continuation tasks are uniformly better than
from-scratch ones (gaps: ENCOURAGE 12.6 pp, MISLEADING 9.8 pp, CRITICAL 0.6 pp). Judged by "not losing
points", the strongest re-ask is to ask again unchanged (best in 10 of 12 types); only on structured
output and style fidelity does a critical re-ask overtake it — consistent with the intuition that
re-asking is re-construction rather than increment, and pointing to two exceptional settings that deserve
larger samples in follow-up work.
