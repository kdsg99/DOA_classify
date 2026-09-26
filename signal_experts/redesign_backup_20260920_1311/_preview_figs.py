# -*- coding: utf-8 -*-
"""方案预览图（草图）：把「份额视图」换成「效应量视图」，
   A. 每策略的动作效应森林图（Δ pp = reask − plain，95% CI）
   B. 5×11 效应热力图（primary / multilabel）
仅供用户拍板用，不替代正式产物。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign")
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
from taxonomy_v4 import IDS, NAMES, TARGET  # noqa: E402

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
df = pd.read_csv(R + r"\all_tasks_v4.csv")


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    o = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank, i in enumerate(o[::-1]):
        prev = min(prev, p[i] * n / (n - rank))
        q[i] = prev
    return q


def table(mode):
    rows = []
    for s in STRATS:
        sub = df[df.strategy == s]
        for t in IDS:
            g = sub[sub.primary == t] if mode == "primary" else sub[sub["o_" + t].astype(bool)]
            n = len(g)
            m = 100 * g.delta.mean() if n else np.nan
            se = 100 * g.delta.std(ddof=1) / np.sqrt(n) if n >= 2 else np.nan
            p = 2 * stats.t.sf(abs(m / se), n - 1) if (n >= 2 and se and se > 0) else 1.0
            rows.append(dict(strategy=s, action=t, n=n, mean=m, se=se, p=p))
    tt = pd.DataFrame(rows)
    tt["q"] = np.nan
    for s in STRATS:
        m = tt.strategy == s
        tt.loc[m, "q"] = bh(tt.loc[m, "p"])
    tt["lo"] = tt["mean"] - 1.96 * tt["se"]
    tt["hi"] = tt["mean"] + 1.96 * tt["se"]
    tt["target"] = [a in TARGET[s]["ops"] for s, a in zip(tt.strategy, tt.action)]
    return tt


TP = table("primary")
TM = table("multilabel")

# ---------- A. 森林图（primary，5 面板） ----------
fig, axes = plt.subplots(1, 5, figsize=(30, 8.2), sharey=True)
ys = np.arange(len(IDS))[::-1]
for ax, s in zip(axes, STRATS):
    g = TP[TP.strategy == s].set_index("action").reindex(IDS)
    ax.axvline(0, color="#333", lw=1.6, zorder=1)
    for i, (t, r) in enumerate(g.iterrows()):
        y = ys[i]
        col = "#C0392B" if r.target else "#4C72B0"
        if np.isfinite(r.se) and r.n > 1:
            ax.plot([r.lo, r.hi], [y, y], "-", color=col, lw=2.4, alpha=0.85, zorder=3)
        ax.scatter(r["mean"], y, s=25 + r.n * 0.55, color=col, zorder=4,
                   edgecolors="k", linewidths=0.7)
        tag = "FDR<.05" if r.q < 0.05 else ("FDR<.10" if r.q < 0.1 else "")
        if tag:
            ax.annotate(tag, (r["hi"] if r["hi"] > 0 else r["lo"], y), fontsize=6.6, color=col,
                        xytext=(4 if r["hi"] > 0 else -4, 0), textcoords="offset points", zorder=6,
                        ha="left" if r["hi"] > 0 else "right", va="center")
    base = 100 * df[df.strategy == s].delta.mean()
    ax.axvline(base, color="#2e8b57", ls="--", lw=1.4, zorder=2)
    ax.set_title("%s  （绿虚线 = 该策略全体基线 %+.1f pp）" % (s, base), fontsize=13, fontweight="bold")
    ax.set_ylim(-0.8, len(IDS) - 0.2)
    ax.set_xlim(-80, 30)
    ax.grid(True, axis="x", alpha=0.25)
    ax.set_xlabel("Δ score (pp) = reask − plain，95% CI", fontsize=10.5)
axes[0].set_yticks(ys)
axes[0].set_yticklabels(["%s %s" % (t, NAMES[t]) for t in IDS], fontsize=9.5)
fig.suptitle("A. 每策略动作效应森林图（primary 口径；点大小 = n，红 = 该策略目标动作，绿虚线 = 该策略自身基线）",
             fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(R + r"\fig_preview_forest_primary.png", dpi=140, bbox_inches="tight")
plt.close(fig)

# ---------- B. 热力图 ----------
order = [t for t in IDS]
for mode, TT in (("primary", TP), ("multilabel", TM)):
    M = np.full((len(STRATS), len(order)), np.nan)
    Q = np.full((len(STRATS), len(order)), np.nan)
    N = np.zeros((len(STRATS), len(order)), int)
    for i, s in enumerate(STRATS):
        g = TT[TT.strategy == s].set_index("action")
        for j, t in enumerate(order):
            M[i, j] = g.loc[t, "mean"]
            Q[i, j] = g.loc[t, "q"]
            N[i, j] = int(g.loc[t, "n"])
    fig, ax = plt.subplots(figsize=(17.5, 4.6))
    im = ax.imshow(M, cmap="RdBu", vmin=-70, vmax=30, aspect="auto")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(["%s\n%s" % (t.split("_")[0], NAMES[t]) for t in order], fontsize=9.5)
    ax.set_yticks(range(len(STRATS)))
    ax.set_yticklabels(STRATS, fontsize=11)
    for i in range(len(STRATS)):
        for j in range(len(order)):
            st = "" if Q[i, j] > 0.10 else ("*" if Q[i, j] > 0.05 else "**")
            ax.text(j, i, "%.0f%s\n(n=%d)" % (M[i, j], st, N[i, j]), ha="center", va="center",
                    fontsize=7.6, color="#111")
    for i, s in enumerate(STRATS):
        for j, t in enumerate(order):
            if t in TARGET[s]["ops"]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="#000", lw=2.6))
    cb = fig.colorbar(im, ax=ax, pad=0.012)
    cb.set_label("Δ score (pp)", fontsize=10)
    ax.set_title("B. 策略 × 思维动作 效应热力图（%s 口径）；黑框 = 该策略目标动作；* q<0.10，** q<0.05（格子内为 Δ 与 n）" % mode,
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(R + r"\fig_preview_heat_%s.png" % mode, dpi=140, bbox_inches="tight")
    plt.close(fig)

print("ok")
