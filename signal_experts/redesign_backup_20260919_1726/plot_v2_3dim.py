# -*- coding: utf-8 -*-
"""
Final figure set B  (v2 taxonomy, 12 types)  -- one figure per strategy.

  x = Low set share  (%) = strategy's low-count of that type / ALL strategies' low-count of that type
  y = High set share (%) = strategy's high-count of that type / ALL strategies' high-count of that type
  diagonal y = x       = plain baseline (above = 优于 plain, below = 劣于 plain)

The THREE dimensions of a thinking type are carried by three visual channels:
  颜色 colour        = 认知层级 Level        (L1 蓝 / L2 绿 / L3 红)
  形状 marker        = 干预对象 Target       (K ○ / R △ / E □ / F ◇)
  空心/实心 fill     = 增益性质 Nature of Gain
                       实心 = 拔高型  (该类型在全部策略下 被提升的次数 ≥ 被拉低的次数)
                       空心 = 保稳型  (被提升 < 被拉低)
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy_v2 import TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
LEVEL_COLOR = {"L1": "#1f77b4", "L2": "#2ca02c", "L3": "#d62728"}
TARGET_MARKER = {"K": "o", "R": "^", "E": "s", "F": "D"}
LEVEL_LABEL = {"L1": "L1 执行层 Execution", "L2": "L2 结构层 Structure", "L3": "L3 元认知层 Metacognition"}
TARGET_LABEL = {"K": "K 知识 Knowledge", "R": "R 推理 Reasoning",
                "E": "E 表达 Expression", "F": "F 格式 Format"}

# ---------------------------------------------------------------- data
df = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
df["is_high"] = df["set"] == "high"
D_high = df[df.is_high].groupby("thinking_type").size()
D_low = df[~df.is_high].groupby("thinking_type").size()
# 增益性质: r = 提升次数 / (提升+拉低)；以 r 的中位数为界
#   r >= median -> 拔高倾向型(实心)：干预相对更容易在这类任务上见效
#   r <  median -> 保稳倾向型(空心)：干预相对更容易失手
R_GAIN = {t: (D_high.get(t, 0) / max(1, D_high.get(t, 0) + D_low.get(t, 0))) for t in TYPE_IDS}
R_THR = float(np.median(list(R_GAIN.values())))
GAIN_SOLID = {t: bool(R_GAIN[t] >= R_THR) for t in TYPE_IDS}

rows = []
for s in STRATS:
    sub = df[df.strategy == s]
    for t in TYPE_IDS:
        g = sub[sub.thinking_type == t]
        h = int(g.is_high.sum()); l = int((~g.is_high).sum())
        dh = int(D_high.get(t, 0)); dl = int(D_low.get(t, 0))
        rows.append(dict(strategy=s, thinking_type=t, level=ID2LEVEL[t], target=ID2TARGET[t],
                         n_high=h, n_low=l, D_high=dh, D_low=dl,
                         high_share=100 * h / dh if dh else 0.0,
                         low_share=100 * l / dl if dl else 0.0,
                         gain="拔高" if GAIN_SOLID[t] else "保稳"))
sh = pd.DataFrame(rows)
sh.to_csv(os.path.join(HERE, "v2_3dim_shares.csv"), index=False)
VMAX = float(np.ceil(max(sh.high_share.max(), sh.low_share.max()) / 5) * 5) + 5

print("r (提升占比):", {t: round(R_GAIN[t], 3) for t in TYPE_IDS})
print("gain nature (实心=拔高倾向):", [t for t in TYPE_IDS if GAIN_SOLID[t]])
print(VMAX)
SOLID_LIST = "、".join([t for t in TYPE_IDS if GAIN_SOLID[t]])
print("solid:", SOLID_LIST)

# ---------------------------------------------------------------- drawing
def nice_offsets():
    return [(9, 6), (9, -16), (-9, 6), (-9, -16), (9, 20), (-9, 20),
            (9, -28), (-9, -28), (20, 8), (-20, 8), (0, 14), (0, -22)]

def draw(ax, s, fontsize=8.5):
    sub = sh[sh.strategy == s].reset_index(drop=True)
    ax.fill_between([0, VMAX], [0, VMAX], [VMAX, VMAX], color="#2e8b57", alpha=0.07, zorder=0)
    ax.fill_between([0, VMAX], [0, 0], [0, VMAX], color="#c0392b", alpha=0.07, zorder=0)
    ax.plot([0, VMAX], [0, VMAX], "-", color="#333333", lw=2.0, zorder=2)
    pts = []
    for _, r in sub.iterrows():
        col = LEVEL_COLOR[r.level]
        fc = col if r.gain == "拔高" else "none"
        ax.scatter(r.low_share, r.high_share, s=230, marker=TARGET_MARKER[r.target],
                   c=fc, edgecolors=col, linewidths=2.2, zorder=4)
        pts.append((r.low_share, r.high_share, r.thinking_type, r.n_high + r.n_low))
    ax.set_xlim(0, VMAX); ax.set_ylim(0, VMAX)
    ax.set_xlabel("Low set share (%)", fontsize=12)
    ax.set_ylabel("High set share (%)", fontsize=12)
    ax.grid(True, alpha=0.25)
    ax.set_aspect("equal", adjustable="box")
    return pts

def place_labels(ax, fig, pts, fontsize=8.5):
    """greedy non-overlapping label placement in display coords"""
    fig.canvas.draw()
    placed = []
    used = []
    for x, y, lab, n in pts:
        best = None
        for dx, dy in nice_offsets():
            t = ax.annotate(f"{lab} (n={n})", (x, y), fontsize=fontsize, fontweight="bold",
                            color="#111111", zorder=6, xytext=(dx, dy),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
            if not any(bb.overlaps(u) for u in used):
                placed.append(t); used.append(bb); best = t; break
            t.remove()
        if best is None:
            t = ax.annotate(f"{lab} (n={n})", (x, y), fontsize=fontsize, fontweight="bold",
                            color="#111111", zorder=6, xytext=(9, 6), textcoords="offset points")
            placed.append(t)

def legend(ax):
    h = []
    for lv in ["L1", "L2", "L3"]:
        h.append(Line2D([0], [0], marker="o", color="w", markerfacecolor=LEVEL_COLOR[lv],
                        markeredgecolor=LEVEL_COLOR[lv], markersize=11, label=LEVEL_LABEL[lv]))
    for tg in ["K", "R", "E", "F"]:
        h.append(Line2D([0], [0], marker=TARGET_MARKER[tg], color="w", markerfacecolor="none",
                        markeredgecolor="#333333", markeredgewidth=2, markersize=10, label=TARGET_LABEL[tg]))
    h.append(Line2D([0], [0], marker="o", color="w", markerfacecolor="none", markeredgecolor="#333333",
                    markeredgewidth=2, markersize=11, label="保稳倾向（空心）"))
    h.append(Line2D([0], [0], marker="o", color="w", markerfacecolor="#333333",
                    markeredgecolor="#333333", markersize=11, label="拔高倾向（实心）"))
    ax.legend(handles=h, loc="lower right", fontsize=8.2, framealpha=0.94,
              title="维度1 颜色=层级  维度2 形状=对象  维度3 填充=增益性质", title_fontsize=8.6)

OUT = os.path.join(HERE, "fig_v2_3dim")
os.makedirs(OUT, exist_ok=True)

for s in STRATS:
    fig, ax = plt.subplots(figsize=(10, 8.4))
    pts = draw(ax, s)
    place_labels(ax, fig, pts)
    ax.set_title(f"Strategy: {s}\n(对角线 y = x 为 plain 基准；上方优于 plain，下方劣于 plain)",
                 fontsize=13, fontweight="bold")
    legend(ax)
    ax.text(0.02, 0.02, f"增益性质 r = 提升次数/(提升+拉低)，中位数阈值 {R_THR:.3f}；实心=拔高倾向：{SOLID_LIST}\n"
                        f"空心=保稳倾向（其余）；对角线 y = x = plain 基准",
            transform=ax.transAxes, fontsize=7.6, color="#444444", va="bottom")
    fig.tight_layout()
    p = os.path.join(OUT, f"v2_{s}.png")
    fig.savefig(p, dpi=200, bbox_inches="tight"); plt.close(fig)
    print("saved", p)

# combined
fig, axes = plt.subplots(1, 5, figsize=(33, 7.6), sharex=True, sharey=True)
for ax, s in zip(axes, STRATS):
    pts = draw(ax, s, fontsize=7)
    place_labels(ax, fig, pts, fontsize=7)
    ax.set_title(s, fontsize=16, fontweight="bold")
    ax.set_xlabel("Low set share (%)", fontsize=10)
axes[0].set_ylabel("High set share (%)", fontsize=11)
fig.suptitle("v2 thinking types — per-strategy Low/High share   (颜色=层级, 形状=对象, 空心/实心=增益性质; 对角线=plain)",
             fontsize=16)
fig.tight_layout(rect=[0, 0, 1, 0.93])
p = os.path.join(OUT, "v2_ALL.png")
fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
print("saved", p)
