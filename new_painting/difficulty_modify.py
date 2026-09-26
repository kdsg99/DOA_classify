import matplotlib.pyplot as plt
import numpy as np

# 1. 设置画图风格
plt.style.use('seaborn-v0_8-whitegrid') 
fig, ax = plt.subplots(figsize=(12, 8), dpi=150)

# 2. 准备数据 (根据新图的走势估算的相对基准值)
x_labels = ['0-.2', '.2-.4', '.4-.6', '.6-.8', '.8-1']
x = np.arange(len(x_labels))

# 注意：这里的数据已经是减去 Plain 基准后的差值 (Delta)
data = {
    'Pressure':  [0.20, 0.25, 0.05, -0.03, -0.06],
    'Critical':  [0.25, 0.16, 0.15, -0.08, -0.25],
    'Heuristic': [0.21, 0.10, 0.02, -0.15, -0.46],
    'Encourage': [0.14, 0.07, -0.08, -0.13, -0.29],
    'Misleading':[0.16, 0.08, 0.02, -0.19, -0.35]
}

# 颜色映射
colors = {
    'Pressure': '#f28e2b',   # 橙色
    'Critical': '#d62728',   # 红色
    'Heuristic': '#3b73b9',  # 蓝色
    'Encourage': '#59a14f',  # 绿色
    'Misleading':'#8c6bb1'   # 紫色
}

# 3. 绘图核心逻辑
lines_dict = {} # 用于存储线条对象，方便后续自定义图例顺序

for label, y_vals in data.items():
    y_vals = np.array(y_vals)
    
    # 模拟误差带：原图中有些误差带很大，跨越了0线。这里用随机偏移量模拟。
    # 为了视觉接近，把误差带设置得稍微宽一些
    error = np.random.uniform(0.08, 0.15, size=len(x))
    upper_bound = y_vals + error
    lower_bound = y_vals - error
    
    # 画阴影带
    ax.fill_between(x, lower_bound, upper_bound, color=colors[label], alpha=0.15, edgecolor='none')
    
    # 画主折线，保留白边圆点
    line, = ax.plot(x, y_vals, label=label, color=colors[label], 
                    marker='o', markersize=7, linewidth=2.5,
                    markeredgecolor='white', markeredgewidth=1.5) 
    lines_dict[label] = line

# 4. 添加 0 基准线 (代表 PLAIN)
# 原图中这是一条贯穿的深灰色/黑色实线
ax.axhline(y=0, color='#444444', linewidth=1.5, zorder=1)

# 5. 设置坐标轴和标签
ax.set_xticks(x)
ax.set_xticklabels(x_labels, fontsize=12)
ax.set_xlabel('PLAIN score bin (left = harder / lower anchor score)', fontsize=14, labelpad=10)
ax.set_ylabel('Re-ask score – PLAIN score', fontsize=14, labelpad=10)
ax.set_title('Pooled difficulty curve relative to PLAIN', fontsize=16, loc='left', pad=15)

# 设置Y轴范围
ax.set_ylim(-0.65, 0.45)

# 6. 调整边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# 7. 定制图例 (关键：列优先排列)
# Matplotlib 默认是行优先填充图例。为了匹配原图（左列：Pressure, Critical, Heuristic；右列：Encourage, Misleading），
# 我们需要按照 "左1, 右1, 左2, 右2, 左3" 的顺序传入 handles 和 labels。
order_col_major = ['Pressure', 'Encourage', 'Critical', 'Misleading', 'Heuristic']

sorted_handles = [lines_dict[lbl] for lbl in order_col_major]
sorted_labels = order_col_major

ax.legend(sorted_handles, sorted_labels, 
          loc='lower left', 
          ncol=2, 
          frameon=False, 
          fontsize=12,
          columnspacing=1.5,
          handlelength=2.5,
          handletextpad=0.5)

# 8. 显示网格线
ax.grid(axis='y', linestyle='-', alpha=0.3)
ax.grid(axis='x', visible=False)

# ================= 保存图片 =================
plt.savefig('difficulty.png', dpi=300, bbox_inches='tight')
# ============================================
