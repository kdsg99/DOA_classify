# -*- coding: utf-8 -*-
"""找第三维度候选：每个 thinking type 上的行级属性分布。"""
import sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv"
d = pd.read_csv(D)
order = ["L1-K", "L1-R", "L1-E", "L1-F", "L2-K", "L2-R", "L2-E", "L2-F",
         "L3-K", "L3-R", "L3-E", "L3-F"]
print("second_turn nunique:", d.second_turn.nunique(), d.second_turn.value_counts(dropna=False).to_dict())
print()
g = d.groupby("thinking_type")
tab = pd.DataFrame({
    "n": g.size(),
    "math_share": g.apply(lambda x: (x.dataset_id == "chat_math500").mean(), include_groups=False),
    "flask_share": g.apply(lambda x: x.dataset_id.str.contains("flask").mean(), include_groups=False),
    "open_share": g.apply(lambda x: x.dataset_id.isin(["mt_bench", "chat_wild_bench"]).mean(), include_groups=False),
    "hard_share": g.original_difficulty.apply(lambda s: (s == "hard").mean()),
    "plain_mean": g.plain_minmax.mean(),
    "n_datasets": g.dataset_id.nunique(),
}).reindex(order)
print("== per thinking type ==")
print(tab.round(2).to_string())
print()
print("== per (strategy, type) hard_share / plain_mean ==")
g2 = d.groupby(["strategy", "thinking_type"])
t2 = pd.DataFrame({"n": g2.size(),
                   "hard_share": g2.original_difficulty.apply(lambda s: (s == "hard").mean()),
                   "plain_mean": g2.plain_minmax.mean(),
                   "math_share": g2.apply(lambda x: (x.dataset_id == "chat_math500").mean(), include_groups=False),
                   }).reset_index()
print(t2.pivot(index="thinking_type", columns="strategy", values="plain_mean").reindex(order).round(1).to_string())
print()
print(t2.pivot(index="thinking_type", columns="strategy", values="hard_share").reindex(order).round(2).to_string())
