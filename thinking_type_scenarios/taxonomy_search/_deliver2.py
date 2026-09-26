# -*- coding: utf-8 -*-
"""交付：拷贝图与报告到 .nanobot\\figs（tt4_*），并追加 command_record.md。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\taxonomy_search"
F = r"C:\Users\kl001\.nanobot\figs"
os.makedirs(F, exist_ok=True)
PAIRS = [("figs/figA_spec.png", "tt4_figA_spec.png"),
         ("figs/figB_taxonomy.png", "tt4_figB_taxonomy.png"),
         ("REPORT.md", "tt4_REPORT.md"),
         ("out/requirements_all.csv", "tt4_requirements_all.csv"),
         ("out/search_ranking.csv", "tt4_search_ranking.csv"),
         ("out/final_level.csv", "tt4_final_level.csv"),
         ("out/final_contrast5.csv", "tt4_final_contrast5.csv")]
for src, dst in PAIRS:
    shutil.copy2(os.path.join(H, src), os.path.join(F, dst))
    print("copied", dst)

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补七：反向推导 thinking type 分类（要求：策略反转 / PRESSURE 平且多为正 / 其他起伏大）"
e = """

### 2026-09-20 增补七：反向推导 thinking type 分类（要求：策略反转 / PRESSURE 平且多为正 / 其他起伏大）
- 用户指出「策略间没有反转、太趋同」，要求从三条要求出发反向总结出能达到该效果的 thinking type 分类。
- 把要求量化成 R1 反转/差异、R2 PRESSURE 平且多为正、R3 其他四家起伏大且只剩一两项特长、R4 拆半可复现，
  硬约束为每格每策略 >=25 个任务；搜索 40+ 个候选分类（v2 12 类、层级/目标/评测族、v4 思维动作、
  文本 TF-IDF 聚类 k=8..20 及层次聚类 J=4..8、以及与层级/格式/长度的交叉）+ 8 个随机分割作噪声地板。
- 关键结论：同任务上四家非 PRESSURE 策略的 Δ 相关 0.83-0.93（近似替代品），两两对比 SD≈23pp，
  所以策略×类型交互上限只有 ~2.5-3pp；反转只有内容型分类能过噪声地板（R1 0.22-0.42 vs 随机 0.08-0.12），
  且 R2「PRESSURE 平」只在 3 类型粗分类下成立（SD<=2.6pp），一旦要其他四家起伏>=5.8pp，PRESSURE 的 SD
  也升到 5.6-6.4pp —— 两条要求互相拉扯。改前的 v2 12 类拆半复现最差（R4=0.05），其 -77pp 的 L1-F 只有 2 个任务。
- 反向总结的规格：主轴必须是「交付物体裁」（代码/格式转换、开放写作与建议、技能约束短答、核验纠错、数理），
  再加「输出是否受格式约束」第二轴；粒度必须粗（每格每策略 >=25 题，类型数 <=7-8）；差异必须在「同一任务内互比」
  的坐标系里读；并逐格给 n / 置信区间 / 拆半复现率。
- 推荐实例（体裁×输出约束，6 格）：PRESSURE 5/6 格为正、均值 +1.5pp、SD 6.3pp（五家最平）；
  CRITICAL 仅在 code/format×受约束 +3.0、open prose×受约束 +0.2 可用；ENCOURAGE/MISLEADING/HEURISTIC
  6 格里 5 格为负且各有 1 格崩掉（-15~-25pp）；同任务互比坐标系下出现 3 对符号反转
  （CRITICAL↔ENCOURAGE、ENCOURAGE↔HEURISTIC、MISLEADING↔HEURISTIC），拆半一致率 0.71-1.00。
- 下一步建议：想稳定呈现 5pp 级反转，每格需 >=100 个任务（当前最大格 138-151 题，其余 25-60 题）；
  更根本的是让策略不近似替代（现相关 0.83-0.93），即改为针对不同干预对象的策略。
- 产物：DOA\\thinking_type_scenarios\\taxonomy_search\\（step1..step12*.py、out\\requirements_all.csv、
  out\\search_ranking.csv、out\\final_level.csv、out\\final_contrast5.csv(+_se)、figs\\figA_spec.png、
  figs\\figB_taxonomy.png、REPORT.md）；副本 C:\\Users\\kl001\\.nanobot\\figs\\tt4_*。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
