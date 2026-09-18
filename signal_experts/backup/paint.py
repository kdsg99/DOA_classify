import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# =========================================================
# 1. 配置：五个策略的 high/low 文件路径
# =========================================================
# 请根据实际情况修改文件名
strategy_files = {
    'PRESSURE':  ('pressure_high.csv',  'pressure_low.csv'),
    # 下面四个请替换成你实际的文件名
    'ENCOURAGE': ('encourage_high.csv', 'encourage_low.csv'),
    'CRITICAL': ('critical_high.csv', 'critical_low.csv'),
    'MISLEADING': ('misleading_high.csv', 'misleading_low.csv'),
    'HEURISTIC': ('heuristic_high.csv', 'heuristic_low.csv'),
}

# =========================================================
# 2. 分类函数
# =========================================================
def classify_thinking_type(row):
    task_text = str(row.get('task', '')) + ' ' + str(row.get('problem', '')) + ' ' + str(row.get('instruction', ''))
    task_text = task_text.lower()
    domain = str(row.get('metadata_domain', '')).lower()

    if any(k in task_text for k in ['critique', 'evaluate', 'review', 'check', 'validate', 'verify', 'correctness', 'confirm']):
        return 'Reviewable repair' if 'review' in task_text or 'critique' in task_text else 'Strict verification'
    if any(k in task_text for k in ['long', 'context', 'document', 'summarize']):
        return 'Long-context fidelity'
    if any(k in task_text for k in ['step-by-step', 'chain', 'trajectory', 'sequence', 'reasoning']):
        return 'Trajectory sensitive'
    if any(k in task_text for k in ['what is', 'who is', 'when', 'where', 'simple fact']) and len(task_text) < 200:
        return 'Plain-answer fragile'
    if any(k in task_text for k in ['json', 'csv', 'table', 'format', 'latex']):
        return 'Format preserving'
    if any(k in task_text for k in ['style', 'tone', 'voice', 'character', 'roleplay', 'pretend']):
        return 'Style preserving'
    if any(k in task_text for k in ['classify', 'identify', 'recognize', 'categorize']):
        return 'Routine recognition'
    if any(k in task_text for k in ['math', 'physics', 'chess', 'prove', 'logic', 'reasoning']) or 'math' in domain:
        return 'Full-reasoning dependent'
    if any(k in task_text for k in ['error', 'bug', 'fix', 'hallucination']):
        return 'Local repair'
    if any(k in task_text for k in ['write', 'blog', 'story', 'essay', 'expand', 'draft']):
        return 'Expression expansion'
    if any(k in task_text for k in ['calculate', 'simple', 'design', 'sudoku']):
        return 'Execution-limited'
    return 'Plain-answer fragile'

# =========================================================
# 3. 读取所有策略数据并合并
# =========================================================
all_dfs = []

for strategy_name, (high_path, low_path) in strategy_files.items():
    if not (os.path.exists(high_path) and os.path.exists(low_path)):
        print(f"[警告] 策略 {strategy_name} 的文件不存在，跳过：{high_path}, {low_path}")
        continue

    h_df = pd.read_csv(high_path)
    l_df = pd.read_csv(low_path)

    h_df['set'] = 'high'
    l_df['set'] = 'low'

    combined = pd.concat([h_df, l_df], ignore_index=True)
    combined['strategy'] = strategy_name   # 用我们自定义的策略名
    all_dfs.append(combined)

df = pd.concat(all_dfs, ignore_index=True)

# 应用分类
df['thinking_type'] = df.apply(classify_thinking_type, axis=1)

# 标记 High / Low / Tie（Tie 保留，但后续计算 High/Low 时不用）
def get_set(row):
    if row['reask_minmax'] > row['plain_minmax']:
        return 'high'
    elif row['reask_minmax'] < row['plain_minmax']:
        return 'low'
    else:
        return 'tie'

df['set'] = df.apply(get_set, axis=1)

# =========================================================
# 4. 计算全局分母：所有策略在某类别下的 High / Low 总数
# =========================================================
global_high = df[df['set'] == 'high'].groupby('thinking_type').size().to_dict()
global_low  = df[df['set'] == 'low'].groupby('thinking_type').size().to_dict()

