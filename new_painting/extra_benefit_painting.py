"""
Nature-style plot for Extra Benefit of the Optimized Completer.
(Updated: Added Original baseline for each dataset)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Nature Style Configuration
# ---------------------------------------------------------------------------
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

plt.rcParams.update({
    'font.size': 8,
    'axes.labelsize': 9,
    'axes.titlesize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 7.5,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.major.size': 3.5,
    'ytick.major.size': 3.5,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'savefig.dpi': 300,
    'figure.dpi': 150,
})

# ---------------------------------------------------------------------------
# 2. Data (增加 Original 数据)
# ---------------------------------------------------------------------------
METHODS = ["CoT", "Self-Refine", "Repeat"]
DATASET_NAMES = ["MT-Bench", "flask-hard", "arena-hard", "Math500"]

# 新增：每个数据集的 Original 基线得分
# MT-Bench = 8.9, 其余 = 8.0
ORIGINAL = np.array([8.9, 8.0, 8.0, 8.0])

mt_base  = np.array([8.07, 8.76, 8.25])
mt_final = np.array([8.96, 9.02, 8.93]) 

d2_base  = np.array([7.0, 7.5, 6.5])
d2_extra = np.array([1.5, 1.0, 2.0])
d2_final = d2_base + d2_extra

BASE = np.stack([mt_base, d2_base, d2_base, d2_base])
FINAL = np.stack([mt_final, d2_final, d2_final, d2_final])
EXTRA = FINAL - BASE

N_DATASETS, N_METHODS = BASE.shape

# ---------------------------------------------------------------------------
# 3. Y-axis Compression Logic
# ---------------------------------------------------------------------------
def ydisp(v):
    v = np.asarray(v, dtype=float)
    return np.where(v <= 6.0, v * 0.12, 0.72 + (v - 6.0))

KINK = 6.0
Y_MAX = 10.0

# ---------------------------------------------------------------------------
# 4. Plotting
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 4.5))

xs = np.arange(N_DATASETS)
# 调整偏移量：现在有 4 个位置 (Original + 3 methods)
# 将 Original 放在最左侧
offsets = np.array([-0.32, -0.10, 0.10, 0.32]) 

SHAPES = ["o", "^", "s"]
color_base = "#0C5DA5"   # Deep Blue
color_extra = "#FF2C00"  # Bright Orange/Red
color_orig = "#333333"   # Dark Grey for Original

# --- 绘制 Original 基线 ---
# 使用黑色空心菱形或星形，并在每个数据集下画一条水平虚线
for i in range(N_DATASETS):
    x_orig = xs[i] + offsets[0]
    y_orig = ydisp(ORIGINAL[i])
    
    # 画一条短横线作为参考线
    ax.hlines(y_orig, xs[i] - 0.45, xs[i] + 0.45, 
              colors=color_orig, linestyles='--', lw=0.8, alpha=0.6, zorder=1)
    
    # 绘制 Original 点 (使用空心菱形 'D' 或 星形 '*')
    ax.scatter(x_orig, y_orig, marker='D', s=35, facecolors='none', 
               edgecolors=color_orig, linewidths=1.0, zorder=4)
    
    # 在点上标注数值 (可选，如果太挤可以注释掉)
    ax.text(x_orig, y_orig - 0.12, f"{ORIGINAL[i]:.1f}", 
            ha="center", va="top", fontsize=6.5, color=color_orig)

# --- 绘制方法提升数据 ---
for i in range(N_DATASETS):
    for j in range(N_METHODS):
        x = xs[i] + offsets[j+1]  # 偏移量后移，避开 Original
        b, f = BASE[i, j], FINAL[i, j]
        e = f - b
        
        # 连接虚线
        ax.plot([x, x], [ydisp(b), ydisp(f)], color="#999999",
                lw=0.7, ls="--", zorder=2)
        
        # Base 点 (蓝色)
        ax.scatter(x, ydisp(b), marker=SHAPES[j], s=45, c=color_base,
                   alpha=1.0, edgecolors='white', linewidths=0.5, zorder=3)
        
        # Final 点 (橙色)
        ax.scatter(x, ydisp(f), marker=SHAPES[j], s=55, c=color_extra,
                   alpha=1.0, edgecolors='white', linewidths=0.5, zorder=5)
        
        # 提升量标注
        ax.text(x, ydisp(f) + 0.08, f"+{e:.1f}", 
                ha="center", va="bottom", fontsize=7, color="#333333", fontweight='bold')

# --- 图例 ---
handles = []
# 添加 Original 图例
handles.append(ax.scatter([], [], marker='D', s=35, facecolors='none', 
                          edgecolors=color_orig, linewidths=1.0, label="Original"))

# 添加方法图例
for j, (name, shape) in enumerate(zip(METHODS, SHAPES)):
    handles.append(ax.scatter([], [], marker=shape, s=45, c=color_base,
                              edgecolors='white', linewidths=0.5, label=f"{name} (base)"))
                              
handles.append(ax.scatter([], [], marker="o", s=55, c=color_extra,
                          edgecolors='white', linewidths=0.5, label="Optimized (final)"))

# 图例排版：调整列数，无边框
ax.legend(handles=handles, loc="upper left", frameon=False, ncol=3, 
          handletextpad=0.2, columnspacing=0.8, borderaxespad=0.5)

# --- 坐标轴与网格 ---
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

tick_vals = list(range(1, 11))
ax.set_yticks([ydisp(v) for v in tick_vals])
ax.set_yticklabels([str(v) for v in tick_vals])
ax.set_ylim(-0.15, ydisp(Y_MAX) + 0.7)
ax.set_xlim(-0.6, N_DATASETS - 1 + 0.6)

ax.set_xticks(xs)
ax.set_xticklabels(DATASET_NAMES, fontsize=8.5, fontweight='bold')

# X 轴下方的标签调整
# Original 标签放最左，方法标签依次排列
x_labels = ["Orig"] + ["CoT", "SR", "Rep"]
for i in range(N_DATASETS):
    for j, name in enumerate(x_labels):
        ax.text(xs[i] + offsets[j], -0.38, name, ha="center", va="top",
                fontsize=7, color="#555555")

# 压缩分界线
ax.axhline(ydisp(KINK), color="#CCCCCC", lw=0.8, ls=":", zorder=1)
ax.text(N_DATASETS - 0.5, ydisp(KINK) + 0.05,
        "score=6 (low range compressed)",
        ha="right", va="bottom", fontsize=7, color="#777777", style='italic')

ax.set_ylabel("Score (1-10)", fontsize=9)
ax.grid(False)

fig.tight_layout()

# 保存
out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "extra_benefit_nature_with_original.png")
fig.savefig(out_path, bbox_inches="tight")
print(f"saved -> {out_path}")