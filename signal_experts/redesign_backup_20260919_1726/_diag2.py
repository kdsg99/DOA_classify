# -*- coding: utf-8 -*-
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
HERE=os.path.dirname(os.path.abspath(__file__))
df=pd.read_csv(os.path.join(HERE,"all_tasks_v2.csv"))
STRATS=["PRESSURE","ENCOURAGE","CRITICAL","MISLEADING","HEURISTIC"]
def kl(p,q):
    p=np.asarray(p,float)+1e-9; q=np.asarray(q,float)+1e-9
    return float(np.sum(p*np.log2(p/q)))
print("type-level KL(high||low) per strategy:")
for s in STRATS:
    sub=df[df.strategy==s]
    d=sub.groupby(['thinking_type','set']).size().unstack(fill_value=0)
    p=(d['high']/d['high'].sum()).values; q=(d['low']/d['low'].sum()).values
    print(f"  {s:12s} {kl(p,q):.3f}")
print("\ntarget aggregated enrichment (raw):")
t=pd.read_csv(os.path.join(HERE,"target_v2.csv"))
print(t.pivot(index='strategy',columns='key',values='enrich').reindex(STRATS).round(2).to_string())
print("\nlevel aggregated enrichment (raw):")
l=pd.read_csv(os.path.join(HERE,"level_v2.csv"))
print(l.pivot(index='strategy',columns='key',values='enrich').reindex(STRATS).round(2).to_string())
print("\nhigh/low sizes:")
print(df.groupby(['strategy','set']).size().unstack().reindex(STRATS).to_string())
print("\nthinking type overall counts (unique-task level):")
u=df.drop_duplicates(['dataset_id','task_id'])
print(u.thinking_type.value_counts().to_string())
