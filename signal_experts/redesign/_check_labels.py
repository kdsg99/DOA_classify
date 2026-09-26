# -*- coding: utf-8 -*-
"""核对：primary 标签是按 (任务, 策略) 行给的，还是每个任务唯一？"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
import pandas as pd                                             # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
print("列名：", list(df.columns))
print("总行数", len(df), "| 行数按策略：")
print(df.strategy.value_counts().to_string())
idc = [c for c in df.columns if "id" in c.lower() or "task" in c.lower()]
print("候选 id 列：", idc)
if idc:
    k = idc[0]
    g = df.groupby(k)["primary"].nunique()
    print("按 %s 分组：任务数 %d，其中 primary 标签在不同策略间不一致的 %d 个（%.0f%%）"
          % (k, len(g), (g > 1).sum(), 100 * (g > 1).mean()))
    v = df.groupby(k)["strategy"].nunique()
    print("每个任务被几种策略覆盖：", v.value_counts().to_dict())
    # chat_math500 的链式推演行，各策略的 plain 分布
    m = df[(df.dataset_id == "chat_math500")]
    print("chat_math500 行数", len(m), "| 其中 primary=T2_CHAIN 按策略：")
    print(m[m.primary == "T2_CHAIN"].groupby("strategy").agg(
        n=("primary", "size"), plain_mean=("plain_minmax", lambda x: 100 * x.mean())).to_string())
    print("chat_math500 全体 plain 均值 %.1f" % (100 * m.plain_minmax.mean()))
