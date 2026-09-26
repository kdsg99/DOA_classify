# -*- coding: utf-8 -*-
"""追加 command_record.md（幂等）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补四：改按三维度组合分类（v2 分类尺）重做场景分析"
e = """

### 2026-09-20 增补四：改按三维度组合分类（v2 分类尺）重做场景分析
- 用户澄清：12 类 thinking type 是三个维度内容的排列组合，不是单层标签。查得原始定义在
  DOA\\signal_experts\\redesign\\taxonomy_v2.py 与 classify_v2.py：维度①操作层级 L1 执行（内容执行）/L2 结构（结构组织）/
  L3 元认知（元认知控制）；维度②干预对象 K 知识事实 / R 过程逻辑 / E 表达创意 / F 格式约束；①×② = 12 类
  （L1-K 知识提取、L1-R 直接求解、L1-E 内容生成、L1-F 格式转换、L2-K 知识整合、L2-R 多步推理、L2-E 篇章组织、
  L2-F 结构化输出、L3-K 事实验证、L3-R 过程控制、L3-E 风格保持、L3-F 约束校验修复）；维度③增益性质
  Defensive/Offensive 是实测的（= 该格 Δ>0 的行占比 gain_rate，≥50% 记 Offensive），不是任务标签。
- 目录重建：C:\\Users\\kl001\\.nanobot\\DOA\\thinking_type_scenarios\\ 顶层改为本三维版（data/rows_v2.csv 来自
  redesign\\all_tasks_v2.csv，2801 行）；上一版（v1 命名 12 类）整体移到 v1_alternative\\ 仅留档。
  脚本：tt3_analysis.py（格估计 + 维度边际，每型一票）、make_figs.py、summarize.py；产物：out\\cells_3dims.csv、
  out\\marginals_3dims.csv、figs\\fig1_raw.png / fig2_difficulty_adjusted.png / fig3_balanced.png、scenarios.md、README.md。
- 三版口径沿用：raw / 去难度（策略内 Δ~plain 回归残差，R²≈0.5）/ 去难度+族等权。
- 结果：raw 除 PRESSURE +3.1 外全负；去难度后整体转正（+4.2~+11.4），目标维度 R（过程逻辑）五家全负（−4.4~−7.3）；
  族等权后只有 PRESSURE 的 R 仍负（−2.1）→ R 的负主要来自数学族 92% 饱和，不能单独当结论。
- 跨口径稳健：L2-E 篇章组织五策略三口径全正（+5.8~+29.1）；L2-K 知识整合、L1-K 知识提取、L3-E 风格保持稳定为正；
  L2-R 多步推理去难度后五家全负（−12~−18）、族等权后仍四家为负 → 唯一稳健的「回避区」（竞赛数学/证明/算法设计）。
- 增益性质实测：gain_rate 总体 PRESSURE 54%（唯一 >50%，即唯一"多数行有增益"）> CRITICAL 42% > ENCOURAGE 30% >
  MISLEADING 23% = HEURISTIC 23% → 后两者属"高方差探针"，均值正但四行里三行掉分。
- 篇幅：图表全部英文；薄格 L1-F（12 行）、L3-F（32 行）已标注；副本在 C:\\Users\\kl001\\.nanobot\\figs\\tt3_*。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("已追加，%.1f KB" % (os.path.getsize(p) / 1024))
