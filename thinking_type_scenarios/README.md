# Thinking type × re-ask strategy — three-dimension analysis

Rebuilt on the **original three-dimension taxonomy** (`taxonomy_v2.py` / `classify_v2.py`): every thinking
type is a **combination of dimension values**, not a stand-alone label.

## The three dimensions

| # | Dimension | Values | Role |
|---|---|---|---|
| 1 | **Operation level** (认知操作层级) | `L1` Execution (内容执行) · `L2` Structure (结构组织) · `L3` Metacognition (元认知控制) | task label |
| 2 | **Target of intervention** (干预对象) | `K` Knowledge/Fact (知识事实) · `R` Reasoning/Logic (过程逻辑) · `E` Expression/Creativity (表达创意) · `F` Format/Constraint (格式约束) | task label |
| 3 | **Nature of strategy gain** (增益性质) | `Defensive` vs `Offensive` | **measured** per (strategy, type) as the share of rows that improved (`gain_rate`); ≥50 % ⇒ Offensive |

Dimension 1 × dimension 2 = the **12 thinking types**: L1-K Knowledge Retrieval, L1-R Direct Computation,
L1-E Content Generation, L1-F Format Transformation, L2-K Knowledge Synthesis, L2-R Multi-Step Derivation,
L2-E Discourse Organization, L2-F Structured Output, L3-K Factual Verification, L3-R Process Control,
L3-E Style & Persona Fidelity, L3-F Constraint Check & Repair (中文名见 `taxonomy_v2.py`).

## How to read the figures

Two readings of the same 12 cells are produced:

* **relative** (bars in the three main figures) — the value of a thinking type minus the strategy's own
  equal-type-weight average over the 12 types. **Positive = a type this strategy does comparatively well on,
  negative = a type to avoid.** This is the "which type is this strategy for?" reading.
* **level** (printed at the right margin of every bar as `lvl`, and drawn in the two `*_levels.png` figures)
  — the same value in absolute terms, i.e. the change against the plain (no-strategy) run. A comparative win
  can still be a small absolute loss.

Difficulty is always the **ORIGINAL** score (`plain_minmax`, the no-strategy run). Δ = 100 × (reask − plain).

1. **Figure 1 (`raw_rel` / `raw`).** No correction, all rows.
2. **Figure 2 (`std_rel` / `std`) — difficulty-corrected by the original score.** Rows restricted to the
   headroom band `5 ≤ original ≤ 95` (a row at 100 % can only lose, a row at 0 % can only gain) and then
   **re-weighted to the same difficulty mix in every cell** (20 pp bins, pooled population as reference;
   `out/meta.json → reference_mix`). A cell covering < 50 % of the reference weight falls back to its in-band
   mean (`coverage` / `fallback` in `out/cells_3dims.csv`).
3. **Figure 3 (`std_fam_rel` / `std_fam`) — + size-balanced.** The Figure-2 values re-averaged with **equal
   weight per evaluation family** (one family = one vote), so a value does not depend on how many rows a type
   happens to have or on being concentrated in one benchmark.

Cells with `n < 15` (L1-F, L3-F) are hatched and pale in the figures and marked `thin` in the CSV.
`resid_lin` (per-strategy OLS residual of Δ on the original score) is exported for reference only: it
re-centres every strategy on its own fitted line and therefore removes part of the level differences the
figures are about.

## Key result

Spread of the 12 type values — SD (range), pp, one type = one vote:

| Strategy | raw | difficulty-corrected | +size-balanced |
|---|---|---|---|
| PRESSURE | **6.2 (26)** | **5.7 (19)** | **7.4 (30)** |
| CRITICAL | 15.8 (57) | 10.6 (38) | 11.1 (40) |
| ENCOURAGE | 23.4 (76) | 20.1 (74) | 19.9 (75) |
| MISLEADING | 19.0 (61) | 20.2 (69) | 20.8 (75) |
| HEURISTIC | 19.4 (65) | 12.7 (48) | 12.1 (45) |

* **PRESSURE is the reference strategy**: the flattest in all three metrics, inside ±11 pp on every type, and
  −0.2 pp on average after the difficulty correction — it neither helps nor hurts anywhere, i.e. it has no
  thinking-type preference.
* **The other four each have types they are comparatively good at and types to avoid** (difficulty-corrected
  relative values, absolute level in brackets):
  * CRITICAL: L3-E +13.8 (−3.1·lvl +5.4), L3-F +10.1 (lvl +1.7), L3-K +7.8 (lvl −0.7) … L1-F −23.8 (lvl −32.3),
    L1-E −12.6 (lvl −21.1)
  * ENCOURAGE: L3-E +13.6 (lvl −3.1), L2-E +12.5 (lvl −4.2), L3-R +11.8 (lvl −4.9) … L1-F −60.4 (lvl −77.1, thin),
    L2-F −1.0 (lvl −17.7), L3-F −8.9
  * MISLEADING: L3-E +16.9 (lvl −8.2), L1-K +15.5, L3-K +14.1 … L3-F −24.7 (lvl −49.9), L1-E −10.5, L1-F −51.9 (thin)
  * HEURISTIC: L2-E +14.1, L3-E +10.8, L2-R +6.6 … L3-K −6.5, L2-F −11.2, L1-F −33.8 (thin)
* In absolute terms only **CRITICAL** has cells that are positive against plain (L3-E +5.4, L3-F +1.7, plus
  L3-K −0.7 ≈ 0); every other non-PRESSURE strategy stays negative even on its best types.

## Confounders that are quantified in the outputs

* Saturation: 24 % of all rows are already perfect before re-asking and can only lose, and the share differs
  strongly by strategy — PRESSURE 7 %, CRITICAL 20 %, MISLEADING 23 %, ENCOURAGE 26 %, HEURISTIC 36 %
  (`out/meta.json`). This is the main driver of the raw levels.
* Labels are single-choice and priority-ordered (L3 > L2 > L1), so a task needing both verification and
  formatting is counted once.
* Thin cells (`L1-F` n=12, `L3-F` n=32) can move several pp by dropping a single row; they are hatched and
  should not be quoted alone.

## Folder layout

```
thinking_type_scenarios/
├─ data/rows_v2.csv            2801 rows, 5 strategies × 6 eval families (copy of redesign/all_tasks_v2.csv)
├─ taxonomy_v2.py / classify_v2.py   taxonomy definition + the classifier that produced the labels
├─ tt3_analysis.py             cells, dimension marginals, spread        → out/
├─ make_figs.py                the three figures + two level figures     → figs/
├─ summarize.py                per-strategy reading                      → scenarios.md
├─ out/cells_3dims.csv         (strategy × type): n, n_band, n_families, coverage, fallback, raw, raw_rel,
│                              std, std_rel, std_fam, std_fam_rel, resid_lin(+_rel), gain_rate, nature,
│                              sat_share, plain_mean, thin
├─ out/marginals_3dims.csv     Level / Target / Nature / Overall marginals per metric
├─ out/spread_by_strategy.csv  mean, SD, range, MAD of the 12 type values per metric
├─ out/meta.json               band, bins, reference difficulty mix, saturation shares
├─ figs/fig1_raw.png, fig2_difficulty.png, fig3_balanced.png            (relative profile)
├─ figs/fig1_raw_levels.png, fig2_difficulty_levels.png                 (absolute reference view)
├─ scenarios.md                evenness table, best/worst types, dimension tables per strategy
└─ v1_alternative/             earlier run on the 12 *named* v1 types (archive only)
```

Re-run: `python tt3_analysis.py && python make_figs.py && python summarize.py`
