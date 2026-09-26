# -*- coding: utf-8 -*-
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv"
d = pd.read_csv(D)
order = ["L1-K", "L1-R", "L1-E", "L1-F", "L2-K", "L2-R", "L2-E", "L2-F",
         "L3-K", "L3-R", "L3-E", "L3-F"]
g = d.groupby("thinking_type")
tab = pd.DataFrame({
    "n": g.size(),
    "math": g.apply(lambda x: (x.dataset_id == "chat_math500").mean(), include_groups=False),
    "flask": g.apply(lambda x: x.dataset_id.str.contains("flask").mean(), include_groups=False),
    "open": g.apply(lambda x: x.dataset_id.isin(["mt_bench", "chat_wild_bench"]).mean(), include_groups=False),
    "plain_mean": g.plain_minmax.mean(),
    "plain_low_share": g.plain_minmax.apply(lambda s: (s <= 20).mean()),
    "n_ds": g.dataset_id.nunique(),
}).reindex(order)
print("== per thinking type (rows_v2) ==")
print(tab.round(2).to_string())
print()
c = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\out\cells_3dims.csv")
cc = c[c.strategy == "PRESSURE"].set_index("thinking_type").reindex(order)
print("== PRESSURE cells: plain_mean / n_band / coverage / fallback / resid_lin ==")
print(cc[["n", "plain_mean", "n_band", "n_families", "coverage", "fallback", "std", "std_fam", "resid_lin"]].round(2).to_string())
print()
print("== cells with fallback=True or low coverage ==")
print(c[c.fallback][["strategy", "thinking_type", "n", "coverage", "fallback"]].to_string())
