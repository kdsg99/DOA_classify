# -*- coding: utf-8 -*-
"""自检：绘制的条形与文字是否落在轴范围内。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

R = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\out\cells_3dims.csv")
PAD = 22.0
for c in ["raw_rel", "std_rel", "std_fam_rel", "raw", "std"]:
    rel = ~R["thin"]
    lim = max(10.0, float(np.nanmax(np.abs(R[c][rel]))))
    lim = float(np.ceil(lim * 1.30 / 5.0) * 5)
    xl = lim + PAD
    # 文字估算：6.3pt 字符 ≈ 3.8pt 宽；面板宽约 5.0in=360pt → 每 pt ≈ 2*xl/360 pp
    pp_per_pt = 2 * xl / 360.0
    txt = 22 * 3.8 * pp_per_pt            # 右边距文字宽
    worst_pos = float(R[c].max()) + 4 * 3.8 * pp_per_pt
    print("%-12s lim=%5.1f  xl=%5.1f  右边距文字占 %4.1fpp（从 %5.1f 起到 %5.1f）  最长正条(含标注)到 %5.1f  %s"
          % (c, lim, xl, txt, xl - txt, xl, worst_pos, "OK" if worst_pos < xl - txt else "**可能重叠**"))
