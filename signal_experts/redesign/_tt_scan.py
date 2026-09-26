# -*- coding: utf-8 -*-
"""看旧 12 类分类数据：列、规模、thinking type 分布。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA\signal_experts"
import pandas as pd                                             # noqa: E402

p = os.path.join(D, "all_tasks_with_thinking_type.csv")
df = pd.read_csv(p)
print("all_tasks_with_thinking_type.csv：%d 行 × %d 列" % (len(df), len(df.columns)))
print("列：", list(df.columns))
print("\n前 2 行（截断）：")
with pd.option_context("display.max_colwidth", 40):
    print(df.head(2).to_string())
for c in ["strategy", "set", "thinking_type", "dataset_id"]:
    print("\n%s 分布：" % c, df[c].value_counts().to_dict())
if "delta" in df:
    print("\ndelta 描述：", df.delta.describe().to_dict())
print("\nthinking_type × strategy 行数：")
print(df.pivot_table(index="thinking_type", columns="strategy", values="delta" if "delta" in df else "task",
                     aggfunc="size").fillna(0).astype(int).to_string())
print("\n另存一份对照：all_strategies_thinking_type_shares.csv")
p2 = os.path.join(D, "all_strategies_thinking_type_shares.csv")
if os.path.exists(p2):
    d2 = pd.read_csv(p2)
    print(d2.head(20).to_string())
