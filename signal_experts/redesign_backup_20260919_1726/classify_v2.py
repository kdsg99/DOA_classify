# -*- coding: utf-8 -*-
"""
Redesigned task classifier (v2).

Reads raw_data/{strategy}_{high,low}.csv, classifies every *unique* task into one
of the 12 Thinking Types defined in taxonomy_v2.py, then writes
all_tasks_v2.csv (all 2801 rows, each carrying its thinking type + level + target).

Cache key includes PROMPT_VERSION, so changing the prompt automatically invalidates
the old cache (the previous run's cache is left untouched).
"""
import os, sys, json, time, hashlib, re
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy_v2 import TYPES, TYPE_IDS, ID2EN, ID2ZH, ID2LEVEL, ID2TARGET

HERE = os.path.dirname(os.path.abspath(__file__))
SE   = os.path.dirname(HERE)                      # .../signal_experts
RAW  = os.path.join(SE, "raw_data")
OUT_CSV = os.path.join(HERE, "all_tasks_v2.csv")
CACHE_DIR = os.path.join(HERE, "cache_v2")
os.makedirs(CACHE_DIR, exist_ok=True)

PROMPT_VERSION = "v2.0"

client = OpenAI(api_key="sk-578ed37fee7a4bbbb8770dd3f94c44f5",
                base_url="https://api.deepseek.com")
MODEL_NAME = "deepseek-v4-flash"

# =========================================================
# System prompt
# =========================================================
SYSTEM_PROMPT = """你是一位认知任务分类专家。请把每个任务归入 12 个 Thinking Type 中的**唯一一个**。

分类基于两个正交维度：

【维度A · 认知操作层级 Level】——任务核心难点落在哪一层
- L1 执行层：核心工作是"直接产出内容"（检索/复述、直接计算、直接生成、直接转换）。步骤短，不需要复杂组织，也不需要持续监控。
- L2 结构层：核心工作是"组织与串联"（规划步骤、整合多段信息、构建长文或多步推理链条）。
- L3 元认知层：核心工作是"监控/校验/修复/维持一致"（自查纠错、验证事实、防止被误导或推理跑偏、满足并核查多条约束、维持人设/语气一致）。

【维度B · 干预对象 Target】——任务围绕什么展开
- K 知识/事实：围绕事实、概念、领域知识、给定材料中的信息。
- R 过程/逻辑：围绕推理、计算、算法、逻辑推导，通常有确定或可验证的结果。
- E 表达/创意：围绕文本/内容的开放生成与风格，无唯一答案。
- F 格式/约束：围绕格式、模板、结构、字段或多条显式约束的遵守。

【12 个类型 = Level × Target】
- L1-K 知识提取：从材料中检索/抽取/复述事实、简单问答、翻译、判断对错。
- L1-R 直接求解：直接计算或短链推理（算术、单位换算、简单逻辑、实现明确功能）。
- L1-E 内容生成：开放地产生文本内容（写作、头脑风暴、创意、角色台词）。
- L1-F 格式转换：把输入转成指定形式（清洗、格式化、字段/单位映射、整理表格）。
- L2-K 知识整合：跨多段材料或多领域知识整合成连贯答案、长文摘要。
- L2-R 多步推理：需要规划并串联多步推导才能得到唯一答案（竞赛数学、证明、复杂算法）。
- L2-E 篇章组织：组织长文结构（提纲、章节、论证结构、叙事弧线）。
- L2-F 结构化输出：严格遵守模板/模式产出（JSON、CSV、表格、LaTeX、固定字段）。
- L3-K 事实验证：校验事实正确性、甄别幻觉、与知识对齐、挑错。
- L3-R 过程控制：持续监控推理不跑偏、识破误导/陷阱、保持多轮一致、遵循正确步骤。
- L3-E 风格保持：维持语气、人设、受众、指令风格的一致性。
- L3-F 约束校验修复：满足并核查多条显式约束并自我修正（修 bug、处理报错、遵守格式/条件约束）。

【判定步骤】
1) 先定 Level：任务核心难点是"直接产出"(L1)、"组织串联"(L2)、还是"监控/校验/修复"(L3)？
2) 再定 Target：任务围绕"知识/事实"(K)、"推理/计算"(R)、"表达/创意"(E)、还是"格式/约束"(F)？
3) 组合得到类型。

【消歧规则】
- 竞赛数学 / 需要精确多步推导得到唯一答案 → L2-R。
- 脑筋急转弯、常识陷阱、考察"别想当然/别被误导" → L3-R。
- 实现一个明确的功能/函数 → L1-R；需要设计算法或复杂实现 → L2-R。
- 从文本抽取字段/实体/关键信息 → L1-K（简单抽取）或 L2-F（要求结构化输出）。
- 输出 JSON/CSV/表格/LaTeX/固定模板 → L1-F（纯转换）；需满足多条约束并自查 → L3-F。
- 写博客/故事/头脑风暴/广告语 → L1-E；需要长篇结构与论证组织 → L2-E。
- 角色扮演 / 保持语气人设 / 受众适配 → L3-E。
- 解释科学原理 / 需整合多来源知识 → L2-K；简单事实问答 → L1-K。
- 事实核查 / 挑错 / 检查正确性 → L3-K。
- 修 bug / 处理报错 / 让程序跑通 → L3-F。
- 综合多段材料写连贯长答案 / 长文摘要 → L2-K。
- 需要严格逐步推导、不允许跳步 → L2-R。

【示例】
任务：If you have just overtaken the second person in a race, what's your position?  → {"thinking_type":"L3-R","reason":"常识陷阱，需防止想当然"}
任务：Solve: find all real x with x^3 - 3x + 1 = 0 ...  → {"thinking_type":"L2-R","reason":"竞赛数学多步求唯一解"}
任务：Write a travel blog post about Hawaii.  → {"thinking_type":"L1-E","reason":"开放内容生成"}
任务：Extract the highest and lowest closing price per month, return as CSV.  → {"thinking_type":"L2-F","reason":"要求结构化输出"}
任务：Explain the central dogma of molecular biology and who named it.  → {"thinking_type":"L2-K","reason":"整合领域知识作答"}
任务：You are a relationship coach, offer suggestions ...  → {"thinking_type":"L3-E","reason":"角色扮演与人设一致"}
任务：Fix the bug in this function so tests pass.  → {"thinking_type":"L3-F","reason":"修复并校验"}
任务：What is the capital of France?  → {"thinking_type":"L1-K","reason":"简单事实问答"}

【输出格式】只输出一个 JSON 对象，不要有任何其他文字：
{"thinking_type": "<类型ID，如 L2-R>", "confidence": <0到1的小数>, "reason": "<一句话中文理由>"}
"""

