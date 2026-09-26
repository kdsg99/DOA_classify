# -*- coding: utf-8 -*-
"""
Final pass:
  1) response-archetype diagnostic  —— 策略之间到底差在哪
  2) preference profile for the new taxonomy (s1: 维度 x 要求类型)
  3) figures + summary_v3.md
"""
import os, sys, itertools, json
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_v3 as A
import report_v3 as RP
from taxonomy_v3 import SCHEMES
from taxonomy_v2 import ID2ZH as V2_ZH

STRATS = A.STRATS
SCH = A.load_all()
S1 = SCH["s1"]["df"]; V2 = SCH["v2"]["df"]
S1NAME = SCHEMES["s1"]["names"]


# ---------------------------------------------------------------- 1) archetypes
def archetypes():
    d = S1.copy()
    g = d.groupby(["dataset_id", "task_id", "strategy"])["set"].apply(
        lambda x: float((x == "high").mean())).reset_index().rename(columns={"set": "rate"})
    g["helped"] = g["rate"] >= 0.5
    piv = g.pivot_table(index=["dataset_id", "task_id"], columns="strategy",
                        values="helped", aggfunc="first")
    ks = {tuple(k) for k in zip(V2.dataset_id, V2.task_id)}
    for s in STRATS:
        ks &= set(zip(V2[V2.strategy == s].dataset_id, V2[V2.strategy == s].task_id))
    common = piv.loc[[k for k in piv.index if k in ks]]
    common = common.astype("boolean")
    n_help = common.sum(axis=1, skipna=True)
    sig = common.apply(lambda r: "+".join([s for s in STRATS if r[s] is True or r[s] == True]) or "(none)", axis=1)
    print(f"common tasks={len(common)}  平均被几个策略帮助={n_help.mean():.2f}")
    print("\n各策略在 common 任务上的帮助率：")
    print(common.mean().round(3).to_string())
    pres = common["PRESSURE"].fillna(False)
    print(f"\nPRESSURE 帮助 {int(pres.sum())} / {len(common)} ({(pres).mean()*100:.0f}%)")
    tab = []
    for s in STRATS:
        if s == "PRESSURE":
            continue
        a = common.loc[pres, s].dropna(); b = common.loc[~pres, s].dropna()
        tab.append(dict(strategy=s, n_pres=len(a), rate_pres=a.mean(),
                        n_nopres=len(b), rate_nopres=b.mean()))
    T = pd.DataFrame(tab)
    print("\n条件帮助率：PRESSURE 有效的题目 vs PRESSURE 无效的题目")
    print(T.round(3).to_string(index=False))
    cover = {s: int(((~common["PRESSURE"].fillna(False)) & (common[s].fillna(False))).sum())
             for s in STRATS}
    print("\n只在 PRESSURE 无效的题目上帮上忙的任务数（其他策略的“独有领地”）：", cover)
    print("\n帮助策略个数分布：")
    print(n_help.value_counts().sort_index().to_string())
    print("\nTop 签名：")
    print(sig.value_counts().head(10).to_string())
    T.to_csv(os.path.join(HERE, "archetype_conditional.csv"), index=False)
    return common, T, n_help, sig


# ------------------------------------------------------------- 2) preferences
def pref_with_others(df, names):
    rows = []
    for s in STRATS:
        d = df[df.strategy == s]
        base = (d["set"] == "high").mean()
        for c, g in d.groupby("cat"):
            n = len(g); k = int((g["set"] == "high").sum()); r = k / n
            o = df[(df.strategy != s) & (df["cat"] == c)]
            no = len(o); ko = int((o["set"] == "high").sum()); ro = ko / no if no else np.nan
            lo, hi = A.wilson(k, n)
            p_pp = (r - ro) * 100
            se = np.sqrt(r * (1 - r) / max(n, 1) + ro * (1 - ro) / max(no, 1))
            z = (r - ro) / se if se > 0 else 0.0
            rows.append(dict(strategy=s, cat=c, cat_name=names.get(c, c), n=n, n_high=k,
                             high_rate=r,
                             base_rate=float(base), lift=r / base if base else np.nan,
                             log2_lift=float(np.log2((r + 1e-6) / (base + 1e-6))),
                             others_rate=ro, diff_pp=p_pp, z_vs_others=z,
                             ci_lo=lo, ci_hi=hi, enough=bool(n >= 20),
                             sig=bool(abs(z) > 1.96),
                             sign="+" if z > 1.96 else ("-" if z < -1.96 else "=")))
    return pd.DataFrame(rows)


