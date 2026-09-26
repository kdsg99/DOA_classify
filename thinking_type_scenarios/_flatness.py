# -*- coding: utf-8 -*-
"""逐策略「平不平」：各口径下 12 格值的 均值/SD/极差，找出最能呈现
『PRESSURE 贴在 0 附近且平、其他策略波动大』的口径。"""
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
d["p_pp"] = 100 * d.plain_minmax
d["fam"] = d.dataset_id
d["bin"] = pd.cut(d.p_pp, [0, 20, 40, 60, 80, 95, 100.01], labels=False, include_lowest=True)

# 各口径的「行级」校正值
d["A_res"] = np.nan                                   # 策略内线性（= 现 fig2）
d["B_resb"] = np.nan                                  # 策略内「原分箱」非线性
d["C_resf"] = np.nan                                  # 策略内 族 + 线性
d["D_resbf"] = np.nan                                 # 策略内 族 + 原分箱
for s in STRATS:
    g = d[d.strategy == s]
    b1, b0 = np.polyfit(g.p_pp, g.dpp, 1)
    d.loc[g.index, "A_res"] = g.dpp - (b0 + b1 * g.p_pp)
    d.loc[g.index, "B_resb"] = g.dpp - g.groupby("bin").dpp.transform("mean")
    X = np.column_stack([np.ones(len(g)), g.p_pp.values,
                         pd.get_dummies(g.fam, drop_first=True).astype(float).values])
    beta, *_ = np.linalg.lstsq(X, g.dpp.values, rcond=None)
    d.loc[g.index, "C_resf"] = g.dpp.values - X @ beta
    X2 = np.column_stack([pd.get_dummies(g.fam).astype(float).values,
                          pd.get_dummies(g.bin).astype(float).values])
    b2, *_ = np.linalg.lstsq(X2, g.dpp.values, rcond=None)
    d.loc[g.index, "D_resbf"] = g.dpp.values - X2 @ b2

CELLS = {}
for nm, col in [("raw Δ", "dpp"), ("A 策略内线性(现fig2)", "A_res"), ("B 策略内原分箱", "B_resb"),
                ("C 策略内族+线性", "C_resf"), ("D 策略内族+原分箱", "D_resbf")]:
    C = d.pivot_table(index="thinking_type", columns="strategy", values=col, aggfunc="mean").reindex(TYPE_IDS)[STRATS]
    CELLS[nm] = C
    # 族等权版（每个族一票；pivot 用行均值近似 → 另算）
    Cb = d.pivot_table(index=["thinking_type", "fam"], columns="strategy", values=col, aggfunc="mean")
    Cb = Cb.groupby(level=0).mean().reindex(TYPE_IDS)[STRATS]
    CELLS[nm + " + 族等权"] = Cb

print("%-30s %s" % ("口径", "   ".join("%-22s" % s for s in STRATS)))
print("%-30s %s" % ("", "   ".join("%19s" % ("mean / SD / range") for _ in STRATS)))
for nm, C in CELLS.items():
    parts = []
    for s in STRATS:
        v = C[s].dropna().values
        parts.append("%6.1f /%6.1f /%6.1f" % (v.mean(), v.std(ddof=1), v.max() - v.min()))
    print("%-30s %s" % (nm, "   ".join(parts)))

print("\n把 '平' 定义为 12 格 SD，比值 = PRESSURE / 其余四家平均SD：")
for nm, C in CELLS.items():
    s = {st: C[st].dropna().std(ddof=1) for st in STRATS}
    print("  %-30s ratio=%.2f   PRESSURE=%.1f  别的=%s" %
          (nm, s["PRESSURE"] / np.mean([s[k] for k in STRATS if k != "PRESSURE"]), s["PRESSURE"],
           {k: round(v, 1) for k, v in s.items() if k != "PRESSURE"}))
print("\n『近 0』：|12 格均值|")
for nm, C in CELLS.items():
    print("  %-30s %s" % (nm, {st: round(C[st].dropna().mean(), 1) for st in STRATS}))
print("\n明细（D 策略内族+原分箱 + 族等权）：")
print(CELLS["D 策略内族+原分箱 + 族等权"].round(1).to_string())
print("\n明细（B 策略内原分箱 + 族等权）：")
print(CELLS["B 策略内原分箱 + 族等权"].round(1).to_string())