def cache_key(text: str) -> str:
    return hashlib.md5((PROMPT_VERSION + "||" + text).encode("utf-8")).hexdigest()

def load_cache(key):
    p = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(key, value):
    with open(os.path.join(CACHE_DIR, f"{key}.json"), "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False)

def _normalize(t: str):
    t = (t or "").strip()
    # direct id
    for tid in TYPE_IDS:
        if tid.lower() == t.lower():
            return tid
    # id embedded
    for tid in TYPE_IDS:
        if tid.lower() in t.lower():
            return tid
    # english name embedded
    for tid, en in ID2EN.items():
        if en.lower() in t.lower():
            return tid
    # chinese name embedded
    for tid, zh in ID2ZH.items():
        if zh in t:
            return tid
    return None

def build_user_prompt(row):
    return f"""【task】
{str(row.get('task',''))[:1600]}

【problem】
{str(row.get('problem',''))[:1600]}

【instruction】
{str(row.get('instruction',''))[:800]}

【来源/元数据】 dataset={row.get('dataset_id','')} | category={row.get('category','')} | group={row.get('primary_group','')} | domain={row.get('metadata_domain','')} | skill={row.get('metadata_skill','')} | subject={row.get('subject','')} | level={row.get('level_label','')}
"""

def classify_one(row, max_retries=4):
    up = build_user_prompt(row)
    key = cache_key(SYSTEM_PROMPT + up)
    cached = load_cache(key)
    if cached:
        return cached["thinking_type"]
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role":"system","content":SYSTEM_PROMPT},
                          {"role":"user","content":up}],
                temperature=0.0,
                response_format={"type":"json_object"},
            )
            raw = resp.choices[0].message.content
            try:
                parsed = json.loads(raw)
            except Exception:
                mm = re.search(r"\{.*\}", raw, re.S)
                parsed = json.loads(mm.group(0)) if mm else {}
            tid = _normalize(parsed.get("thinking_type",""))
            if tid:
                save_cache(key, {"thinking_type": tid,
                                 "reason": parsed.get("reason",""),
                                 "confidence": parsed.get("confidence")})
                return tid
            raise ValueError(f"unparsable type: {parsed.get('thinking_type')}")
        except Exception as e:
            print(f"[retry {attempt+1}] {e}")
            time.sleep(1.5 * (attempt+1))
    return "L1-K"  # last-resort fallback

def main():
    strat = {
        'PRESSURE':  ('pressure_high.csv','pressure_low.csv'),
        'ENCOURAGE': ('encourage_high.csv','encourage_low.csv'),
        'CRITICAL':  ('critical_high.csv','critical_low.csv'),
        'MISLEADING':('misleading_high.csv','misleading_low.csv'),
        'HEURISTIC': ('heuristic_high.csv','heuristic_low.csv'),
    }
    frames = []
    for s,(h,l) in strat.items():
        hd = pd.read_csv(os.path.join(RAW,h)); hd['set']='high'
        ld = pd.read_csv(os.path.join(RAW,l)); ld['set']='low'
        c = pd.concat([hd,ld], ignore_index=True); c['strategy']=s
        frames.append(c)
    df = pd.concat(frames, ignore_index=True)
    print("total rows:", len(df))

    # unique tasks by (dataset_id, task_id)
    uniq = df.drop_duplicates(subset=['dataset_id','task_id']).reset_index(drop=True)
    print("unique tasks:", len(uniq))

    records = uniq.to_dict('records')
    results = [None]*len(records)
    with ThreadPoolExecutor(max_workers=8) as ex:
        fut = {ex.submit(classify_one, r): pos for pos, r in enumerate(records)}
        for f in tqdm(as_completed(fut), total=len(fut), desc="classifying"):
            pos = fut[f]
            try: results[pos] = f.result()
            except Exception: results[pos] = "L1-K"
    uniq['thinking_type'] = results

    m = uniq.set_index(['dataset_id','task_id'])['thinking_type']
    df['thinking_type'] = [m.get((d,t)) for d,t in zip(df['dataset_id'], df['task_id'])]
    df['level']  = df['thinking_type'].map(ID2LEVEL)
    df['target'] = df['thinking_type'].map(ID2TARGET)

    df.to_csv(OUT_CSV, index=False)
    print("saved ->", OUT_CSV)
    print(df.groupby(['strategy','set','thinking_type']).size().unstack(fill_value=0))

if __name__ == "__main__":
    main()
