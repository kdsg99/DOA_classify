# -*- coding: utf-8 -*-
"""核对：同一 (dataset_id, task_id) 在不同策略间的覆盖与 plain 是否一致；PRESSURE 数学行的标签构成。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
import pandas as pd                                             # noqa: E402
from taxonomy_v4 import NAMES                                   # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
key = ["dataset_id", "task_id"]
v = df.groupby(key)["strategy"].nunique()
print("(dataset,task) 覆盖策略数分布：", v.value_counts().sort_index().to_dict(), "| 唯一任务数", len(v))
p = df.groupby(key)["plain_minmax"].nunique()
print("同一任务在不同策略间 plain 不同的占比：%.1f%%（共 %d 个任务）" % (100 * (p > 1).mean(), len(p)))
sh = df.groupby(key)["reask_minmax"].nunique()
print("同一任务在不同策略间 reask 不同的占比：%.1f%%" % (100 * (sh > 1).mean()))

m = df[df.dataset_id == "chat_math500"]
print("\nchat_math500：PRESSURE 行的标签构成")
g = m[m.strategy == "PRESSURE"].copy()
g["pn"] = g.primary.map(NAMES)
t = g.groupby(["pn", "original_difficulty"]).agg(n=("delta", "size"),
                                                 plain=("plain_minmax", lambda x: 100 * x.mean()),
                                                 dpp=("delta", lambda x: 100 * x.mean()))
print(t.to_string())
print("\nPRESSURE 数学行的 overall plain 均值 %.1f（其他策略 %.1f）"
      % (100 * g.plain_minmax.mean(), 100 * m[m.strategy != "PRESSURE"].plain_minmax.mean()))
o = m[m.strategy != "PRESSURE"].copy()
o["pn"] = o.primary.map(NAMES)
print("其他策略在 chat_math500 的标签构成：")
print(o.groupby("pn").agg(n=("delta", "size"), plain=("plain_minmax", lambda x: 100 * x.mean())).to_string())
