# -*- coding: utf-8 -*-
"""
Alternative task taxonomies (v3), designed to maximise the visibility of
*strategy preferences* (which kind of task a strategy reliably helps / hurts).

Two candidate schemes are provided; both are labelled by the same LLM pipeline as
taxonomy_v2, and the winner is chosen by a discriminability metric (see analyze_v3.py).

  s1  "需求维度 x 要求类型"   4 x 3 = 12 类   (题目在要什么  x  判分依据是什么)
  s2  "易错环节归因"          1 x 8 = 8 类    (模型最容易在哪个环节出错)
"""

SCHEMES = {}

# ----------------------------------------------------------------------------- s1
S1_IDS = [f"{a}-{b}" for a in ["K", "R", "B", "E"] for b in ["V", "C", "Q"]]

S1_NAME = {
    "K-V": "知识·精确答案", "K-C": "知识·约束合规", "K-Q": "知识·主观质量",
    "R-V": "推理·精确答案", "R-C": "推理·约束合规", "R-Q": "推理·主观质量",
    "B-V": "建构·精确答案", "B-C": "建构·约束合规", "B-Q": "建构·主观质量",
    "E-V": "表达·精确答案", "E-C": "表达·约束合规", "E-Q": "表达·主观质量",
}

S1_PROMPT = """你是一位任务分析专家。请把一个任务按两个维度定位，归入 12 类中的唯一一类。

【维度 D · 题目维度】—— 这个任务真正要求模型付出的是什么（难点所在）
- K 知识：核心是调用准确的领域知识、事实、常识、给定材料中的信息；做得好不好取决于"知不知道、记得准不准"。
- R 推理：核心是严密的推导、计算、算法或逻辑判断；取决于"算得对不对、推得通不通"。
- B 建构：核心是按明确规格交付一个成品/结构（代码、表格、字段、模板、数据清洗、结构化输出）。
- E 表达：核心是产出没有唯一正确答案的文本内容（写作、建议、创意、语体适配）。

【维度 Q · 要求类型】—— 判分依据是什么
- V 精确可验：存在确定答案或硬性正确性，可以判定对错（数值、事实、代码能否跑通）。
- C 约束合规：判分主要看是否满足多条显式要求（字数、格式、字段、条件、必须覆盖的要点）。
- Q 主观质量：没有标准答案，由评审/读者的主观偏好判定优劣（文采、说服力、有用性、得体）。

【判定步骤】
1) 先定要求类型 V/C/Q：有唯一正确答案 → V；主要看是否满足显式约束/格式/条件 → C；无标准答案、看质量 → Q。
2) 再定题目维度 K/R/B/E：难点在"知道多少"→K；在"推得对不对"→R；在"按规格交付成品"→B；在"写得好不好"→E。
3) 组合为"维度-要求"，如 R-V。

【消歧规则】
- 竞赛数学、需要多步推导得到唯一数值/结论 → R-V。
- 只要背出/说出某个事实、定义、结论、日期 → K-V。
- 写代码解决明确问题、要求代码正确/可运行 → B-V；若重点是设计算法或推导复杂度 → R-V。
- 修 bug、处理报错、让程序跑通、按规格改写代码 → B-C。
- 输出 JSON/CSV/表格/固定字段/模板/LaTeX → B-C；纯格式转换且只要求转换正确 → B-V。
- 翻译 → E-C（要求准确且得体，通常无唯一字符串答案）。
- 写博客/故事/广告语/建议/角色扮演/解释给外行听 → E-Q。
- 提纲/总结/多篇材料整合成一篇长文 → E-C（有覆盖要点与结构约束时）或 E-Q（只看质量时），优先 E-Q。
- 事实核查、挑错、判断说法对不对 → K-V。
- 数字表格类计算（求某列统计量）→ R-V。
- 按多条约束改写/压缩/润色文本 → E-C。

【示例】
任务：If you have just overtaken the second person in a race, what's your position? → {"type":"R-V","reason":"常识陷阱但答案唯一，靠推理判断"}
任务：Solve for all real x: x^3-3x+1=0 ... → {"type":"R-V","reason":"竞赛数学多步求唯一解"}
任务：Write a travel blog post about Hawaii. → {"type":"E-Q","reason":"开放写作，按质量评审"}
任务：Extract the highest and lowest closing price per month, return as CSV. → {"type":"B-C","reason":"要求按格式交付结构化成品"}
任务：Explain the central dogma of molecular biology and who named it. → {"type":"K-V","reason":"领域事实与命名，有确定答案"}
任务：You are a relationship coach, offer suggestions ... → {"type":"E-Q","reason":"角色扮演与建议，看质量"}
任务：Fix the bug in this function so tests pass. → {"type":"B-C","reason":"按测试/规格修复代码"}
任务：What is the capital of France? → {"type":"K-V","reason":"简单事实问答"}

【输出格式】只输出一个 JSON 对象：
{"type": "<K/R/B/E>-<V/C/Q>", "confidence": <0到1>, "reason": "<一句话中文理由>"}
"""

