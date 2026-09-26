# Design Rationale for Figure 2: the Three-Dimension System and the Thinking-Type Taxonomy

*This document explains the design rationale behind the encoding "one bar = one thinking type" used in
Figure 2: what the three dimensions are, why these three, how the 12 types are constructed, and how each
dimension is read off the figure. Companion files: `fig2_types_table.md` (per-type three-dimension
values), `fig2_strategy_findings.md` (strategy profiles and conclusions), `difficulty_correction.md`
(difficulty-correction method).*

---

## 0 Terminology

- **thinking type (the "thinking style" plotted in Figure 2)**: one bar in the figure; there are 12 of
  them, obtained by crossing two task-intrinsic axes and denoted `L1..L3 x K/R/E/F` (e.g. `L2-F`).
- **dimension**: the coordinates of a type. The three dimensions used here are **operation level**,
  **target of intervention**, and **starting state**.
- **strategy**: a way of re-asking, of which five are compared (PRESSURE / CRITICAL / ENCOURAGE /
  MISLEADING / HEURISTIC). Each strategy has 12 bars, forming one profile panel.

## 1 Design goals

The taxonomy has to satisfy four requirements simultaneously; otherwise the question "which strategy is
good at which kind of thinking" cannot be answered at all:

1. **Orthogonality** — the two axes must not determine each other. If "target" implied "level", half of
   the 12 cells would be empty and the comparison would collapse into a single-axis one.
2. **Observability** — every type must be backed by enough task rows (in this dataset: 12–680 rows per
   type), otherwise every difference is noise.
3. **Task-intrinsic** — a type must be determined by the **task itself**, independent of which strategy
   is applied and of how strong the current model is. This is what rules out empirically derived
   attributes as classification axes (see §3 on "nature of gain" and "headroom").
4. **Cognitive interpretability** — taken together, the three dimensions must be able to answer "what
   kind of thinking does this type demand?", not "how much did the numbers move for this type?".

## 2 Dimensions 1 and 2: the classification grid (where the 12 types come from)

### 2.1 Dimension 1 — operation level (how deep the thinking goes)

| Value | Name | Meaning | Characteristic failure |
|---|---|---|---|
| L1 | Execution | single-step direct production: retrieve one fact, do one computation, write one passage, perform one format conversion | cannot produce it / computes it wrong |
| L2 | Structure | multi-step organisation and chaining: synthesise several sources, chain a multi-step derivation, organise a discourse, produce a structured artefact | steps do not connect, structure does not hold |
| L3 | Metacognition | monitoring, checking, repairing: verify facts, control a process, hold a style, check and repair constraints | does not notice the deviation, repairs the wrong thing |

The layering rests on **what the operation acts upon**: L1 acts on the input itself, L2 acts on the
intermediate product the model has just produced, L3 acts on the correctness and consistency of an
already-existing output. This dimension determines at which level a re-ask has to do its work again.

### 2.2 Dimension 2 — target of intervention (where the thinking is directed)

| Value | Name | Meaning | Scoring (data fact) |
|---|---|---|---|
| K | Knowledge | knowledge and factual content | whether the fact is right (including exact match in the math family) |
| R | Reasoning | the reasoning and computation process | whether the conclusion (and the derivation) holds |
| E | Expression | expression: prose, discourse, style, tone | judged (LLM/human) — open-ended output |
| F | Format | format constraints: structure, schema, length, template | whether the constraints are satisfied |

This dimension is the concrete landing place of the open question "what counts as success": K and R have
verifiable anchors, E is negotiated, F is a hard constraint.

### 2.3 Crossing the two axes yields the 12 types

`3 x 4 = 12`, and all 12 cells contain real tasks (the smallest cell, L1-F, has 12 rows in total; note
that on the **per-strategy** level L1-F keeps only 2–3 rows, so that cell is flagged "thin" in every
strategy profile). The two axes do not imply each other by construction: L1 contains both K (knowledge
retrieval) and F (format transformation), and L3 contains both K (factual verification) and E (style
fidelity).

Names and Chinese labels are in `fig2_types_table.md`; the raw definitions live in the `TYPES` table of
`taxonomy_v2.py`.

## 3 Two rejected "third dimensions", and the one that is used

### 3.1 Rejected: "nature of gain" (offensive / defensive)

The original third dimension was "is this strategy's gain on this type offensive or defensive?" It was
dropped because it is **empirically derived and almost entirely determined by the strategy**: in this
dataset ENCOURAGE and HEURISTIC are defensive on all 12 types, CRITICAL is 3 offensive / 9 defensive,
MISLEADING 1 / 11, and only PRESSURE is 7 / 5. It is therefore not a property of the type but a
consequence of "strategy x current difficulty of that type"; plotted on a bar it makes a whole panel
uniformly coloured and carries no information. It also fails requirement 3 of §1 (task-intrinsic).

### 3.2 Rejected: "headroom"

