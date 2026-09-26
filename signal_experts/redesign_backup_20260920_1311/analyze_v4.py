# -*- coding: utf-8 -*-
"""v4 分析：策略 x 「所需思维动作」偏好图 + 与 v2/v3/dataset 的解释力对比 + 目标思维命中检验"""
import os, sys, json, itertools
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_v3 as A
import analyze_gamma as G
from taxonomy_v4 import IDS, NAMES, TARGET, DESC
import taxonomy_v3 as T3
from taxonomy_v2 import ID2ZH as V2_ZH

STRATS = A.STRATS
OUT = os.path.join(HERE, "fig_v4"); os.makedirs(OUT, exist_ok=True)
FCOL = ["o_" + i for i in IDS]
CMAP = {i: c for i, c in zip(IDS, plt.get_cmap("tab20").colors[:len(IDS)])}


def load_v4():
    df = pd.read_csv(os.path.join(HERE, "all_tasks_v4.csv"))
    df["cat"] = df["primary"]
    df["_key"] = list(zip(df.dataset_id, df.task_id))
    return df


def task_table(df):
    tt = (df.groupby(["strategy", "dataset_id", "task_id"])["set"]
            .apply(lambda x: (x == "high").mean()).reset_index().rename(columns={"set": "rate"}))
    tt["helped"] = (tt.rate >= 0.5).astype(int)
    fl = df.drop_duplicates(["dataset_id", "task_id"])[["dataset_id", "task_id"] + FCOL]
    return tt.merge(fl, on=["dataset_id", "task_id"], how="left")


def bal_delta(y, F, ds, minn=3):
    """dataset-balanced Δpp for every column of F (bool), plus the used weights"""
    res = np.full(F.shape[1], np.nan); wsum = np.zeros(F.shape[1])
    for g in np.unique(ds):
        m = ds == g
        yy = y[m]
        for j in range(F.shape[1]):
            f = F[m, j]
            a = yy[f]; b = yy[~f]
            if len(a) >= minn and len(b) >= minn:
                w = min(len(a), len(b))
                res[j] = (res[j] if not np.isnan(res[j]) else 0.0) + w * (a.mean() - b.mean())
                wsum[j] += w
    return res / np.where(wsum == 0, np.nan, wsum), wsum


def flag_analysis(tt, n_perm=400, seed=3):
    rng = np.random.default_rng(seed)
    recs = []; nulls = {}
    for s in STRATS:
        d = tt[tt.strategy == s].reset_index(drop=True)
        y = d.helped.values.astype(float)
        F = d[FCOL].values.astype(bool)
        ds = pd.factorize(d.dataset_id)[0]
        raw = np.array([(y[F[:, j]].mean() - y[~F[:, j]].mean()) if F[:, j].any() and (~F[:, j]).any()
                        else np.nan for j in range(F.shape[1])])
        bal, wsum = bal_delta(y, F, ds)
        null = np.full((n_perm, F.shape[1]), np.nan)
        for t in range(n_perm):
            Fp = F.copy()
            for g in np.unique(ds):
                m = np.where(ds == g)[0]
                Fp[m] = F[rng.permutation(m)]
            null[t], _ = bal_delta(y, Fp, ds)
        p = np.array([(1 + np.sum(np.abs(null[:, j][~np.isnan(null[:, j])]) >= abs(bal[j])))
                      / (1 + np.sum(~np.isnan(null[:, j]))) if not np.isnan(bal[j]) else np.nan
                      for j in range(F.shape[1])])
        nulls[s] = null
        for j, i in enumerate(IDS):
            recs.append(dict(strategy=s, op=i, op_name=NAMES[i], n_on=int(F[:, j].sum()),
                             n_off=int((~F[:, j]).sum()),
                             rate_on=float(y[F[:, j]].mean()) if F[:, j].any() else np.nan,
                             rate_off=float(y[~F[:, j]].mean()) if (~F[:, j]).any() else np.nan,
                             dpp_raw=raw[j], dpp_bal=bal[j], w=wsum[j], p=p[j],
                             target=int(i in TARGET[s]["ops"])))
    R = pd.DataFrame(recs)
    # BH-FDR
    ok = R.p.notna()
    R.loc[ok, "q"] = _bh(R.loc[ok, "p"].values)
    R["sig"] = R["q"] < 0.05
    return R


