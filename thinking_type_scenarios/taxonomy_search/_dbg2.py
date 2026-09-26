# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd                                             # noqa: E402

d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
d["key"] = d.dataset_id.astype(str) + "|" + d.task_id.astype(str) + "|" + d["model"].astype(str)
print("rows", len(d), "keys", d.key.nunique())
print(d.groupby("dataset_id").key.nunique())
print()
print(d[["dataset_id", "task_id", "model", "key"]].head(3).to_string())
print(d[d.dataset_id == "chat_math500"][["dataset_id", "task_id", "model", "key"]].head(5).to_string())
print()
print("dtypes:", d.task_id.dtype, d.task_id.isna().sum(), d.dataset_id.isna().sum())
print(d.key.value_counts().head(5))
