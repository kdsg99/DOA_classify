# -*- coding: utf-8 -*-
"""难度校正算例：逐箱明细（直接用 tt3_analysis 的 bin 列，保证与 csv 完全一致）。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
sys.path.insert(0, H)
import tt3_analysis as T                                        # noqa: E402

d, band, W = T.prepare()
print("全样本 %d 行；带内（5<=p<=95）%d 行" % (len(d), len(band)))
print("参考混合（带内全体在四箱上的边际分布，来自数据）:",
      {int(k): round(float(v), 3) for k, v in W.items()})
mc = T.cells(d, band, W).set_index(["strategy", "thinking_type"])
LAB = {0: "[  5, 25]", 1: "( 25, 45]", 2: "( 45, 65]", 3: "( 65, 95]"}
for strat, t in (("PRESSURE", "L2-R"), ("PRESSURE", "L1-E"), ("PRESSURE", "L3-K")):
    g = d[(d.strategy == strat) & (d.thinking_type == t)]
    b = band[(band.strategy == strat) & (band.thinking_type == t)]
    print("=" * 86)
    print("%s / %s : 总行 %d，带内 %d；全格基线均值 %.1f；raw 均值 %+.1f"
          % (strat, t, len(g), len(b), g.p.mean(), g.dpp.mean()))
    num = cov = 0.0
    for k in (0, 1, 2, 3):
        s = b[b.bin == k]
        m = float(s.dpp.mean()) if len(s) else np.nan
        print("  箱%d %s  n=%3d   该箱平均涨幅 %s   统一权重 %.3f"
              % (k, LAB[k], len(s), ("%+.1f" % m) if not np.isnan(m) else "   --", W[k]))
        if not np.isnan(m):
            cov += W[k]
            num += W[k] * m
    print("  覆盖度 %.2f → 校正值 = %.3f / %.2f = %+.1f    (csv 的 std 列 %+.1f)"
          % (cov, num, cov, num / cov, mc.loc[(strat, t), "std"]))
