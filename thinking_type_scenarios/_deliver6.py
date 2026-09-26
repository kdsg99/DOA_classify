# -*- coding: utf-8 -*-
"""交付 tt7（第三维度改为起点状态）：拷图 + 文档/脚本到 deliver，追加 command_record。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
F = r"C:\Users\kl001\.nanobot\figs"
DEL = r"C:\Users\kl001\.nanobot\deliver"
for d in (F, DEL):
    os.makedirs(d, exist_ok=True)
for src, dst in [("fig1_raw.png", "tt7_fig1_raw_3dim.png"),
                 ("fig2_difficulty.png", "tt7_fig2_difficulty_3dim.png"),
                 ("fig3_balanced.png", "tt7_fig3_balanced_3dim.png"),
                 ("fig2_difficulty_levels.png", "tt7_fig2L_difficulty_levels_3dim.png")]:
    shutil.copy2(os.path.join(H, "figs_tt7", src), os.path.join(F, dst))
    print("figs\\%s" % dst)
for src, dst in [("figs_tt7\\fig2_difficulty.png", "tt7_fig2_difficulty.png"),
                 ("figs_tt7\\fig1_raw.png", "tt7_fig1_raw.png"),
                 ("figs_tt7\\fig3_balanced.png", "tt7_fig3_balanced.png"),
                 ("figs_tt7\\fig2_difficulty_levels.png", "tt7_fig2L_levels.png"),
                 ("DIM3_DESIGN.md", "DIM3_DESIGN.md"),
                 ("make_figs_tt7.py", "make_figs_tt7.py"),
                 ("_marg_dim3.py", "_marg_dim3.py"),
                 ("_pixcheck7.py", "_pixcheck7.py")]:
    shutil.copy2(os.path.join(H, src), os.path.join(DEL, dst))
    print("deliver\\%-28s %6.0f KB" % (dst, os.path.getsize(os.path.join(DEL, dst)) / 1024))

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-22 增补十一：第三维度由「头寸」改为「起点状态」（承接 vs 从零）"
e = """

### 2026-09-22 增补十一：第三维度由「头寸」改为「起点状态」（承接 vs 从零）
- 用户质疑：头寸的认知意义是什么，能否与前两维（操作层级、干预对象）置于同一套认知系统；要求第三维
  必须是"有意义的认知需求"维度。
- 结论（已写进 DIM3_DESIGN.md）：头寸 = 100 − 该型基线分，属"模型×任务"的测量属性（模型换代即变），
  是 fig2/3 的校正对象本身，只能当调节变量，不能当认知需求轴；它退出 bar 的第三通道，只保留在难度
  校正与薄格提示里。
- 冗余度体检（Cramér's V vs 层级/对象）：头寸 0.41/0.58；起点状态 0.00/0.33；答案收敛性 0.00/1.00
  （被对象轴完全吸收，排除）；精确判分 0.32/0.77（排除）。
- 新第三维 =「起点状态」：承接型（该型 ≥30% 任务承接上一轮产出，即 MT-Bench 二轮占比 ≥0.30）= 实心；
  从零型（<30%）= 浅底虚线。6/6 划分，层级上每级恰好 2:2、对象上 1~2:2~1。
  承接：L1-R(.30)、L1-E(.49)、L2-K(.38)、L2-F(.68)、L3-R(.34)、L3-E(.57)；从零：L1-K(.24)、L1-F(0)、
  L2-R(.05)、L2-E(.26)、L3-K(0)、L3-F(.28)。
- 认知解释：从零型 = 构建负荷（输入闭合、自定判据、完整构造）；承接型 = 整合与保持负荷（读入既有产出、
  判断可复用面、在继承约束下增量修改）。
- 附带发现（std_rel，一型一票）：ENCOURAGE 承接 +6.3 / 从零 −6.3（落差 12.6）、MISLEADING ±4.9（9.8）、
  HEURISTIC ±1.8、PRESSURE ∓1.8、CRITICAL ±0.3 —— 即"换个方向再答"类策略在承接型任务上相对不吃亏，
  在从零构建型上最吃亏；std_fam_rel 同向。
- 已注明构念效度：归属目前是测量口径（多轮承接占比）而非标注；L3-K/L3-F/L1-F 定义上带承接色彩但按
  测量划为从零型；若要严格，可对这 12 个类型补一次"是否承接"标注（成本极低）。
- 产物：make_figs_tt7.py（取代 tt6 出图脚本，图例沿用放大的三组格式）、figs_tt7\\ 四张图、
  DIM3_DESIGN.md、_marg_dim3.py（分组边际）、_pixcheck7.py（编码+冗余度自检）。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