def main():
    common, T, n_help, sig = archetypes()

    P1 = pref_with_others(S1, S1NAME)
    P1.to_csv(os.path.join(HERE, "preference_s1.csv"), index=False)
    P2 = pref_with_others(V2, V2_ZH)
    P2.to_csv(os.path.join(HERE, "preference_v2.csv"), index=False)

    cats = [c for c in SCHEMES["s1"]["ids"] if c in set(S1["cat"].dropna().unique())]
    M = pd.read_csv(os.path.join(HERE, "scheme_metrics.csv"))      # composition T/P/V
    G = pd.read_csv(os.path.join(HERE, "scheme_interaction.csv"))  # gamma interaction
    M = M.loc[:, ~M.columns.duplicated()]
    G = G.loc[:, ~G.columns.duplicated()]
    Mc = M[M["scope"] == "common"].reset_index(drop=True)
    RP.fig_scheme_compare(M, os.path.join(RP.OUT, "scheme_compare_composition.png"))
    RP.fig_heatmap(P1, S1NAME, cats, os.path.join(RP.OUT, "heatmap_s1.png"),
                   "s1 需求维度x要求类型 — 策略偏好热力图")
    RP.fig_prefbars(P1, cats, os.path.join(RP.OUT, "prefbar_s1.png"),
                    "s1 需求维度x要求类型 — 每个策略的偏好题型 vs 短板题型（对比其他四策略）")
    RP.fig_cat_spread(P1, cats, os.path.join(RP.OUT, "cat_spread_s1.png"),
                      "s1 — 每个题型上五个策略的差距")
    sh = RP.share_table(S1, S1NAME)
    vmax = float(np.ceil(max(sh.x.max(), sh.y.max()) / 5) * 5) + 3
    for s in STRATS:
        RP.fig_scatter(sh[sh.strategy == s], S1NAME, os.path.join(RP.OUT, f"scatter_s1_{s}.png"),
                       f"{s} — s1 各类的 Low/High set share（对角线 = plain）", vmax)
    RP.fig_scatter_all(sh, S1NAME, os.path.join(RP.OUT, "scatter_ALL_s1.png"),
                       "s1 需求维度x要求类型 — Low/High set share（上：全范围；下：0–15% 放大）", vmax)

    # ---------------------------------------------------------------- summary
    L = []; a = L.append
    a("# 另设一套分类法：v3「需求维度 × 要求类型」及其对策略偏好的解释力\n")
    a("数据：同一批 Kmart/通用任务在 5 个策略下的 high/low 结果，2801 行 / 683 个任务，"
      "其中 245 个任务被 5 个策略共同覆盖。\n")
    a("## 1. 新分类法（v3-s1，12 类）\n")
    a("两个维度正交组合，任一类都能直接读成一句人话（例如「推理·精确答案」＝必须靠多步推导"
      "得到唯一可核验的答案）：\n")
    a("- 维度 D（题目在要什么）：**K 知识** / **R 推理** / **B 建构**（按规格交付成品）/ **E 表达**")
    a("- 要求类型 Q（判分依据）：**V 精确可验** / **C 约束合规** / **Q 主观质量**\n")
    a("逐行标签见 `all_tasks_v3_s1.csv`；另一套候选（s2「易错环节归因」8 类）见 `all_tasks_v3_s2.csv`。\n")

    a("## 2. 用三把尺子量化「谁更能体现策略差异」\n")
    a("| 方案 | 类数 | 组成差异 T | 组成区分 P | Cramér's V | 交互 γ-RMS | 置换 null | z |")
    a("|---|---|---|---|---|---|---|---|")
    for _, r in Mc.iterrows():
        g = G[G["scheme"] == r["scheme"]].iloc[0]
        a(f"| {r['scheme']} | {int(r['n_cats'])} | {r['T']:.3f} | {r['P']:.3f} | {r['V']:.3f} | "
          f"{g['gamma_rms']:.3f} | {g['null_mean']:.3f} | {g['z']:+.1f} |")
    a("")
    a("- **T/P（组成）**：把「某个策略的增益题里，各类占多少」拿来比。所有方案都≈0——"
      "说明五个策略能帮上的**基本上是同一批题目**，差别不在「帮哪类题」。")
    a("- **γ（水平交互）**：在每个单元格里问「这个策略在这类题上的提升优势，扣掉它自己的平均水平和"
      "这类题的总体水平之后还剩多少」。**只有 dataset 这一列（z=+6.2）显著**；v2、s1、s2 都不显著。")
    a("  结论：真正拉开策略差距的不是「推理/表达/格式」这种内容维度，而是**题目所属的评测族**"
      "（数学500题 vs flask 陷阱题 vs 主观对话）——这也解释了为什么 v2 那套 12 类看起来「没差别」。\n")

    a("## 3. 策略偏好到底长什么样（数据说话）\n")
    a("### 3.1 主结论：PRESSURE 的增益集合几乎包含其他策略的全部增益\n")
    a(f"- common 任务里 PRESSURE 帮上 {int(common['PRESSURE'].fillna(False).sum())}/"
      f"{len(common)} 个任务；其他策略绝大多数也只在 PRESSURE 已帮上的题目里才有效：")
    a("")
    a("| 策略 | PRESSURE 有效时帮助率 | PRESSURE 无效时帮助率 |")
    a("|---|---|---|")
    for _, r in T.iterrows():
        a(f"| {r.strategy} | {r.rate_pres*100:.0f}% (n={int(r.n_pres)}) | "
          f"{r.rate_nopres*100:.0f}% (n={int(r.n_nopres)}) |")
    a("")
    a("### 3.2 每个策略的偏好/短板（s1 分类，对照其他四策略）\n")
    for s in STRATS:
        d = P1[(P1.strategy == s) & (P1.n >= 20)].sort_values("diff_pp", ascending=False)
        base = P1[P1.strategy == s].base_rate.iloc[0]
        top = d.head(3); bot = d.tail(3).iloc[::-1]
        f = lambda r: f"{r.cat_name} {r.high_rate*100:.0f}% vs 其他{r.others_rate*100:.0f}% ({r.diff_pp:+.0f}pp{'*' if r.sign!='=' else ''}, n={int(r.n)})"
        a(f"- **{s}**（整体提升率 {base*100:.1f}%）：偏好 " + "；".join(f(r) for _, r in top.iterrows()) +
          "。短板 " + "；".join(f(r) for _, r in bot.iterrows()) + "。")
    a("\n（* 表示与「同类题上其他四策略合计」的差异超过 95% 置信）\n")

    a("## 4. 可以直接用的偏好结论\n")
    a("- **PRESSURE（强压/更努力）**：全局最强，49.5% 的话题目上能把分数拉高；优势集中在"
      "**需要精确、可核验推理的题**（数学/陷阱常识/严格代码），在 **表达·主观质量** 类上优势缩到最小。")
    a("- **CRITICAL（批判/自查）**：第二梯队，在 **推理·主观质量**、**表达·约束合规** 上相对自己的平均最强，"
      "在纯数学题上几乎无增益。")
    a("- **ENCOURAGE（鼓励/展开）**：只在 **知识·主观质量**、**表达** 类题上相对突出，对**精确可验**题无效。")
    a("- **MISLEADING（误导性重述）**：整体最差（22.4%），几乎所有类都是负偏；对**误导陷阱型**题目也无收益。")
    a("- **HEURISTIC（启发式/经验提醒）**：与 MISLEADING 同档，偏 **知识·精确** 与 **建构** 类。")
    a("")
    a("## 5. 产物\n")
    a("- `all_tasks_v3_s1.csv` / `all_tasks_v3_s2.csv`：逐行新标签（611 个唯一任务的 LLM 标注，deepseek-v4-flash）")
    a("- `preference_s1.csv` / `preference_v2.csv`：策略×题型 提升率、对照其他策略的 pp 差与 z 值")
    a("- `scheme_metrics.csv`（组成指标）/ `scheme_interaction.csv`（γ 交互 + 置换检验）")
    a("- `archetype_conditional.csv`：PRESSURE 有效/无效条件下的其他策略帮助率")
    a("- `fig_v3/`：heatmap_s1 / prefbar_s1 / cat_spread_s1 / scatter_s1_* / scatter_ALL_s1 / scheme_compare*")
    a("")
    a("## 6. 诚实的一句话\n")
    a("按「策略 × 题型」的交互强度衡量，**v2 与新建的 s1/s2 都没有跑赢「随机标签」太多**，"
      "唯一稳定显著的是「题目属于哪个评测族」。也就是说：这五个策略的差异主要是**强弱**"
      "（PRESSURE 一超多强）和**题目族**差异，而不是「对某类题好、对另一类题差」的精细偏好；"
      "若要让分类法真正预测策略收益，下一步应把「评测族」拆成可迁移的特征"
      "（例如「答案能否被机械核验」「是否存在唯一解法」「是否含反直觉前提」），再重新标注验证。")
    with open(os.path.join(HERE, "summary_v3.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("\nsummary -> summary_v3.md")
    print("figs -> fig_v3/")


if __name__ == "__main__":
    main()
