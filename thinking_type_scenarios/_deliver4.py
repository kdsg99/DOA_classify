# -*- coding: utf-8 -*-
"""交付 tt6：拷图到 .nanobot\\figs，并把方法文档/代码拷到交付目录，追加 command_record。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
F = r"C:\Users\kl001\.nanobot\figs"
os.makedirs(F, exist_ok=True)
PAIRS = [("fig1_raw.png", "tt6_fig1_raw_3dim.png"),
         ("fig2_difficulty.png", "tt6_fig2_difficulty_3dim.png"),
         ("fig3_balanced.png", "tt6_fig3_balanced_3dim.png"),
         ("fig2_difficulty_levels.png", "tt6_fig2L_difficulty_levels_3dim.png")]
for src, dst in PAIRS:
    s = os.path.join(H, "figs_tt6", src)
    shutil.copy2(s, os.path.join(F, dst))
    print("copied %-34s %6.0f KB" % (dst, os.path.getsize(s) / 1024))

DEL = r"C:\Users\kl001\.nanobot\deliver"
os.makedirs(DEL, exist_ok=True)
for src, dst in [(r"figs_tt6\fig2_difficulty.png", "tt6_fig2_difficulty.png"),
                 (r"figs_tt6\fig1_raw.png", "tt6_fig1_raw.png"),
                 (r"figs_tt6\fig3_balanced.png", "tt6_fig3_balanced.png"),
                 (r"figs_tt6\fig2_difficulty_levels.png", "tt6_fig2L_levels.png"),
                 ("DIFFICULTY_CORRECTION.md", "DIFFICULTY_CORRECTION.md"),
                 ("make_figs_tt6.py", "make_figs_tt6.py"),
                 ("tt3_analysis.py", "tt3_analysis.py"),
                 ("taxonomy_v2.py", "taxonomy_v2.py"),
                 ("_sens_mix.py", "_sens_mix.py")]:
    shutil.copy2(os.path.join(H, src), os.path.join(DEL, dst))
    print("delivered", dst, "%.0f KB" % (os.path.getsize(os.path.join(DEL, dst)) / 1024))

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-21 增补九：第三维度换为「头寸 headroom」+ 难度校正方法论文档 + 图面减字"
e = """

### 2026-09-21 增补九：第三维度换为「头寸 headroom」+ 难度校正方法论文档 + 图面减字
- 用户要求：原第三维度（增益性质 Offensive/Defensive）图上体现不出来，要换一个维度（只换第三维度的
  表现，不做重新分类）；另外要一份论文式的难度校正方法说明（写进 md）；图表文字要精简；并把 figure 2
  的代码作为附件交付。
- 第三维度改为「头寸 headroom」= 100 − 该 thinking type 自身的基线分（无策略 plain，按行均值）；
  实心 bar = 基线 ≤ 70（还有 ≥30pp 空间，6 型），浅底+虚线 = 基线 > 70（已基本做对，6 型）。
  该维度横跨层级与对象两轴：L1 1高/3低，L2 3高/1低，L3 2高/2低；F 对象三型全部低头寸。
  逐型基线：L1-K 67.4、L1-R 85.8、L1-E 74.7、L1-F 92.0、L2-K 77.7、L2-R 68.7、L2-E 67.7、
  L2-F 71.6、L3-K 55.2、L3-R 65.6、L3-E 69.9、L3-F 77.7。
- 新脚本 make_figs_tt6.py（取代 make_figs_enc.py 作为当前出图脚本），输出 figs_tt6\\ 四张图；
  文字大幅精简：去掉每根 bar 右侧的「lvl/n/增益率」三合一串（只留 n=）、去掉边际面板的百分比注记、
  页眉压成一行「mean/SD/range」、说明框改为 3 行 + 三行图例。
- 新增方法论文档 DIFFICULTY_CORRECTION.md：完整写出难度校正（头寸带 5–95、20pp 分箱、
  参考混合 w=(0.093,0.068,0.108,0.731)、直接标准化公式、族平衡、基线居中、薄格退化规则），
  识别假设、阴性对照（PRESSURE）、四组敏感性（A 当前 / B 等权 / C 带 5–65 / D 带 25–95）、
  局限与复现清单。
- 敏感性关键读数：水平值高度依赖参照系（PRESSURE 在当前口径 −0.2pp，等权口径 +11.0，带 5–65 +20.9）；
  「PRESSURE 最平」只在偏向高分段的参照系下成立（带 5–65 时其 SD 24.4 反而最大）。
- 交付：deliver\\ 下 tt6_* 图 4 张 + DIFFICULTY_CORRECTION.md + make_figs_tt6.py + tt3_analysis.py
  + taxonomy_v2.py + _sens_mix.py。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
