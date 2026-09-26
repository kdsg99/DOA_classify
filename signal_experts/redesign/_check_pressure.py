# -*- coding: utf-8 -*-
"""核对 PRESSURE 链式推演在族内是否也负。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from scipy import stats                                         # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
df["delta_pp"] = 100 * df.delta
df["plain_pp"] = 100 * df.plain_minmax
for s in ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]:
    sub = df[(df.strategy == s) & (df.primary == "T2_CHAIN")]
    ws, w = [], []
    out = []
    for f, g in sub.groupby("dataset_id"):
        m = g.delta_pp.mean()
        se = g.delta_pp.std(ddof=1) / np.sqrt(len(g)) if len(g) > 1 else np.nan
        nd = np.mean([g[g.dataset_id == f].plain_pp.mean()]) if False else g.plain_pp.mean()
        out.append("%s:%+.0f(n=%d,CI%+.0f~%+.0f,plain%.0f)"
                   % (f, m, len(g), m - 1.96 * se, m + 1.96 * se, nd))
        w.append(len(g))
        ws.append(m * len(g))
    print("%-11s 族内加权 %+.1f pp | %s" % (s, np.sum(ws) / np.sum(w), "  ".join(out)))
