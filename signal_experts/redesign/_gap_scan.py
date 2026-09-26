# -*- coding: utf-8 -*-
"""扩样前的缺口盘点：族×动作 的现有样本量、缺题格、模型与打分信息、提示语来源。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import pandas as pd                                             # noqa: E402
from taxonomy_v4 import IDS, NAMES, TARGET                      # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
print("行数 %d；列 mode/set/model 取值：" % len(df))
for c in ["mode", "set", "model"]:
    if c in df:
        print("  %-6s %s" % (c, df[c].value_counts().head(8).to_dict()))
if "n_valid_scores" in df:
    print("  n_valid_scores 描述：", df.n_valid_scores.describe()[["min", "25%", "50%", "75%", "max"]].to_dict())
print("\n各族×策略 行数：")
print(df.pivot_table(index="dataset_id", columns="strategy", values="delta", aggfunc="size").fillna(0).astype(int).to_string())

for mode in ("primary", "multilabel"):
    if mode == "primary":
        M = df.pivot_table(index="primary", columns="dataset_id", values="delta", aggfunc="size").fillna(0).astype(int)
    else:
        rows = []
        for t in IDS:
            s = df[df["o_" + t].astype(bool)]
            rows.append(s.groupby("dataset_id").size().rename(t))
        M = pd.concat(rows, axis=1).T.fillna(0).astype(int)
    M = M.reindex(IDS).fillna(0).astype(int)
    M.index = [NAMES[t] for t in M.index]
    print("\n=== %s 口径：族 × 动作 行数（行=动作）" % mode)
    print(M.to_string())
    print("每动作的族覆盖：>=30 行的族数 / >=15 行的族数")
    for nm, r in M.iterrows():
        print("   %-8s %d / %d ；空缺族：%s" % (nm, (r >= 30).sum(), (r >= 15).sum(),
              [c for c in M.columns if r[c] == 0]))

# 缺格：683 题 × 5 策略
tot = df.groupby(["dataset_id", "task_id"])["strategy"].nunique()
print("\n每题的策略覆盖数分布：", tot.value_counts().sort_index().to_dict(), "| 唯一题数", len(tot))
print("理论格数 683×5=%d，实际 %d，缺 %d" % (683 * 5, len(df), 683 * 5 - len(df)))
peri = df.groupby("dataset_id")["task_id"].nunique()
print("各族题数：", peri.to_dict())
print("各族实际行数/理论行数：")
for f, n in peri.items():
    got = len(df[df.dataset_id == f])
    print("   %-16s %3d 题 × 5 = %3d 格，实际 %3d（缺 %d）" % (f, n, n * 5, got, n * 5 - got))
