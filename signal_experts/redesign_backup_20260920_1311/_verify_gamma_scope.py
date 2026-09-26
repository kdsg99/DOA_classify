# -*- coding: utf-8 -*-
"""核对 scheme_interaction.csv 里 dataset γ z=+6.2 的口径：all-rows vs common-245。
直接调用原始 analyze_gamma.perm_test（不是我复制的版本）。"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyze_gamma as G, analyze_v3 as A
from taxonomy_v3 import SCHEMES
from taxonomy_v4 import IDS, NAMES

keys = A.common_keys(pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"),
                                 usecols=["dataset_id", "task_id", "strategy"]))
sch = A.load_all()
v4 = pd.read_csv(os.path.join(HERE, "all_tasks_v4.csv"))
v4["cat"] = v4["primary"]; v4["_key"] = list(zip(v4.dataset_id, v4.task_id))
sch["v4"] = dict(df=v4, title="v4 (11类)")

print(f"{'scheme':8s} {'scope':7s} {'cats':>4s} {'rows':>5s} {'gammaRMS':>8s} {'null_sd':>8s} {'z':>6s}")
for scope in ["all", "common"]:
    for tag, v in sch.items():
        d = v["df"].copy()
        cats = sorted(d["cat"].dropna().unique())
        if tag in SCHEMES:
            cats = [c for c in SCHEMES[tag]["ids"] if c in set(d["cat"].dropna().unique())]
        if tag == "v4":
            cats = [c for c in IDS if c in set(d["cat"].dropna().unique())]
        d = d[d["cat"].notna()]
        if scope == "common":
            d = d[d["_key"].isin(keys)]
        obs, nm, ns, z = G.perm_test(d, cats, n_perm=200)
        print(f"{tag:8s} {scope:7s} {len(cats):4d} {len(d):5d} {obs:8.3f} {ns:8.3f} {z:+6.2f}")
