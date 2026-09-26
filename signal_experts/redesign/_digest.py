# -*- coding: utf-8 -*-
"""汇总关键读数，供写总结与邮件用。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import numpy as np                                               # noqa: E402
import pandas as pd                                              # noqa: E402
from taxonomy_v4 import IDS, NAMES, TARGET                       # noqa: E402

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
N = NAMES

for mode in ("primary", "multilabel"):
    T = pd.read_csv(R + r"\effect_table_%s.csv" % mode)
    A = pd.read_csv(R + r"\adjust_%s.csv" % mode)
    C = pd.read_csv(R + r"\consistency_family_%s.csv" % mode)
    D = pd.read_csv(R + r"\strat_difficulty_%s.csv" % mode)
    F = pd.read_csv(R + r"\strat_family_%s.csv" % mode)
    print("=" * 100)
    print("### %s 口径" % mode)
    sig = T[(T.n >= 5) & (T.q_strat < 0.1)]
    print("过 FDR<0.10 的格子：%d / %d（n>=5 的 %d 格）"
          % (len(sig), len(T), len(T[T.n >= 5])))
    print("--- 每策略：目标动作 & 链式推演 & 最强/最弱动作（原始 Δ / 难度校正 Δ）")
    for s in STRATS:
        g = A[A.strategy == s].set_index("action")
        tg = [t for t in IDS if t in TARGET[s]["ops"]]
        gg = g.loc[[t for t in IDS if t in g.index]]
        top = gg.sort_values("adjusted_pp", ascending=False)
        print("  %-11s 基线 %+6.1f pp" % (s, T[T.strategy == s].base_pp.iloc[0]))
        for t in tg:
            if t in g.index:
                print("     目标 %-6s 原始 %+7.1f / 校正 %+7.1f pp" % (N[t], g.loc[t, "raw_pp"], g.loc[t, "adjusted_pp"]))
        if "T2_CHAIN" in g.index and "T2_CHAIN" not in tg:
            print("     对照 链式推演 原始 %+7.1f / 校正 %+7.1f pp"
                  % (g.loc["T2_CHAIN", "raw_pp"], g.loc["T2_CHAIN", "adjusted_pp"]))
        print("     校正后最高：%s %+.1f / 次高 %s %+.1f ；最低：%s %+.1f"
              % (N[top.index[0]], top.adjusted_pp.iloc[0], N[top.index[1]], top.adjusted_pp.iloc[1],
                 N[top.index[-1]], top.adjusted_pp.iloc[-1]))
        row = C[(C.strategy == s) & (C.action == "T2_CHAIN")]
        if len(row):
            r = row.iloc[0]
            print("     链式推演跨族：%d 族有数据，负 %d / 正 %d（n>=5 族内）"
                  % (r.n_families, r.n_neg, r.n_pos))
    print("--- D2 难度分层（plain 低/中/高）下的 链式推演 与各目标动作")
    for s in STRATS:
        g = D[D.strategy == s]
        line = []
        for t in IDS:
            if t in TARGET[s]["ops"] or t == "T2_CHAIN":
                vals = []
                for f in ["plain低", "plain中", "plain高"]:
                    r = g[(g.hr_tercile == f) & (g.action == t)]
                    vals.append("%+.0f(n=%d)" % (r.mean_pp.iloc[0], r.n.iloc[0]) if len(r) else "na(n=0)")
                line.append("%s [%s]" % (N[t], " ".join(vals)))
        print("  %-11s %s" % (s, " ; ".join(line)))
    print("--- D1 各族 链式推演（策略×族）")
    for s in STRATS:
        g = F[(F.strategy == s) & (F.action == "T2_CHAIN") & (F.n >= 5)]
        print("  %-11s %s" % (s, "  ".join("%s:%+.0f(n=%d)" % (r.family, r.mean_pp, r.n)
                                           for _i, r in g.iterrows())))
