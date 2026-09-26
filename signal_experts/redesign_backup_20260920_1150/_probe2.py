# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd
from classify_v2 import classify_one

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw_data")
# real math500 samples
m = pd.read_csv(os.path.join(RAW, "heuristic_low.csv"))
m = m[m.dataset_id == "chat_math500"].drop_duplicates("task_id").head(5)
print("=== chat_math500 ===")
for _, r in m.iterrows():
    print(classify_one(r.to_dict()), "|", str(r["problem"])[:90])
print()
# real mt_bench reasoning samples
t = pd.read_csv(os.path.join(RAW, "pressure_high.csv"))
t = t[(t.dataset_id == "mt_bench") & (t.category == "reasoning")].drop_duplicates("task_id").head(5)
print("=== mt_bench reasoning ===")
for _, r in t.iterrows():
    print(classify_one(r.to_dict()), "|", str(r["task"])[:90])
print()
# mt_bench extraction (low-ish)
t2 = pd.read_csv(os.path.join(RAW, "heuristic_low.csv"))
t2 = t2[(t2.dataset_id == "mt_bench") & (t2.category == "extraction")].drop_duplicates("task_id").head(5)
print("=== mt_bench extraction ===")
for _, r in t2.iterrows():
    print(classify_one(r.to_dict()), "|", str(r["task"])[:90])
