# -*- coding: utf-8 -*-
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
df=pd.read_csv(os.path.join(HERE,"all_tasks_v2.csv"))
df["is_high"]=df["set"]=="high"
STRATS=["PRESSURE","ENCOURAGE","CRITICAL","MISLEADING","HEURISTIC"]
TYPES=sorted(df.thinking_type.unique())

# denominators
rows_total = df.groupby("thinking_type").size()            # all task-instances of type B (pooled)
uniq_total = df.groupby("thinking_type").apply(lambda g: g.groupby(["dataset_id","task_id"]).ngroups, include_groups=False)

print("type        #rows  #uniq")
for t in TYPES:
    print(f"{t:8s}{rows_total.get(t,0):7d}{uniq_total.get(t,0):7d}")

for strat in ["PRESSURE","ENCOURAGE"]:
    print("\n==================",strat)
    sub=df[df.strategy==strat]
    g=sub.groupby("thinking_type")["is_high"].agg(["sum","count"])
    g.columns=["high","total"]; g["low"]=g["total"]-g["high"]
    g=g.reindex(TYPES).fillna(0)
    g["A_x"]=100*g["low"]/g["total"].replace(0,np.nan)
    g["A_y"]=100*g["high"]/g["total"].replace(0,np.nan)
    g["B_x"]=100*g["low"]/rows_total.reindex(TYPES)
    g["B_y"]=100*g["high"]/rows_total.reindex(TYPES)
    print(g[["high","low","total","A_x","A_y","B_x","B_y"]].round(1).to_string())
