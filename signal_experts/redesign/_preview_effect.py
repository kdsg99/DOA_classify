# -*- coding: utf-8 -*-
"""预演：换用「每策略×动作内自己作基准」的效应量，看差异是否显出来（不落盘，仅供出方案用）"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign")
import numpy as np
import pandas as pd
from taxonomy_v4 import IDS, NAMES, TARGET
from scipy import stats

R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
df = pd.read_csv(R + r"\all_tasks_v4.csv")
STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank, i in enumerate(o[::-1]):
        k = n - rank
        prev = min(prev, p[i] * n / k)
        q[i] = prev
    return q


def table(mode):
    rows = []
    for s in STRATS:
        sub = df[df.strategy == s]
        base = sub.delta.mean()
        for t in IDS:
            g = sub[sub.primary == t] if mode == "primary" else sub[sub["o_" + t].astype(bool)]
            n = len(g)
            if n >= 2:
                m, sd = g.delta.mean(), g.delta.std(ddof=1)
                se = sd / np.sqrt(n)
                tstat = m / se if se > 0 else np.nan
                p = 2 * stats.t.sf(abs(tstat), n - 1) if np.isfinite(tstat) else 1.0
            else:
                m, se, p = (g.delta.mean() if n else np.nan), np.nan, np.nan
            rows.append(dict(strategy=s, action=t, n=n, mean_delta=100 * m if n else np.nan,
                             se_pp=100 * se if n >= 2 else np.nan, p=p,
                             base_pp=100 * base, net_pp=100 * (m - base) if n else np.nan))
    out = pd.DataFrame(rows)
    out["q_strat"] = np.nan
    for s in STRATS:                                   # 策略内 11 个动作做 BH
        m = out.strategy == s
        out.loc[m, "q_strat"] = bh(out.loc[m, "p"].fillna(1.0))
    out["q_all"] = bh(out["p"].fillna(1.0))            # 55 个格子整体 BH
    return out


for mode in ("primary", "multilabel"):
    t = table(mode)
    print("\n########## %s 口径：Δscore(pp) = reask − plain，按动作内部" % mode)
    print("（每策略基线 = 该策略全体行均值；net = 该动作均值 − 该策略基线）")
    for s in STRATS:
        g = t[t.strategy == s]
        base = g.base_pp.iloc[0]
        n_show = g[g.n >= 5].sort_values("net_pp", ascending=False)
        print("\n[%s] 基线 %.2f pp；目标动作 %s" % (s, base, "、".join(NAMES[x] for x in TARGET[s]["ops"])))
        for _, r in n_show.iterrows():
            star = ""
            if r.q_all < 0.05:
                star = " **FDR<.05"
            elif r.q_all < 0.1:
                star = " *FDR<.10"
            elif r.p < 0.05:
                star = " (p<.05 未过FDR)"
            print("   %-12s n=%4d  Δ=%+6.2f pp  net=%+6.2f  p=%.3f q=%.3f%s%s"
                  % (NAMES[r.action], r.n, r.mean_delta, r.net_pp, r.p, r.q_all, star,
                     "  <=目标" if r.action in TARGET[s]["ops"] else ""))
    sig = t[(t.n >= 5) & (t.q_all < 0.1)].sort_values("q_all")
    print("\n  过 FDR<0.10 的格子：", len(sig))
    for _, r in sig.iterrows():
        print("   %-11s %-12s n=%4d net=%+6.2f q=%.3f" % (r.strategy, NAMES[r.action], r.n, r.net_pp, r.q_all))

# 目标 vs 非目标（每策略内）
print("\n########## 目标动作 vs 非目标动作（primary 口径，均值差）")
t = table("primary")
for s in STRATS:
    g = t[(t.strategy == s) & (t.n >= 5)]
    tg = g[g.action.isin(TARGET[s]["ops"])]
    ot = g[~g.action.isin(TARGET[s]["ops"])]
    print("  %-11s 目标 n=%d net=%+.2f | 非目标 n=%d net=%+.2f | 差 %+.2f pp"
          % (s, len(tg), tg.net_pp.mean(), len(ot), ot.net_pp.mean(),
             (tg.net_pp.mean() - ot.net_pp.mean()) if len(tg) and len(ot) else np.nan))
