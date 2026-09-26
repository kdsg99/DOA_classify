# -*- coding: utf-8 -*-
"""追加 command_record.md（幂等）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补三：12 类思维类型 × 策略场景分析（新文件夹）"
e = """

### 2026-09-20 增补三：12 类思维类型 × 策略场景分析（新文件夹）
- 用户要求重开文件夹，回到最初的 12 类 thinking type（classifier.py）与三个类别维度（元认知层/结构层/执行层），
  看每个策略擅长什么类型，出三张图（原始 / 去难度 / 去难度+数量无关），图内文字用英文。
- 新目录：C:\\Users\\kl001\\.nanobot\\DOA\\thinking_type_scenarios\\（data / out / figs + tt_scenario_analysis.py、
  make_figs.py、summarize.py、README.md、scenarios.md）；输入 = signal_experts\\all_tasks_with_thinking_type.csv 的副本（2801 行）。
- 三个口径：v1 raw = 各格 mean Δ(pp)；v2 去难度 = 各策略内 Δ~plain 线性拟合后的残差均值（R²=0.45~0.55）；
  v3 去难度+数量无关 = v2 残差按评测族等权平均（每族一票，消除样本量与族分布影响），另给 lodo_range 稳健性列。
- 主要结果：raw 下五策略一律「元认知层最好、执行层最差」（PRESSURE +19.9/+0.3；HEURISTIC −28.4/−32.1），属难度混淆；
  去难度后整体转正或接近 0（PRESSURE +5.9、CRITICAL +8.2、ENCOURAGE +6.4、HEURISTIC +5.5、MISLEADING +3.6）。
  去难度+等权后的层均值：CRITICAL 元认知 +15.4 / 结构 +9.9 / 执行 +2.2（最高且最均衡）；PRESSURE 元认知 +14.7、执行 −1.0；
  ENCOURAGE +13.2/+6.0/+11.2；HEURISTIC 执行 +14.7（噪声大）；MISLEADING +8.7/+7.2/+2.5。
  三版一致的稳定增益：Long-context fidelity、Style preserving、Expression expansion；三版一致偏差：Execution-limited、
  Full-reasoning dependent（去难度后仍偏负）。薄格提示：Strict verification n=1~2、Reviewable repair n=4~6、
  Trajectory sensitive n=2~6；lodo_range>10pp 的格（如 ENCOURAGE 的 Execution-limited，raw −60.5 → balanced +13.1）
  属族驱动噪声，不可单独解读。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("已追加，%.1f KB" % (os.path.getsize(p) / 1024))
