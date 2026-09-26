import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

# 1. 定义12个Thinking Type的三维属性 (这是固定不变的)
# 格式: label: (维度一_层级, 维度二_对象, 维度三_是否保稳)
# 层级: 1=执行(蓝), 2=结构(绿), 3=元认知(红)
# 对象: 1=目标知识(圆), 2=过程逻辑(三角), 3=结果质量(正方)
# 是否保稳: True=空心(保稳), False=实心(拔高)
dimensions = {
    'LR': (1, 1, True), 'ES': (1, 2, True), 'RV': (3, 3, False),
    'EE': (1, 1, False), 'RR': (2, 2, False), 'FR': (2, 2, True),
    'SV': (3, 3, True), 'FP': (2, 3, True), 'SP': (2, 3, True),
    'LC': (3, 1, False), 'TP': (3, 2, False), 'PF': (3, 3, True)
}

# 2. 定义5种策略下的坐标数据 (格式: 策略名: {标签: (x, y)})
# 注意：这里的坐标是根据你提供的拼图粗略估算的
data_by_strategy = {
    'PRESSURE': {
        'LR': (1.5, 1.5), 'ES': (21.5, 20.5), 'RV': (5.5, 10.5),
        'EE': (1.0, 0.8), 'RR': (8.0, 12.0), 'FR': (14.5, 15.0),
        'SV': (6.0, 3.5), 'FP': (13.5, 5.5), 'SP': (11.5, 10.5),
        'LC': (6.5, 8.5), 'TP': (4.5, 3.0), 'PF': (11.5, 9.5)
    },
    'CRITICAL': {
        'LR': (1.5, 1.5), 'ES': (8.0, 21.5), 'RV': (5.0, 8.5),
        'EE': (1.0, 0.8), 'RR': (12.5, 12.5), 'FR': (23.0, 11.0),
        'SV': (4.5, 4.5), 'FP': (9.0, 5.5), 'SP': (7.0, 12.0),
        'LC': (3.5, 9.0), 'TP': (4.0, 3.0), 'PF': (8.0, 4.5)
    },
    'ENCOURAGE': {
        'LR': (3.5, 3.0), 'ES': (9.5, 22.0), 'RV': (6.5, 8.0),
        'EE': (1.5, 1.5), 'RR': (17.0, 10.0), 'FR': (28.0, 18.0),
        'SV': (5.5, 7.5), 'FP': (9.5, 5.0), 'SP': (8.5, 10.5),
        'LC': (4.5, 8.5), 'TP': (3.0, 2.5), 'PF': (10.0, 8.0)
    },
    'HEURISTIC': {
        'LR': (4.0, 3.0), 'ES': (9.0, 21.5), 'RV': (7.5, 8.5),
        'EE': (1.0, 1.0), 'RR': (18.5, 9.0), 'FR': (34.5, 13.0),
        'SV': (5.0, 8.0), 'FP': (8.0, 6.0), 'SP': (8.5, 12.0),
        'LC': (3.0, 5.5), 'TP': (4.5, 4.0), 'PF': (7.0, 7.5)
    },
    'MISLEADING': {
        'LR': (1.5, 1.5), 'ES': (9.0, 28.0), 'RV': (6.0, 8.0),
        'EE': (1.0, 0.8), 'RR': (18.0, 10.0), 'FR': (25.0, 16.0),
        'SV': (6.5, 4.5), 'FP': (9.0, 5.5), 'SP': (8.5, 14.5),
        'LC': (3.0, 6.5), 'TP': (4.0, 3.5), 'PF': (11.0, 5.0)
    }
}

# 3. 设置视觉编码映射
level_colors = {1: '#1f77b4', 2: '#2ca02c', 3: '#d62728'} # 蓝, 绿, 红
target_shapes = {1: 'o', 2: '^', 3: 's'} # 圆, 三角, 正方
strategies = list(data_by_strategy.keys())

# 4. 创建画布 (1行5列)
fig, axes = plt.subplots(1, 5, figsize=(25, 6), sharey=True, sharex=True)

# 5. 循环绘制每个子图
for i, strategy in enumerate(strategies):
    ax = axes[i]
    
    # 画对角线
    ax.plot([0, 35], [0, 35], color='#5b9bd5', linewidth=2, zorder=1)
    
    # 画散点
    for label, (x, y) in data_by_strategy[strategy].items():
        level, target, is_stable = dimensions[label]
        color = level_colors[level]
        shape = target_shapes[target]
        
        # 设置填充
        face_color = 'none' if is_stable else color
        
        # 绘制点
        ax.scatter(x, y, c=face_color, marker=shape, s=180, 
                   edgecolors=color, linewidth=2.5, zorder=3)
        
        # 添加标签文字 (微调偏移量)
        # 针对容易重叠的区域做特殊处理
        offset_y = -2.0 if label in ['ES', 'LR', 'EE'] else 1.5
        if label == 'FR' and strategy == 'HEURISTIC':
             offset_y = -2.0
             
        ax.text(x, y + offset_y, label, fontsize=10, ha='center', va='center', color='#333333', zorder=4)

    # 设置每个子图的样式
    ax.set_xlim(0, 35)
    ax.set_ylim(0, 35)
    ax.set_xlabel('Low set share (%)', fontsize=11)
    if i == 0:
        ax.set_ylabel('High set share (%)', fontsize=11)
        
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.tick_params(axis='both', which='major', labelsize=10, width=1.5)
    
    # 设置子图标题
    ax.set_title(f'{strategy}', fontsize=14, fontweight='bold', loc='left')

# 6. 构建全局图例 (只放在最右侧)
legend_colors = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=level_colors[1], markersize=10, label='Layer 1: Execution (执行层)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=level_colors[2], markersize=10, label='Layer 2: Structural (结构层)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=level_colors[3], markersize=10, label='Layer 3: Metacognitive (元认知层)')
]
legend_shapes = [
    Line2D([0], [0], marker='o', color='k', markerfacecolor='none', markersize=8, label='Target: Goal & Knowledge (目标知识)'),
    Line2D([0], [0], marker='^', color='k', markerfacecolor='none', markersize=8, label='Target: Process & Logic (过程逻辑)'),
    Line2D([0], [0], marker='s', color='k', markerfacecolor='none', markersize=8, label='Target: Output & Quality (结果质量)')
]
legend_fill = [
    Line2D([0], [0], marker='o', color='k', markerfacecolor='none', markeredgewidth=2, markersize=10, label='Defensive (基线保稳-空心)'),
    Line2D([0], [0], marker='o', color='k', markerfacecolor='k', markersize=10, label='Offensive (性能拔高-实心)')
]

# 将图例放置在最后一个子图的右侧
l1 = axes[-1].legend(handles=legend_colors, title='Dim 1: Operation Level', loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)
axes[-1].add_artist(l1)
l2 = axes[-1].legend(handles=legend_shapes, title='Dim 2: Target', loc='upper left', bbox_to_anchor=(1.05, 0.75), fontsize=10)
axes[-1].add_artist(l2)
l3 = axes[-1].legend(handles=legend_fill, title='Dim 3: Nature of Gain', loc='upper left', bbox_to_anchor=(1.05, 0.5), fontsize=10)

plt.tight_layout()
# 调整子图间距，给右侧图例留出空间
fig.subplots_adjust(right=0.85, wspace=0.15)
plt.savefig('reasoning_style_all.png', dpi=300, bbox_inches='tight')