import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 1. 读取数据
# =========================================================
df = pd.read_csv('all_tasks_with_thinking_type.csv')

# =========================================================
# 2. 全局分母
# =========================================================
global_high = df[df['set'] == 'high'].groupby('thinking_type').size().to_dict()
global_low  = df[df['set'] == 'low'].groupby('thinking_type').size().to_dict()

# =========================================================
# 3. 计算每个策略的 share
# =========================================================
strategies_list = df['strategy'].unique()
results = []

for strategy in strategies_list:
    strat_df = df[df['strategy'] == strategy]
    for t_type in strat_df['thinking_type'].unique():
        type_df = strat_df[strat_df['thinking_type'] == t_type]
        high_count = len(type_df[type_df['set'] == 'high'])
        low_count  = len(type_df[type_df['set'] == 'low'])
        h_denom = global_high.get(t_type, 0)
        l_denom = global_low.get(t_type, 0)

        results.append({
            'strategy': strategy,
            'thinking_type': t_type,
            'high_share': high_count / h_denom if h_denom else 0,
            'low_share':  low_count  / l_denom if l_denom else 0,
            'high_count': high_count,
            'low_count': low_count,
            'total_tasks': len(type_df),
        })

results_df = pd.DataFrame(results)
results_df.to_csv('all_strategies_thinking_type_shares.csv', index=False)

# =========================================================
# 4. 自动计算统一坐标轴范围
#    - 用分位数（比如 95%）排除极端离群点，避免范围被拉太宽
#    - 再加 10% padding
#    - 范围下限不小于 0，上限不大于 1
# =========================================================
all_x = results_df['low_share'].values
all_y = results_df['high_share'].values

# 用 95 分位数作为上限参考（如果数据里有极端点，不至于把轴拉满）
x_hi_ref = np.percentile(all_x, 95)
y_hi_ref = np.percentile(all_y, 95)

# 但也至少要覆盖最大值的一小部分（保证最大点不被裁掉太多）
x_hi_ref = max(x_hi_ref, all_x.max() * 0.9)
y_hi_ref = max(y_hi_ref, all_y.max() * 0.9)

# 加 10% padding
x_pad = x_hi_ref * 0.10
y_pad = y_hi_ref * 0.10

X_LIM = (0, min(1.0, x_hi_ref + x_pad))
Y_LIM = (0, min(1.0, y_hi_ref + y_pad))

print(f"自动计算的统一坐标轴范围：")
print(f"  X (Low Share) : [{X_LIM[0]:.3f}, {X_LIM[1]:.3f}]")
print(f"  Y (High Share): [{Y_LIM[0]:.3f}, {Y_LIM[1]:.3f}]")
print(f"  （数据实际最大值：Low={all_x.max():.3f}, High={all_y.max():.3f}）")

# =========================================================
# 5. 画 2x3 大图（统一缩放）
# =========================================================
strategy_order = ['PRESSURE', 'ENCOURAGE', 'CRITICAL', 'MISLEADING', 'HEURISTIC']

fig, axes = plt.subplots(2, 3, figsize=(22, 15))
axes = axes.flatten()

for i, strategy in enumerate(strategy_order):
    ax = axes[i]
    strat_results = results_df[results_df['strategy'] == strategy].copy()

    if len(strat_results) == 0:
        ax.set_visible(False)
        continue

    # 散点大小代表总任务数
    sizes = strat_results['total_tasks'] * 15

    ax.scatter(strat_results['low_share'], strat_results['high_share'],
               s=sizes, c='steelblue', alpha=0.75,
               edgecolors='black', linewidth=1.5, zorder=3)

    # 标签
    for _, row in strat_results.iterrows():
        ax.annotate(f"{row['thinking_type']}\n(n={row['total_tasks']})",
                    (row['low_share'], row['high_share']),
                    fontsize=8, ha='center', va='center',
                    xytext=(0, 16), textcoords='offset points', zorder=4)

    # y = x 参考线（只在当前视野内画）
    x_line = np.linspace(X_LIM[0], X_LIM[1], 200)
    y_line = x_line.copy()
    mask = (y_line >= Y_LIM[0]) & (y_line <= Y_LIM[1])
    if mask.any():
        ax.plot(x_line[mask], y_line[mask], 'g--', alpha=0.6,
                linewidth=1.5, label='y = x (High = Low)', zorder=1)

    # 坐标轴设置
    ax.set_xlim(*X_LIM)
    ax.set_ylim(*Y_LIM)
    ax.set_xlabel('Low Share (global-normalized)', fontsize=10)
    ax.set_ylabel('High Share (global-normalized)', fontsize=10)
    ax.set_title(f'{strategy}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=8)
    ax.set_aspect('equal', adjustable='box')

# 隐藏第 6 个空位
axes[5].set_visible(False)

# 总标题
fig.suptitle('Thinking Type Distribution Across 5 Strategies (Unified Zoom)',
             fontsize=18, fontweight='bold', y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.98])
plt.savefig('all_strategies_grid_unified_zoom.png', dpi=250, bbox_inches='tight')
print("已生成大图: all_strategies_grid_unified_zoom.png")