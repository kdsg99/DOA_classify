# -*- coding: utf-8 -*-
"""
v2 taxonomy, per-strategy own-set share plot (diagonal = plain).

x = 该策略在类别 t 的 low 数 / 该策略的 low 总数 x 100
y = 该策略在类别 t 的 high 数 / 该策略的 high 总数 x 100

This version adds a ZOOM view for the crowded low-share region and
leader-line labels so every point near the origin stays readable.

Outputs (redesign/fig_ownset_v2/):
    {STRATEGY}.png    1x2  [full range | zoom 0-15%]
    {STRATEGY}_full.png   single full panel (previous look)
    ALL.png           2x5  [full row | zoom row]
    ALL_full.png      1x5  single full row
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy_v2 import TYPE_IDS, ID2LEVEL, ID2TARGET

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
LEVEL_COLOR = {"L1": "#1f77b4", "L2": "#2ca02c", "L3": "#d62728"}
TARGET_MARKER = {"K": "o", "R": "^", "E": "s", "F": "D"}
LEVEL_LABEL = {"L1": "L1 执行层", "L2": "L2 结构层", "L3": "L3 元认知层"}
TARGET_LABEL = {"K": "K 知识", "R": "R 推理", "E": "E 表达", "F": "F 格式"}
ZOOM = 15.0            # zoom window 0..15 (%)

df = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
df["is_high"] = df["set"] == "high"
D_high = df[df.is_high].groupby("thinking_type").size()
D_low = df[~df.is_high].groupby("thinking_type").size()
R_GAIN = {t: int(D_high.get(t, 0)) / max(1, int(D_high.get(t, 0)) + int(D_low.get(t, 0))) for t in TYPE_IDS}
R_THR = float(np.median(list(R_GAIN.values())))
GAIN_SOLID = {t: bool(R_GAIN[t] >= R_THR) for t in TYPE_IDS}

rows = []
for s in STRATS:
    sub = df[df.strategy == s]
    L = int((~sub.is_high).sum()); H = int(sub.is_high.sum())
    for t in TYPE_IDS:
        g = sub[sub.thinking_type == t]
        l = int((~g.is_high).sum()); h = int(g.is_high.sum())
        rows.append(dict(strategy=s, thinking_type=t, level=ID2LEVEL[t], target=ID2TARGET[t],
                         n_high=h, n_low=l, n_task=h + l,
                         low_share=100 * l / L if L else 0.0,
                         high_share=100 * h / H if H else 0.0,
                         gain="拔高" if GAIN_SOLID[t] else "保稳"))
sh = pd.DataFrame(rows)
sh.to_csv(os.path.join(HERE, "share_ownset_v2.csv"), index=False)
VMAX = float(np.ceil(max(sh.high_share.max(), sh.low_share.max()) / 5) * 5) + 3

CANDS = [(11, 9), (11, -14), (-11, 9), (-11, -14), (17, 15), (-17, 15), (17, -20), (-17, -20),
         (26, 0), (-26, 0), (0, 17), (0, -20), (30, 16), (-30, 16), (30, -22), (-30, -22),
         (0, 28), (0, -32), (40, 0), (-40, 0), (36, 24), (-36, 24), (36, -28), (-36, -28)]


def markers_only(ax, s, lim, ms=250, lw=2.2):
    sub = sh[sh.strategy == s]
    for _, r in sub.iterrows():
        col = LEVEL_COLOR[r.level]
        fc = col if r.gain == "拔高" else "none"
        ax.scatter(r.low_share, r.high_share, s=ms, marker=TARGET_MARKER[r.target],
                   c=fc, edgecolors=col, linewidths=lw, zorder=4, clip_on=False)


def frame(ax, lim, diag=True, ticks=None):
    ax.fill_between([lim[0], lim[1]], [lim[0], lim[0]], [lim[1], lim[1]],
                    color="#2e8b57", alpha=0.07, zorder=0)
    ax.fill_between([lim[0], lim[1]], [lim[0], lim[0]], [lim[0], lim[0]], color="#c0392b",
                    alpha=0.0, zorder=0)
    if diag:
        ax.plot([lim[0], lim[1]], [lim[0], lim[1]], "-", color="#333333", lw=1.8, zorder=2)
    ax.set_xlim(*lim); ax.set_ylim(*lim)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.22)
    ax.set_xlabel("Low set share (%)", fontsize=11.5)
    ax.set_ylabel("High set share (%)", fontsize=11.5)


def label_points(ax, fig, sub, lim, fs=8.0):
    """collision-aware labels with leader lines; only points inside lim get labels."""
    inside = sub[(sub.low_share >= lim[0]) & (sub.low_share <= lim[1]) &
                 (sub.high_share >= lim[0]) & (sub.high_share <= lim[1])]
    if inside.empty:
        return 0, 0
    fig.canvas.draw()
    placed = []
    for _, r in inside.iterrows():
        px, py = ax.transData.transform((r.low_share, r.high_share))
        placed.append(Bbox.from_bounds(px - 10, py - 10, 20, 20))
    forced = 0
    for _, r in inside.iterrows():
        done = False
        for (dx, dy) in CANDS:
            far = (abs(dx) > 18 or abs(dy) > 18)
            kw = dict(arrowprops=dict(arrowstyle="-", lw=0.6, color="#9a9a9a",
                                      shrinkA=1, shrinkB=3)) if far else {}
            t = ax.annotate(f"{r.thinking_type} {r.n_task}", (r.low_share, r.high_share),
                            fontsize=fs, fontweight="bold", color="#111111", zorder=7,
                            xytext=(dx, dy), textcoords="offset points", ha="center",
                            va="center", bbox=dict(boxstyle="round,pad=0.14", fc="white",
                                                   ec="#cccccc", lw=0.6, alpha=0.88), **kw)
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer()).expanded(1.03, 1.10)
            if not any(bb.overlaps(u) for u in placed):
                placed.append(bb); done = True; break
            t.remove()
        if not done:
            forced += 1
            ax.annotate(f"{r.thinking_type} {r.n_task}", (r.low_share, r.high_share),
                        fontsize=fs, fontweight="bold", color="#111111", zorder=7,
                        xytext=(6, 26), textcoords="offset points", ha="center", va="center",
                        arrowprops=dict(arrowstyle="-", lw=0.6, color="#9a9a9a", shrinkA=1, shrinkB=3),
                        bbox=dict(boxstyle="round,pad=0.14", fc="#fff2cc", ec="#e0b000",
                                  lw=0.6, alpha=0.95))
    return len(inside), forced


def legend(ax, small=False):
    h = [Line2D([0], [0], marker="o", color="w", markerfacecolor=LEVEL_COLOR[lv],
                markeredgecolor=LEVEL_COLOR[lv], markersize=11, label=LEVEL_LABEL[lv])
         for lv in ["L1", "L2", "L3"]]
    h += [Line2D([0], [0], marker=TARGET_MARKER[tg], color="w", markerfacecolor="none",
                 markeredgecolor="#333333", markeredgewidth=2, markersize=10, label=TARGET_LABEL[tg])
          for tg in ["K", "R", "E", "F"]]
    h += [Line2D([0], [0], marker="o", color="w", markerfacecolor="none", markeredgecolor="#333333",
                 markeredgewidth=2, markersize=11, label="保稳倾向（空心）"),
          Line2D([0], [0], marker="o", color="w", markerfacecolor="#333333",
                 markeredgecolor="#333333", markersize=11, label="拔高倾向（实心）")]
    ax.legend(handles=h, loc="lower right", fontsize=8.0 if not small else 7.2,
              framealpha=0.94, ncol=2, title="颜色=层级  形状=对象  填充=增益" if not small else None,
              title_fontsize=8.4)


OUT = os.path.join(HERE, "fig_ownset_v2"); os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, "full"), exist_ok=True)
FULL_LIM = (-1.2, VMAX)
ZOOM_LIM = (-1.2, ZOOM)

for s in STRATS:
    sub = sh[sh.strategy == s]

    # 1x2 : full | zoom
    fig, axes = plt.subplots(1, 2, figsize=(17.5, 8.4))
    for ax, lim, tag in ((axes[0], FULL_LIM, f"全范围 0–{VMAX:.0f}%"), (axes[1], ZOOM_LIM, f"放大 0–{ZOOM:.0f}%")):
        frame(ax, lim)
        if lim is ZOOM_LIM:
            ax.add_patch(plt.Rectangle((0, 0), ZOOM, ZOOM, fill=False, ec="#888888",
                                       ls=(0, (4, 3)), lw=1.2, zorder=1))
        else:
            ax.add_patch(plt.Rectangle((0, 0), ZOOM, ZOOM, fill=False, ec="#888888",
                                       ls=(0, (4, 3)), lw=1.2, zorder=1))
        markers_only(ax, s, lim)
        ax.set_title(tag, fontsize=12)
    fig.tight_layout()
    n0, f0 = label_points(axes[0], fig, sub, FULL_LIM, fs=7.6)
    n1, f1 = label_points(axes[1], fig, sub, ZOOM_LIM, fs=9.2)
    print(f"  {s}: full {n0} labeled ({f0} forced), zoom {n1} labeled ({f1} forced)")
    legend(axes[0], small=True)
    fig.suptitle(f"{s}  （对角线 y=x = plain；点标为“类别 任务数”）", fontsize=14.5, fontweight="bold")
    fig.savefig(os.path.join(OUT, f"{s}.png"), dpi=190, bbox_inches="tight"); plt.close(fig)

    # single full panel (kept for continuity)
    fig, ax = plt.subplots(figsize=(10, 8.4))
    frame(ax, FULL_LIM); markers_only(ax, s, FULL_LIM)
    fig.tight_layout(); label_points(ax, fig, sub, FULL_LIM, fs=8.0)
    legend(ax)
    ax.set_title(f"{s}   （对角线 y=x = plain 基准）", fontsize=13, fontweight="bold")
    fig.savefig(os.path.join(OUT, "full", f"{s}.png"), dpi=200, bbox_inches="tight"); plt.close(fig)
    print("saved", s)

# ALL: 2 x 5
fig, axes = plt.subplots(2, 5, figsize=(33, 14.5), sharex="row", sharey="row")
for j, s in enumerate(STRATS):
    sub = sh[sh.strategy == s]
    for i, lim in ((0, FULL_LIM), (1, ZOOM_LIM)):
        ax = axes[i][j]
        frame(ax, lim)
        ax.add_patch(plt.Rectangle((0, 0), ZOOM, ZOOM, fill=False, ec="#888888",
                                   ls=(0, (4, 3)), lw=1.1, zorder=1))
        markers_only(ax, s, lim, ms=210, lw=2.0)
        if i == 0:
            ax.set_title(s, fontsize=16, fontweight="bold")
        if i == 1:
            ax.set_xlabel("Low set share (%)", fontsize=10)
        if j == 0:
            ax.set_ylabel(("High set share (%)" if i == 0 else "High set share (%)"), fontsize=10)
fig.tight_layout()
for j, s in enumerate(STRATS):
    sub = sh[sh.strategy == s]
    label_points(axes[0][j], fig, sub, FULL_LIM, fs=6.6)
    label_points(axes[1][j], fig, sub, ZOOM_LIM, fs=8.2)
legend(axes[1][4], small=True)
fig.suptitle("v2 thinking types — 每策略 Low/High set share（上：全范围；下：0–15% 放大；对角线=plain）",
             fontsize=16)
for j in range(5):
    print("check col", j, axes[0][j].get_xlim(), axes[1][j].get_xlim())
fig.savefig(os.path.join(OUT, "ALL.png"), dpi=140, bbox_inches="tight"); plt.close(fig)

fig, axes = plt.subplots(1, 5, figsize=(33, 7.6), sharex=True, sharey=True)
for ax, s in zip(axes, STRATS):
    sub = sh[sh.strategy == s]
    frame(ax, FULL_LIM); markers_only(ax, s, FULL_LIM, ms=220, lw=2.1)
    ax.set_title(s, fontsize=16, fontweight="bold")
    ax.set_xlabel("Low set share (%)", fontsize=10)
axes[0].set_ylabel("High set share (%)", fontsize=11)
fig.tight_layout()
for ax, s in zip(axes, STRATS):
    label_points(ax, fig, sh[sh.strategy == s], FULL_LIM, fs=7.0)
fig.suptitle("v2 thinking types — 每策略 Low/High set share（对角线=plain；颜色=层级，形状=对象，空心/实心=增益性质）",
             fontsize=16)
fig.savefig(os.path.join(OUT, "ALL_full.png"), dpi=150, bbox_inches="tight"); plt.close(fig)
print("ALL saved ->", OUT)
