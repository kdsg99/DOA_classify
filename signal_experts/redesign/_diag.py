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

print("== CEILING CHECK: if we label by dataset_id ==")
for s in STRATS:
    sub=df[df.strategy==s]
    d=sub.groupby(['dataset_id','set']).size().unstack(fill_value=0)
    p=(d['high']/d['high'].sum()).values; q=(d['low']/d['low'].sum()).values
    print(f"  {s:12s} KL={kl(p,q):.3f}  high_by_ds={dict(zip(d.index,(d['high']/d['high'].sum()).round(3)))}")

print("\n== STRATIFIED (within dataset): does thinking_type predict high/low? ==")
print("   log2( high-rate(type) / base-high-rate(dataset) ) averaged over datasets, per strategy")
for s in STRATS:
    sub=df[df.strategy==s].copy()
    sub['is_high']=(sub['set']=='high')
    # base rate per dataset
    base=sub.groupby('dataset_id')['is_high'].mean()
    sub['base']=sub.dataset_id.map(base)
    rows=[]
    for tid in sub.thinking_type.unique():
        t=sub[sub.thinking_type==tid]
        # weighted mean of log ratio vs dataset base
        ratios=[]
        w=[]
        for ds,g in t.groupby('dataset_id'):
            if len(g)>=5:
                ratio=np.log2((g.is_high.mean()+0.02)/(base[ds]+0.02))
                ratios.append(ratio); w.append(len(g))
        if ratios:
            rows.append((tid, np.average(ratios,weights=w), int(t.shape[0])))
    rows.sort(key=lambda x:-x[1])
    print(f"  -- {s}")
    for tid,val,n in rows:
        print(f"       {tid:6s} adj_enrich={val:+.2f}  n={n}")
