# -*- coding: utf-8 -*-
"""核对 L1-F / L3-F 这些薄格：逐行看 plain/reask/delta。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd                                             # noqa: E402

d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
d["dpp"] = 100 * d.delta
d["p"] = 100 * d.plain_minmax
for t in ["L1-F", "L3-F"]:
    g = d[d.thinking_type == t]
    print("=== %s  n=%d" % (t, len(g)))
    print(g.groupby(["strategy", "dataset_id"]).agg(n=("dpp", "size"), plain=("p", "mean"),
                                                    delta=("dpp", "mean")).round(1).to_string())
    print()
R = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\out\cells_3dims.csv")
print(R[R.thinking_type.isin(["L1-F", "L3-F"])][["strategy", "thinking_type", "n", "n_band", "n_families",
                                                  "coverage", "fallback", "raw", "std", "std_fam",
                                                  "plain_mean", "sat_share"]].round(2).to_string(index=False))
