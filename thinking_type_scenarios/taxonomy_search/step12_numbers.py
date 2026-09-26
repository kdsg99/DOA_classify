# -*- coding: utf-8 -*-
"""Numbers quoted in the report."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screen2 as S2                                            # noqa: E402

pd.set_option("display.width", 240)
piv, feat = S2.load()
print("tasks", len(piv), "rows 2801; tasks per strategy:", piv.notna().sum().to_dict())
print("complete (all five):", int(piv.notna().all(axis=1).sum()))
print("mean dpp:", (100 * piv.mean()).round(1).to_dict())
print("sd   dpp:", (100 * piv.std()).round(1).to_dict())
print("\ncorrelation of per-task deltas:")
print(piv.corr().round(2).to_string())
F = piv[["CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]]
c = F.sub(F.mean(axis=1), axis=0)
print("\nwithin-task contrast (four focal): SD per strategy (pp)",
      (100 * c.std()).round(1).to_dict(), " mean |contrast|", round(float(100 * c.abs().mean().mean()), 1))
print("SD of pairwise contrasts (pp):", round(float(100 * (F["CRITICAL"] - F["ENCOURAGE"]).std()), 1))
R = pd.read_csv(os.path.join(HERE, "out", "requirements_all.csv"))
sel = ["GENRE x output-constraint", "GENRE x level x output-constraint", "GENRE x level", "agg8 x level",
       "agg8 x len", "agg4 x level", "v2 12 types", "v2 operation level (3)", "family"]
print("\n" + R[R.partition.isin(sel)][["partition", "n_types", "R1", "R2", "R3", "R4", "total",
                                      "c_inter", "rev_pairs", "p_mean", "p_sd", "p_pos", "o_sd", "rel"]]
      .round(2).to_string(index=False))
rnd = R[R.kind == "random"]
print("\nrandom floor (8 splits):", {c: round(float(rnd[c].mean()), 2) for c in ["R1", "R2", "R3", "R4", "total"]},
      "| R1 range %.2f-%.2f" % (rnd.R1.min(), rnd.R1.max()))
print("\ncontent splits R1: max %.2f  (headroom %.2f-%.2f)" % (R[R.kind == "content"].R1.max(), 0.45, 0.86))
