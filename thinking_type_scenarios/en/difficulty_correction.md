# Difficulty Correction: Method and Diagnostics

*Handling the difficulty confounder in the thinking-type x re-ask-strategy analysis*

This document specifies the difficulty correction used for Figure 2 / Figure 3 (and for the `std` and
`std_fam` columns of `out/cells_3dims.csv`): the estimator, the identification assumptions, diagnostics,
a sensitivity analysis, and limitations. All numbers are reproducible from `tt3_analysis.py`.

---

## 1 The problem: why the effect of "asking again" cannot be compared directly

Let a task have scored `p` (0–100, min-max normalised) in the previous turn. Call the attempt with no
strategy applied "plain", and let `p'` be the score of the same task after applying strategy `s`. The
quantity of interest for each *(strategy, thinking type)* cell is

    Δ = 100 · (p' − p)                       (in pp)

together with the profile of "is this strategy comparatively good or bad at this thinking type?". Taking
the arithmetic mean of Δ per cell (call it `raw`) mixes in three components that have nothing to do with
the strategy:

**(i) Ceiling saturation.** Δ is bounded above by `100 − p` and below by `−p`. When `p = 100`, Δ ≤ 0: a
task that is already perfect can only lose points when asked again. The share of saturated rows differs
wildly across strategies (Table 1, third column): PRESSURE 6.6 %, CRITICAL 20.2 %, MISLEADING 23.2 %,
ENCOURAGE 26.5 %, HEURISTIC 36.1 %. Without correction, these rows impose a systematic penalty on the
"talkative" strategies, regardless of strategy quality.

**(ii) Headroom heterogeneity.** The size of Δ is not uniform in `p`: when `p` is low the model is
already wrong and one more attempt buys the most; when `p` is already high there is almost no room left,
and a rewrite may even lose points. The expectation of Δ inside a cell is therefore a function `μ_s(p)`
of `p`, not a constant.

**(iii) Composition confounding.** A thinking type is a content label and is strongly correlated with
task difficulty: the mathematical reasoning types (L1-R, L2-R) have clearly lower baselines `p`, while
the format types (L1-F, L2-F) sit very high (mostly around 0.92 / 0.72). Moreover, the row sets of the
same type differ somewhat across strategies (differences in `mode` and in family availability). A
cross-cell comparison of "which type does well" is therefore really a comparison of "which cells happen
to contain the hard problems".

Together these three components make the `raw` column systematically overstate the differences between
strategy profiles and create an ordering between strategies that does not exist (example: HEURISTIC's raw
mean is −24.3 pp, of which about 36 % of rows come from saturated tasks that can only lose).

## 2 Notation

| Symbol | Meaning |
|---|---|
| `s ∈ {PRESSURE, CRITICAL, ENCOURAGE, MISLEADING, HEURISTIC}` | strategy |
| `t ∈ T`, `|T| = 12` | thinking type = operation level L1/L2/L3 x target K/R/E/F |
| `p_i` | baseline (plain / no-strategy) score of row i, 0–100 |
| `Δ_i` | score change of row i, in pp |
| `b(p) ∈ {0,1,2,3}` | baseline binning function, see §3.2 |
| `w_b` | reference difficulty mix, `Σ_b w_b = 1` |
| `m_{s,t,b}` | mean Δ of the rows of cell (s,t) that fall in bin b |
| `cov_{s,t} = Σ_b w_b · 1[bin b non-empty in (s,t)]` | coverage of the reference mix by that cell |

Sample: 2801 *(strategy, task)* observations; 1954 rows inside the headroom band. Cell row counts:
min / median / max = 2 / 36.5 / 204.

## 3 The correction

### 3.1 Step 1: headroom band truncation

Keep only rows with **5 ≤ p_i ≤ 95**. Rationale: rows with `p = 100` have no upward room at all, and rows
with `p ≈ 0` are almost always wrong with tiny variance and a bound hugging 0; in both cases the
expectation of Δ is decoupled from strategy quality. The in-band share therefore becomes a sample-size
constraint: PRESSURE 84.1 %, CRITICAL 73.7 %, MISLEADING 70.7 %, ENCOURAGE 67.9 %, HEURISTIC 59.1 %.

**This is the main cost of the method**: HEURISTIC loses 40.9 % of its rows and has the smallest in-band
sample; and truncating saturated rows means the method no longer answers "what happens when you re-ask a
task that is already solved", only "on tasks that still have room, what is the average effect of asking
again".

### 3.2 Step 2: difficulty binning and the reference mix

Inside the band, bin in 20 pp steps:

    b(p) = 0 : [ 5, 25)      b(p) = 2 : [45, 65)
    b(p) = 1 : [25, 45)      b(p) = 3 : [65, 95]

The reference mix `w` is the marginal distribution of all in-band rows over the four bins (pooled across
strategies and types):

| Bin | Baseline p | Weight w_b |
|---|---|---|
| 0 | [5, 25) | 0.093 |
| 1 | [25, 45) | 0.068 |
| 2 | [45, 65) | 0.108 |
| 3 | [65, 95) | 0.731 |

That is, most in-band rows fall in the 65–95 stretch of "only a little room left", which matches the
experimental situation of "re-asking a model that already answers reasonably well".

### 3.3 Step 3: direct standardisation (post-stratification)

A cell value is defined by re-weighting the per-bin mean Δ of that cell to the common reference mix:

    Δ̂_{s,t} = Σ_b  w_b · m_{s,t,b}  /  Σ_{b ∈ B(s,t)} w_b        (= the std column)

where `B(s,t)` is the set of non-empty bins in the cell and the denominator `cov_{s,t}` is the coverage.
Missing bins are dropped rather than imputed as 0, so the denominator shrinks with coverage; in this
dataset `cov` ranges from 0.731 to 1.000 and no cell triggers the fallback rule (§3.6). Statistically
this is exactly post-stratification: each cell's difficulty composition is replaced by the same
counterfactual composition.

Note that this is a **choice of reference frame**, not a "truth": it defines "a good effect" as "an effect
under this reference difficulty composition". Levels under different mixes are therefore not comparable;
only comparisons within one mix are (see §6 for the sensitivity analysis).

### 3.4 Step 4: evaluation-family balancing

The in-band sample is unevenly distributed over evaluation families (MT-Bench / MATH-500 / FLASK-Chat /
FLASK-Llama / FLASK-Qwen / WildBench), and family is coupled with task genre and scoring mode. Hence one
more re-average with "one family, one vote":

    Δ̂^{fam}_{s,t} = (1 / |F(s,t)|) Σ_{f ∈ F(s,t)} Δ̂_{s,t|f}        (= the std_fam column)

where `Δ̂_{s,t|f}` applies the formula of §3.3 to the subsample of family f alone. `|F(s,t)|` is 2–6. This
step does not change a cell's difficulty composition (already fixed by §3.3); it only changes which family
dominates the cell, preventing a type's conclusion from actually coming from a single benchmark.

### 3.5 Step 5: baseline centring (relative profile)

The main figures (Figures 1–3) plot the **relative profile**: each strategy minus its own equally weighted
mean over the 12 types (one type, one vote)

    Δ̃_{s,t} = Δ̂_{s,t} − (1/|T|) Σ_{t'} Δ̂_{s,t'}                   (= the *_rel columns)

so that 0 means "for this strategy, this type is at its own average": positive = comparatively good,
negative = comparatively bad. The reference views (Figures 1L / 2L) plot the uncentred absolute level
`Δ̂`.

### 3.6 Fallback rule and thin cells

If `cov_{s,t} < 0.5` (i.e. the cell covers less than half of the reference-mix mass), the weighting is
abandoned and replaced by the cell's in-band arithmetic mean, flagged `fallback = True` in
`out/cells_3dims.csv`. No cell in this dataset triggers it. Cells with `n < 15` are flagged `thin = True`
(most cells of L1-F, with n as low as 2); the figure marks them with a lighter bar and a red `n`, and
their values are reference only — they enter no conclusive ranking.

### 3.7 An alternative scale (not used for the main figures)

`resid_lin` is an alternative: run an OLS regression of Δ on `p` separately per strategy and take the mean
residual per cell. It removes each strategy's own "Δ–p trend" and therefore also removes the strategy's
own level, which erases level differences between strategies (both PRESSURE's and HEURISTIC's means get
pulled towards 0). It is kept in the CSV as a robustness reference only.

## 4 Identification assumptions and scope of interpretation

1. **Within-stratum exchangeability**: inside a difficulty bin, the rows of the various cells have no
   residual systematic difference in strategy effect. With only 4 bins, a residual slope of `μ_s(p)`
   within a bin is possible (`p` moving from 65 to 95 is not a small change). This is the assumption most
   easily violated and the direct reason why levels move violently with the mix in §6.
2. **Single confounder**: the method adjusts for one discrete confounder (baseline score / headroom).
   Task genre, scoring mode (human judgement vs exact match) and language are not in the adjustment set
   and are only partly absorbed by family balancing (§3.4).
3. **No measurement error**: `p` and `p'` are treated as exact; in reality the scoring is noisy, and
   noise on a bounded scale shrinks towards the centre.
4. **Descriptive, not causal**: the output is "an average difference under a given reference difficulty
   composition" — a descriptive adjustment, with no causal claim. There is no randomisation across
   strategies; the mapping between strategies and task sets is determined by data collection.
5. **Truncation changes the estimand**: conclusions apply to tasks with 5 ≤ p ≤ 95, excluding both solved
   and near-zero tasks.

## 5 Diagnostics

**(a) Negative control: PRESSURE.** PRESSURE is designed to be an almost semantics-free repetition and
should be near 0 everywhere. The raw scale gives a mean of +3.1 pp; after correction it is −0.2 pp with
SD 5.7 and range 19 (Table 3). The correction flattens its spurious positive gain (mainly produced by the
intra-band low-score rows cancelling against the saturated rows), as expected.

**(b) Net effect of the correction (12 cells per strategy, one type one vote).** See Table 3: after
correction the SDs of the four non-PRESSURE strategies narrow markedly (CRITICAL 15.8 → 10.6, HEURISTIC
19.4 → 12.7), whereas ENCOURAGE / MISLEADING are essentially unchanged (23.4 → 20.1, 19.0 → 20.2) — their
profiles are driven by content differences rather than difficulty composition. This difference is itself
informative: **difficulty composition explains only two of the four**; the variation of the other two is a
genuine content interaction (though still not FDR-significant, as noted earlier).

**(c) Coverage.** The median `cov` is 1.000 and the minimum 0.731, so the four reference bins are
essentially always covered in every cell; the fallback rule is never used.

## 6 Sensitivity analysis

Four replacements of the reference frame (12 cells per strategy, one type one vote; format: mean / SD /
range, in pp):

| Scale | PRESSURE | CRITICAL | ENCOURAGE | MISLEADING | HEURISTIC |
|---|---|---|---|---|---|
| RAW (no correction) | +3.1 / 6.2 / 26 | −12.5 / 15.8 / 57 | −23.1 / 23.4 / 76 | −27.6 / 19.0 / 61 | −24.3 / 19.4 / 65 |
| A. band 5–95, reference mix w (current) | −0.2 / 5.7 / 19 | −8.5 / 10.6 / 38 | −16.7 / 20.1 / 74 | −25.1 / 20.2 / 69 | −18.3 / 12.7 / 48 |
| B. band 5–95, four bins equal weight | +11.0 / 12.7 / 49 | +4.1 / 15.5 / 52 | −7.6 / 24.6 / 91 | −13.9 / 25.9 / 86 | −9.0 / 17.3 / 66 |
| C. band 5–65, own mix | +20.9 / 24.4 / 90 | +16.3 / 12.9 / 45 | +6.1 / 12.1 / 39 | +4.0 / 11.4 / 37 | +0.9 / 13.6 / 52 |
| D. band 25–95, own mix | −3.3 / 5.0 / 15 | −11.6 / 9.9 / 34 | −18.6 / 19.1 / 72 | −27.8 / 19.0 / 65 | −19.8 / 12.0 / 44 |

Three readings:

1. **Levels depend strongly on the reference frame.** Frames B and C push the weight towards the low
   score range (5–65), where every strategy becomes a net gain and PRESSURE jumps from −0.2 to +11.0 and
   +20.9. The meaning is clear: on hard problems, asking again generally helps; on near-perfect problems
   it generally hurts. Any statement "this strategy is worth X pp" must therefore come with its
   difficulty composition.
2. **What is robust in the ordering.** When the frame leans towards the high range (A, D), the order of
   the five is stable: PRESSURE >> CRITICAL > HEURISTIC ≈ ENCOURAGE > MISLEADING (by mean), and
   PRESSURE's SD is always the smallest (5.0–5.7).
3. **What is not robust**: under frame C, PRESSURE's SD (24.4) is the *largest*, i.e. the claim
   "PRESSURE is the flattest" holds only in high-baseline frames. This is the single most important
   self-limitation of the method.

## 7 Limitations

- **Cell granularity ceiling**: 12 types, 12 cells per strategy, median 36.5 rows per cell, thinnest cell
  n = 2. To resolve differences of the order of 5 pp at the present noise level, each cell needs about
  100 rows (a result from the earlier analysis); the current data does not reach that.
- **Strategies are near-substitutes**: pairwise Δ correlations of 0.66–0.93; correction cannot create
  "specialisation" where none exists.
- **Bin granularity**: 4 bins are a compromise between sample size and residual slope; the residual
  slope of `μ_s(p)` inside a bin contaminates levels.
- **Family balancing is not cluster-robust inference**: §3.4 only rebalances weights and does not estimate
  clustered variance by family; no confidence intervals are reported. Intervals would require bootstrapping
  with family as the cluster unit (not implemented here).
- **Cost of truncation**: HEURISTIC drops 40.9 % of its rows, so its in-band conclusions are the least
  representative of that strategy's domain of applicability.

## 8 Reproducibility

| File | Role |
|---|---|
| `tt3_analysis.py` | main computation: `prepare()` → `cells()` → writes `out/cells_3dims.csv`, `out/marginals_3dims.csv`, `out/spread_by_strategy.csv`, `out/meta.json` |
| `data/rows_v2.csv` | row-level input: `strategy, thinking_type, plain_minmax, reask_minmax, delta, dataset_id`, etc. |
| `taxonomy_v2.py` | definitions and names of the 12 thinking types |
| `make_figs_tt7.py` | figure rendering: `build("std_rel", ...)` is Figure 2 |
| `_sens_mix.py` | the sensitivity analysis of §6 |
| `_doc_numbers.py` | extraction script for all numbers quoted here |

Run:

    python tt3_analysis.py        # produce std / std_fam and the diagnostic tables
    python make_figs_tt7.py       # render the four figures into figs_tt7/
    python _sens_mix.py           # reproduce the table of §6

Key constants (top of `tt3_analysis.py`): `BAND = (5.0, 95.0)`, `EDGES = [5, 25, 45, 65, 95]`,
`MIN_COVER = 0.5`, `THIN = 15`.

## Appendix A Pseudocode

    for s in strategies:
        D_s   = rows where strategy == s
        B_s   = [r in D_s if 5 <= r.p <= 95]
        for t in types:
            gb = [r in B_s if r.type == t]
            if len(gb) == 0: continue
            for b in bins(0..3):
                m[b] = mean(dpp of rows in gb with bin == b)
            w        = [w[b] for b in bins if m[b] is not None]
            cov      = sum(w)
            std[s,t] = sum(w[b] * m[b] for b in bins if m[b] is not None) / cov   if cov >= 0.5
                     else mean(dpp of gb)
            per_fam  = [ same standardization inside each family f of gb ]
            std_fam[s,t] = mean(per_fam)
        for t in types:                      # baseline-relative profile
            std_rel[s,t] = std[s,t] - mean_t'(std[s,t'])

