# -*- coding: utf-8 -*-
"""v4 连续化改造：第二轮体检（重复行、delta 定义、标签频次）"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy_v4 import IDS, NAMES, TARGET

df = pd.read_csv(os.path.join(HERE, "all_tasks_v4.csv"))
FCOL = ["o_" + i for i in IDS]

print("IDS:", IDS)
print("NAMES:", [NAMES[i] for i in IDS])
print("FCOL ok:", all(c in df.columns for c in FCOL))
print()

d = df.delta.values
print("delta == reask - plain ?", np.allclose(df.reask_minmax - df.plain_minmax, d))
print("set/ delta sign crosstab:")
print(pd.crosstab(df['set'], pd.Series(np.sign(d), name="sign_of_delta")).to_string())
print()

print("delta by strategy (mean/median):")
print(df.groupby('strategy').delta.agg(['count', 'mean', 'median', 'std']).round(4).to_string())
print()
print("delta by dataset (mean):")
print(df.groupby('dataset_id').delta.agg(['count', 'mean']).round(4).to_string())
print()

g = df.groupby(['strategy', 'dataset_id', 'task_id'])
dup = g.size()
print("duplicated groups:", int((dup > 1).sum()))
dd = df.merge(dup.rename("nruns").reset_index(), on=['strategy', 'dataset_id', 'task_id'])
sub = dd[dd.nruns > 1]
for c in ["mode", "second_turn", "session_id", "n_valid_scores", "difficulty", "primary", "category"]:
    if c in dd.columns:
        print(f"  {c}: n_unique={sub[c].nunique(dropna=False)}  values={sub[c].drop_duplicates().head(6).tolist()}")
print("example duplicated block:")
ex = sub.groupby(['strategy', 'dataset_id', 'task_id']).head(3).head(6)
print(ex[["strategy", "dataset_id", "task_id", "mode", "second_turn", "delta", "n_valid_scores"]].to_string(index=False))
print()

fl = df.drop_duplicates(['dataset_id', 'task_id'])
print("task-level op frequency (n=%d tasks):" % len(fl))
freq = {NAMES[i]: int(fl["o_" + i].sum()) for i in IDS}
print(pd.Series(freq).sort_values(ascending=False).to_string())
print()
print("primary freq:")
print(fl.primary.value_counts().to_string())
print()
print("tasks per dataset:")
print(fl.dataset_id.value_counts().to_string())
print()
print("TARGET map:")
for s, v in TARGET.items():
    print(" ", s, "->", [NAMES[x] for x in v["ops"]])
