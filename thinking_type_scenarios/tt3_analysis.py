# -*- coding: utf-8 -*-
"""Three-dimension thinking-type x strategy analysis.

Taxonomy (taxonomy_v2.py / classify_v2.py):
    thinking type = operation level (L1 Execution / L2 Structure / L3 Metacognition)
                  x target           (K Knowledge / R Reasoning / E Expression / F Format)
    third dimension (nature of gain: Defensive / Offensive) is MEASURED per cell as the
    share of rows that actually improved (gain_rate, threshold 50%).

Metrics (all in pp; Delta = 100 * (reask_minmax - plain_minmax))
    raw      : mean Delta over all rows of the cell
    std      : difficulty-standardised -- rows are restricted to the band where the model has
               headroom (5 <= original score <= 95) and re-weighted so that every cell is
               compared at the SAME mix of original scores (the objective difficulty measure).
               A cell that happens to be full of already-perfect tasks (original = 100) can
               therefore no longer be dragged down mechanically.
    std_fam  : std, then averaged with equal weight per evaluation family (one family = one
               vote) so the value does not depend on how many rows a type has.
    resid_lin: reference only -- per-strategy OLS residual of Delta on the original score
               (this removes each strategy's own level, which is why it is not used for the
               main figures: it destroys the strategy-vs-strategy level differences).

Dimension marginals are unweighted means over the thinking types of a dimension value
(one type = one vote).
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import (TYPE_IDS, ID2EN, ID2ZH, ID2LEVEL,      # noqa: E402
                         ID2TARGET, LEVELS, TARGETS, LEVEL_EN, TARGET_EN)

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
BAND = (5.0, 95.0)                       # headroom band on the ORIGINAL (plain) score
EDGES = [5, 25, 45, 65, 95]              # bins of 20 pp inside the band
MIN_COVER = 0.5                          # below this the cell falls back to its in-band mean
THIN = 15


def prepare():
    d = pd.read_csv(os.path.join(HERE, "data", "rows_v2.csv"))
    d["dpp"] = 100 * d.delta
    d["p"] = 100 * d.plain_minmax
    d["fam"] = d.dataset_id
    d = d[d.thinking_type.isin(TYPE_IDS)].copy()
    band = d[(d.p >= BAND[0]) & (d.p <= BAND[1])].copy()
    band["bin"] = pd.cut(band.p, EDGES, labels=False, include_lowest=True)
    W = band.groupby("bin").size() / len(band)                       # reference difficulty mix
    d["bin"] = pd.cut(d.p, EDGES, labels=False, include_lowest=True)
    return d, band, W


def weighted_mean(g, W):
    """reference-score-weighted mean of dpp inside one group; returns (value, coverage, n)."""
    if len(g) == 0:
        return np.nan, 0.0, 0
    mb = g.groupby("bin").dpp.mean()
    w = W.reindex(mb.index).fillna(0.0)
    cov = float(w.sum())
    if cov <= 0:
        return np.nan, 0.0, len(g)
    return float((mb * w).sum() / cov), cov, len(g)


def cells(d, band, W):
    recs = []
    for s in STRATS:
        sub, subband = d[d.strategy == s], band[band.strategy == s]
        b1, b0 = np.polyfit(sub.p.values, sub.dpp.values, 1)
        sub_res = sub.dpp.values - (b0 + b1 * sub.p.values)
        for t in TYPE_IDS:
            g = sub[sub.thinking_type == t]
            gb = subband[subband.thinking_type == t]
            val, cov, n = weighted_mean(gb, W)
            if cov < MIN_COVER:                     # thin cells: fall back to the in-band mean
                val = float(gb.dpp.mean()) if len(gb) else np.nan
            per_fam = []
            for _, gd in gb.groupby("fam"):
                v, c, _ = weighted_mean(gd, W)
                if c > 0:
                    per_fam.append(v)
            recs.append(dict(
                strategy=s, thinking_type=t, level=ID2LEVEL[t], target=ID2TARGET[t],
                type_en=ID2EN[t], type_zh=ID2ZH[t],
                n=len(g), n_band=len(gb), n_families=int(gb.fam.nunique()),
                coverage=cov, fallback=bool(cov < MIN_COVER),
                raw=float(g.dpp.mean()) if len(g) else np.nan,
                std=val,
                std_fam=float(np.mean(per_fam)) if per_fam else np.nan,
                resid_lin=float(sub_res[sub.thinking_type == t].mean()) if len(g) else np.nan,
                gain_rate=float((g.delta > 0).mean()) if len(g) else np.nan,
                sat_share=float((g.p >= 99.5).mean()) if len(g) else np.nan,
                plain_mean=float(g.p.mean()) if len(g) else np.nan,
                thin=len(g) < THIN))
    R = pd.DataFrame(recs)
    R["nature"] = np.where(R.gain_rate >= 0.5, "Offensive", "Defensive")
    # Baseline-relative profile: each strategy centred on its own equal-type-weight mean, so a
    # positive value means "better than what this strategy usually does on a task of the same
    # thinking type at the same difficulty".  PRESSURE, whose effect is uniform, stays flat here.
    for ver in ["raw", "std", "std_fam", "resid_lin"]:
        R[ver + "_rel"] = R[ver] - R.groupby("strategy")[ver].transform("mean")
        R[ver + "_mad"] = R.groupby("strategy")[ver + "_rel"].transform(lambda s: s.abs().mean())
    return R


def marginals(R):
    rows = []
    for s in STRATS:
        g = R[R.strategy == s]
        for ver in ["raw", "std", "std_fam", "raw_rel", "std_rel", "std_fam_rel", "resid_lin"]:
            # raw/std/std_fam* are the "level" metrics; the *_rel columns are the centred profile.
            for dim, values, key in [("Level", LEVELS, "level"), ("Target", TARGETS, "target"),
                                     ("Nature", ["Defensive", "Offensive"], "nature")]:
                for v in values:
                    sub = g[g[key] == v].dropna(subset=[ver])
                    rows.append(dict(strategy=s, version=ver, dimension=dim, value=v,
                                     n_types=len(sub), n_rows=int(sub.n.sum()),
                                     mean=float(sub[ver].mean()) if len(sub) else np.nan,
                                     gain_rate=float(sub.gain_rate.mean()) if len(sub) else np.nan))
            sub = g.dropna(subset=[ver])
            rows.append(dict(strategy=s, version=ver, dimension="Overall", value="all",
                             n_types=len(sub), n_rows=int(sub.n.sum()),
                             mean=float(sub[ver].mean()) if len(sub) else np.nan,
                             gain_rate=float(sub.gain_rate.mean()) if len(sub) else np.nan))
    return pd.DataFrame(rows)


def spread(R):
    rows = []
    for s in STRATS:
        g = R[R.strategy == s]
        for ver in ["raw", "std", "std_fam", "raw_rel", "std_rel", "std_fam_rel", "resid_lin"]:
            v = g[ver].dropna().values
            rows.append(dict(strategy=s, version=ver, mean=float(v.mean()), sd=float(v.std(ddof=1)),
                             rng=float(v.max() - v.min()), mn=float(v.min()), mx=float(v.max()),
                             n_types=len(v), mad=float(np.abs(v - v.mean()).mean())))
    return pd.DataFrame(rows)


def main():
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    d, band, W = prepare()
    R = cells(d, band, W)
    M, S = marginals(R), spread(R)
    R.to_csv(os.path.join(HERE, "out", "cells_3dims.csv"), index=False)
    M.to_csv(os.path.join(HERE, "out", "marginals_3dims.csv"), index=False)
    S.to_csv(os.path.join(HERE, "out", "spread_by_strategy.csv"), index=False)
    meta = dict(n_rows=int(len(d)), n_rows_band=int(len(band)), band=list(BAND), edges=EDGES,
                reference_mix={str(int(k)): round(float(v), 3) for k, v in W.items()},
                sat_share_total=float((d.p >= 99.5).mean()),
                sat_share_by_strategy={s: float((d[d.strategy == s].p >= 99.5).mean()) for s in STRATS},
                in_band_share_by_strategy={s: float(len(band[band.strategy == s]) / len(d[d.strategy == s]))
                                           for s in STRATS})
    json.dump(meta, open(os.path.join(HERE, "out", "meta.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("参考难度分布（按 original 得分分箱）：", meta["reference_mix"])
    print("饱和行占比 全体 %.1f%%，分策略：" % (100 * meta["sat_share_total"]),
          {k: "%.0f%%" % (100 * v) for k, v in meta["sat_share_by_strategy"].items()})
    print("\n%-14s %s" % ("口径", "   ".join("%-26s" % s for s in STRATS)))
    for ver in ["raw", "std", "std_fam", "raw_rel", "std_rel", "std_fam_rel", "resid_lin"]:
        sub = S[S.version == ver].set_index("strategy")
        rr = sub.loc["PRESSURE", "sd"] / sub.drop("PRESSURE").sd.mean()
        print("%-14s %s   PRESSURE/其他SD=%.2f" %
              (ver, "   ".join("%6.1f /%6.1f /%6.1f" % (sub.loc[s, "mean"], sub.loc[s, "sd"], sub.loc[s, "rng"])
                               for s in STRATS), rr))
    print("\n（每策略 = 12 格均值 / SD / 极差，一型一票；_rel = 去掉该策略自身平均后的相对画像）")

    for ver in ["raw", "std", "std_fam", "std_rel", "std_fam_rel"]:
        print("\n=== %s — rows = thinking type" % ver.upper())
        P = R.pivot(index="thinking_type", columns="strategy", values=ver).reindex(TYPE_IDS)[STRATS]
        P.index = ["%-5s %-26s" % (i, ID2EN[i]) for i in P.index]
        print(P.round(1).to_string())
    print("\n难度标准化后各格覆盖度/是否退化：")
    print(R.pivot(index="thinking_type", columns="strategy", values="coverage").reindex(TYPE_IDS).round(2).to_string())
    print("\nwritten:", os.path.join(HERE, "out"))


if __name__ == "__main__":
    main()
