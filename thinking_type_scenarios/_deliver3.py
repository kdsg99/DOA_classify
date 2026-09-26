# -*- coding: utf-8 -*-
"""交付：把三维修饰版 tt3 图拷到 .nanobot\\figs（tt5_*），并追加 command_record.md。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\figs_enc"
F = r"C:\Users\kl001\.nanobot\figs"
os.makedirs(F, exist_ok=True)
PAIRS = [("fig1_raw.png", "tt5_fig1_raw_3dim.png"),
         ("fig2_difficulty.png", "tt5_fig2_difficulty_3dim.png"),
         ("fig3_balanced.png", "tt5_fig3_balanced_3dim.png"),
         ("fig1_raw_levels.png", "tt5_fig1L_raw_levels_3dim.png"),
         ("fig2_difficulty_levels.png", "tt5_fig2L_difficulty_levels_3dim.png")]
for src, dst in PAIRS:
    shutil.copy2(os.path.join(H, src), os.path.join(F, dst))
    print("copied", dst)

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补八：tt3 三张图 + 二维图加「三维度」视觉编码（颜色/图案/虚实）"
e = """

### 2026-09-20 增补八：tt3 三张图 + 二维图加「三维度」视觉编码（颜色/图案/虚实）
- 用户判定：tt3 版（新建 thinking_type_scenarios 后的第一版）的图与 thinking style 分类可以保留，
  只要求把「组成每个 thinking style 的三维度」用颜色/图案/虚实表现在每根 bar 上。
- 实现（新脚本 thinking_type_scenarios\\make_figs_enc.py，输出 figs_enc\\，原 make_figs.py 与 tt3 图不动）：
  维度1 操作层级 L1/L2/L3 → bar 底色（蓝/绿/红，沿用原配色）；
  维度2 干预对象 K/R/E/F → bar 图案（K 无、R 斜杠 ///、E 交叉 xxx、F 反斜杠 \\\\\\ ）；
  维度3 增益性质 Offensive/Defensive（由该策略在该类型上「救回的题 vs 弄坏的题」推得，非任务标签）
  → 实心（白图案线，alpha .95）= 进攻型；浅底 + 虚线边框 + 同色图案线（alpha .30）= 防守型；
  薄格（n<15）仍用更淡的 bar + 右侧红字标注；每图右下新增三维度图例。
- 边际面板（右列）在原有 3 层级 + 4 对象 + 全部之外，新增第三维度的两行（Offensive / Defensive）。
- 编码生效性已做像素级自检（实心 bar 饱和纯色、防守 bar 浅底多色=图案线确实画上）。
- 本版图揭示的读数：增益性质几乎与「全局胜负」绑定——PRESSURE 7 类型进攻 / 5 防守、CRITICAL 3/9、
  MISLEADING 1/11、ENCOURAGE 0/12、HEURISTIC 0/12（四家激进重问在任何 thinking type 上都做不到
  「救回多于弄坏」）。
- 产物：figs_enc\\fig1_raw.png、fig2_difficulty.png、fig3_balanced.png、fig1_raw_levels.png、
  fig2_difficulty_levels.png；副本 C:\\Users\\kl001\\.nanobot\\figs\\tt5_*_3dim.png。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
