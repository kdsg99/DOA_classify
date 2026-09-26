# -*- coding: utf-8 -*-
"""把 v4 散点图（High/Low set share）这一版进展追加到 command_record.md（只追加）"""
import io

BLK = """

# DOA 进展（v4 分类尺下的 High/Low set share 散点图）
时间：2026-09-20 11:5x（K026）｜脚本：DOA/signal_experts/redesign/make_scatter_v4.py
备份：redesign 的 py/csv/md -> DOA/signal_experts/redesign_backup_20260920_1150（57 文件 / 16 MB）

一句话：沿用旧版 make_scatter.py 的份额定义，把分类尺从 v2 的 12 类换成 v4 的 11 个思维动作，
出「x=Low set share、y=High set share、对角线=plain 基准」的散点，五策略各一张 + 合图。

- 数据：all_tasks_v4.csv（2801 行 = 策略×题目，含 set=high/low 与 primary、多标签 o_T1..o_T11）。
- 两种口径：primary（每题只算主标签，份额加总 100%，与旧版可比）；multilabel（题同时计入其所有动作）。
- 已知口径限制：T11_SUSTAIN（长程一致）在 primary 口径下永远为 0（它从不被标为主标签，只在多标签里
  出现在 3.3% 的行），所以 primary 图实际只有 10 个动作在动；ENCOURAGE 的目标动作之一就是 T11，
  该策略的目标命中只能在 multilabel 口径里评。
- 主要看点（primary 口径 net = high_share − low_share，>0 即该策略在此动作上的提升份额大于下降份额）：
  PRESSURE 目标「链式推演」+12.8 (n=146)；CRITICAL 目标「校验纠错」+12.8 (n=24) —— 两个设计上该
  命中的格子确实在基准线上方；MISLEADING 目标「抗扰判断」−17.9 (n=28)、HEURISTIC 目标「换表征」
  −28.6 (n=9) 与「探索发散」−1.6 (n=81)、ENCOURAGE 目标「探索发散」−1.6 (n=81) 都在基准线下方。
  multilabel 口径整体同向、幅度收敛：PRESSURE +13.8、CRITICAL +10.6、MISLEADING −12.5、
  HEURISTIC 换表征 −12.1 / 探索发散 −5.1、ENCOURAGE 长程一致 +3.0（primary 下该动作无数据）。
- 落点在基准线上方 = 优于 plain，下方 = 劣于 plain；五策略在同一动作上的份额按构造加总 100%。

产物（都在 redesign/）：make_scatter_v4.py、fig_v4scatter/（五策略单图 + 合图，各出 primary 与
multilabel 两版，共 12 张 png）、v4scatter_shares_primary.csv、v4scatter_shares_multilabel.csv、
_run_v4scatter.log
"""

p = r"C:\Users\kl001\.nanobot\command_record.md"
with io.open(p, "a", encoding="utf-8") as f:
    f.write(BLK)
print("appended %d chars -> %s" % (len(BLK), p))
