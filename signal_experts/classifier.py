import pandas as pd
import json
import os
import time
import hashlib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# =========================================================
# 1. 配置 API
# =========================================================
client = OpenAI(
    api_key="sk-578ed37fee7a4bbbb8770dd3f94c44f5",   # 或直接写死
    base_url="https://api.deepseek.com",       # 换成你的供应商
)
MODEL_NAME = "deepseek-v4-flash"   # 建议用便宜且稳定的模型做分类


# =========================================================
# 2. 缓存目录
# =========================================================
CACHE_DIR = "llm_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def cache_key(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def load_cache(key: str):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(key: str, value):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False)

# =========================================================
# 3. System Prompt
# =========================================================
SYSTEM_PROMPT = """你是一位专业的认知任务分类专家。你的任务是把一个给定的任务（task/problem/instruction）归类到 12 种 Thinking Type 中的**唯一一个**。

【12 种 Thinking Type 定义】

1. Local repair（局部修复）
   - 针对具体的错误、bug、幻觉进行修补。
   - 关键词：error, bug, fix, hallucination, identify the error, correct the mistake

2. Execution-limited（受限执行）
   - 执行简单明确的操作，但可能受资源/算力限制。
   - 关键词：calculate, design, simple, sudoku, basic arithmetic

3. Reviewable repair（可审查修复）
   - 需要审查、评价、批判并给出修改建议。
   - 关键词：critique, evaluate, review, assess, feedback

4. Expression expansion（表达扩展）
   - 扩展内容、写长文、创作性表达。
   - 关键词：write, blog, story, essay, expand, draft, compose

5. Routine recognition（常规识别）
   - 模式匹配、分类、识别。
   - 关键词：classify, identify, recognize, categorize, match

6. Full-reasoning dependent（全推理依赖）
   - 需要多步复杂推理，依赖完整推理链。
   - 关键词：math, physics, chess, prove, logic, reasoning, multi-step

7. Strict verification（严格验证）
   - 验证正确性、确认事实、校验结果。
   - 关键词：verify, correctness, confirm, validate, fact-check

8. Format preserving（格式保持）
   - 需要保持特定输出格式。
   - 关键词：JSON, CSV, table, format, LaTeX, markdown

9. Style preserving（风格保持）
   - 需要保持特定风格、语气、人设。
   - 关键词：style, tone, voice, character, roleplay, pretend, persona

10. Long-context fidelity（长文本保真）
    - 需要处理长上下文，保持信息一致。
    - 关键词：long, context, document, summarize, multi-turn, long passage

11. Trajectory sensitive（轨迹敏感）
    - 需要保持推理轨迹、步骤顺序。
    - 关键词：step-by-step, chain, trajectory, sequence, reasoning path

12. Plain-answer fragile（纯答案脆弱）
    - 直接给出简单事实性答案，不需要复杂推理。
    - 关键词：what is, who is, when, where, simple fact

【优先级规则】
如果一个任务同时符合多个类别，按以下优先级选择**唯一**类别：
元认知层（3, 7, 10, 11, 12） > 结构层（6, 8, 9, 5） > 执行层（1, 4, 2）

【输出格式】
只输出一个 JSON 对象，不要有任何其他文字：
{"thinking_type": "<类别英文名>"}
"""

# =========================================================
# 4. 单条分类函数
# =========================================================
VALID_TYPES = {
    "Local repair", "Execution-limited", "Reviewable repair",
    "Expression expansion", "Routine recognition", "Full-reasoning dependent",
    "Strict verification", "Format preserving", "Style preserving",
    "Long-context fidelity", "Trajectory sensitive", "Plain-answer fragile"
}

def classify_one(row, max_retries=3):
    user_prompt = f"""请对以下任务进行分类：

【task】
{str(row.get('task', ''))[:2000]}

【problem】
{str(row.get('problem', ''))[:2000]}

【instruction】
{str(row.get('instruction', ''))[:1000]}

【metadata_skill】
{row.get('metadata_skill', '')}

【metadata_domain】
{row.get('metadata_domain', '')}
"""

    key = cache_key(SYSTEM_PROMPT + user_prompt)
    cached = load_cache(key)
    if cached:
        return cached["thinking_type"]

    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content
            parsed = json.loads(content)
            t_type = parsed.get("thinking_type", "").strip()

            # 校验
            if t_type not in VALID_TYPES:
                # 尝试模糊匹配
                for v in VALID_TYPES:
                    if v.lower() in t_type.lower():
                        t_type = v
                        break
                else:
                    t_type = "Plain-answer fragile"  # 回退

            result = {"thinking_type": t_type}
            save_cache(key, result)
            return t_type

        except Exception as e:
            print(f"[重试 {attempt+1}] 错误: {e}")
            time.sleep(2 ** attempt)

    # 全部失败 -> 回退到规则分类
    return fallback_rule_classify(row)


# =========================================================
# 5. 回退规则（可选，防止 API 全挂）
# =========================================================
def fallback_rule_classify(row):
    task_text = str(row.get('task', '')) + ' ' + str(row.get('problem', '')) + ' ' + str(row.get('instruction', ''))
    task_text = task_text.lower()
    if any(k in task_text for k in ['error', 'bug', 'fix', 'hallucination']):
        return 'Local repair'
    if any(k in task_text for k in ['json', 'csv', 'table', 'format', 'latex']):
        return 'Format preserving'
    if any(k in task_text for k in ['math', 'physics', 'chess', 'prove']):
        return 'Full-reasoning dependent'
    if any(k in task_text for k in ['write', 'blog', 'story', 'essay']):
        return 'Expression expansion'
    return 'Plain-answer fragile'


# =========================================================
# 6. 批量并发分类
# =========================================================
def batch_classify(df, max_workers=8):
    results = [None] * len(df)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(classify_one, row): idx
            for idx, row in df.iterrows()
        }
        for fut in tqdm(as_completed(futures), total=len(futures), desc="LLM 分类中"):
            idx = futures[fut]
            try:
                results[idx] = fut.result()
            except Exception as e:
                print(f"行 {idx} 分类失败: {e}")
                results[idx] = "Plain-answer fragile"
    return results


# =========================================================
# 7. 主流程：读取所有策略数据 -> 分类 -> 保存
# =========================================================
strategy_files = {
    'PRESSURE':  ('pressure_high.csv',  'pressure_low.csv'),
    'ENCOURAGE': ('encourage_high.csv', 'encourage_low.csv'),
    'CRITICAL': ('critical_high.csv', 'critical_low.csv'),
    'MISLEADING': ('misleading_high.csv', 'misleading_low.csv'),
    'HEURISTIC': ('heuristic_high.csv', 'heuristic_low.csv'),
}

all_dfs = []
for strategy_name, (high_path, low_path) in strategy_files.items():
    h_df = pd.read_csv(high_path); h_df['set'] = 'high'
    l_df = pd.read_csv(low_path);  l_df['set'] = 'low'
    combined = pd.concat([h_df, l_df], ignore_index=True)
    combined['strategy'] = strategy_name
    all_dfs.append(combined)

df = pd.concat(all_dfs, ignore_index=True)
print(f"总任务数: {len(df)}")

# 去重：同一任务可能在 high/low 中出现两次，但内容是相同的，
# 我们只需要对唯一任务分类一次（缓存也会自动去重）
df['thinking_type'] = batch_classify(df)

# 保存带分类的完整数据
df.to_csv('all_tasks_with_thinking_type.csv', index=False)
print("分类完成，已保存到 all_tasks_with_thinking_type.csv")