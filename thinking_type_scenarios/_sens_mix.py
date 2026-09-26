# -*- coding: utf-8 -*-
"""敏感性：参考混合的选择对结论的影响（写进方法文档第 6 节）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
sys.path.insert(0, H)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import TYPE_IDS                                # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
d = pd.read_csv(os.path.join(H, "data", "rows_v2.csv"))
d["dpp"] = 100 * d.delta
d["p"] = 100 * d.plain_minmax
d = d[d.thinking_type.isin(TYPE_IDS)].copy()


def std_cells(band, W, edges, min_cov=0.5):
    band = band.copy()
    band["bin"] = pd.cut(band.p, edges, labels=False, include_lowest=True)
    out = {}
    for s in STRATS:
        sub = band[band.strategy == s]
        vals = []
        for t in TYPE_IDS:
            g = sub[sub.thinking_type == t]
            mb = g.groupby("bin").dpp.mean()
            w = W.reindex(mb.index).fillna(0.0)
            cov = float(w.sum())
            vals.append(float((mb * w).sum() / cov) if cov > 0 else np.nan)
        out[s] = np.array(vals)
    return out


def report(tag, vals):
    print("%-34s" % tag, "  ".join("%s %6.1f/%5.1f/%4.0f" % (
        s, np.nanmean(vals[s]), np.nanstd(vals[s], ddof=1), np.nanmax(vals[s]) - np.nanmin(vals[s]))
        for s in STRATS))


EDGES = [5, 25, 45, 65, 95]
band = d[(d.p >= 5) & (d.p <= 95)].copy()
band["bin"] = pd.cut(band.p, EDGES, labels=False, include_lowest=True)
W = band.groupby("bin").size() / len(band)
print("reference mix W:", {int(k): round(float(v), 3) for k, v in W.items()})
report("A. band 5-95, reference mix (=current)", std_cells(band, W, EDGES))

Wuni = pd.Series([0.25] * 4, index=[0, 1, 2, 3])
report("B. band 5-95, uniform bin weights", std_cells(band, Wuni, EDGES))

band2 = d[(d.p >= 5) & (d.p <= 65)].copy()
band2["bin"] = pd.cut(band2.p, [5, 25, 45, 65], labels=False, include_lowest=True)
W2 = band2.groupby("bin").size() / len(band2)
print("reference mix W(5-65):", {int(k): round(float(v), 3) for k, v in W2.items()})
report("C. band 5-65, own reference mix", std_cells(band2, W2, [5, 25, 45, 65]))

band3 = d[(d.p >= 25) & (d.p <= 95)].copy()
band3["bin"] = pd.cut(band3.p, [25, 45, 65, 95], labels=False, include_lowest=True)
W3 = band3.groupby("bin").size() / len(band3)
report("D. band 25-95, own reference mix", std_cells(band3, W3, [25, 45, 65, 95]))

print("\n(格式：mean / SD / range，每策略 12 格，一型一票)")
print("\n原始（无校正）对照：")
rawv = {s: d[d.strategy == s].groupby("thinking_type").dpp.mean().reindex(TYPE_IDS).values for s in STRATS}
report("RAW", rawv)
