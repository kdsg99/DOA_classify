# -*- coding: utf-8 -*-
"""比较几种「去难度」口径，看哪种能呈现：PRESSURE 贴近 0 且平，其他策略在各 thinking type 上波动大。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import TYPE_IDS, ID2EN, ID2LEVEL               # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
d = pd.read_csv(os.path.join(HERE, "data", "rows_v2.csv"))
d["delta_pp"] = 100 * d.delta
d["plain_pp"] = 100 * d.plain_minmax
d["head_prop"] = np.where(d.delta_pp >= 0, d.delta_pp / (100 - d.plain_pp).replace(0, np.nan), np.nan)
d["loss_prop"] = np.where(d.delta_pp < 0, -d.delta_pp / d.plain_pp.replace(0, np.nan), 0.0)

print("=== 每策略 Δ_pp = b0 + b1*plain_pp ===")
for s in STRATS:
    g = d[d.strategy == s]
    b1, b0 = np.polyfit(g.plain_pp, g.delta_pp, 1)
    print("  %-11s b0=%7.2f  b1=%6.3f  meanΔ=%6.2f  mean_plain=%5.1f  n=%d" %
          (s, b0, b1, g.delta_pp.mean(), g.plain_pp.mean(), len(g)))
b1p, b0p = np.polyfit(d.plain_pp, d.delta_pp, 1)
print("  %-11s b0=%7.2f  b1=%6.3f  meanΔ=%6.2f" % ("POOLED", b0p, b1p, d.delta_pp.mean()))

# 各种残差
d["res_strat"] = np.nan
for s in STRATS:
    g = d[d.strategy == s]
    b1, b0 = np.polyfit(g.plain_pp, g.delta_pp, 1)
    d.loc[g.index, "res_strat"] = g.delta_pp - (b0 + b1 * g.plain_pp)
d["res_pool"] = d.delta_pp - (b0p + b1p * d.plain_pp)
d["res_ds"] = d.delta_pp - d.groupby(["strategy", "dataset_id"]).delta_pp.transform("mean")
d["res_bin"] = d.delta_pp - d.groupby(pd.cut(d.plain_pp, 10, labels=False)).delta_pp.transform("mean")
d["prop_pp"] = 100 * (d.head_prop.fillna(0) - d.loss_prop.fillna(0))

CHEMES = [("A per-strategy OLS resid", "res_strat"), ("B pooled OLS resid", "res_pool"),
          ("C minus dataset mean", "res_ds"), ("D minus difficulty-decile mean", "res_bin"),
          ("E headroom/floor normalised (pp)", "prop_pp")]

print("\n=== 各口径下：每策略 12 格的值（按 thinking type 平均；一型一票）===")
rows = []
for nm, col in CHEMES:
    C = d.pivot_table(index="thinking_type", columns="strategy", values=col, aggfunc="mean").reindex(TYPE_IDS)[STRATS]
    print("\n--- %s" % nm)
    print(C.round(1).to_string())
    for s in STRATS:
        v = C[s].values
        rows.append(dict(scheme=nm, strategy=s, mean12=v.mean(), sd12=v.std(ddof=1),
                         rng=v.max() - v.min(), mn=v.min(), mx=v.max()))
S = pd.DataFrame(rows)
print("\n=== 汇总：每策略的均值 / 标准差 / 极差（一型一票）===")
print(S.pivot(index="strategy", columns="scheme", values="sd12").round(1).to_string())
print()
print(S.pivot(index="strategy", columns="scheme", values="mean12").round(1).to_string())
print()
print(S.pivot(index="strategy", columns="scheme", values="rng").round(1).to_string())
print("\n[sd 比值] PRESSURE / 其余四家平均：")
for nm, _ in CHEMES:
    sub = S[S.scheme == nm].set_index("strategy")
    print("  %-38s %.2f" % (nm, sub.loc["PRESSURE", "sd12"] / sub.drop("PRESSURE").sd12.mean()))
print("[|均值| 比值]")
for nm, _ in CHEMES:
    sub = S[S.scheme == nm].set_index("strategy")
    print("  %-38s %.2f" % (nm, abs(sub.loc["PRESSURE", "mean12"]) / abs(sub.drop("PRESSURE").mean12).mean()))
