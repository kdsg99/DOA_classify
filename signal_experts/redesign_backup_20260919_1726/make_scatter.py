# -*- coding: utf-8 -*-
"""
Per-strategy scatter: one figure per strategy, 12 points = 12 thinking types.

Corrected definition (v2):
  x = Low set share  = (# category-B tasks where THIS strategy scored strictly below plain)
                       / (# ALL category-B tasks that are "low", i.e. below plain, pooled over all strategies) * 100
  y = High set share = (# category-B tasks where THIS strategy scored strictly above plain)
                       / (# ALL category-B tasks that are "high", pooled over all strategies) * 100

=> different denominators per axis (low pool vs high pool).  Each type's five strategy
   values sum to 100% on each axis.  A point ABOVE the y=x line means: this strategy
   contributes more to that type's "improvement pool" than to its "damage pool".
- "plain" = plain_minmax. high/low are strict (raw files contain only strict high/low rows).
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy_v2 import TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET, LEVEL_EN

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
df["is_high"] = df["set"] == "high"
STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]

# ---- denominators: global HIGH pool / LOW pool per type (merged over the 5 strategies) ----
D_high = df[df.is_high].groupby("thinking_type").size()
D_low  = df[~df.is_high].groupby("thinking_type").size()
print("D_high (all 'high' tasks of that type):"); print(D_high.to_string())
print("D_low  (all 'low'  tasks of that type):"); print(D_low.to_string())

rows = []
for s in STRATS:
    sub = df[df.strategy == s]
    for t in TYPE_IDS:
        g = sub[sub.thinking_type == t]
        h = int(g.is_high.sum()); l = int((~g.is_high).sum())
        dh = int(D_high.get(t, 0)); dl = int(D_low.get(t, 0))
        rows.append(dict(strategy=s, thinking_type=t, level=ID2LEVEL[t], target=ID2TARGET[t],
                         n_high=h, n_low=l, n_total=h + l,
                         D_high=dh, D_low=dl,
                         high_share=100 * h / dh if dh else 0,
                         low_share=100 * l / dl if dl else 0))
sc = pd.DataFrame(rows)
sc.to_csv(os.path.join(HERE, "scatter_v2.csv"), index=False)

COLORS = {"L1": "#4C72B0", "L2": "#DD8452", "L3": "#55A868"}
vmax = float(np.ceil(max(sc.high_share.max(), sc.low_share.max()) / 5) * 5) + 2

def draw(ax, s, annotate_n=True):
    sub = sc[sc.strategy == s]
    lim = vmax
    # ---- the PLAIN baseline: y = x ----
    # When this strategy's high-rate / low-rate on a type equal the pooled average, then
    # n_high/D_high == n_low/D_low  ->  the point lands exactly ON y = x. So y = x IS plain
    # (net zero effect). Above  -> better than plain;  below -> worse than plain.
    ax.fill_between([0, lim], [0, lim], [lim, lim], color="#2e8b57", alpha=0.08, zorder=0)
    ax.fill_between([0, lim], [0, 0], [0, lim], color="#c0392b", alpha=0.08, zorder=0)
    ax.plot([0, lim], [0, lim], "-", color="#333333", lw=2.2, zorder=2)
    for _, r in sub.iterrows():
        ax.scatter(r.low_share, r.high_share, s=40 + r.n_total * 1.6,
                   c=COLORS[r.level], edgecolors="black", linewidths=0.9,
                   alpha=0.85, zorder=3)
        off = (7, 4) if r.high_share >= r.low_share else (7, -11)
        lab = f"{r.thinking_type} {ID2EN[r.thinking_type]}\n(n={r.n_total})" if annotate_n else r.thinking_type
        ax.annotate(lab, (r.low_share, r.high_share), fontsize=7.5,
                    xytext=off, textcoords="offset points", zorder=4)
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel("Low set share  (%)   = 该策略在该类别的下降数 / 全类别下降总数", fontsize=9.5)
    ax.set_ylabel("High set share (%)   = 该策略在该类别的提升数 / 全类别提升总数", fontsize=9.5)
    # note the plain baseline inside the axes
    ax.annotate("y = x  →  plain（净影响为零）", xy=(lim * 0.62, lim * 0.62),
                xytext=(lim * 0.30, lim * 0.66), fontsize=9.5, color="#333333",
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2), zorder=5)
    ax.grid(True, alpha=0.25)

for s in STRATS:
    fig, ax = plt.subplots(figsize=(9.5, 8))
    draw(ax, s)
    ax.text(0.97, 0.03, "劣于 plain（基准线下方）", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=11, color="#c0392b", alpha=0.8)
    ax.text(0.03, 0.97, "优于 plain（基准线上方）", transform=ax.transAxes, ha="left", va="top",
            fontsize=11, color="#1e8449", alpha=0.85)
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS[k],
                      markersize=9, markeredgecolor="k", label=f"{k} {LEVEL_EN[k]}")
               for k in ["L1", "L2", "L3"]]
    handles.append(Line2D([0], [0], color="#333333", ls="-", lw=2.2,
                          label="y = x  =  plain 基准线"))
    ax.legend(handles=handles, loc="lower right", fontsize=9, framealpha=0.9)
    ax.set_title(f"Strategy: {s}\nThinking-type High/Low share — 对角线 y = x 为 plain 基准"
                 f" (denominator = all 'high' / all 'low' tasks of that type)", fontsize=11.5)
    fig.tight_layout()
    fn = os.path.join(HERE, f"scatter_{s}.png")
    fig.savefig(fn, dpi=180, bbox_inches="tight"); plt.close(fig)
    print("saved", fn)

fig, axes = plt.subplots(1, 5, figsize=(30, 7), sharex=True, sharey=True)
for ax, s in zip(axes, STRATS):
    draw(ax, s, annotate_n=False)
    ax.set_title(s, fontsize=15, fontweight="bold")
fig.suptitle("Thinking-type High/Low share per strategy — 对角线 y = x 代表 plain 基准\n"
             "(x = Low set share, y = High set share; denominators = global high/low pool of that type)",
             fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(HERE, "scatter_all_strategies.png"), dpi=150, bbox_inches="tight"); plt.close(fig)
print("saved", os.path.join(HERE, "scatter_all_strategies.png"))

print("\n" + sc[["strategy","thinking_type","n_high","n_low","D_high","D_low","low_share","high_share"]].round(1).to_string(index=False))
