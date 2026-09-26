# Thinking-type × re-ask strategy — scenario analysis (fresh folder)

Clean re-start of the analysis on the **original 12 thinking types** of `signal_experts/classifier.py`
(not the later v4 "thinking actions"), grouped by the classifier's own **three dimensions
(priority layers)**: Metacognitive layer > Structural layer > Execution layer.

Question answered: *which thinking types does each re-ask strategy actually help or hurt* —
i.e. in which situation each strategy is worth using.

## Folder layout

```
thinking_type_scenarios/
├─ data/rows_with_thinking_type.csv     input: 2801 rows (5 strategies × 6 eval families), verbatim copy
├─ tt_scenario_analysis.py              computes the three estimates  → out/
├─ make_figs.py                         draws the three figures        → figs/
├─ summarize.py                         per-strategy reading           → scenarios.md
├─ out/tt_all_versions.csv              one row per strategy × type, all three estimates + n, families, spread
├─ out/difficulty_trend.csv             per-strategy OLS of Δ on plain (used by version 2)
├─ out/tt_raw.csv / tt_difficulty_adjusted.csv / tt_balanced.csv
├─ figs/fig1_raw.png / fig2_difficulty_adjusted.png / fig3_balanced.png
└─ scenarios.md                         layer means + top-3 helps/hurts per strategy
```

Re-run: `python tt_scenario_analysis.py && python make_figs.py && python summarize.py`

## The three versions

`Δ = re-ask score − plain score`, in percentage points (pp), min-max scored, 3 instruction models
(Chat / Llama / Qwen), 6 evaluation families (chat_math500, chat_wild_bench, chat_flask,
llama_flask, qwen_flask, mt_bench).

1. **Figure 1 — raw.** Mean Δ of each strategy × thinking type. No control: a type that happens to
   contain easy or hard tasks carries that difficulty difference with it.
2. **Figure 2 — difficulty-adjusted.** Inside each strategy, fit `Δ_pp = b0 + b1 · plain_pp`
   (per-strategy OLS, R² = 0.45–0.55) and take the mean residual per cell. Because the residual mean
   equals `cell mean Δ − expected Δ at the cell's own difficulty`, a value of 0 means
   *"as expected for this strategy at the difficulty of these tasks"*, not *"same as plain"*.
3. **Figure 3 — difficulty-adjusted + size-balanced.** The Figure-2 residuals are re-averaged with
   **equal weight per evaluation family** (every family counts once, no matter how many rows it
   contributed). This removes the dependence on how many samples a thinking type happens to have,
   and on which family it is plentiful in.

## How to read the figures

* one subplot per strategy; rows = the 12 thinking types, grouped and colour-coded by dimension;
* bar length = strength: right = gain from re-asking, left = reduction; symmetric axis per figure;
* `n=` behind the bar = number of rows; **hatched, pale bars have n < 10 and are indicative only**;
* the boxed `μ` per dimension is that layer's mean for the strategy;
* robustness: `lodo_range` in `out/tt_all_versions.csv` is the spread of the cell value when each
  family is dropped in turn. **Cells with `lodo_range ≳ 10 pp are family-driven and should not be
  read individually** (e.g. `Execution-limited` under ENCOURAGE flips from −60.5 raw to +13.1
  balanced with a 16.4 pp spread — that is noise, not a scenario).

## Caveats worth keeping in mind

* The 12-type taxonomy is a **single-label, priority-ordered** classifier (Metacognitive > Structural
  > Execution), so a task that needs both verification and format-keeping is counted once.
* Cells are thin in the Metacognitive layer (`Strict verification` n = 1–2, `Reviewable repair` n = 4–6,
  `Trajectory sensitive` n = 2–6). Their large values are shown but should not be quoted as findings.
* Thinking types correlate with families and with difficulty, so Figure 2/3 partly re-allocate the
  confound rather than removing it; that is exactly why Figure 3 equalises families. What survives
  all three versions is reported in `scenarios.md`.
* 24 % of rows have `plain_minmax = 100 %` (92 % inside chat_math500) — a saturated row can only lose,
  so any type dominated by such rows looks bad in Figure 1 by construction.
