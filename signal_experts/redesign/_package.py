# -*- coding: utf-8 -*-
"""打包表格、复制总结到 figs、并把本次记录追加到 command_record.md。"""
import os
import shutil
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
FIGS = r"C:\Users\kl001\.nanobot\figs"
NANO = r"C:\Users\kl001\.nanobot"

tables = [f for f in sorted(os.listdir(R)) if f.endswith(".csv")
          and (f.startswith("effect_table_") or f.startswith("target_hit_") or f.startswith("strat_")
               or f.startswith("adjust_") or f.startswith("consistency_"))]
zp = os.path.join(FIGS, "effect_tables.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in tables:
        z.write(os.path.join(R, f), f)
print("zip:", zp, len(tables), "个表", "%.1f KB" % (os.path.getsize(zp) / 1024))
for f in tables:
    print("  -", f)

shutil.copy2(os.path.join(R, "summary_effect_v4.md"), os.path.join(FIGS, "summary_effect_v4.md"))
print("summary copied")

REC = os.path.join(NANO, "command_record.md")
entry = """
## 2026-09-20 v4 效应量分析（份额视图 → 效应量视图；方案 A/B/C/E/D 全部开工）
- 指令原文：把公平且能展现规律的画法详细说明 → 用户拍板「A+B+C+E+D 可以开工」
- 口径更正并正式化：不再用份额（构成比）散点，改用配对差值 delta = reask_minmax − plain_minmax（pp）；
  每格给 95% CI、n、策略内 11 格 BH-FDR；基准线同时画 0（vs plain）与该策略自身基线。
- A 森林图：primary 24/55 格、multilabel 33/55 格过 q<0.10。基线 PRESSURE +1.8（唯一为正）、CRITICAL −20.9、
  ENCOURAGE −28.8、MISLEADING −32.8、HEURISTIC −41.5 pp。
- E 目标命中（行级 2 万次置换）：ENCOURAGE +19.3 (p=0.0007)、CRITICAL +29.5 (p=0.0031)、HEURISTIC +29.5 (p<0.0001)、
  MISLEADING +10.3 (p=0.25；multilabel +15.1, p=0.030)、PRESSURE −3.4 (p=0.375，无命中)。
  动作级等权（枚举，n≥5 动作）全部不显著（分辨率只有 10~11 个动作）。
- D2 难度分层（plain 低/中/高）给出一条跨五策略单调规律：Δ 随题难单调变负（低档 +9~+23 → 高档 −52~−92 pp）。
- D3 扣除 plain 余量（delta ~ plain 线性残差）后：链式推演 −37~−63 pp 缩到 −9~−17 pp，仍是各策略最差动作；
  除 PRESSURE 外四个策略的目标动作全部转正（+1.3 ~ +21.5 pp）。
- D1 族分层显示链式推演的巨额负面几乎全部来自 chat_math500（−81~−96），其它族仅 −1~−26 → 动作与族纠缠。
- 产物：fig_effect\（24 张图）、effect_table_{primary,multilabel}.csv、target_hit_*.csv、strat_family_*.csv、
  strat_difficulty_*.csv、adjust_*.csv、consistency_family_*.csv、effect_analysis_v4.py、summary_effect_v4.md、
  _run_effect.log；开工前备份 redesign_backup_20260920_1311（33.1 MB / 2857 文件）。
"""
with open(REC, "a", encoding="utf-8") as fh:
    fh.write(entry)
print("appended to", REC, "%.1f KB" % (os.path.getsize(REC) / 1024))