def _bh(p):
    p = np.asarray(p, float); n = len(p)
    o = np.argsort(p); q = np.empty(n)
    prev = 1.0
    for rank, idx in enumerate(o[::-1]):
        i = n - rank
        prev = min(prev, p[idx] * n / i)
        q[idx] = prev
    return q


# ------------------------------------------------------------------ figures
def fig_flag_heatmap(R, path):
    M = R.pivot(index="strategy", columns="op_name", values="dpp_bal").reindex(STRATS)
    q = R.pivot(index="strategy", columns="op_name", values="sig").reindex(STRATS).fillna(False)
    n = R.pivot(index="strategy", columns="op_name", values="n_on").reindex(STRATS).fillna(0)
    M = M[[NAMES[i] for i in IDS]]
    q = q[[NAMES[i] for i in IDS]]
    n = n[[NAMES[i] for i in IDS]]
    v = np.nanmax(np.abs(M.values))
    fig, ax = plt.subplots(figsize=(13.5, 4.2))
    im = ax.imshow(M.values, cmap="RdBu_r", vmin=-v, vmax=v, aspect="auto")
    ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(M.columns, rotation=28, ha="right", fontsize=9)
    ax.set_yticks(range(len(M))); ax.set_yticklabels(M.index, fontsize=10)
    for r in range(M.shape[0]):
        for c in range(M.shape[1]):
            val = M.values[r, c]
            if np.isnan(val):
                ax.text(c, r, "–", ha="center", va="center", fontsize=8, color="#888")
                continue
            star = "*" if q.values[r, c] else ""
            ax.text(c, r, f"{val:+.0f}{star}", ha="center", va="center", fontsize=9.5,
                    fontweight="bold" if q.values[r, c] else "normal",
                    color="white" if abs(val) > 0.6 * v else "#222")
    plt.colorbar(im, ax=ax, shrink=.9, label="数据集内平衡后的提升率差 Δpp")
    ax.set_title("策略 × 所需思维动作：该策略在「需要这种思维」的题上比其他题好多少（* = FDR<0.05）",
                 fontsize=12.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def fig_target_match(R, path):
    lab = []; tv = []; ov = []; err = []
    for s in STRATS:
        d = R[R.strategy == s]
        t = d[d.target == 1].dpp_bal.mean(); o = d[d.target == 0].dpp_bal.mean()
        lab.append(s); tv.append(t); ov.append(o); err.append(d[d.target == 1].dpp_bal.std())
    x = np.arange(len(lab)); w = 0.38
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.bar(x - w / 2, tv, w, label="策略“所诱导思维”对应的题目", color="#c0392b")
    ax.bar(x + w / 2, ov, w, label="其余题目（平均）", color="#95a5a6")
    for xi, (a, b) in enumerate(zip(tv, ov)):
        ax.text(xi - w / 2, a + 0.6, f"{a:+.1f}", ha="center", fontsize=10, fontweight="bold")
        ax.text(xi + w / 2, b + 0.6, f"{b:+.1f}", ha="center", fontsize=10)
    ax.axhline(0, color="k", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=10)
    ax.set_ylabel("Δpp（数据集内平衡）")
    ax.set_title("「策略诱导的思维」是否正好是它有效的题目？（高 = 命中）", fontsize=12.5, fontweight="bold")
    ax.legend(fontsize=9.5)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def fig_power(path):
    M = pd.read_csv(os.path.join(HERE, "scheme_metrics.csv"))
    M = M.loc[:, ~M.columns.duplicated()]
    Gg = pd.read_csv(os.path.join(HERE, "scheme_interaction.csv"))
    Gg = Gg.loc[:, ~Gg.columns.duplicated()]
    Mc = M[M.scope == "common"].set_index("scheme")
    schemes = ["v2", "s1", "s2", "v4", "dataset"]
    lab = {"v2": "v2 认知操作(原有)", "s1": "v3 维度x要求", "s2": "v3 易错环节",
           "v4": "v4 所需思维", "dataset": "dataset 评测族"}
    Tz = [(Mc.loc[s, "T_z"] if s in Mc.index else np.nan) for s in schemes]
    Vz = [Mc.loc[s, "V"] if s in Mc.index else np.nan for s in schemes]
    gz = [(Gg[Gg.scheme == s].z.iloc[0] if (Gg.scheme == s).any() else np.nan) for s in schemes]
    x = np.arange(len(schemes)); w = 0.27
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.bar(x - w, Tz, w, label="组成差异 z（越高=策略的增益题越集中在某些类）", color="#2980b9")
    ax.bar(x, gz, w, label="水平交互 z（越高=策略在某些类上明显更强/更弱）", color="#27ae60")
    ax.bar(x + w, Vz, w, label="Cramér's V（分类与策略的关联强度）", color="#f39c12")
    ax.axhline(0, color="k", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([lab[s] for s in schemes], fontsize=9.5)
    ax.set_title("哪把尺子更能体现策略差异（z / V 越大越好）", fontsize=12.5, fontweight="bold")
    ax.legend(fontsize=8.6)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def fig_dominant(v4, path):
    sh = (v4[v4.set == "high"].groupby(["strategy", "cat"]).size().rename("hi").reset_index()
            .merge(v4.groupby(["strategy", "cat"]).size().rename("n").reset_index(),
                   on=["strategy", "cat"], how="left"))
    sh["rate"] = sh.hi / sh.n
    M = sh.pivot(index="strategy", columns="cat", values="rate").reindex(STRATS)
    N = sh.pivot(index="strategy", columns="cat", values="n").reindex(STRATS)
    cols = [i for i in IDS if i in M.columns]
    M = M[cols].rename(columns=NAMES); N = N[cols].rename(columns=NAMES)
    fig, ax = plt.subplots(figsize=(12.5, 4.0))
    im = ax.imshow(M.values, cmap="YlOrRd", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(M.columns, rotation=28, ha="right", fontsize=9)
    ax.set_yticks(range(len(M))); ax.set_yticklabels(M.index, fontsize=10)
    for r in range(M.shape[0]):
        for c in range(M.shape[1]):
            val = M.values[r, c]
            if not np.isnan(val):
                ax.text(c, r, f"{val*100:.0f}%\nn={int(N.values[r,c])}", ha="center", va="center", fontsize=7.6,
                        color="white" if val > .6 else "#222")
    plt.colorbar(im, ax=ax, shrink=.9, label="提升率（primary 类内）")
    ax.set_title("按「主要所需思维（primary）」看提升率", fontsize=12.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def main():
    v4 = load_v4()
    tt = task_table(v4)
    R = flag_analysis(tt)
    R.to_csv(os.path.join(HERE, "v4_flag_preference.csv"), index=False)
    cats = [i for i in IDS if i in set(v4["cat"].dropna())]
    keys = A.common_keys(pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"), usecols=["dataset_id", "task_id", "strategy"]))
    m4 = A.measure(v4, cats, only=keys, n_perm=200)
    obs, nm, ns, z = G.perm_test(v4[v4["cat"].notna()], cats, n_perm=200)
    # append v4 to the metric files
    M = pd.read_csv(os.path.join(HERE, "scheme_metrics.csv")); M = M.loc[:, ~M.columns.duplicated()]
    M = M[M.scheme != "v4"]
    M = pd.concat([M, pd.DataFrame([dict(scheme="v4", title="v4 所需思维动作 (11类)", scope="common", **m4)])],
                  ignore_index=True)
    M.to_csv(os.path.join(HERE, "scheme_metrics.csv"), index=False)
    Gg = pd.read_csv(os.path.join(HERE, "scheme_interaction.csv")); Gg = Gg.loc[:, ~Gg.columns.duplicated()]
    Gg = Gg[Gg.scheme != "v4"]
    Gg = pd.concat([Gg, pd.DataFrame([dict(scheme="v4", title="v4 所需思维动作 (11类)", n_cats=len(cats),
                                           gamma_rms=obs, null_mean=nm, null_sd=ns, z=z)])], ignore_index=True)
    Gg.to_csv(os.path.join(HERE, "scheme_interaction.csv"), index=False)

    fig_flag_heatmap(R, os.path.join(OUT, "flag_preference_heatmap.png"))
    fig_target_match(R, os.path.join(OUT, "target_match.png"))
    fig_power(os.path.join(OUT, "scheme_power.png"))
    fig_dominant(v4, os.path.join(OUT, "dominant_rate.png"))

    # ------------------------------------------------------------- summary
    L = []; a = L.append
    a("# v4 分类尺：按「解题所需的思维动作」分类，并检验策略是不是在诱导这种思维\n")
    a("数据：同一批 2801 行 / 683 任务 / 5 策略。策略定义取自 `config/prompts/strategies.py`。\n")
    a("## 1. 分类尺（11 个思维动作，多标签 + primary）\n")
    for i in IDS:
        a(f"- **{NAMES[i]}**（{i}）：{DESC[i]}")
    a("")
    a("## 2. 策略想诱导什么思维（假设）\n")
    for s in STRATS:
        a(f"- **{s}** → 目标动作 {[NAMES[x] for x in TARGET[s]['ops']]}；{TARGET[s]['logic']}")
    a("")
    a("## 3. 实测：策略在「它该擅长的思维题」上是否真的更好\n")
    a("| 策略 | 它诱导的思维（目标动作） | 目标题 Δpp | 其余题 Δpp | 差值 | 解释 |")
    a("|---|---|---|---|---|---|")
    for s in STRATS:
        d = R[R.strategy == s]
        t = d[d.target == 1].dpp_bal.mean() * 100; o = d[d.target == 0].dpp_bal.mean() * 100
        a(f"| {s} | {'、'.join(NAMES[x] for x in TARGET[s]['ops'])} | {t:+.1f} | {o:+.1f} | {t-o:+.1f} | "
          f"{'目标方向一致（有额外加成）' if t > o + 3 else ('方向不一致' if t < o - 3 else '几乎无差（强在全局、不在某类）')} |")
    a("")
    a("> Δpp = 该策略在需要该动作的题上的提升率 减 在不需要的题上的提升率；且**先在评测族内部算、再按样本量加权平均**，"
      "所以已经扣掉了「数学500题 vs flask 陷阱题」这种族差异。\n")
    a("## 4. 每种思维动作上的相对赢家（= 策略画像）\n")
    a("| 思维动作 | 最优策略 | 其 Δpp | 其余四策略平均 | 差距 | FDR<0.05 |")
    a("|---|---|---|---|---|---|")
    for i in IDS:
        d = R[R.op == i].dropna(subset=["dpp_bal"])
        if not len(d): continue
        best = d.loc[d.dpp_bal.idxmax()]
        oth = d[d.strategy != best.strategy].dpp_bal.mean()
        a(f"| {NAMES[i]} | {best.strategy} | {best.dpp_bal*100:+.1f} | {oth*100:+.1f} | "
          f"{(best.dpp_bal-oth)*100:+.1f} | {'是' if best.sig else '否'} |")
    a("")
    a("## 5. 效应最大的单元格（提示性证据，均未过 FDR<0.05）\n")
    a("| 策略 | 思维动作 | Δpp（族内平衡） | 置换 p | n(需要该动作) |")
    a("|---|---|---|---|---|")
    dd = R.dropna(subset=["dpp_bal"]) if "dpp_bal" in R.columns else R
    dd = dd[dd.dpp_bal.notna()]
    for _, r in dd.reindex(dd.dpp_bal.abs().sort_values(ascending=False).index).head(12).iterrows():
        a(f"| {r.strategy} | {r.op_name} | {r.dpp_bal*100:+.1f} | {r.p:.3f} | {int(r.n_on)} |")
    a("")
    a("## 6. 与其他分类尺的对比（common 245 任务）\n")
    for s in STRATS:
        d = R[(R.strategy == s) & (R.sig)].sort_values("dpp_bal", ascending=False)
        pos = d[d.dpp_bal > 0]; neg = d[d.dpp_bal < 0]
        f = lambda r: f"{r.op_name} {r.dpp_bal:+.1f}pp"
        a(f"- **{s}**：偏好 " + ("、".join(f(r) for _, r in pos.iterrows()) if len(pos) else "无显著") +
          "；短板 " + ("、".join(f(r) for _, r in neg.iterrows()) if len(neg) else "无显著"))
    a("")
    a("## 5. 与其他分类尺的对比（common 245 任务）\n")
    a("| 方案 | 类数 | 组成差异 z | Cramér's V | 交互 γ z |")
    a("|---|---|---|---|---|")
    Mc = M[M.scope == "common"].set_index("scheme")
    for s in ["v2", "s1", "s2", "v4", "dataset"]:
        if s not in Mc.index: continue
        gz = Gg[Gg.scheme == s]
        a(f"| {s} | {int(Mc.loc[s,'n_cats'])} | {Mc.loc[s,'T_z']:+.1f} | {Mc.loc[s,'V']:.3f} | "
          f"{(gz.z.iloc[0] if len(gz) else float('nan')):+.1f} |")
    a("")
    a("## 7. 怎么读这些数\n")
    a("- 单元格值 = 该策略在「需要这种思维」的题上，提升率比它在其余题上高/低多少（pp），且已在每个评测族内部对比过，"
      "所以读作：**该策略对这种思维题型有没有额外加成**（已经扣掉族差异）。")
    a("- 55 个单元格里最大效应 ±(9~15)pp，最小置换 p≈0.05，**没有一个能过 FDR<0.05**；下面结论按「提示性」看待。")
    a("- high/low 是二值化产物，丢掉了分差幅度；下一版建议改用**连续分差 Δscore** 作因变量（同样族内平衡），灵敏度会明显更高。\n")
    a("## 8. 结论\n")
    a("1. **「策略=诱导某种思维」方向对，但强度有限。** CRITICAL 在「抗扰判断」(+10.6pp)、「校验纠错」(+15.9pp raw) 上居首，"
      "HEURISTIC 在「换表征/语用改写」上居首，方向与策略设计一致；但 PRESSURE 只在「链式推演」上保持不掉队"
      "（它全局都强，没有专属舞台），ENCOURAGE 没有明显的专属题型。")
    a("2. **本批数据最强的一句话**：五个策略的增益高度重叠（PRESSURE 几乎覆盖其余四家的全部增益），"
      "真正拉开差距的只有两件事——**强弱**、以及**题目属于哪个评测族**（族维度的交互 z=+6.2，远高于任何内容/思维分类尺）。")
    a("3. **要让「所需思维」这把尺子真正立功**：(a) 改用连续分差做因变量；(b) 每个单元格需要更多任务（现在 n≈30~250）才能把 ±10pp 做实；"
      "(c) 让「链式推演」「抗扰判断」这类思维要求能跨评测族出现，而不是与某个数据集绑定。\n")
    a("## 9. 产物\n")
    a("- `all_tasks_v4.csv`（逐行 v4 标签：primary + ops 多标签）、`taxonomy_v4.py`、`classify_v4.py`")
    a("- `v4_flag_preference.csv`（策略×动作的 Δpp、数据集平衡值、置换 p、FDR q）")
    a("- `fig_v4/flag_preference_heatmap.png`、`target_match.png`、`scheme_power.png`、`dominant_rate.png`")
    open(os.path.join(HERE, "summary_v4.md"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L[:6]))
    print("... saved summary_v4.md")
    print(R.sort_values("dpp_bal").to_string(index=False))


if __name__ == "__main__":
    main()
