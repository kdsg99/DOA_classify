# -*- coding: utf-8 -*-
"""天花板效应盘点：plain=100% 的行有多少、它们的 Δ 结构。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
df["delta_pp"] = 100 * df.delta
df["plain_pp"] = 100 * df.plain_minmax
df["ceil"] = df.plain_pp >= 99.999
print("全表 %d 行，其中 plain=100%%（无上升空间）%d 行（%.0f%%）"
      % (len(df), df.ceil.sum(), 100 * df.ceil.mean()))
print("\n按族：饱和行占比 与 饱和行 Δ 均值 / 非饱和行 Δ 均值")
for f, g in df.groupby("dataset_id"):
    c = g[g.ceil]
    n = g[~g.ceil]
    print("  %-16s n=%4d 饱和 %4d(%3.0f%%)  Δ(饱和)=%+6.1f  Δ(非饱和)=%+6.1f  n(非饱和)=%d"
          % (f, len(g), len(c), 100 * g.ceil.mean(), c.delta_pp.mean(), n.delta_pp.mean(), len(n)))
print("\n按策略：")
for s, g in df.groupby("strategy"):
    c = g[g.ceil]
    n = g[~g.ceil]
    print("  %-11s n=%4d 饱和 %4d(%3.0f%%)  Δ(饱和)=%+6.1f  Δ(非饱和)=%+6.1f"
          % (s, len(g), len(c), 100 * g.ceil.mean(), c.delta_pp.mean(), n.delta_pp.mean()))
print("\n按动作（primary）：饱和占比 与 非饱和 Δ")
for t, g in df.groupby("primary"):
    c = g[g.ceil]
    n = g[~g.ceil]
    print("  %-14s n=%4d 饱和 %3.0f%%  Δ(饱和)=%+6.1f  Δ(非饱和)=%+6.1f (n=%d)"
          % (t, len(g), 100 * g.ceil.mean(), c.delta_pp.mean() if len(c) else np.nan,
             n.delta_pp.mean() if len(n) else np.nan, len(n)))
print("\n若只保留非饱和行：五策略整体 delta（pp）")
print(df[~df.ceil].groupby("strategy").delta_pp.mean().round(1).to_string())
print("\n非饱和行里 族×动作 的有效样本（primary）")
M = df[~df.ceil].pivot_table(index="primary", columns="dataset_id", values="delta", aggfunc="size").fillna(0).astype(int)
from taxonomy_v4 import NAMES                                    # noqa: E402
M.index = [NAMES[i] for i in M.index]
print(M.to_string())
