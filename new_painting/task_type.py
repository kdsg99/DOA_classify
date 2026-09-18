import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ==========================================
# 1. 数据准备 (已修正 AIME 数据)
# ==========================================
data = {
    'Dataset': ['MT-Bench', 'Flask-Hard', 'Wild-Bench', 'MATH500', 'OlympiadBench', 'AIME'],
    'Logic_Content': ['0%', '10%', '20%', '100%\n(MATH500)', '100%\n(Olympiad)', '100%\n(AIME)'],
    'Pressure':   [8.122, 2.926, 7.457, 0.588, 0.165, 0.100],
    'Critical':   [7.411, 2.841, 5.853, 0.426, 0.127, 0.067],
    'Encourage':  [7.6244, 2.819, 4.553, 0.324, 0.055, 0.033], 
    'Misleading': [6.367, 2.651, 4.586, 0.370, 0.106, 0.067],  
    'Heuristic':  [7.333, 2.671, 4.344, 0.136, 0.051, 0.033]
}

df = pd.DataFrame(data)

# 计算每个数据集下，5个 signal 的排名 (1为最高，5为最低)
signals = ['Pressure', 'Critical', 'Encourage', 'Misleading', 'Heuristic']
df_ranks = df[signals].rank(axis=1, ascending=False)

# 将排名和数据集名称合并
df_ranks['Dataset'] = df['Dataset']
df_ranks['Logic_Content'] = df['Logic_Content']

# ==========================================
# 2. Nature 风格绘图设置
# ==========================================
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False 

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

# --- 策略颜色映射 (你要求的颜色) ---
colors = {
    'Pressure': '#F28E2B',    # 橙色
    'Critical': '#E15759',    # 红色
    'Encourage': '#59A14F',   # 绿色 (重点)
    'Misleading': '#B07AA1',  # 紫色 (重点)
    'Heuristic': '#4E79A7'    # 蓝色
}

# --- 数据集形状映射 (你要求的形状) ---
# 注意：matplotlib 没有直接的"灵性"形状，使用星形 '*' 或菱形 'D' 作为替代，这里选用菱形
markers_by_dataset = {
    'MT-Bench': 's',        # 方形 (Square)
    'Flask-Hard': '^',      # 三角形 (Triangle)
    'Wild-Bench': 'D',      # 菱形 (Diamond，示意灵性)
    'MATH500': 'o',         # 圆形 (Circle)
    'OlympiadBench': 'o',   # 圆形 (Circle)
    'AIME': 'o'             # 圆形 (Circle)
}

# --- 突出显示设置 ---
# 重点策略：加粗、不透明、大标记
highlight_signals = ['Encourage', 'Misleading']
# 背景策略：细线、低透明度、小标记
background_signals = ['Pressure', 'Critical', 'Heuristic']

# ==========================================
# 3. 绘制图形
# ==========================================
x = np.arange(len(df_ranks)) # 离散的 x 坐标：0, 1, 2, 3, 4, 5

# 先画背景策略 (降低视觉干扰)
for signal in background_signals:
    y = df_ranks[signal].values
    ax.plot(x, y, 
            color=colors[signal], 
            linewidth=1.5, 
            alpha=0.35,       # 低透明度
            zorder=2)         # 图层靠下
    
    # 背景策略的标记需要按数据集形状单独画
    for i, dataset in enumerate(df_ranks['Dataset']):
        ax.scatter(x[i], y[i], 
                   marker=markers_by_dataset[dataset], 
                   s=40,                # 小标记
                   color=colors[signal], 
                   alpha=0.35, 
                   edgecolor='white', 
                   linewidth=0.5, 
                   zorder=2)

# 再画重点策略 (覆盖在上方)
for signal in highlight_signals:
    y = df_ranks[signal].values
    ax.plot(x, y, 
            color=colors[signal], 
            linewidth=4.0,    # 加粗线条
            alpha=0.95, 
            zorder=5)         # 图层靠上
    
    # 重点策略的标记
    for i, dataset in enumerate(df_ranks['Dataset']):
        ax.scatter(x[i], y[i], 
                   marker=markers_by_dataset[dataset], 
                   s=120,               # 大标记
                   color=colors[signal], 
                   edgecolor='white',   # 白边更清晰
                   linewidth=1.5, 
                   zorder=5)

# ==========================================
# 4. 添加标签
# ==========================================
# 在所有点的旁边添加策略名称（起点和终点）
for signal in signals:
    y = df_ranks[signal].values
    
    # 起点标签
    ax.text(x[0] - 0.15, y[0], signal, 
            fontsize=12 if signal in highlight_signals else 10, 
            fontweight='bold' if signal in highlight_signals else 'normal', 
            color=colors[signal], 
            alpha=0.95 if signal in highlight_signals else 0.6,
            ha='right', va='center')
    
    # 终点标签 (为了避免重叠，略微错开)
    offset = 0
    if signal == 'Pressure': offset = 0.15
    if signal == 'Critical': offset = -0.15
    if signal == 'Heuristic': offset = 0.1
    if signal == 'Misleading': offset = 0.1
    if signal == 'Encourage': offset = -0.1
    
    ax.text(x[-1] + 0.15, y[-1] + offset, signal, 
            fontsize=12 if signal in highlight_signals else 10, 
            fontweight='bold' if signal in highlight_signals else 'normal', 
            color=colors[signal], 
            alpha=0.95 if signal in highlight_signals else 0.6,
            ha='left', va='center')

# ==========================================
# 5. 坐标轴和网格美化 (Nature 风格)
# ==========================================
# 设置纵轴 (排名)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_ylim(5.5, 0.5) # 反转 Y 轴，使 Rank 1 在最上方
ax.set_ylabel('Rank (1 = Highest Score)', fontsize=13, fontweight='bold', labelpad=12)
ax.tick_params(axis='y', labelsize=11, length=0) # 隐藏刻度线

# 设置横轴 (离散的 6 个数据集)
ax.set_xticks(x)
ax.set_xticklabels(df_ranks['Logic_Content'], fontsize=11)
ax.set_xlabel('Logic Content in Dataset', fontsize=13, fontweight='bold', labelpad=12)
ax.set_xlim(-0.8, len(df_ranks) - 0.2)

# 添加水平虚线网格，辅助看排名
for y_val in [1, 2, 3, 4, 5]:
    ax.axhline(y=y_val, color='#E0E0E0', linestyle='--', linewidth=1, zorder=1)

# 隐藏顶部和右侧的边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.2)

# 添加一条垂直虚线，分隔低逻辑含量和高逻辑含量
ax.axvline(x=2.5, color='#888888', linestyle=':', linewidth=1.5, alpha=0.5)
ax.text(2.55, 0.3, 'High Logic Content', fontsize=10, color='#888888', fontstyle='italic')

plt.tight_layout()
plt.savefig('nature_style_ranking_final.png', dpi=300, bbox_inches='tight')