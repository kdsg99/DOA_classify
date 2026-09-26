# -*- coding: utf-8 -*-
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__))
df=pd.read_csv(os.path.join(HERE,"all_tasks_v2.csv"))
print("rows",len(df))
# duplicates within (strategy, dataset, task_id)?
d=df.groupby(['strategy','dataset_id','task_id']).size()
print("dup (strategy,ds,tid) groups:", int((d>1).sum()), " max repeats:", int(d.max()))
print(d[d>1].head(10))
print()
# rows per strategy
print(df.groupby('strategy').size())
# unique task ids per strategy
print(df.groupby('strategy').apply(lambda g: g.groupby(['dataset_id','task_id']).ngroups, include_groups=False))
# unique (ds,tid) overall
print("unique (ds,tid):", df.groupby(['dataset_id','task_id']).ngroups)
