# -*- coding: utf-8 -*-
"""
Per-strategy scatter, v2 taxonomy, THREE visual dimensions.

Axes (per-strategy "own-set shares" — this is the normalisation that makes the
diagonal = plain and puts every strategy's points on BOTH sides of it):

  x = Low set share  =  该策略在类别 t 的 low 数 / 该策略的 low 总数  x 100
  y = High set share =  该策略在类别 t 的 high 数 / 该策略的 high 总数 x 100

  A strategy with no type-specific effect (i.e. "plain-like") has its highs and
  lows spread over the types in the same proportion  ->  x = y  ->  ON the diagonal.
  So the diagonal y = x is the plain baseline; the type's size decides how far
  out along that diagonal the point sits, the strategy's type-specific strength
  decides how far it deviates.

Visual channels (3 dimensions of a thinking type):
  colour = 认知层级 Level      L1 蓝 / L2 绿 / L3 红
  marker = 干预对象 Target     K ○ / R △ / E □ / F ◇
  fill   = 增益性质 Gain       实心 = 拔高倾向 (r >= median), 空心 = 保稳倾向
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy_v2 import TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
LEVEL_COLOR = {"L1": "#1f77b4", "L2": "#2ca02c", "L3": "#d62728"}
TARGET_MARKER = {"K": "o", "R": "^", "E": "s", "F": "D"}
LEVEL_LABEL = {"L1": "L1 执行层", "L2": "L2 结构层", "L3": "L3 元认知层"}
TARGET_LABEL = {"K": "K 知识", "R": "R 推理", "E": "E 表达", "F": "F 格式"}

df = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
df["is_high"] = df["set"] == "high"
D_high = df[df.is_high].groupby("thinking_type").size()
D_low = df[~df.is_high].groupby("thinking_type").size()
R_GAIN = {t: D_high.get(t, 0) / max(1, int(D_high.get(t, 0)) + int(D_low.get(t, 0))) for t in TYPE_IDS}
R_THR = float(np.median(list(R_GAIN.values())))
GAIN_SOLID = {t: bool(R_GAIN[t] >= R_THR) for t in TYPE_IDS}
SOLID_LIST = "、".join([t for t in TYPE_IDS if GAIN_SOLID[t]])

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
print("R_THR", round(R_THR, 3), "solid:", SOLID_LIST, "VMAX", VMAX)
for s in STRATS:
    g = sh[sh.strategy == s]
    print(f"{s:11s} above={int((g.high_share > g.low_share).sum()):2d} "
          f"below={int((g.high_share < g.low_share).sum()):2d} "
          f"corr={np.corrcoef(g.low_share, g.high_share)[0,1]:+.2f} "
          f"xmax={g.low_share.max():5.1f} ymax={g.high_share.max():5.1f} "
          f"maxdev={(g.high_share - g.low_share).abs().max():5.1f}")

OFFS = [(9, 6), (-9, 6), (9, -16), (-9, -16), (14, 18), (-14, 18), (14, -26), (-14, -26),
        (26, 6), (-26, 6), (0, 14), (0, -22)]

def draw(ax, s, fs=8.5, fig=None):
    sub = sh[sh.strategy == s].reset_index(drop=True)
    ax.fill_between([0, VMAX], [0, VMAX], [VMAX, VMAX], color="#2e8b57", alpha=0.07, zorder=0)
    ax.fill_between([0, VMAX], [0, 0], [0, VMAX], color="#c0392b", alpha=0.07, zorder=0)
    ax.plot([0, VMAX], [0, VMAX], "-", color="#333333", lw=2.0, zorder=2)
    for _, r in sub.iterrows():
        col = LEVEL_COLOR[r.level]
        fc = col if r.gain == "拔高" else "none"
        ax.scatter(r.low_share, r.high_share, s=230, marker=TARGET_MARKER[r.target],
                   c=fc, edgecolors=col, linewidths=2.2, zorder=4)
    ax.set_xlim(0, VMAX); ax.set_ylim(0, VMAX)
    ax.set_xlabel("Low set share (%)", fontsize=12)
    ax.set_ylabel("High set share (%)", fontsize=12)
    ax.grid(True, alpha=0.25)
    ax.set_aspect("equal", adjustable="box")
    return sub

def place(ax, fig, sub, fs=8.5):
    fig.canvas.draw()
    used = []
    for _, r in sub.iterrows():
        done = False
        for dx, dy in OFFS:
            t = ax.annotate(f"{r.thinking_type} (n={r.n_task})", (r.low_share, r.high_share),
                            fontsize=fs, fontweight="bold", color="#111111", zorder=6,
                            xytext=(dx, dy), textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.7))
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
            if not any(bb.overlaps(u) for u in used):
                used.append(bb); done = True; break
            t.remove()
    return

def legend(ax):
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
    ax.legend(handles=h, loc="lower right", fontsize=8.2, framealpha=0.94, ncol=2,
              title="颜色=层级   形状=对象   填充=增益性质", title_fontsize=8.6)

OUT = os.path.join(HERE, "fig_ownset_v2")
os.makedirs(OUT, exist_ok=True)
for s in STRATS:
    fig, ax = plt.subplots(figsize=(10, 8.4))
    sub = draw(ax, s)
    place(ax, fig, sub)
    ax.set_title(f"{s}   （对角线 y=x = plain 基准）", fontsize=13, fontweight="bold")
    legend(ax)
    fig.tight_layout()
    p = os.path.join(OUT, f"{s}.png")
    fig.savefig(p, dpi=200, bbox_inches="tight"); plt.close(fig)
    print("saved", p)

fig, axes = plt.subplots(1, 5, figsize=(33, 7.6), sharex=True, sharey=True)
for ax, s in zip(axes, STRATS):
    sub = draw(ax, s, fs=7)
    place(ax, fig, sub, fs=7)
    ax.set_title(s, fontsize=16, fontweight="bold")
    ax.set_xlabel("Low set share (%)", fontsize=10)
axes[0].set_ylabel("High set share (%)", fontsize=11)
fig.suptitle("v2 thinking types — 每策略 Low/High set share（对角线=plain；颜色=层级，形状=对象，空心/实心=增益性质）",
             fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.93])
p = os.path.join(OUT, "ALL.png")
fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
print("saved", p)