Headroom is defined as `100 − the type's baseline score`, i.e. "how much room for improvement is left on
this kind of task". It ranges over 8.0–44.8 pp across the 12 types (median ≈ 29 pp). It is rejected
because **it belongs to a different coordinate system**: the baseline is a property of "the current
model x this kind of task" and changes as soon as the model is upgraded, whereas dimensions 1 and 2 are
properties of the task and do not change with the model. Headroom answers "in which cells is there still
room to gain if we re-ask", not "what kind of thinking does this type demand". In the analysis it is in
fact the quantity being **corrected for** (see `difficulty_correction.md`): it is a moderator of the
outcome variable and cannot be promoted to an independent variable (a classification axis).

### 3.3 Adopted: "starting state" — continuation vs from scratch

**The third question**: dimensions 1 and 2 answer "how deep" and "acting on what"; what is missing is
"**from what state does the thinking start**" — from a blank sheet, or from an existing output that must
be continued and incrementally modified.

- **continuation**: the type contains items that build on a previous turn's output (the directly
  identifiable case in the data is MT-Bench second turns, whose items carry a follow-up instruction such
  as rewrite / elaborate / reformat / continue from the earlier answer). The measured value `c_t` is the
  share of such items among the type's rows.
- **from scratch**: `c_t < 30 %`, i.e. the type's tasks are essentially "given an input, produce a
  complete output".
- What the 30 % threshold buys: a 6 : 6 split in which each level gets **exactly 2 : 2** and each target
  1–2 : 2–1, so the new dimension does not reintroduce an imbalance on either existing axis.

**Why it satisfies the four requirements of §1**:

| Requirement | How it is met |
|---|---|
| Orthogonality | Cramér's V = 0.00 vs level and 0.33 vs target (compare: headroom 0.41 / 0.58; "answer convergence" 0.00 / **1.00**, i.e. fully absorbed by the target axis, hence unusable) |
| Observability | computed directly from task rows (share of MT-Bench second turns); no extra annotation needed |
| Task-intrinsic | a structural property of the task set, independent of model strength and of the strategy applied |
| Cognitive interpretability | see below |

**Cognitive reading**:

- **From scratch = construction load.** The input is closed and there is no existing output. The thinker
  must choose the solution path and the criterion of completion on its own, and must **construct the
  product in full**; the characteristic failures are "cannot build it" and "builds in the wrong
  direction".
- **Continuation = integration-and-preservation load.** The input is open: an existing output is present
  and **most of it must be preserved**, while the change is requested only along a specified dimension.
  The thinker must read the existing output, decide what can be reused and what must change, and perform
  an **incremental modification under inherited constraints**; the characteristic failures are
  "over-shooting the edit" and "not actually implementing the new constraint".

Within the same target and the same level these two situations are substantively different: `L2-E`
(discourse organisation, `c_t` 0.26, mostly building a structure from scratch) and `L3-E` (style
fidelity, 0.57, mostly preserving a style in an existing draft) both belong to the "expression" target,
yet their starting states are opposite.

**Construct-validity caveat (recorded honestly)**: the current assignment is a **measurement** (the share
of continuation items), not an annotation. As a proxy for "builds on an existing output" it does not
always agree with the literal definition of the type: `L3-K` (factual verification), `L3-F` (constraint
check and repair) and `L1-F` (format transformation) all carry, by definition, a flavour of "checking /
transforming an existing output", yet by measurement they fall on the from-scratch side. Turning this into
a **annotated** axis on a par with level and target would require a single annotation pass over the 12
types ("does it build on an existing output?" — 12 items, not 683 tasks), which can be added on request,
with the figures regenerated; the present figures use the measurement version because it is
data-determined, reproducible, and already satisfies the orthogonality requirement.

## 4 How the three dimensions are read off the figure

| Dimension | Visual channel | Encoding |
|---|---|---|
| operation level | **colour** | L1 blue / L2 green / L3 red |
| target of intervention | **pattern** | K none / R diagonal `///` / E cross `xxx` / F backslash `\\\` |
| starting state | **solid vs hollow** | continuation = solid (hatch lines drawn in white); from scratch = pale fill + dashed edge + hatch in the level colour |

Additional conventions: the value of each bar (`std_rel`, i.e. relative to that strategy's own 12-type
mean) is printed at the bar end; the right margin gives `n=` for that cell, with `n < 15` flagged in red
and the bar lightened; bars clipped by the axis carry `↯`. Four grey rows below each panel give the
marginals of that dimension (3 level rows, 4 target rows, 2 starting-state rows, 1 all-types row), so
that "which dimension explains more" can be compared at a glance.

## 5 Division of labour between the documents

- **This document**: the design rationale (why these three dimensions, why these 12 types).
- **`fig2_types_table.md`**: the three-dimension value table for the 12 types (with measured values and a
  one-line cognitive-demand description each).
- **`fig2_strategy_findings.md`**: strategy profiles (who is good at which type, and on which side of
  each dimension) with paper-style conclusions and limitations.
- **`difficulty_correction.md`**: difficulty correction (headroom band, binning, reference mix, direct
  standardisation, sensitivity).
- **Code**: `taxonomy_v2.py` (type definitions), `tt3_analysis.py` (corrected cells), `make_figs_tt7.py`
  (Figure 2 rendering), `_fig2_stats.py` (every marginal and η² quoted in these documents).