print("全局 High 分母 (按类别):", global_high)
print("全局 Low  分母 (按类别):", global_low)

# =========================================================
# 5. 计算每个策略的 High Share / Low Share
# =========================================================
strategies = df['strategy'].unique()
results = []

for strategy in strategies:
    strat_df = df[df['strategy'] == strategy]

    for t_type in strat_df['thinking_type'].unique():
        type_df = strat_df[strat_df['thinking_type'] == t_type]

        high_count = len(type_df[type_df['set'] == 'high'])
        low_count  = len(type_df[type_df['set'] == 'low'])
        tie_count  = len(type_df[type_df['set'] == 'tie'])
        total      = len(type_df)

        # 分子 = 该策略在该类别的 high/low 数
        # 分母 = 全局所有策略在该类别的 high/low 总数
        h_denom = global_high.get(t_type, 0)
        l_denom = global_low.get(t_type, 0)

        high_share = high_count / h_denom if h_denom > 0 else 0.0
        low_share  = low_count  / l_denom if l_denom > 0 else 0.0

        results.append({
            'strategy': strategy,
            'thinking_type': t_type,
            'high_share': high_share,
            'low_share': low_share,
            'high_count': high_count,
            'low_count': low_count,
            'tie_count': tie_count,
            'total_tasks': total,
            'global_high_denom': h_denom,
            'global_low_denom': l_denom
        })

results_df = pd.DataFrame(results)
print("\n各策略 High/Low Share 计算结果：")
print(results_df.to_string(index=False))

# 保存结果
results_df.to_csv('all_strategies_thinking_type_shares.csv', index=False)

# =========================================================
# 6. 画图：每个策略一张图
# =========================================================
for strategy in strategies:
    strat_results = results_df[results_df['strategy'] == strategy].copy()
    if len(strat_results) == 0:
        continue

    fig, ax = plt.subplots(figsize=(11, 9))

    # 散点大小代表总任务数
    sizes = strat_results['total_tasks'] * 15

    ax.scatter(strat_results['low_share'], strat_results['high_share'],
               s=sizes, c='steelblue', alpha=0.75,
               edgecolors='black', linewidth=1.5, zorder=3)

    # 标签
    for i, row in strat_results.iterrows():
        ax.annotate(f"{row['thinking_type']}\n(n={row['total_tasks']})",
                    (row['low_share'], row['high_share']),
                    fontsize=8, ha='center', va='center',
                    xytext=(0, 16), textcoords='offset points', zorder=4)

    # y = x 参考线（High Share = Low Share）
    x = np.linspace(0, 1, 100)
    ax.plot(x, x, 'g--', alpha=0.6, linewidth=1.8,
            label='y = x (High Share = Low Share)', zorder=1)

    # 区域标注
    ax.text(0.15, 0.85, '专长区\n(High 高, Low 低)\n主导提升', fontsize=10,
            color='green', alpha=0.7, ha='center', fontweight='bold')
    ax.text(0.85, 0.15, '短板区\n(High 低, Low 高)\n主导下降', fontsize=10,
            color='red', alpha=0.7, ha='center', fontweight='bold')
    ax.text(0.85, 0.85, '高参与区\n(High 高, Low 高)\n既提升也下降', fontsize=9,
            color='purple', alpha=0.7, ha='center')
    ax.text(0.15, 0.15, '低参与区\n(High 低, Low 低)\nTie 为主', fontsize=9,
            color='gray', alpha=0.7, ha='center')

    ax.set_xlabel(f'Low Share (该策略在该类别的下降数 / 所有策略在该类别的下降总数)', fontsize=11)
    ax.set_ylabel(f'High Share (该策略在该类别的提升数 / 所有策略在该类别的提升总数)', fontsize=11)
    ax.set_title(f'Strategy: {strategy}\nThinking Type Distribution (Global Normalization)', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig(f'{strategy}_thinking_type_distribution.png', dpi=300, bbox_inches='tight')