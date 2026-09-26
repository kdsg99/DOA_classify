# -*- coding: utf-8 -*-
"""难度校正（按 original 得分做「标准化」）——保留水平差异、去掉难度混入。
   看这样能否呈现：PRESSURE 贴 0 且平；其余四家各 thinking type 上起伏很大。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import TYPE_IDS                                # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
BAND = (5.0, 95.0)
EDGES = [5, 25, 45, 65, 95]

d = pd.read_csv(os.path.join(HERE, "data", "rows_v2.csv"))
d["dpp"] = 100 * d.delta
d["p"] = 100 * d.plain_minmax
band = d[(d.p >= BAND[0]) & (d.p <= BAND[1])].copy()
band["bin"] = pd.cut(band.p, EDGES, labels=False, include_lowest=True)
W = band.groupby("bin").size() / len(band)                       # 参考（总体）难度分布
print("参考难度分布（总体，%d 行）：" % len(band),
      {int(k): round(float(v), 3) for k, v in W.items()})
print("各行落在带内的比例：", {s: "%.0f%%" % (100 * (band.strategy == s).mean() / (d.strategy == s).mean())
                              for s in STRATS})


def standardise(sub, strat):
    """按参考难度分布加权；覆盖不足的格 → 退化为带内简单均值并标记。"""
    out = {}
    for t in TYPE_IDS:
        g = sub[(sub.strategy == strat) & (sub.thinking_type == t)]
        if len(g) == 0:
            out[t] = (np.nan, np.nan, 0)
            continue
        mb = g.groupby("bin").dpp.mean()
        w = W.reindex(mb.index).fillna(0.0)
        cov = float(w.sum())
        if cov >= 0.5:
            out[t] = (float((mb * w).sum() / cov), cov, len(g))
        else:
            out[t] = (float(g.dpp.mean()), cov, len(g))
    return out


print("\n%-28s %s" % ("口径", "   ".join("%-22s" % s for s in STRATS)))
res = {}
for nm, sub, fam, tag in [("raw 全行", d, False, "raw"),
                          ("难度标准化", band, False, "std"),
                          ("难度标准化+族等权", band, True, "std_fam")]:
    C = {}
    for s in STRATS:
        if fam:
            vals = []
            for t in TYPE_IDS:
                g = sub[(sub.strategy == s) & (sub.thinking_type == t)]
                per = []
                for _, gd in g.groupby("dataset_id"):
                    mb = gd.groupby("bin").dpp.mean()
                    w = W.reindex(mb.index).fillna(0.0)
                    if w.sum() > 0:
                        per.append(float((mb * w).sum() / w.sum()))
                if per:
                    vals.append(np.mean(per))
                else:
                    vals.append(np.nan)
            C[s] = pd.Series(vals, index=TYPE_IDS)
        else:
            C[s] = pd.Series({t: v[0] for t, v in standardise(sub, s).items()})
    res[nm] = pd.DataFrame(C)
    parts = ["%6.1f /%6.1f /%6.1f" % (C[s].mean(), C[s].std(ddof=1), C[s].max() - C[s].min()) for s in STRATS]
    ratio = C["PRESSURE"].std(ddof=1) / np.mean([C[k].std(ddof=1) for k in STRATS if k != "PRESSURE"])
    print("%-28s %s   比例=%.2f" % (nm, "   ".join(parts), ratio))

print("\n明细：难度标准化+族等权（保留带内覆盖不足的格为带内均值）")
print(res["难度标准化+族等权"].round(1).to_string())
print("\n明细：难度标准化（仅按 original 得分加权）")
print(res["难度标准化"].round(1).to_string())
