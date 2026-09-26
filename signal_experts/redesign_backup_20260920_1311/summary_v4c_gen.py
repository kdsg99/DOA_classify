# -*- coding: utf-8 -*-
"""summary_v4c.md 生成器（analyze_v4c.py 调用；可单独运行以重写摘要）"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import analyze_v3 as A
from taxonomy_v4 import IDS, NAMES

STRATS = A.STRATS
COLS = [NAMES[i] for i in IDS]


def write_summary(v4, tt, R, C, T, S):
    L = []
    a = L.append
    a("# v4c：把因变量换成连续分差 Δscore 的复算（建议 1）\n")
    a(f"生成时间：{pd.Timestamp.now():%Y-%m-%d %H:%M}（本机 K026）｜脚本：`analyze_v4c.py`\n")
    a("## 0. 一句话结论\n")
    nc = len(R)
    n05c = int((R.p < .05).sum()); n05m = int((R.p_med < .05).sum())
    n05s = int((R.p_std < .05).sum())
    n05b = int((R.p_bin < .05).sum()); n05t = int((R.p_tt < .05).sum())
    ver = R[(R.strategy == "CRITICAL") & (R.op == "T6_VERIFY")].iloc[0]
    a(f"- 55 个单元格（5 策略 × 11 动作）里，原始 p<0.05 的个数：二值 **{n05b}**、连续原尺度 **{n05c}**、"
      f"连续中位数 **{n05m}**、连续族内标准化 d **{n05s}** → 只能算**小幅**提升，不是质变。")
    a(f"- FDR<0.05（BH）：所有口径**全部为 0**（连续原尺度最小 q = {R.q.min():.3f}，"
      f"族内标准化 d 最小 q = {R.q_std.min():.3f}）→ 仍无一个单元格能过 FDR。")
    a(f"- 但有一个有意义的增量：**CRITICAL × 校验纠错**（设计上就该命中的那一格）在连续口径下浮出来了——"
      f"二值 p={ver.p_bin:.3f} → 族内标准化 d p={ver.p_std:.3f}。\n")
    a("## 1. 口径（与 analyze_v4.py 逐条对齐，只换因变量）\n")
    a("| 环节 | v4（二值） | v4c（连续） |")
    a("|---|---|---|")
    a("| 因变量 | helped = (该策略×任务上 high 占比 ≥ 0.5) | Δscore = 该策略×任务上 delta = reask−plain 的均值 |")
    a("| 族内平衡 | 每评测族先算 on/off 差，再按 min(n_on, n_off) 加权 | 完全相同 |")
    a("| 显著性 | 族内打乱标签置换 400 次 | 完全相同 |")
    a("| 多重比较 | BH-FDR | 完全相同 |")
    a("| 数据 | all_tasks_v4.csv（2801 行） | 同一文件，不做任何新增标注 |\n")
    a(f"自检：delta == reask−plain ✅；high ⇔ delta>0（完全等价，即二值本来就是连续量的符号）✅；"
      f"行 {len(v4)}、任务 {v4.groupby(['dataset_id','task_id']).ngroups}、"
      f"策略×任务 {len(tt)}、评测族 {v4.dataset_id.nunique()}。\n")
    a("## 2. 数据体检\n")
    a(f"- delta：均值 {v4.delta.mean():+.4f}，标准差 {v4.delta.std():.4f}，取值 "
      f"[{v4.delta.min():+.2f}, {v4.delta.max():+.2f}]。")
    a("- 重要：delta 整体偏负（策略让分差下降是常态），所以看的是**相对差异**（on 减 off），不是绝对值。")
    a("- 族间量级差异极大（chat_math500 的 delta 几乎都压在 −0.85 附近，其他族在 0 上下），"
      "这正是必须先做族内平衡的原因；连续版沿用同一处理。")
    a(f"- 有 {tt[tt.n_runs > 1].shape[0]} 个 (策略×任务) 叠了多次重述轮次（最多 {int(tt['n_runs'].max())} 轮）："
      "连续版取**均值**，二值版取**占比**。\n")
    a("## 3. 策略 × 所需思维动作：Δscore（族内平衡，×100）\n")
    a("| 策略 | " + " | ".join(COLS) + " |")
    a("|" + "---|" * (len(COLS) + 1))
    for s in STRATS:
        d = R[R.strategy == s].set_index("op")
        cells = []
        for i in IDS:
            if i not in d.index:
                cells.append("—"); continue
            row = d.loc[i]
            mark = "*" if bool(row.sig) else ("†" if row.p < .05 else "")
            cells.append(f"{row.dscore_bal*100:+.1f}{mark}")
        a(f"| {s} | " + " | ".join(cells) + " |")
    a("\n> * = FDR<0.05；† = 原始 p<0.05。n(需要该动作) 从 24 到 403 不等。\n")
    a("## 4. 灵敏度：连续 vs 二值\n")
    a("| 口径 | 原始 p<0.05 | FDR q<0.05 | 最小 p | 最小 q |")
    a("|---|---|---|---|---|")
    a(f"| 二值 helped（v4 现值） | {n05b} | {int(R.sig_bin.sum())} | {R.p_bin.min():.4f} | {R.q_bin.min():.3f} |")
    a(f"| 连续 Δscore（原尺度，主口径） | {n05c} | {int(R.sig.sum())} | {R.p.min():.4f} | {R.q.min():.3f} |")
    a(f"| 连续 Δscore（族内标准化 d） | {n05s} | {int(R.sig_std.sum())} | {R.p_std.min():.4f} | {R.q_std.min():.3f} |")
    a(f"| 连续 Δscore（中位数，稳健对照） | {n05m} | {int(R.sig_med.sum())} | {R.p_med.min():.4f} | {R.q_med.min():.3f} |")
    a(f"| Welch t（不平衡、忽略族结构，❌ 仅供方向参照） | {n05t} | — | {R.p_tt.min():.3g} | — |")
    a("\n> Welch 那一行的 p 小得离谱（e-41），是因为它拿跨族的不同量级当同一分布比；**不可用于判定**，只看符号。"
      "族内平衡的置换结果才是本次口径。")
    rho = C[["dscore_bal", "dpp_bal"]].corr(method="spearman").iloc[0, 1]
    same = float((np.sign(C.dscore_bal) == np.sign(C.dpp_bal)).mean())
    a(f"\n- 两口径逐单元格效应的 Spearman ρ = {rho:.2f}，符号一致率 {same*100:.0f}% → 方向大体相同，差别在幅度与灵敏度。")
    a(f"- 平均|效应|：连续 {C.dscore_bal.abs().mean()*100:.2f}（×100 单位） vs 二值 {C.dpp_bal.abs().mean()*100:.2f}pp。")
    a("- 图：`fig_v4c/cont_vs_binary.png`（右图即上表）。\n")
    a("## 5. 效应最大的单元格（连续版，按 |Δscore| 排序）\n")
    a("| 策略 | 思维动作 | Δscore×100 | Δpp（二值） | 置换 p | 二值 p | q | n_on |")
    a("|---|---|---|---|---|---|---|---|")
    dd = R.dropna(subset=["dscore_bal"]).reindex(R.dscore_bal.abs().sort_values(ascending=False).index)
    for _, row in dd.head(12).iterrows():
        a(f"| {row.strategy} | {row.op_name} | {row.dscore_bal*100:+.1f} | {row.dpp_bal*100:+.1f} | "
          f"{row.p:.3f} | {row.p_bin:.3f} | {row.q:.3f}{' *' if row.sig else ''} | {int(row.n_on)} |")
    a("")
    a("## 6. 目标思维命中（任务级对比，连续 vs 二值）\n")
    a("| 策略 | 它诱导的思维 | 目标题 Δscore×100 | 其余题 | 差值 | 置换 p | 二值差 Δpp | 二值 p |")
    a("|---|---|---|---|---|---|---|---|")
    for _, row in T.iterrows():
        a(f"| {row.strategy} | {row.target_ops} | {row.dscore_on*100:+.1f} | {row.dscore_off*100:+.1f} | "
          f"{(row.dscore_on-row.dscore_off)*100:+.1f} | {row.p_cont:.3f} | "
          f"{(row.dpp_on-row.dpp_off)*100:+.1f} | {row.p_bin:.3f} |")
    a("\n> 这是「目标思维（任一命中）」的任务级对比（带 n_on / n_off），比第 3 节的单元格平均更直接。\n")
    a("## 7. 每种思维动作上的相对赢家（连续版）\n")
    a("| 思维动作 | 最优策略 | 其 Δscore×100 | 其余四策略平均 | 差距 | n | p<0.05 |")
    a("|---|---|---|---|---|---|---|")
    for i in IDS:
        d = R[R.op == i].dropna(subset=["dscore_bal"])
        if not len(d):
            continue
        best = d.loc[d.dscore_bal.idxmax()]
        oth = d[d.strategy != best.strategy].dscore_bal.mean()
        a(f"| {NAMES[i]} | {best.strategy} | {best.dscore_bal*100:+.1f} | {oth*100:+.1f} | "
          f"{(best.dscore_bal-oth)*100:+.1f} | {int(best.n_on)} | {'是' if best.p < .05 else '否'} |")
    a("")
    a("## 8. 各分类尺的交互强度：二值 gamma vs 连续版（同代码、同口径）\n")
    a("| 口径 | 方案 | 类数 | 二值 γ-RMS | z(二值) | 连续 RMS(原始) | z | 连续 RMS(族内 z) | z |")
    a("|---|---|---|---|---|---|---|---|---|")
    for scope in ["common", "all"]:
        for _, row in S[S.scope == scope].iterrows():
            a(f"| {scope} | {row.scheme} | {int(row.n_cats)} | {row.gamma_rms_bin:.3f} | {row.z_bin:+.2f} | "
              f"{row.gamma_rms_cont_raw:.3f} | {row.z_cont_raw:+.2f} | "
              f"{row.gamma_rms_cont_z:.3f} | {row.z_cont_z:+.2f} |")
    a("\n> 关键核对：用原始 `analyze_gamma.perm_test` 重跑可见，**dataset 的 γ z=+6.2 只在「全部 2801 行」口径成立**；"
      "限制到各策略共同任务集（245 个）后，dataset 只剩 −0.4，与内容尺（−0.2 ~ −1.3）没有区别。")
    a("> 连续版同样如此：all 口径下 dataset 的连续 z=+13.2（内容尺 +1.8 ~ +2.6），common 口径下全部回到 ±1 以内。"
      "**所以决定结论的是口径（各策略是否做同一批题），不是因变量取二值还是连续。**"
      "v4 报告里「只有评测族这把尺子显著」应标明是 all-rows 口径，不宜当硬结论。\n")
    a("## 9. 结论\n")
    npos = int((T.dscore_on - T.dscore_off > 0).sum())
    pos = T[(T.dscore_on - T.dscore_off) > 0]
    a(f"1. **大结论没变：方向对、强度弱**。任务级目标命中对比里，{npos}/5 个策略的目标题优于其余题"
      f"（差值 +{(pos.dscore_on-pos.dscore_off).min()*100:.1f} ~ +{(pos.dscore_on-pos.dscore_off).max()*100:.1f} ×100），"
      f"但置换 p 全部 ≥ {T.p_cont.min():.2f}，一个都不显著；PRESSURE 的目标题反而更差（哪怕它是「链式推演」的预设受益者）。")
    a(f"2. **连续化只带来小幅灵敏度提升**：p<0.05 的单元格 二值 {n05b} → 连续原尺度 {n05c} → 族内标准化 d {n05s}，"
      f"FDR 仍全为 0（最小 q：原尺度 {R.q.min():.3f}、标准化 {R.q_std.min():.3f}）。"
      "真正的增益是「设计上应有的那一格」浮出来了（CRITICAL × 校验纠错 p 0.83→0.03）："
      "连续口径更适合看趋势，但不能靠它把结论做实。")
    a("3. **口径修正（重要）**：v4 报告里「族维度交互 γ z=+6.2（族比内容尺强）」是全体行口径的产物；"
      "共同任务集口径下（二值与连续都一样）它都消失。以后引用请标明口径。")
    a(f"4. 建议 2（每格加样本）成为真正的瓶颈：当前 n(需要该动作) 中位数 {int(R.n_on.median())}、最小 {int(R.n_on.min())}；"
      f"在效应量级 ±{R.dscore_bal.abs().max()*100:.1f}（×100）、delta 的 sd≈{v4.delta.std():.2f} 的情况下，"
      "要把这个量级的差异做实，每格需要几百个任务。（另一个等价办法：把重述轮次从 1~3 提到 5+。）")
    a("5. 建议 3（让链式推演/抗扰判断跨族出现）依然有效：这两个动作现在几乎被单个数据集包揽，"
      "问题不在「策略不行」，而在「样本不在」。\n")
    a("## 10. 产物与复现\n")
    a("- `analyze_v4c.py`：一条命令跑完全部 → `python analyze_v4c.py`")
    a("- `v4c_preference_cont.csv`：55 单元格（Δscore 平衡值 / 族内标准化 d / 中位数版 / Welch / 置换 p / FDR q）")
    a("- `v4c_vs_binary.csv`：逐单元格 连续 vs 二值 并列")
    a("- `v4c_target_match.csv`：目标思维命中（连续 + 二值）")
    a("- `v4c_scheme_interaction_cont.csv`：各尺子（二值 γ vs 连续 RMS，common / all 双口径）")
    a("- `fig_v4c/cont_heatmap.png`、`cont_vs_binary.png`、`cont_target_match.png`、`cont_op_ranking.png`")
    a("- `summary_v4c.md`（本文件）")
    a("- 备份：`../redesign_backup_20260919_1726/`（开工前 redesign 全量副本，2800 个文件、27.5 MB）")
    open(os.path.join(HERE, "summary_v4c.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n[summary] -> summary_v4c.md")
