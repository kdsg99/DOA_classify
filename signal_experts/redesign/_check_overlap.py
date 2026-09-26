# -*- coding: utf-8 -*-
"""PRESSURE 与其它策略在 chat_math500 的任务是否重叠。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
import pandas as pd                                             # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
m = df[df.dataset_id == "chat_math500"]
P = set(m[m.strategy == "PRESSURE"].task_id)
O = set(m[m.strategy != "PRESSURE"].task_id)
print("chat_math500 任务数：PRESSURE %d，其它策略合集 %d，交集 %d" % (len(P), len(O), len(P & O)))
print("PRESSURE 独有 %d，其它独有 %d" % (len(P - O), len(O - P)))
print("\n各策略在 6 个族上的行数：")
print(df.pivot_table(index="dataset_id", columns="strategy", values="delta", aggfunc="size").fillna(0).astype(int).to_string())
print("\n各策略 overall plain 均值（pp）：")
print((100 * df.groupby("strategy").plain_minmax.mean()).round(1).to_string())
print("\n各策略 overall delta 均值（pp）：")
print((100 * df.groupby("strategy").delta.mean()).round(1).to_string())
