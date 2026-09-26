# -*- coding: utf-8 -*-
"""扩样缺口量化：按 66 格算缺口行数与题数。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import pandas as pd                                             # noqa: E402
from taxonomy_v4 import IDS, NAMES                              # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
df["plain_pp"] = 100 * df.plain_minmax
df = df[df.plain_pp < 99.999]                                    # 只算非饱和
fam = sorted(df.dataset_id.unique())
M = df.pivot_table(index="primary", columns="dataset_id", values="delta", aggfunc="size").reindex(IDS).reindex(columns=fam).fillna(0).astype(int)
print("非饱和行：族 × 动作 现有行数")
print(M.to_string())
T = 30
gap_rows = int(sum(max(0, T - M.loc[t, f]) for t in IDS for f in fam))
print("\n若每格目标 %d 行（primary、非饱和）：需要补 %d 行" % (T, gap_rows))
per_task = len(df) / df.groupby(["dataset_id", "task_id"]).ngroups
print("平均每题行数（=策略覆盖数）%.2f → 折合 ≈ %d 道题" % (per_task, gap_rows / per_task))
print("\n各族可用于扩样的非饱和题数（现有池）：")
tt = df.groupby("dataset_id").apply(lambda g: g.groupby("task_id").ngroups)
print(tt.to_string())
print("合计 %d 道非饱和题" % tt.sum())
print("\n每族需按动作铺开：每族 11 个动作 × 7 题 = 77 题 → 6 族约 460 题（现有非饱和池 %d 题，另有 DOA\\*.jsonl 可扩）" % tt.sum())
