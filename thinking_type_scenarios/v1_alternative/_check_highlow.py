# -*- coding: utf-8 -*-
"""核对 set=high/low 与 delta 的关系（用于「Nature of gain」的实测口径）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

df = pd.read_csv(os.path.join(HERE, "data", "rows_with_thinking_type.csv"))
print("set 取值：", df["set"].value_counts().to_dict())
g = df.groupby("set")["delta"].agg(["mean", "min", "max", "size"])
print(g.round(4).to_string())
print("\nhigh 中 delta<=0 的行数：%d / %d" % ((df[df['set'] == 'high'].delta <= 0).sum(), (df['set'] == 'high').sum()))
print("low  中 delta>0  的行数：%d / %d" % ((df[df['set'] == 'low'].delta > 0).sum(), (df['set'] == 'low').sum()))
print("\n各 (strategy, thinking_type) 的 high/low 计数样例：")
p = df.pivot_table(index=["strategy", "thinking_type"], columns="set", values="delta", aggfunc="size").fillna(0).astype(int)
print(p.head(14).to_string())
print("\n高/低与 delta 符号的一致率：%.1f%%" % (100 * (((df['set'] == 'high') == (df.delta > 0)).mean())))
