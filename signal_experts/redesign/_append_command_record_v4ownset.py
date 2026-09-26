# -*- coding: utf-8 -*-
"""把 v4 散点图的口径更正（分母改为该策略自己的 low/high 总数）追加到 command_record.md（只追加）"""
import io

BLK = """

# DOA 口径更正（v4 散点图的 High/Low set share）
时间：2026-09-20 12:0x（K026）｜脚本已改写：DOA/signal_experts/redesign/make_scatter_v4.py

用户更正：分母不是"全体五策略的合计"，而是"该策略自己的 low / high 总数"——
    x = Low set share  = 该策略在某动作上的 low 数 / 该策略的 low 总数 × 100
    y = High set share = 该策略在某动作上的 high 数 / 该策略的 high 总数 × 100
这正是旧版 plot_ownset.py（fig_ownset_v2）用的 own-set 归一化：两轴各自加总 100%，
没有类型特异效应的策略会沿 y=x 分布 → 对角线 = plain 基准，偏离量 = 该策略在该动作上的特异效应。

- 更正后的读数（primary 口径，net = high_share − low_share）：
  PRESSURE  above 6 / below 4，corr +0.99，最大偏离 7.1；目标「链式推演」net −7.14（在基准线下方）
  ENCOURAGE above 6 / below 4，最大偏离 12.1；「探索发散」−0.31、「长程一致」n=0（primary 无数据）
  CRITICAL  above 6 / below 4，最大偏离 11.5；目标「校验纠错」+4.28（线上方）
  MISLEADING above 6 / below 4，最大偏离 5.3；目标「抗扰判断」+0.72（基本贴线）
  HEURISTIC above 8 / below 2，最大偏离 19.8；「探索发散」+4.59（线上方）、「换表征」−0.81
  四个策略（PRESSURE / ENCOURAGE / CRITICAL / HEURISTIC）的最大偏离动作都是「链式推演」且都为负
  （HEURISTIC −19.8 / ENCOURAGE −12.1 / CRITICAL −11.5 / PRESSURE −7.1），MISLEADING 的最大偏离是
  「探索发散」−5.3；即提升集中在别的动作上，下降却仍压在这个最大的动作上。
- multilabel 口径同向且更温和：PRESSURE 链式推演 −3.09；CRITICAL 校验纠错 +5.13；HEURISTIC 探索发散 +4.82、
  换表征 +0.81；ENCOURAGE 探索发散 +1.97、长程一致 +0.67；MISLEADING 抗扰判断 +2.75。
- 结论提示：own-set 口径下"策略自己的目标动作"并不必然占优（PRESSURE 的目标动作甚至在基准线下方），
  与 v4c 的置换检验结果方向一致——提示性差异多、多数不显著。

产物：fig_v4ownset/（五策略单图 + 合图，primary 与 multilabel 各 6 张，共 12 张 png）、
v4ownset_shares_primary.csv、v4ownset_shares_multilabel.csv、_run_v4ownset.log；
旧（错分母）产物已移到 redesign/_deprecated_wrongdenom/（fig_v4scatter 等 15 个文件）。
"""

p = r"C:\Users\kl001\.nanobot\command_record.md"
with io.open(p, "a", encoding="utf-8") as f:
    f.write(BLK)
print("appended %d chars -> %s" % (len(BLK), p))
