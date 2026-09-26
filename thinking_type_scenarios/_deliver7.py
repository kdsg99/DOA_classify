# -*- coding: utf-8 -*-
"""交付 FIG2 三份文档 + 统计脚本。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
DEL = r"C:\Users\kl001\.nanobot\deliver"
os.makedirs(DEL, exist_ok=True)
for f in ("FIG2_DESIGN.md", "FIG2_TYPES_TABLE.md", "FIG2_STRATEGY_FINDINGS.md", "_fig2_stats.py"):
    shutil.copy2(os.path.join(H, f), os.path.join(DEL, f))
    print("deliver\\%-30s %6.0f KB" % (f, os.path.getsize(os.path.join(DEL, f)) / 1024))

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-22 增补十二：Figure 2 三份文档（设计依据 / 逐型表 / 策略画像）"
e = """

### 2026-09-22 增补十二：Figure 2 三份文档（设计依据 / 逐型表 / 策略画像）
- 用户要求三件事，均以 md 交付：(1) 三维度设计依据 + thinking type 设计依据；(2) 每个 type 的三维度
  取值表格；(3) 论文式总结"不同策略擅长什么 thinking type 以及三维度上的哪一侧"。
- FIG2_DESIGN.md：术语、设计四准则（正交/可观测/任务内在/认知可解释）、维度1 层级（L1 执行 / L2 结构 /
  L3 元认知）与维度2 对象（K 知识 / R 推理 / E 表达 / F 格式）的定义与失败模式、12 型交叉来源、被否掉
  的两个第三维（增益性质：经验导出且几乎由策略决定；头寸：属"模型×任务"坐标系）、采用起点状态的理由
  与构念效度提醒、三通道编码表、5 份文件分工。
- FIG2_TYPES_TABLE.md：表1 12 型 × 三维取值（含承接占比 c_t、基线、n）；表2 逐型"三维度合起来要求什么
  思考"+ 主要失败模式；表3 正交性核对（层级各 4 型、对象各 3 型、起点 6:6 且每级 2:2、Cramér's V
  0.00/0.33）；表4 样本量核对（L1-F n=2~3、L3-F n=5~7 为薄格）。
- FIG2_STRATEGY_FINDINGS.md：数据口径 →主结果（绝对值口径下 PRESSURE 在 12 型中 10 型最优，仅 L2-F 与
  L3-E 上 CRITICAL 反超）→ 维度1（四家 L1 为负、L2/L3 为正；CRITICAL 跨度 18.2pp、L3 边际 +9.3）→
  维度2（F 是共同短板：−5.1~−23.5；E 是甜点：+4.8~+9.3；K 上 MISLEADING 最高 +11.2）→ 维度3（落差
  ENCOURAGE 12.6 / MISLEADING 9.8 / HEURISTIC 3.6 / PRESSURE 3.6 / CRITICAL 0.6）→ η² 维度解释力
  （CRITICAL 由层级主导 .54，ENCOURAGE/MISLEADING/HEURISTIC 由对象主导 .50/.50/.43，起点状态最小
  .02~.11）→ 逐型 12×5 主表 → 单策略画像五段 → 限制 → 结论段。
- 过程校验：写作时逐条回查数据，修掉 8 处口径/范围笔误（F 边际区间、L2-F 口径混淆、L2-R/L3-R 的 R 轴
  叙述、L1-E 负值归属等），现文中所有数字均与 _fig2_stats.py 输出一致。
- 数值来源脚本 _fig2_stats.py 一并交付。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
