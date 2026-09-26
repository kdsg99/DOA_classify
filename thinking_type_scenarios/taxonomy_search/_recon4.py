# -*- coding: utf-8 -*-
"""Recon 4: correct task identity (dataset_id|task_id) -> design balance."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
d["key"] = d.dataset_id.astype(str) + "|" + d.task_id.astype("string").fillna("NA")
print("rows", len(d), "tasks", d.key.nunique())
print(d.groupby("dataset_id").key.nunique().to_dict())
cnt = d.groupby("key").strategy.nunique()
print("strategies per task:", cnt.value_counts().sort_index().to_dict())
print("rows per task:", d.groupby("key").size().value_counts().to_dict())
print()
# does each task have all 5 strategies exactly once?
g = d.groupby(["key", "strategy"]).size()
print("task x strategy duplicates:", int((g > 1).sum()), "of", len(g))
print()
piv = d.pivot_table(index="key", columns="strategy", values="delta", aggfunc="mean")
print("pivot shape", piv.shape, "complete cases", int(piv.notna().all(axis=1).sum()))
print(piv.notna().sum().to_dict())
print()
F = piv[["CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]]
print("mean delta (pp) per strategy:", (100 * piv.mean()).round(1).to_dict())
print("sd   delta (pp) per strategy:", (100 * piv.std()).round(1).to_dict())
print("\ncorrelation of strategy deltas across tasks:")
print(piv.corr().round(2).to_string())
