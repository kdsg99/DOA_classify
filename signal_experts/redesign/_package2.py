# -*- coding: utf-8 -*-
"""补发 D4/D5 机制图 + 更新总结；追加一条增补记录（幂等）。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
FIGS = r"C:\Users\kl001\.nanobot\figs"
for f in ["D4_mechanism_pressure.png", "D5_mechanism_all.png"]:
    shutil.copy2(os.path.join(R, "fig_effect", f), os.path.join(FIGS, "eff_" + f))
    print("copied eff_" + f, "%.0f KB" % (os.path.getsize(os.path.join(FIGS, "eff_" + f)) / 1024))
shutil.copy2(os.path.join(R, "summary_effect_v4.md"), os.path.join(FIGS, "summary_effect_v4.md"))
print("summary updated")

REC = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-20 增补：D3 指标详解"
txt = open(REC, encoding="utf-8").read()
if mark in txt:
    print("增补记录已存在，跳过")
else:
    entry = """
### 2026-09-20 增补：D3 指标详解（用户提问「D3 的指标是什么 / 为什么 PRESSURE 校正后更低」）
- D3 指标定义：逐策略拟合 delta_pp = b0 + b1·plain_pp（PRESSURE +56.49−0.847, R²0.45；ENCOURAGE +61.82−1.213；
  CRITICAL +68.16−1.232；MISLEADING +56.43−1.206；HEURISTIC +64.13−1.348）；
  校正值 = 该格实际均值 − (b0 + b1·该格 plain 均值)，即「与同难度期望相差多少」（恒等式已校验 1e-15）。
- PRESSURE 校正后 −0.4 → −8.9pp 的原因：其链式推演行 plain 均值 56.7，比该策略全体 64.6 低 7.9pp（五策略中唯一
  显著偏易的一格），该难度档期望为 +8.5pp，实际只有 −0.4pp → 差 8.9pp。其它四策略的同类行反而偏难（+0.4~+5.6），
  期望本身 −21~−49pp，故校正后抬升到 −12~−17pp。PRESSURE 拟合线最平（−0.847）且 R² 最低，基准线本身较弱。
- 数据构成提醒：PRESSURE 仅 408 行（其它 524~690），chat_math500 只覆盖 29 个任务（其它 94~231），其中 19 行 easy
  （plain 57.9, Δ−15.8）、10 行 hard（plain 10.0, Δ+80.0）→「链式推演」标签跨策略并非同一批题，跨策略比同格需谨慎。
- 稳健性：双扣除（delta ~ plain + 族）后链式推演仅剩 PRESSURE −7.3 / ENCOURAGE −2.4 / CRITICAL −3.1 /
  MISLEADING −1.4 / HEURISTIC −1.2pp；目标动作缩到 +1.1/+1.1/−6.6/+2.9pp → 现设计下动作效应过半是族差异。
- 新增产物：fig_effect\\D4_mechanism_pressure.png、D5_mechanism_all.png（机制示意）；脚本 d3_explain.py、d3_explain_fig.py；
  summary_effect_v4.md 已补写「D3 指标详解」「为什么 PRESSURE 校正后更低」「族双扣除」三节。
"""
    open(REC, "a", encoding="utf-8").write(entry)
    print("appended addendum, now %.1f KB" % (os.path.getsize(REC) / 1024))
