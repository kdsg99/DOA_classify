# -*- coding: utf-8 -*-
"""Recon 2: coverage design + current convergence + moderator screening."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
d = pd.read_csv(H + r"\data\rows_v2.csv")
print("rows_v2 columns:", list(d.columns))
d["key"] = d.dataset_id.astype(str) + "|" + d.task_id.astype(str) + "|" + d["model"].astype(str)
c = d.groupby("key").strategy.nunique()
print("\ntasks (dataset|task|model):", len(c))
print("strategy-count distribution per task:", c.value_counts().sort_index().to_dict())
print("tasks with all 5 strategies:", int((c == 5).sum()))
print("model values:", d["model"].value_counts().to_dict() if "model" in d else None)

# which strategies co-occur
piv = d.pivot_table(index="key", columns="strategy", values="delta", aggfunc="mean")
print("\nper-strategy non-null tasks:")
print(piv.notna().sum().to_dict())
print("\npairwise complete-case counts:")
print(piv.notna().astype(int).T.dot(piv.notna().astype(int)).to_string())
