# -*- coding: utf-8 -*-
"""收集写方法论文档所需的数字。"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
meta = json.load(open(H + r"\out\meta.json", encoding="utf-8"))
print("meta:", json.dumps(meta, ensure_ascii=False, indent=1))
R = pd.read_csv(H + r"\out\cells_3dims.csv")
S = pd.read_csv(H + r"\out\spread_by_strategy.csv")
print("\ncoverage min/median:", round(R.coverage.min(), 3), round(R.coverage.median(), 3),
      "fallback:", int(R.fallback.sum()))
print("\nspread table (mean / sd / range):")
for ver in ["raw", "std", "std_fam"]:
    sub = S[S.version == ver].set_index("strategy")
    print(" %-8s" % ver, "  ".join("%s %6.1f/%5.1f/%4.0f" % (s, sub.loc[s, "mean"], sub.loc[s, "sd"], sub.loc[s, "rng"])
                                   for s in ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]))
print("\nPRESSURE raw vs std by type:")
p = R[R.strategy == "PRESSURE"].set_index("thinking_type")[["n", "plain_mean", "sat_share", "raw", "std", "coverage"]]
print(p.round(1).to_string())
print("\nsat_share mean by strategy (raw metric denominator):")
print(R.groupby("strategy").sat_share.mean().round(3).to_string())
print("\nrows per strategy, in-band share:")
rows = pd.read_csv(H + r"\data\rows_v2.csv")
rows["p"] = 100 * rows.plain_minmax
print(rows.groupby("strategy").apply(lambda x: pd.Series({
    "n": len(x), "in_band": ((x.p >= 5) & (x.p <= 95)).mean(),
    "sat": (x.p >= 99.5).mean(), "low": (x.p < 5).mean()}), include_groups=False).round(3).to_string())
print("\ncell n distribution:", R.n.describe()[["min", "25%", "50%", "75%", "max"]].to_dict())
