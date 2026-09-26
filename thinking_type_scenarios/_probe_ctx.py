# -*- coding: utf-8 -*-
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
print("second_turn:", d.second_turn.value_counts(dropna=False).head(10).to_dict())
print("category:", d.category.value_counts(dropna=False).head(12).to_dict())
print("_")
print("dataset x second_turn:")
print(pd.crosstab(d.dataset_id, d.second_turn.fillna("NA")).to_string())
# 是否"会话第 2 轮"
print()
col = None
for c in ("session_id", "wildbench_id", "set"):
    print(c, "nunique", d[c].nunique(dropna=False), d[c].dropna().head(3).tolist())
print()
d["ctx"] = d.dataset_id.isin(["mt_bench", "chat_wild_bench"])
order = ["L1-K", "L1-R", "L1-E", "L1-F", "L2-K", "L2-R", "L2-E", "L2-F",
         "L3-K", "L3-R", "L3-E", "L3-F"]
print("per type: mt/wildbench share (=contextual datasets)")
print(d.groupby("thinking_type").ctx.mean().reindex(order).round(2).to_string())
