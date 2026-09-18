#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务完成器得分分布示意图（Nature 风格 · 提升/下降双色编码版）

核心改动：
  - Task Completer 比 Origin 提高的点 → 亮橙菱形 (#E64B35)
  - Task Completer 比 Origin 降低的点 → 靛蓝菱形 (#3C5488)
  - 离群点（4-6分）→ 深紫圆形 (#5B2C6F)，保持独立
  - 相同分数的点（提升=0）也归入"提升"色（或单独处理，见代码注释）
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Nature 风格全局设置
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#333333",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})

# ---------------------------------------------------------------------------
# 一、模拟数据
# ---------------------------------------------------------------------------
N = 166
SCORE_MIN, SCORE_MAX = 0.0, 10.0
rng = np.random.default_rng(42)

INIT_COUNTS = {1: 2, 2: 2, 3: 2, 4: 2, 5: 9, 6: 2, 7: 10, 8: 65, 9: 35, 10: 37}
UP_COUNTS = {4: 1, 5: 3, 6: 2, 7: 15, 8: 39, 9: 27, 10: 79}

def make_scores(counts, seed):
    arr = []
    for score, cnt in counts.items():
        arr.extend([score] * cnt)
    r = np.random.default_rng(seed)
    r.shuffle(arr)
    return np.asarray(arr, dtype=float)

initial = make_scores(INIT_COUNTS, seed=101)
upgraded = make_scores(UP_COUNTS, seed=202)

# ---------------------------------------------------------------------------
# 二、Nature 风格配色
# ---------------------------------------------------------------------------
C_ORIGIN   = "#8C8C8C"   # 中性灰
C_UP       = "#E64B35"   # NPG 亮橙（提升）
C_DOWN     = "#3C5488"   # NPG 靛蓝（下降）
C_OUTLIER  = "#5B2C6F"   # 深紫（离群点）
C_BAND     = "#7FB3D5"   # 低饱和天蓝（稳定带）
C_AXIS     = "#333333"

# ---------------------------------------------------------------------------
# 三、分类：判断每个点是提升、下降还是不变
# ---------------------------------------------------------------------------
diff = upgraded - initial

# 提升：upgraded > initial
mask_up = diff > 0
# 下降：upgraded < initial
mask_down = diff < 0
# 不变：diff == 0
mask_same = diff == 0

# 离群点（Task Completer 在 4-6 之间）
mask_outlier = (upgraded >= 4) & (upgraded < 7)

# 打印统计，便于核对
print(f"提升点数 (Task > Origin) : {mask_up.sum()}")
print(f"下降点数 (Task < Origin) : {mask_down.sum()}")
print(f"不变点数 (Task = Origin) : {mask_same.sum()}")
print(f"离群点数 (4-6)         : {mask_outlier.sum()}")

# ---------------------------------------------------------------------------
# 四、画图
# ---------------------------------------------------------------------------
x = np.arange(1, N + 1)
OFFSET = 0.15
xj_origin = x - OFFSET + rng.uniform(-0.09, 0.09, N)
xj_task   = x + OFFSET + rng.uniform(-0.09, 0.09, N)

INIT_MEAN, INIT_STD = initial.mean(), initial.std()
UP_MEAN, UP_STD = upgraded.mean(), upgraded.std()
UP_MEAN_T, UP_STD_T = 8.92, 1.02

fig, ax = plt.subplots(figsize=(8.5, 5.5))

# ---------- 稳定带 ----------
lo_band = max(SCORE_MIN, UP_MEAN_T - 2 * UP_STD_T)   # 6.88
hi_band = min(SCORE_MAX, UP_MEAN_T + 2 * UP_STD_T)   # 10.0
ax.axhspan(lo_band, hi_band, color=C_BAND, alpha=0.15, zorder=0,
           label=f"Task Completer stable range (μ±2σ)")

# ---------- 均值线 ----------
ax.axhline(INIT_MEAN, color=C_ORIGIN, linestyle="--", linewidth=1.0, zorder=1)
ax.axhline(UP_MEAN, color=C_UP, linestyle="--", linewidth=1.3, zorder=1)

# ---------- Origin 散点（灰色正方形） ----------
ax.scatter(xj_origin, initial, s=16, alpha=0.55, c=C_ORIGIN,
           marker='s', edgecolors="none",
           label=f"Origin (mean = {INIT_MEAN:.2f})", zorder=2)

# ---------- Task Completer 散点（按提升/下降/不变分类着色） ----------
# 先画离群点（紫色圆形，覆盖在菱形之上，确保可见）
outlier_not_up = mask_outlier & ~mask_up   # 离群点里非提升的部分（下降或不变）
outlier_up     = mask_outlier & mask_up    # 离群点里提升的部分

# 提升的离群点：用橙色圆（表示"提升"，但形状还是圆）
ax.scatter(xj_task[outlier_up], upgraded[outlier_up], s=30, alpha=1.0,
           c=C_UP, marker='o', edgecolors="white", linewidth=0.5,
           label="Outliers ↑", zorder=5)

# 未提升的离群点：用紫色圆
ax.scatter(xj_task[outlier_not_up], upgraded[outlier_not_up], s=30, alpha=1.0,
           c=C_OUTLIER, marker='o', edgecolors="white", linewidth=0.5,
           label="Outliers (4–6)", zorder=5)

# 非离群点：按提升/下降/不变着色（菱形）
normal_mask = ~mask_outlier

# 提升（橙色菱形）
ax.scatter(xj_task[normal_mask & mask_up], upgraded[normal_mask & mask_up],
           s=20, alpha=0.92, c=C_UP, marker='D',
           edgecolors="white", linewidth=0.4,
           label=f"Improved ({mask_up.sum()})", zorder=3)

# 下降（靛蓝菱形）
ax.scatter(xj_task[normal_mask & mask_down], upgraded[normal_mask & mask_down],
           s=20, alpha=0.92, c=C_DOWN, marker='D',
           edgecolors="white", linewidth=0.4,
           label=f"Degraded ({mask_down.sum()})", zorder=3)

# 不变（浅灰菱形，可选，如果你想区分"没变"的点）
if mask_same.sum() > 0:
    ax.scatter(xj_task[normal_mask & mask_same], upgraded[normal_mask & mask_same],
               s=20, alpha=0.92, c="#B0B0B0", marker='D',
               edgecolors="white", linewidth=0.4,
               label=f"Unchanged ({mask_same.sum()})", zorder=3)

# ---------- 文字标注 ----------
ax.text(1.2, INIT_MEAN - 0.42, f"Origin μ = {INIT_MEAN:.2f}",
        color=C_ORIGIN, fontsize=8.5, va="top")
ax.text(1.2, UP_MEAN + 0.18, f"Task Completer μ = {UP_MEAN:.2f}",
        color=C_UP, fontsize=8.5, va="bottom")

ax.text(N + 1, lo_band, f"{lo_band:.2f} (μ-2σ)",
        color="#4A7FA5", fontsize=8, va="center", ha="left")
ax.text(N + 1, hi_band, f"{hi_band:.2f} (μ+2σ)",
        color="#4A7FA5", fontsize=8, va="center", ha="left")

# ---------- 坐标轴与格式 ----------
ax.set_xlim(0, N + 6)
ax.set_ylim(SCORE_MIN - 0.3, SCORE_MAX + 0.5)
ax.set_yticks(np.arange(0, 11, 2))
ax.set_yticks(np.arange(1, 11, 2), minor=True)
ax.set_xlabel("Data index", fontsize=9)
ax.set_ylabel("Score (0–10)", fontsize=9)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.grid(axis="y", alpha=0.18, linestyle=":", linewidth=0.6, color="#999999", zorder=0)

# 图例：无边框、两列
ax.legend(loc="lower left", fontsize=7.5, ncol=2,
          handletextpad=0.4, columnspacing=0.9,
          borderpad=0.3, labelspacing=0.3,
          framealpha=0.0)

ax.set_title(f"Score distribution: Origin vs Task Completer (N = {N})",
             fontsize=10, color=C_AXIS, pad=8)

fig.tight_layout()

# 保存
out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "task_completer_scores.png")
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"saved -> {out_path}")