# -*- coding: utf-8 -*-
"""补发 D6 图 + 更新总结 + 追加记录（幂等）。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
FIGS = r"C:\Users\kl001\.nanobot\figs"
for f in ["D6_ceiling_effect.png"]:
    shutil.copy2(os.path.join(R, "fig_effect", f), os.path.join(FIGS, "eff_" + f))
    print("copied eff_" + f, "%.0f KB" % (os.path.getsize(os.path.join(FIGS, "eff_" + f)) / 1024))
shutil.copy2(os.path.join(R, "summary_effect_v4.md"), os.path.join(FIGS, "summary_effect_v4.md"))
print("summary updated (%.1f KB)" % (os.path.getsize(os.path.join(FIGS, "summary_effect_v4.md")) / 1024))

REC = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补二：天花板效应 + 跨族扩样方案"
txt = open(REC, encoding="utf-8").read()
if mark in txt:
    print("已存在，跳过")
else:
    entry = """
### 2026-09-20 增补二：天花板效应 + 跨族扩样方案（用户提问「跨族扩样是什么意思、具体怎么做」）
- 关键发现（D6）：2801 行中 675 行（24%）plain_minmax 已 100%，只可能掉分；chat_math500 92%（570/617）饱和且
  饱和行 Δ 平均 −100.0pp，非饱和 47 行反而 +100.0pp。按策略：饱和行 −53~−96pp，非饱和行 −15.1~+5.7pp；
  只看非饱和行整体 Δ = PRESSURE +5.7 / CRITICAL −3.8 / ENCOURAGE −6.2 / HEURISTIC −10.8 / MISLEADING −15.1pp。
  链式推演：饱和行 −96.1pp vs 非饱和行 +0.0pp(n=668) → 「链式推演崩盘」主要是数学族饱和(0/1 判分)造成的。
- 事实更正：动作标签是按「题」固定的（683 题跨策略 0% 不一致），不是按策略；差异来自每策略覆盖的题集不同
  （PRESSURE 只覆盖 29/262 道数学题，其中 8 道独有）。此前「链式推演标签跨策略不是同一批题」的说法不准确。
- 跨族扩样定义：让 11 个动作在 ≥4 个族、且都在非饱和题（plain<100）上各拿 ≥30 行（≈7 题 × 5 策略），
  以解决动作效应与族效应不可辨识（族双扣除后动作效应只剩 −1.2~−7.3pp）的问题。
- 五步做法：①定 66 格目标 ②用 classify_v4.py 对现有 683 题 + DOA\\*.jsonl（arena_hard/alpaca_eval/flask_hard/aime2024）
  做标签勘察定补样清单 ③沿用 config\\prompts\\strategies.py 的 5 套策略模板造 reask ④plain/reask 各 N 次 min-max 打分
  ⑤重跑 effect_analysis_v4.py 出「动作×族」二因素表。三档规模：L 只换口径（今天可做）/ M 补 1200~1500 行评估 /
  P 正式实验约 9900 行。
- 阻塞点：打分上游池 *_minmax_outputs\\data\\*.csv 不在本机，只有派生数据 raw_data（2801 行）；新增行须重跑打分，
  需确认上游 harness 能否重跑或重建本地小 harness。分类器（DeepSeek+cache_v4）与策略模板本机可用。
- 新增产物：fig_effect\\D6_ceiling_effect.png；脚本 ceiling_fig.py、_gap_scan.py、_ceiling_scan.py、_verify_key_facts.py 等；
  summary_effect_v4.md 增加「D6 天花板效应」与「6 跨族扩样：是什么、怎么做」两节（原 6/7/8 顺延为 7/8/9）。
"""
    open(REC, "a", encoding="utf-8").write(entry)
    print("record appended, %.1f KB" % (os.path.getsize(REC) / 1024))
