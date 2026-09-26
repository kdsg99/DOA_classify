# -*- coding: utf-8 -*-
"""盘点 v2 分类（3 维 × 12 型）的数据：行列、每格样本量、high/low 与 delta 关系。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
SE = r"C:\Users\kl001\.nanobot\DOA\signal_experts"
sys.path.insert(0, os.path.join(SE, "redesign"))
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import TYPES, TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET   # noqa: E402

p = os.path.join(SE, "redesign", "all_tasks_v2.csv")
print("存在：", os.path.exists(p))
df = pd.read_csv(p)
print("%d 行 × %d 列" % (len(df), len(df.columns)))
print("列：", list(df.columns))
for c in ["strategy", "set", "thinking_type", "level", "target", "dataset_id"]:
    if c in df:
        print("\n%s：" % c, df[c].value_counts().to_dict())

print("\nset × delta：")
print(df.groupby("set")["delta"].agg(["mean", "size"]).round(4).to_string())
print("high 中 delta<=0 的行：%d/%d" % ((df[df['set'] == 'high'].delta <= 0).sum(), (df['set'] == 'high').sum()))
print("low  中 delta>0  的行：%d/%d" % ((df[df['set'] == 'low'].delta > 0).sum(), (df['set'] == 'low').sum()))

print("\nv2 12 型 × 策略 行数：")
M = df.pivot_table(index="thinking_type", columns="strategy", values="delta", aggfunc="size").reindex(TYPE_IDS).fillna(0).astype(int)
M.insert(0, "level", [ID2LEVEL[t] for t in M.index])
M.insert(1, "target", [ID2TARGET[t] for t in M.index])
print(M.to_string())
print("\n每型行数合计：")
print(df.thinking_type.value_counts().reindex(TYPE_IDS).to_string())
print("\n按 level 自治：", df.groupby("level").size().to_dict(), " 按 target：", df.groupby("target").size().to_dict())
