# -*- coding: utf-8 -*-
"""Figure 2 三份文档所需的全部分组统计（表格/边际/维度解释力）。"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
sys.path.insert(0, H)
from taxonomy_v2 import ID2EN, LEVEL_EN, TARGET_EN              # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
R = pd.read_csv(H + r"\out\cells_3dims.csv")
ROWS = pd.read_csv(H + r"\data\rows_v2.csv")
cs = ROWS.groupby("thinking_type").apply(
    lambda x: float((x.dataset_id == "mt_bench").mean()), include_groups=False)
R["d3"] = np.where(R.thinking_type.map(cs).to_numpy() >= 0.30, "continuation", "from scratch")
ORDER = R[[True] * len(R)] if False else None
TYPES = ["L1-K", "L1-R", "L1-E", "L1-F", "L2-K", "L2-R", "L2-E", "L2-F",
         "L3-K", "L3-R", "L3-E", "L3-F"]

# 1) 逐型完整表（每个策略）
print("=" * 100)
for s in STRATS:
    g = R[R.strategy == s].set_index("thinking_type").reindex(TYPES)
    print("\n### %s" % s)
    print(g[["n", "thin", "coverage", "plain_mean", "std", "std_rel", "std_fam_rel"]].round(1).to_string())

# 2) 三维边际（相对口径）
print("\n" + "=" * 100)
for col in ("std_rel", "std_fam_rel", "std"):
    print("\n===== marginals, %s =====" % col)
    for dim, keys in (("level", ["L1", "L2", "L3"]), ("target", ["K", "R", "E", "F"]),
                      ("d3", ["continuation", "from scratch"])):
        p = R.pivot_table(index=dim, columns="strategy", values=col, aggfunc="mean")[STRATS]
        print("-- %s --" % dim)
        print(p.reindex(keys).round(1).to_string())

# 3) 维度解释力 eta^2（策略内，12 格）
print("\n" + "=" * 100)
print("eta^2 per strategy (share of between-type variance explained by each axis)")
for col in ("std_rel", "std_fam_rel"):
    print("\n-- %s --" % col)
    print("%-11s %8s %8s %8s" % ("strategy", "level", "target", "dim3"))
    for s in STRATS:
        g = R[R.strategy == s]
        y = g[col].to_numpy(dtype=float)
        tot = float(np.var(y) * len(y))
        row = []
        for dim in ("level", "target", "d3"):
            ss = 0.0
            for k, sub in g.groupby(dim):
                m = sub[col].mean()
                ss += len(sub) * (m - y.mean()) ** 2
            row.append(ss / tot if tot else np.nan)
        print("%-11s %8.2f %8.2f %8.2f" % (s, row[0], row[1], row[2]))

# 4) 极值格（每策略最强/最弱三型，相对口径）
print("\n" + "=" * 100)
for s in STRATS:
    g = R[(R.strategy == s)].set_index("thinking_type").reindex(TYPES)
    g = g.sort_values("std_rel")
    print("\n%s  best:" % s, [(t, round(g.loc[t, "std_rel"], 1), int(g.loc[t, "n"]),
                              bool(g.loc[t, "thin"])) for t in g.index[-3:][::-1]])
    print("%s  worst:" % s, [(t, round(g.loc[t, "std_rel"], 1), int(g.loc[t, "n"]),
                              bool(g.loc[t, "thin"])) for t in g.index[:3]])

# 5) 每型跨策略：谁在这型上最好（用难度校正后的绝对水平 std）
print("\n" + "=" * 100)
p = R.pivot_table(index="thinking_type", columns="strategy", values="std", aggfunc="mean")[STRATS]
p["best"] = p.idxmax(axis=1)
p["n_L1F"] = 0
print(p.round(1).to_string())
print("\nthin cells per strategy (std_rel):")
print(R[R.thin].groupby("strategy").thinking_type.apply(list).to_string())
meta = json.load(open(H + r"\out\meta.json", encoding="utf-8"))
print("\nmeta:", json.dumps(meta, ensure_ascii=False)[:600])
