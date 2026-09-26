# -*- coding: utf-8 -*-
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
print("cols:", list(d.columns))
print("shape:", d.shape)
for c in d.columns:
    n = d[c].nunique(dropna=False)
    if n <= 20:
        print("--", c, "|", d[c].value_counts(dropna=False).head(20).to_dict())
print()
print("dataset_id:", d.dataset_id.value_counts().to_dict())
print()
print(d.head(3).to_string())
