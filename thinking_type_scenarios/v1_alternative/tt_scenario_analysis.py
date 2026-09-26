# -*- coding: utf-8 -*-
"""Thinking-type × re-ask strategy scenario analysis.

Outputs three strength estimates per (strategy, thinking_type):
  v1  raw                : mean score change  (Delta in pp)
  v2  difficulty-adjusted: residual of Delta after removing the within-strategy
                           difficulty trend  Delta_pp ~ b0 + b1 * plain_pp
  v3  balanced           : v2 residuals, re-averaged with equal weight per
                           evaluation family (datasets with n>=5), so the value
                           no longer depends on how many rows a thinking type
                           happens to have inside one family.

Input : data/rows_with_thinking_type.csv   (2801 rows from the original DOA run)
Output: out/tt_raw.csv, out/tt_difficulty_adjusted.csv, out/tt_balanced.csv
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]

# 12 thinking types, laid out by the three dimensions used in the classifier
# priority rule: Metacognitive layer > Structural layer > Execution layer.
LAYERS = {
    "Execution": ["Local repair", "Expression expansion", "Execution-limited"],
    "Structural": ["Routine recognition", "Full-reasoning dependent",
                   "Format preserving", "Style preserving"],
    "Metacognitive": ["Reviewable repair", "Strict verification",
                      "Long-context fidelity", "Trajectory sensitive",
                      "Plain-answer fragile"],
}
ORDER = [t for lyr in ["Metacognitive", "Structural", "Execution"] for t in LAYERS[lyr]]
LAYER_OF = {t: lyr for lyr, ts in LAYERS.items() for t in ts}
ABBR = {
    "Local repair": "Local repair",
    "Expression expansion": "Expression expansion",
    "Execution-limited": "Execution-limited",
    "Routine recognition": "Routine recognition",
    "Full-reasoning dependent": "Full-reasoning dependent",
    "Format preserving": "Format preserving",
    "Style preserving": "Style preserving",
    "Reviewable repair": "Reviewable repair",
    "Strict verification": "Strict verification",
    "Long-context fidelity": "Long-context fidelity",
    "Trajectory sensitive": "Trajectory sensitive",
    "Plain-answer fragile": "Plain-answer fragile",
}

MIN_N_DATASET = 1          # every evaluation family with data gets equal weight in v3
THIN = 10                  # cells with fewer rows are flagged as thin evidence


def load():
    df = pd.read_csv(os.path.join(HERE, "data", "rows_with_thinking_type.csv"))
    df["delta_pp"] = 100.0 * df["delta"]
    df["plain_pp"] = 100.0 * df["plain_minmax"]
    df = df[df.thinking_type.isin(ORDER)].copy()
    return df


def strat_lines(df):
    """Per-strategy difficulty trend (used by v2)."""
    rows = []
    for s in STRATS:
        g = df[df.strategy == s]
        b1, b0 = np.polyfit(g.plain_pp.values, g.delta_pp.values, 1)
        pred = b0 + b1 * g.plain_pp.values
        ss = 1 - ((g.delta_pp.values - pred) ** 2).sum() / ((g.delta_pp.values - g.delta_pp.mean()) ** 2).sum()
        rows.append((s, b0, b1, ss, len(g)))
        df.loc[g.index, "resid"] = g.delta_pp.values - pred
    return pd.DataFrame(rows, columns=["strategy", "b0", "b1", "R2", "n"])


def estimate(df, value, strat):
    """1/2/3: raw mean, difficulty residual, family-balanced residual."""
    recs = []
    for t in ORDER:
        g = df[(df.strategy == strat) & (df.thinking_type == t)]
        raw = 100 * g.delta.mean() if len(g) else np.nan
        adj = g.resid.mean() if len(g) else np.nan
        w, vals, lodo = [], [], []
        for ds, gd in g.groupby("dataset_id"):
            if len(gd) >= MIN_N_DATASET:
                vals.append(gd.resid.mean())
        bal = float(np.mean(vals)) if vals else np.nan
        for ds in g.dataset_id.unique():                       # leave-one-family-out spread
            keep = [v for k, v in zip([d for d, gd in g.groupby("dataset_id")
                                       if len(gd) >= MIN_N_DATASET], vals) if k != ds]
            if len(keep) >= 2:
                lodo.append(np.mean(keep))
        recs.append(dict(strategy=strat, thinking_type=t, layer=LAYER_OF[t],
                         n=len(g), n_families=len(vals),
                         raw=raw, difficulty_adjusted=adj, balanced=bal,
                         lodo_range=(max(lodo) - min(lodo)) if len(lodo) >= 2 else np.nan,
                         thin=len(g) < THIN))
    return recs


def main():
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    df = load()
    lines = strat_lines(df)
    print("Per-strategy difficulty trend  Delta_pp = b0 + b1 * plain_pp")
    print(lines.round(3).to_string(index=False))
    lines.to_csv(os.path.join(HERE, "out", "difficulty_trend.csv"), index=False)

    recs = []
    for s in STRATS:
        recs += estimate(df, None, s)
    R = pd.DataFrame(recs)
    R.to_csv(os.path.join(HERE, "out", "tt_all_versions.csv"), index=False)
    for name, col in [("tt_raw", "raw"), ("tt_difficulty_adjusted", "difficulty_adjusted"),
                      ("tt_balanced", "balanced")]:
        R[["strategy", "thinking_type", "layer", "n", "n_families", col, "thin"]] \
            .rename(columns={col: "value"}) \
            .to_csv(os.path.join(HERE, "out", name + ".csv"), index=False)

    for ver, col in [("RAW", "raw"), ("DIFFICULTY-ADJUSTED", "difficulty_adjusted"),
                     ("BALANCED", "balanced")]:
        print("\n=== %s : value (pp) by strategy x thinking type" % ver)
        M = R.pivot(index="thinking_type", columns="strategy", values=col).reindex(ORDER)[STRATS]
        print(M.round(1).to_string())
    print("\nBalanced version vs raw: rank correlation per strategy")
    for s in STRATS:
        g = R[R.strategy == s]
        print("   %-11s rho=%.2f" % (s, g["raw"].corr(g["balanced"], method="spearman")))
    print("\nWritten:", os.path.join(HERE, "out"))


if __name__ == "__main__":
    main()
