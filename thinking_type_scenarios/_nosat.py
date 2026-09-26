# -*- coding: utf-8 -*-
"""难度相关的几种「保水平」校正：剔除无余量行后，PRESSURE 是否仍贴 0 且平。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import TYPE_IDS                                # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
d = pd.read_csv(os.path.join(HERE, "data", "rows_v2.csv"))
d["dpp"] = 100 * d.delta
d["p"] = 100 * d.plain_minmax

VAR = {
    "raw 全部行": d,
    "去掉饱和行 p<99.5": d[d.p < 99.5],
    "去掉饱和与地板 0<p<99.5": d[(d.p < 99.5) & (d.p > 0)],
    "只留有余量 p<=95": d[d.p <= 95],
    "只留中间带 5<=p<=95": d[(d.p >= 5) & (d.p <= 95)],
}
print("%-26s %s" % ("口径", "   ".join("%-24s" % s for s in STRATS)))
for nm, sub in VAR.items():
    parts = []
    for s in STRATS:
        C = sub[sub.strategy == s].groupby("thinking_type").dpp.mean().reindex(TYPE_IDS)
        v = C.dropna().values
        parts.append("%6.1f /%6.1f /%6.1f" % (v.mean(), v.std(ddof=1), v.max() - v.min()))
    sd = {s: sub[sub.strategy == s].groupby("thinking_type").dpp.mean().reindex(TYPE_IDS).dropna().std(ddof=1)
          for s in STRATS}
    ratio = sd["PRESSURE"] / np.mean([sd[k] for k in STRATS if k != "PRESSURE"])
    print("%-26s %s   比例=%.2f" % (nm, "   ".join(parts), ratio))
print("\n（每策略三个数 = 12 格均值 / SD / 极差；比例 = PRESSURE 的 SD ÷ 其他四家平均 SD）")

print("\n去掉饱和行后的明细：")
sub = VAR["去掉饱和行 p<99.5"]
C = sub.pivot_table(index="thinking_type", columns="strategy", values="dpp", aggfunc="mean").reindex(TYPE_IDS)[STRATS]
N = sub.pivot_table(index="thinking_type", columns="strategy", values="dpp", aggfunc="size").reindex(TYPE_IDS)[STRATS]
print(C.round(1).to_string())
print("\n(行数)")
print(N.fillna(0).astype(int).to_string())
print("\n全表饱和行占比：%.1f%%" % (100 * (d.p >= 99.5).mean()))
print("各策略饱和行占比：" +
      "  ".join("%s %.0f%%" % (s, 100 * (d[d.strategy == s].p >= 99.5).mean()) for s in STRATS))