## Appendix B Key numbers

**Table 1 Sample and saturation per strategy**

| Strategy | rows | in-band share | saturated share (p ≥ 99.5) |
|---|---|---|---|
| PRESSURE | 408 | 84.1 % | 6.6 % |
| CRITICAL | 524 | 73.7 % | 20.2 % |
| ENCOURAGE | 589 | 67.9 % | 26.5 % |
| MISLEADING | 590 | 70.7 % | 23.2 % |
| HEURISTIC | 690 | 59.1 % | 36.1 % |
| all | 2801 | 69.8 % | 24.1 % |

**Table 2 PRESSURE cell by cell: raw vs std (the correction at work)**

| type | n | baseline p | raw | std | coverage |
|---|---|---|---|---|---|
| L1-K | 45 | 66.2 | +3.8 | +6.6 | 1.00 |
| L1-R | 70 | 68.8 | +0.6 | −3.0 | 1.00 |
| L1-E | 25 | 71.4 | +4.6 | −1.2 | 0.80 |
| L1-F | 2 | 93.8 | +3.1 | +2.1 | 0.73 |
| L2-K | 48 | 76.8 | +1.8 | +0.5 | 0.80 |
| L2-R | 82 | 50.4 | −1.4 | −10.3 | 1.00 |
| L2-E | 31 | 65.3 | +8.4 | +1.0 | 0.90 |
| L2-F | 16 | 68.5 | −10.0 | −11.0 | 0.90 |
| L3-K | 22 | 52.8 | +7.9 | +1.9 | 1.00 |
| L3-R | 40 | 66.4 | −0.0 | +0.5 | 1.00 |
| L3-E | 22 | 68.2 | +3.1 | +2.3 | 1.00 |
| L3-F | 5 | 67.5 | +15.8 | +8.0 | 0.80 |

(L2-R, L3-K and L2-E illustrate the point best: raw −1.4 / +7.9 / +8.4 against corrected −10.3 / +1.9 /
+1.0. Their baselines are 50.4 / 52.8 / 65.3, i.e. low-baseline cells, and `raw` mixes them with
high-baseline cells, producing an upward shift.)

**Table 3 Before and after correction (12 cells, one type one vote)** — see rows 1–2 (raw / A) of §6.

**Table 4 The headroom band (5–95) and the reference mix**

| Bin | Interval | w_b | Meaning |
|---|---|---|---|
| 0 | [5, 25) | 0.093 | almost all wrong |
| 1 | [25, 45) | 0.068 | mostly wrong |
| 2 | [45, 65) | 0.108 | half right |
| 3 | [65, 95) | 0.731 | nearly solved, a little room left |
