# -*- coding: utf-8 -*-
"""交付英文版四份文档 + 更新后的中文策略画像（含新增 §0 高层总结）。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
DEL = r"C:\Users\kl001\.nanobot\deliver"
for src, dst in [(r"en\fig2_design.md", "fig2_design.md"),
                 (r"en\fig2_types_table.md", "fig2_types_table.md"),
                 (r"en\fig2_strategy_findings.md", "fig2_strategy_findings.md"),
                 (r"en\difficulty_correction.md", "difficulty_correction.md"),
                 ("FIG2_STRATEGY_FINDINGS.md", "FIG2_STRATEGY_FINDINGS.md")]:
    shutil.copy2(os.path.join(H, src), os.path.join(DEL, dst))
    print("deliver\\%-28s %6.0f KB" % (dst, os.path.getsize(os.path.join(DEL, dst)) / 1024))

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-22 增补十三：策略画像补高层「思维位移」总结 + 四份文档英文化"
e = """

### 2026-09-22 增补十三：策略画像补高层「思维位移」总结 + 四份文档英文化
- 用户反馈：strategy-finding 只在描述客观事实，缺高层总结；要求补"某策略擅长激发…思维方式，把 LLM
  thinking 往…方面 adapt"这类总结；并把 fig2 系列三份 md 与 difficulty correction 的 md 全部改成英文。
- 中文 FIG2_STRATEGY_FINDINGS.md 新增 §0「高层总结：每个策略把模型思维往哪里 adapt」：
  表 0.1 五策略思维位移画像（激发的思维模式 / 位移方向 / 收益来源 / 代价 / 一句话定位）：
  PRESSURE = 思维零位移的重演器；CRITICAL = 把模型改造成审阅者（元认知专精）；ENCOURAGE = 推向表达性
  发散（内容扩张）；MISLEADING = 推向证据核验与立场辩护（有锚点则抗、无锚点则崩）；HEURISTIC = 推向
  线索驱动的局部修补（最温和，代价是替代独立判断）。
  表 0.2 位移量三刻度（层级跨度 / 对象轴最强最弱 / 起点落差 / SD / 绝对均值）。
  跨策略三规律：①层级律「再问是再加工不是再执行」；②对象律「内容扩张与约束满足此消彼长」；
  ③起点律「修订优于重建，位移越大越依赖锚」。末尾附摘要级一段小结。
- 英文版四份（en\\ 目录，方法：逐段翻译 + 数字逐条核对；顺带把 tt6 脚本名更新为 make_figs_tt7.py，
  图目录 figs_tt7）：fig2_design.md、fig2_types_table.md、fig2_strategy_findings.md（含英文 §0）、
  difficulty_correction.md。
- 交付：deliver\\ 下四份英文 md + 更新后的中文 FIG2_STRATEGY_FINDINGS.md。
- 数值核对：层级跨度 ENCOURAGE 由 15.1 更正为 15.2（max−min = 5.1−(−10.1)）。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
