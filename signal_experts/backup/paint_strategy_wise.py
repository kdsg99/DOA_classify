import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. 读取数据
high_df = pd.read_csv('encourage_high.csv')
low_df = pd.read_csv('encourage_low.csv')
df = pd.concat([high_df, low_df], ignore_index=True)

# 2. 分类函数（保持不变）
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

df['thinking_type'] = df.apply(classify_thinking_type, axis=1)

# 3. 标记 High / Low / Tie
def get_set(row):
    if row['reask_minmax'] > row['plain_minmax']:
        return 'high'
    elif row['reask_minmax'] < row['plain_minmax']:
        return 'low'
    else:
        return 'tie'

df['set'] = df.apply(get_set, axis=1)

# 4. 计算每个策略下每个类别的 High/Low Share（分母=该类别全部任务）
strategies = df['mode'].unique()
results = []

for strategy in strategies:
    strat_df = df[df['mode'] == strategy]
    for t_type in strat_df['thinking_type'].unique():
        type_df = strat_df[strat_df['thinking_type'] == t_type]
        total = len(type_df)
        high_count = len(type_df[type_df['set'] == 'high'])
        low_count = len(type_df[type_df['set'] == 'low'])
        tie_count = len(type_df[type_df['set'] == 'tie'])

        results.append({
            'strategy': strategy,
            'thinking_type': t_type,
            'high_share': high_count / total,
            'low_share': low_count / total,
            'tie_share': tie_count / total,
            'high_count': high_count,
            'low_count': low_count,
            'tie_count': tie_count,
            'total_tasks': total
        })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# 5. 画图（加入 y=x 线）
for strategy in strategies:
    strat_results = results_df[results_df['strategy'] == strategy].copy()
    if len(strat_results) == 0:
        continue

    fig, ax = plt.subplots(figsize=(11, 9))

    # 散点
    sizes = strat_results['total_tasks'] * 15
    ax.scatter(strat_results['low_share'], strat_results['high_share'],
               s=sizes, c='steelblue', alpha=0.75, edgecolors='black', linewidth=1.5, zorder=3)

    # 标签
    for i, row in strat_results.iterrows():
        ax.annotate(f"{row['thinking_type']}\n(n={row['total_tasks']})",
                    (row['low_share'], row['high_share']),
                    fontsize=8, ha='center', va='center',
                    xytext=(0, 16), textcoords='offset points', zorder=4)

    # 对角线1: y = 1 - x (Tie=0 边界)
    x = np.linspace(0, 1, 100)
    ax.plot(x, 1 - x, 'r--', alpha=0.5, linewidth=1.5,
            label='y = 1 - x (Tie = 0 边界)', zorder=1)

    # 对角线2: y = x (High = Low，净效果为零)
    ax.plot(x, x, 'g--', alpha=0.6, linewidth=1.8,
            label='y = x (High = Low，净效果为零)', zorder=1)

    # 区域标注
    ax.text(0.20, 0.85, '专长区\n(High > Low)\n净提升', fontsize=10, color='green',
            alpha=0.7, ha='center', fontweight='bold')
    ax.text(0.85, 0.20, '短板区\n(Low > High)\n净下降', fontsize=10, color='red',
            alpha=0.7, ha='center', fontweight='bold')
    ax.text(0.55, 0.45, 'Tie 密集区\n(离 y=1-x 越远\nTie 越多)', fontsize=9, color='gray',
            alpha=0.7, ha='center')

    # 坐标轴与标题
    ax.set_xlabel('Low Set Share (reask < plain)', fontsize=12)
    ax.set_ylabel('High Set Share (reask > plain)', fontsize=12)
    ax.set_title(f'Strategy: {strategy}\nThinking Type Distribution (with y=x and y=1-x boundaries)',
                 fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='upper right', fontsize=10)

    # 加等比例参考，让 y=x 看起来是45度
    ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig(f'{strategy}_thinking_type_distribution.png', dpi=300, bbox_inches='tight')
