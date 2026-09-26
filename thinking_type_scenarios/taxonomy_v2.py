# -*- coding: utf-8 -*-
"""
Redesigned Thinking-Type taxonomy (v2).

Design goal: make the taxonomy a *clean, orthogonal* grid so that
(a) a strategy's high vs low sets are separable, and
(b) different strategies get different signatures.

Two orthogonal axes (task-intrinsic):
  Axis A: Cognitive Operation Level  (Execution / Structure / Metacognition)
  Axis B: Target of Intervention     (Knowledge / Reasoning / Expression / Format)
=> 3 x 4 = 12 Thinking Types.

The third original dimension (Nature of Strategy Gain: defensive vs offensive)
is NOT a task label -- it is *derived empirically* per (strategy, type) from the
high/low ratio, so it can be computed and plotted instead of guessed by the LLM.
"""

# (id, en name, zh name, level, target)
TYPES = [
    # ---- Level 1: Execution (直接产出) --------------------------------------
    ("L1-K", "Knowledge Retrieval",     "知识提取",   "L1", "K"),
    ("L1-R", "Direct Computation",      "直接求解",   "L1", "R"),
    ("L1-E", "Content Generation",      "内容生成",   "L1", "E"),
    ("L1-F", "Format Transformation",   "格式转换",   "L1", "F"),
    # ---- Level 2: Structure (组织串联) -------------------------------------
    ("L2-K", "Knowledge Synthesis",     "知识整合",   "L2", "K"),
    ("L2-R", "Multi-Step Derivation",   "多步推理",   "L2", "R"),
    ("L2-E", "Discourse Organization",  "篇章组织",   "L2", "E"),
    ("L2-F", "Structured Output",       "结构化输出", "L2", "F"),
    # ---- Level 3: Metacognition (监控/校验/修复) ---------------------------
    ("L3-K", "Factual Verification",    "事实验证",   "L3", "K"),
    ("L3-R", "Process Control",         "过程控制",   "L3", "R"),
    ("L3-E", "Style & Persona Fidelity","风格保持",   "L3", "E"),
    ("L3-F", "Constraint Check & Repair","约束校验修复", "L3", "F"),
]

TYPE_IDS = [t[0] for t in TYPES]
ID2EN = {t[0]: t[1] for t in TYPES}
ID2ZH = {t[0]: t[2] for t in TYPES}
ID2LEVEL = {t[0]: t[3] for t in TYPES}
ID2TARGET = {t[0]: t[4] for t in TYPES}

LEVELS = ["L1", "L2", "L3"]
LEVEL_EN = {"L1": "Execution", "L2": "Structure", "L3": "Metacognition"}
LEVEL_ZH = {"L1": "执行层", "L2": "结构层", "L3": "元认知层"}
TARGETS = ["K", "R", "E", "F"]
TARGET_EN = {"K": "Knowledge", "R": "Reasoning", "E": "Expression", "F": "Format"}
TARGET_ZH = {"K": "知识", "R": "推理", "E": "表达", "F": "格式"}

# short label used on plots: "L2-R  Multi-Step Derivation"
def short_label(tid):
    return f"{tid}  {ID2EN[tid]}"
