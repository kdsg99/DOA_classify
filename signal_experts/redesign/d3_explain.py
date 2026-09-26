# -*- coding: utf-8 -*-
"""D3 详解：指标定义、逐格分解，以及「为何 PRESSURE 校正后更低」。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v4 import IDS, NAMES, TARGET                      # noqa: E402

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
df = pd.read_csv(R + r"\all_tasks_v4.csv")
df["delta_pp"] = 100 * df.delta
df["plain_pp"] = 100 * df.plain_minmax
df["family"] = df.dataset_id

for s in STRATS:
    sub = df[df.strategy == s]
    x, y = sub.plain_pp.values, sub.delta_pp.values
    b1, b0 = np.polyfit(x, y, 1)
    r = y - (b0 + b1 * x)
    r2 = 1 - np.sum(r ** 2) / np.sum((y - y.mean()) ** 2)
    print("=" * 104)
    print("%s：pooled 回归 delta_pp = %.2f + (%.3f) * plain_pp，R²=%.3f，n=%d；plain 均值 %.1f（sd %.1f）"
          % (s, b0, b1, r2, len(sub), x.mean(), x.std(ddof=1)))
    print("  检验恒等式：adjusted == raw − (b0 + b1*该格 plain 均值)")
    rows = []
    for t in IDS:
        g = sub[sub.primary == t]
        if len(g) == 0:
            continue
        xa = g.plain_pp.mean()
        raw = g.delta_pp.mean()
        pred = b0 + b1 * xa
        adj = (g.delta_pp - (b0 + b1 * g.plain_pp)).mean()
        rows.append((NAMES[t], len(g), xa, raw, pred, adj, raw - pred, t in TARGET[s]["ops"]))
    for nm, n, xa, raw, pred, adj, chk, tg in rows:
        print("    %s%-10s n=%3d 该格 plain 均值 %5.1f | raw %+7.1f | 难度期望 %+7.1f | 校正后 %+7.1f | 恒等校验差 %+.2e%s"
              % ("★" if tg else "  ", nm, n, xa, raw, pred, adj, chk - adj, "  ←目标" if tg else ""))
    # family mix of chain rows
    ch = sub[sub.primary == "T2_CHAIN"]
    print("  链式推演行的族构成：" + "  ".join("%s %d(%.0f%%,plain均值%.0f)"
          % (f, c, 100 * c / len(ch), ch[ch.family == f].plain_pp.mean())
          for f, c in ch.family.value_counts().items()))
    print("  链式推演行 plain 均值 %.1f vs 该策略全体 %.1f（差 %+.1f）"
          % (ch.plain_pp.mean(), x.mean(), ch.plain_pp.mean() - x.mean()))

print("=" * 104)
print("【稳健性】把「族」也一并刨掉：delta ~ plain + 族哑变量，看残差均值（primary 目标动作与链式推演）")
for s in STRATS:
    sub = df[df.strategy == s].copy()
    D = pd.get_dummies(sub.family, drop_first=True).astype(float).values
    X = np.column_stack([np.ones(len(sub)), sub.plain_pp.values, D])
    beta, *_ = np.linalg.lstsq(X, sub.delta_pp.values, rcond=None)
    sub["resid2"] = sub.delta_pp.values - X @ beta
    out = []
    for t in IDS:
        if t in TARGET[s]["ops"] or t == "T2_CHAIN":
            g = sub[sub.primary == t]
            if len(g):
                raw = g.delta_pp.mean()
                a1 = (g.delta_pp - (np.polyfit(sub.plain_pp.values, sub.delta_pp.values, 1)[1]
                                    + np.polyfit(sub.plain_pp.values, sub.delta_pp.values, 1)[0] * g.plain_pp)).mean()
                out.append("%s(raw%+.1f,仅扣难度%+.1f,难度+族%+.1f,n=%d)"
                           % (NAMES[t], raw, a1, g.resid2.mean(), len(g)))
    print("  %-11s %s" % (s, " ; ".join(out)))
