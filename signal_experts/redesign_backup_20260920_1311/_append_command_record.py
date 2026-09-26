# -*- coding: utf-8 -*-
"""把本次 v4c 进展追加到 command_record.md（仅追加，不改动已存在内容）"""
import io

BLK = """

# DOA 进展（v4c：因变量换成连续 Δscore，建议 1）
时间：2026-09-19 17:46（K026）｜脚本：DOA/signal_experts/redesign/analyze_v4c.py
备份：redesign 全量副本 -> DOA/signal_experts/redesign_backup_20260919_1726（2800 文件 / 27.5 MB）

一句话：只换因变量带来小幅灵敏度提升，大结论没变（方向对、强度弱）；顺带查出 v4 报告里
「族维度交互 γ z=+6.2」是 all-rows 口径的产物，共同任务集口径下消失。

- 因变量：helped（high 占比≥0.5）-> Δscore =（reask_minmax − plain_minmax）的均值；族内平衡加权、400 次族内置换、BH-FDR 全部与 analyze_v4.py 一致。
- 自检：high ⇔ delta>0 完全等价（二值本来就是连续量的符号）；2801 行 / 683 任务 / 2412 策略×任务 / 6 评测族。
- 灵敏度：p<0.05 的单元格 二值 2 -> 连续原尺度 2 / 族内标准化 d 3 / 中位数 2；FDR 全部仍为 0（最小 q：原尺度 0.885、标准化 0.686）。
- 有价值的增量：CRITICAL × 校验纠错（设计上应有的命中）p 0.830 -> 0.032（族内标准化 d）。
- 任务级目标命中：4/5 策略的目标题优于其余题（差值 +18 ~ +36 ×100），但置换 p 全部 ≥ 0.26，一个都不显著；PRESSURE 的目标题反而更差。
- 各尺子交互：common 口径下二值 −0.2~−1.7、连续都在 ±1 以内（v4 尺子 +0.95 最好）；all 口径下 dataset 仍最高（二值 +6.2 / 连续 +13.2）。
- 结论：瓶颈在样本量（n 中位数 48、最小 14）+ 思维动作跨族不足，不在因变量二值化；建议 2、3 优先。

产物（都在 redesign/）：summary_v4c.md、v4c_preference_cont.csv、v4c_vs_binary.csv、v4c_target_match.csv、
v4c_scheme_interaction_cont.csv、fig_v4c/{cont_heatmap,cont_vs_binary,cont_target_match,cont_op_ranking}.png
"""

p = r"C:\Users\kl001\.nanobot\command_record.md"
with io.open(p, "a", encoding="utf-8") as f:
    f.write(BLK)
print("appended %d chars -> %s" % (len(BLK), p))
