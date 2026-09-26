# -*- coding: utf-8 -*-
"""dim3 分组边际：承接型 vs 从零型（难度校正后，一型一票）。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd                                             # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
sys.path.insert(0, H)
from taxonomy_v2 import TYPE_IDS                                # noqa: E402

R = pd.read_csv(H + r"\out\cells_3dims.csv")
ROWS = pd.read_csv(H + r"\data\rows_v2.csv")
ROWS = ROWS[ROWS.thinking_type.isin(TYPE_IDS)]
cs = ROWS.groupby("thinking_type").apply(
    lambda x: float((x.dataset_id == "mt_bench").mean()), include_groups=False)
d3 = {t: ("continuation" if cs.get(t, 0) >= 0.30 else "from scratch") for t in TYPE_IDS}
R["d3"] = R.thinking_type.map(d3)
for col in ("raw_rel", "std_rel", "std_fam_rel"):
    p = R.pivot_table(index="d3", columns="strategy", values=col, aggfunc="mean")
    print("== %s (pp, one type = one vote) ==" % col)
    print(p[["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]].round(1).to_string())
    print()
print("continuation share per type:", {t: round(float(cs.get(t, 0)), 2) for t in TYPE_IDS})
print("\ndim3 x n of cells:", R.groupby(["d3", "strategy"]).size().unstack().to_dict())