# ----------------------------------------------------------------------------- s2
S2_IDS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]

S2_NAME = {
    "F1": "知识缺口型", "F2": "计算推导型", "F3": "约束遗漏型", "F4": "误导陷阱型",
    "F5": "表达平庸型", "F6": "长文一致型", "F7": "检查修复型", "F8": "低风险常规型",
}

S2_PROMPT = """你是一位任务风险分析专家。请判断：模型在做这类任务时，最容易在哪个环节出错？归入唯一一类。

候选类别（互斥，按"最可能出错的环节"选一）：
- F1 知识缺口型：答案取决于长尾/精确的事实或领域知识，模型容易不知道、记错或编造。
- F2 计算推导型：需要多步数字运算、符号推导或算法推演，容易算错、跳步、丢解、推不严谨。
- F3 约束遗漏型：任务带多条显式要求（字数、格式、字段、条件、必须覆盖的要点），容易漏项、越界或格式不符。
- F4 误导陷阱型：题面含陷阱、错误前提、诱导性常识或"想当然"的空间，容易被题面带偏。
- F5 表达平庸型：开放式写作/建议/创意/角色扮演，容易写得空洞、套路、不具体、不贴合受众。
- F6 长文一致型：材料很长或需要整合多段信息/多轮上下文，容易遗漏关键信息、前后矛盾。
- F7 检查修复型：任务本身要求检查、调试、校对、验证并改正（找错、修 bug、核算、复核）。
- F8 低风险常规型：简单直接、模型通常不会出错（日常问答、简单生成、常规改写、简单转换）。

【判定优先级】
1) 任务本身要求"找错/修错/验证/复核" → F7。
2) 题面有明显陷阱、错误前提或诱导 → F4。
3) 明显是多步计算/推导/算法推演 → F2。
4) 明显是多条格式/字段/条件约束的交付 → F3。
5) 明显依赖长尾或精确领域知识、且不是简单常识 → F1。
6) 需要消化很长材料或多轮上下文 → F6。
7) 开放式写作/建议/创意/人设 → F5。
8) 以上都不显著、几乎是常规操作 → F8。

【示例】
任务：If you have just overtaken the second person in a race, what's your position? → {"type":"F4","reason":"常识陷阱，容易被想当然带偏"}
任务：Solve for all real x: x^3-3x+1=0 ... → {"type":"F2","reason":"多步符号推导易出错"}
任务：Fix the bug in this function so tests pass. → {"type":"F7","reason":"任务要求定位并修正错误"}
任务：Extract the highest and lowest closing price per month, return as CSV. → {"type":"F3","reason":"字段与格式约束易漏"}
任务：Explain the central dogma and who named it. → {"type":"F1","reason":"依赖准确的领域事实与命名"}
任务：You are a relationship coach, offer suggestions ... → {"type":"F5","reason":"开放建议，看是否具体有用"}
任务：What is the capital of France? → {"type":"F8","reason":"常规常识，几乎不出错"}
任务：Summarise this 40-page interview transcript and give 3 codes. → {"type":"F6","reason":"长材料整合易遗漏关键信息"}

【输出格式】只输出一个 JSON 对象：
{"type": "<F1..F8>", "confidence": <0到1>, "reason": "<一句话中文理由>"}
"""

SCHEMES["s1"] = dict(tag="s1", title="需求维度 x 要求类型", ids=S1_IDS, names=S1_NAME, prompt=S1_PROMPT)
SCHEMES["s2"] = dict(tag="s2", title="易错环节归因", ids=S2_IDS, names=S2_NAME, prompt=S2_PROMPT)
