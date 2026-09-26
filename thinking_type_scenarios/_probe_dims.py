# -*- coding: utf-8 -*-
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data"
d = pd.read_csv(D + r"\rows_v2.csv")
print("rows_v2 shape", d.shape)
print("cols:", list(d.columns))
for c in d.columns:
    try:
        n = d[c].nunique()
    except Exception:
        continue
    if n <= 15:
        print("--", c, d[c].value_counts(dropna=False).to_dict())
print()
for name in ("cells_3dims.csv", "marginals_3dims.csv"):
    t = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\out" + "\\" + name)
    print(name, list(t.columns))
