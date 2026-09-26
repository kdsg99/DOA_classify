# -*- coding: utf-8 -*-
"""拷图与说明到 .nanobot\\figs，并追加 command_record.md。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = os.path.dirname(os.path.abspath(__file__))
F = r"C:\Users\kl001\.nanobot\figs"
os.makedirs(F, exist_ok=True)
PAIRS = [("figs/fig1_raw.png", "tt3_fig1_raw.png"),
         ("figs/fig2_difficulty.png", "tt3_fig2_difficulty_corrected.png"),
         ("figs/fig3_balanced.png", "tt3_fig3_balanced.png"),
         ("figs/fig1_raw_levels.png", "tt3_fig1L_raw_levels.png"),
         ("figs/fig2_difficulty_levels.png", "tt3_fig2L_difficulty_levels.png"),
         ("README.md", "tt3_README.md"),
         ("scenarios.md", "tt3_scenarios.md"),
         ("out/cells_3dims.csv", "tt3_cells_3dims.csv"),
         ("out/spread_by_strategy.csv", "tt3_spread.csv"),
         ("out/marginals_3dims.csv", "tt3_marginals.csv")]
for src, dst in PAIRS:
    shutil.copy2(os.path.join(H, src), os.path.join(F, dst))
    print("copied", dst)

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补六：改成「策略自身基准的相对画像」，让每家既有强项也有弱项"
e = """

### 2026-09-20 增补六：改成「策略自身基准的相对画像」，让每家既有强项也有弱项
- 用户反馈：只有水平值（去难度后五家几乎全为负）不行，必须让每家策略都出现「很好的 thinking type」与
  「很差的 thinking type」，同时 PRESSURE 仍平贴 0。
- 做法：保留难度校正（original 得分标准化：5<=original<=95 带内 + 按全体 original 分布加权），再对每个策略
  减去它自己 12 格的一型一票均值 → 得到「相对画像」：正 = 该类型上比这家自己的常态更好，负 = 该回避。
  每根条右侧仍标出绝对水平（lvl），薄格（n<15）打斜纹，超轴值的条打标记并截断。
- 结果（相对画像 SD / 极差 pp，一型一票；列分别为 raw / 去难度 / +族等权）：
  PRESSURE 6.2/26、5.7/19、7.4/30（三口径都最平，去难度后绝对水平 −0.2，12 格全在 ±11pp 内）；
  CRITICAL 15.8/57 → 10.6/38 → 11.1/40；ENCOURAGE 23.4/76 → 20.1/74 → 19.9/75；
  MISLEADING 19.0/61 → 20.2/69 → 20.8/75；HEURISTIC 19.4/65 → 12.7/48 → 12.1/45。
- 各家的强项/弱项（去难度相对值，括号为绝对水平）：CRITICAL 强 L3-E +13.8(+5.4)、L3-F +10.1(+1.7)、
  L3-K +7.8(−0.7)，弱 L1-F −23.8(−32.3)、L1-E −12.6；ENCOURAGE 强 L3-E +13.6、L2-E +12.5、L3-R +11.8，
  弱 L1-F −60.4(−77.1，仅 2 行薄格)、L3-F −8.9；MISLEADING 强 L3-E +16.9、L1-K +15.5、L3-K +14.1，
  弱 L3-F −24.7、L1-E −10.5、L1-F −51.9（薄格）；HEURISTIC 强 L2-E +14.1、L3-E +10.8、L2-R +6.6，
  弱 L3-K −6.5、L2-F −11.2、L1-F −33.8（薄格）。绝对口径下只有 CRITICAL 有真正为正的格（L3-E +5.4、L3-F +1.7）。
- 产物：figs\\fig1_raw.png、fig2_difficulty.png、fig3_balanced.png（相对画像）+ fig1_raw_levels.png、
  fig2_difficulty_levels.png（绝对参考）；out\\cells_3dims.csv 新增 raw_rel/std_rel/std_fam_rel、mad；
  spread_by_strategy.csv 新增 mad；README.md、scenarios.md 同步。副本 C:\\Users\\kl001\\.nanobot\\figs\\tt3_*。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
