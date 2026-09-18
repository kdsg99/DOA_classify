import matplotlib.pyplot as plt
import numpy as np

# 1. 设置画图风格
plt.style.use('seaborn-v0_8-whitegrid') 
fig, ax = plt.subplots(figsize=(12, 8), dpi=150)

# 2. 准备原始模拟数据 (X轴为分类标签)
x_labels = ['0-.2', '.2-.4', '.4-.6', '.6-.8', '.8-1']
x = np.arange(len(x_labels))

# 原始数据字典
raw_data = {
    'Plain':     [0.03, 0.05, 0.12, -0.05, -0.05],
    'Pressure':  [0.08, 0.20, 0.14, -0.03, -0.09],
    'Critical':  [0.09, 0.29, 0.20, -0.11, -0.27],
    'Heuristic': [0.06, 0.33, 0.07, -0.15, -0.50],
    'Encourage': [0.04, 0.34, 0.08, -0.14, -0.33],
    'Misleading':[0.06, 0.02, 0.13, -0.22, -0.37]
}

# ================= 核心修改：以 Plain 为基准转换数据 =================
bench_values = np.array(raw_data['Plain'])
data = {}
for label, y_vals in raw_data.items():
    # 所有数据减去 Plain 基准的值
    data[label] = np.array(y_vals) - bench_values
# ====================================================================

# 定义颜色
colors = {
    'Plain': '#7f7f7f',      
    'Pressure': '#f28e2b',   
    'Critical': '#d62728',   
    'Heuristic': '#3b73b9',  
    'Encourage': '#59a14f',  
    'Misleading':'#8c6bb1'   
}

# 3. 绘图核心逻辑
lines = []
for label, y_vals in data.items():
    if label == 'Plain':
        # Plain 作为基准，误差带通常设为 0（因为它自己和自己没有差异），或者保留原始误差传递
        error = np.zeros(len(x)) 
    else:
        # 其他曲线保留模拟的误差带
        error = np.random.uniform(0.05, 0.12, size=len(x))
        
    upper_bound = y_vals + error
    lower_bound = y_vals - error
    
    # 画阴影带 (基准线 Plain 的宽度设为 0，看起来就是一条线)
    ax.fill_between(x, lower_bound, upper_bound, color=colors[label], alpha=0.15, edgecolor='none')
    
    # 画主折线
    line, = ax.plot(x, y_vals, label=label, color=colors[label], 
                    marker='o', markersize=7, linewidth=2.5,
                    markeredgecolor='white', markeredgewidth=1.5) 
    lines.append(line)

# 4. 添加参考线 (y=0 代表与 Plain 持平)
ax.axhline(y=0, color='black', linewidth=1.2, alpha=0.8)

# 5. 设置坐标轴和标签 (修改了标题和Y轴标签)
ax.set_xticks(x)
ax.set_xticklabels(x_labels, fontsize=12)
ax.set_xlabel('ORIGINAL score bin (left = harder / lower anchor score)', fontsize=14, labelpad=10)
# Y轴标签改为相对基准
ax.set_ylabel('Score difference relative to Plain (Bench)', fontsize=14, labelpad=10)
# 标题加上 Benchmark 说明
ax.set_title('Difficulty curve relative to Plain Baseline', fontsize=16, loc='left', pad=15)

# 根据数据动态调整Y轴范围（稍微留点白边）
all_vals = np.concatenate([data[k] for k in data.keys()])
ax.set_ylim(np.min(all_vals) - 0.15, np.max(all_vals) + 0.15)

# 6. 调整边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# 7. 定制图例
order = ['Plain', 'Pressure', 'Critical', 'Heuristic', 'Encourage', 'Misleading']
handles = [l for l in lines]
labels = [l.get_label() for l in lines]

sorted_handles_labels = sorted(zip(labels, handles), key=lambda x: order.index(x[0]))
sorted_labels, sorted_handles = zip(*sorted_handles_labels)

ax.legend(sorted_handles, sorted_labels, 
          loc='lower left', 
          ncol=2, 
          frameon=False, 
          fontsize=12,
          columnspacing=1.5,
          handlelength=2.5)

# 8. 显示网格线
ax.grid(axis='y', linestyle='-', alpha=0.3)
ax.grid(axis='x', visible=False)

# ================= 保存图片 =================
plt.savefig('difficulty_curve_relative_to_plain.png', dpi=300, bbox_inches='tight')
# ============================================