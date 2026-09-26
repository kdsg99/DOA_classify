# -*- coding: utf-8 -*-
"""v4 效应量分析（方案 A/B/C/E/D）—— 取代份额视图。

定义
----
delta = reask_minmax − plain_minmax（同题同模型配对差，单位 pp）= 该策略在该题上的效应
A  每策略动作效应森林图（Δ 均值 + 95% CI，0 线 + 该策略自身基线）
B  5×11 效应热力图（primary / multilabel）
C  效应量 vs 暴露度散点（x = 该动作行数占比，y = Δ pp）
E  目标命中度汇总（目标动作 vs 非目标动作，行级置换检验 + 动作级等权枚举）
D  分层稳健性：按评测族 / 按难度（plain 高低的头寸）分层；以及扣除"难度余量"的线性校正效应
"""
import itertools
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import numpy as np                                                   # noqa: E402
import pandas as pd                                                  # noqa: E402
import matplotlib                                                    # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                      # noqa: E402
from scipy import stats                                              # noqa: E402
from taxonomy_v4 import IDS, NAMES, TARGET                           # noqa: E402

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

FIG = os.path.join(R, "fig_effect")
os.makedirs(FIG, exist_ok=True)
STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
MODES = ["primary", "multilabel"]
CBAR = plt.get_cmap("RdBu")
VMAX, VMIN = 30, -70

LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s)


# ---------------------------------------------------------------- 数据
df = pd.read_csv(os.path.join(R, "all_tasks_v4.csv"))
df["delta_pp"] = 100 * df["delta"]
df["plain_pp"] = 100 * df["plain_minmax"]
df["family"] = df["dataset_id"]
df["diff"] = df["original_difficulty"]
df["hr_tercile"] = pd.qcut(df["plain_minmax"], 3, labels=["plain低", "plain中", "plain高"])
log("数据：%d 行；策略 %s；族 %d；难度档 %d" % (len(df), list(df.strategy.unique()),
    df.family.nunique(), df.hr_tercile.nunique()))


def is_target(s, t):
    return t in TARGET[s]["ops"]


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    q = np.full(n, np.nan)
    m = np.isfinite(p)
    if m.sum() == 0:
        return q
    pp = p[m]
    order = np.argsort(pp)
    prev = 1.0
    out = np.empty(len(pp))
    for rank, i in enumerate(order[::-1]):
        k = len(pp) - rank
        prev = min(prev, pp[i] * len(pp) / k)
        out[i] = prev
    q[m] = out
    return q


def rows_of(sub, s, t, mode):
    ss = sub[sub.strategy == s]
    if mode == "primary":
        return ss[ss.primary == t]
    return ss[ss["o_" + t].astype(bool)]


def cells(data, mode, by=()):
    by = list(by)
    out = []
    groups = data.groupby(by) if by else [((), data)]
    for key, sub in groups:
        key = key if isinstance(key, tuple) else (key,)
        for s in STRATS:
            for t in IDS:
                g = rows_of(sub, s, t, mode)
                n = len(g)
                m = 100 * g.delta.mean() if n else np.nan
                se = 100 * g.delta.std(ddof=1) / np.sqrt(n) if n >= 2 else np.nan
                p = 2 * stats.t.sf(abs(m / se), n - 1) if (n >= 2 and np.isfinite(se) and se > 0) else np.nan
                out.append(dict(zip(by or ["_all"], key)) | dict(strategy=s, action=t, n=n,
                                                                 mean_pp=m, se_pp=se, p=p))
    t = pd.DataFrame(out)
    t["lo"] = t.mean_pp - 1.96 * t.se_pp
    t["hi"] = t.mean_pp + 1.96 * t.se_pp
    key = by + ["strategy"]
    t["q_strat"] = np.nan
    for _k, g in t.groupby(key):
        t.loc[g.index, "q_strat"] = bh(g["p"])
    t["q_all"] = bh(t["p"])
    base = {s: 100 * data[data.strategy == s].delta.mean() for s in STRATS}
    t["base_pp"] = t.strategy.map(base)
    t["net_pp"] = t.mean_pp - t.base_pp
    t["target"] = [is_target(s, a) for s, a in zip(t.strategy, t.action)]
    return t


MAIN = {m: cells(df, m) for m in MODES}
EFF = {}

# ---------------------------------------------------------------- 画图工具
def stars(q):
    if not np.isfinite(q):
        return ""
    return "**" if q < 0.05 else ("*" if q < 0.1 else "")


def draw_forest(ax, g, s, base, mode, ylabels=True):
    ys = np.arange(len(IDS))[::-1]
    ax.axvline(0, color="#222", lw=1.6, zorder=1)
    gg = g.set_index("action").reindex(IDS)
    for i, (t, r) in enumerate(gg.iterrows()):
        y = ys[i]
        col = "#C0392B" if r.target else "#3B6FB6"
        if np.isfinite(r.se_pp) and r.n > 1:
            ax.plot([r.lo, r.hi], [y, y], "-", color=col, lw=2.2, alpha=0.85, zorder=3)
        if r.n:
            ax.scatter(r.mean_pp, y, s=22 + r.n * 0.5, color=col, zorder=4,
                       edgecolors="k", linewidths=0.6)
        st = stars(r.q_strat)
        txt = ("%s%d" % (st, r.n)) if r.n else "0"
        ax.annotate(txt, (max(r.hi, 0) if np.isfinite(r.hi) else 0, y), fontsize=6.4, color=col,
                    xytext=(3, 0), textcoords="offset points", ha="left", va="center", zorder=6)
    ax.axvline(base, color="#1F7A4D", ls="--", lw=1.5, zorder=2)
    ax.set_xlim(-88, 38)
    ax.set_ylim(-0.8, len(IDS) - 0.2)
    ax.grid(True, axis="x", alpha=0.22)
    if ylabels:
        ax.set_yticks(ys)
        ax.set_yticklabels(["%s %s" % (t.split("_")[0], NAMES[t]) for t in IDS], fontsize=9.5)
    else:
        ax.set_yticks([])
    ax.set_xlabel("Δ score (pp) = reask − plain，95% CI", fontsize=10)
    ax.set_title("%s（自身基线 %+.1f pp）" % (s, base), fontsize=13, fontweight="bold")


# ================================================================ A 森林图
for mode in MODES:
    T = MAIN[mode]
    for s in STRATS:
        fig, ax = plt.subplots(figsize=(9.6, 6.4))
        draw_forest(ax, T[T.strategy == s], s, T[T.strategy == s].base_pp.iloc[0], mode)
        fig.suptitle("A. %s 的动作效应森林图（%s 口径）：点大小=n，红=目标动作，"
                     "绿虚线=该策略整体基线" % (s, mode), fontsize=13.5)
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(os.path.join(FIG, "A_forest_%s_%s.png" % (s, mode)), dpi=135, bbox_inches="tight")
        plt.close(fig)
    fig, axes = plt.subplots(1, 5, figsize=(31, 8.6), sharey=True)
    for ax, s in zip(axes, STRATS):
        draw_forest(ax, T[T.strategy == s], s, T[T.strategy == s].base_pp.iloc[0], mode, ylabels=(s == STRATS[0]))
    fig.suptitle("A. 五策略动作效应森林图（%s 口径）：点大小=n，红=该策略目标动作，"
                 "绿虚线=该策略自身基线，黑线=0（vs plain）" % mode, fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.925])
    fig.savefig(os.path.join(FIG, "A_forest_ALL_%s.png" % mode), dpi=135, bbox_inches="tight")
    plt.close(fig)
log("A 森林图完成（%d 张）" % (2 * 6))

# ================================================================ B 热力图
for mode in MODES:
    T = MAIN[mode]
    M = np.full((len(STRATS), len(IDS)), np.nan)
    Q = np.full_like(M, np.nan)
    N = np.zeros_like(M, int)
    for i, s in enumerate(STRATS):
        g = T[T.strategy == s].set_index("action")
        for j, t in enumerate(IDS):
            M[i, j], Q[i, j], N[i, j] = g.loc[t, "mean_pp"], g.loc[t, "q_strat"], int(g.loc[t, "n"])
    fig, ax = plt.subplots(figsize=(18, 4.8))
    im = ax.imshow(M, cmap=CBAR, vmin=VMIN, vmax=VMAX, aspect="auto")
    ax.set_xticks(range(len(IDS)))
    ax.set_xticklabels(["%s\n%s" % (t.split("_")[0], NAMES[t]) for t in IDS], fontsize=9.5)
    ax.set_yticks(range(len(STRATS)))
    ax.set_yticklabels(STRATS, fontsize=11)
    for i in range(len(STRATS)):
        for j in range(len(IDS)):
            ax.text(j, i, "%.0f%s\nn=%d" % (M[i, j], stars(Q[i, j]), N[i, j]), ha="center",
                    va="center", fontsize=7.8, color="#111")
    for i, s in enumerate(STRATS):
        for j, t in enumerate(IDS):
            if is_target(s, t):
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, ec="k", lw=2.6))
    cb = fig.colorbar(im, ax=ax, pad=0.012)
    cb.set_label("Δ score (pp)", fontsize=10)
    ax.set_title("B. 策略 × 思维动作 效应热力图（%s 口径）：格子=Δ 与 n，黑框=该策略目标动作，"
                 "**q<0.05 *q<0.10（策略内 11 格 BH）" % mode, fontsize=13)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "B_heat_%s.png" % mode), dpi=135, bbox_inches="tight")
    plt.close(fig)
log("B 热力图完成（2 张）")

# ================================================================ C 效应-暴露度散点
for mode in MODES:
    T = MAIN[mode]
    fig, ax = plt.subplots(figsize=(12.4, 8.2))
    ax.axhline(0, color="#222", lw=1.5)
    cols = plt.get_cmap("tab10").colors
    for k, s in enumerate(STRATS):
        g = T[T.strategy == s]
        Ntot = len(df[df.strategy == s])
        x = 100 * g.n / Ntot
        ax.plot(x, g.mean_pp, ls="--", lw=0.8, color=cols[k], alpha=0.45, zorder=2)
        ax.scatter(x, g.mean_pp, s=30 + g.n * 0.55, color=cols[k], alpha=0.85, zorder=4,
                   edgecolors="k", linewidths=0.6, label="%s（基线 %+.1f pp）" % (s, g.base_pp.iloc[0]))
        ax.axhline(g.base_pp.iloc[0], color=cols[k], ls=":", lw=1.1, alpha=0.7)
        gg = g[g.n >= 5].sort_values("mean_pp")
        keep = set(list(gg.index[:2]) + list(gg.index[-2:]) + list(g[g.target].index))
        for _i, r in g.iterrows():
            if r.n >= 5 and _i in keep:
                w = "bold" if r.target else "normal"
                ax.annotate("%s %s" % (r.action.split("_")[0], NAMES[r.action]),
                            (100 * r.n / Ntot, r.mean_pp), fontsize=6.8, color="#222",
                            fontweight=w, xytext=(5, 4), textcoords="offset points")
        tg = g[g.target]
        ax.scatter(100 * tg.n / Ntot, tg.mean_pp, s=60 + tg.n * 0.55, facecolors="none",
                   edgecolors="#C0392B", linewidths=2.0, zorder=5)
    ax.set_xlabel("暴露度 = 该动作行数占该策略总行数的比例 (%)", fontsize=11.5)
    ax.set_ylabel("效应量 Δ score (pp) = reask − plain", fontsize=11.5)
    ax.set_title("C. 效应量 vs 暴露度（%s 口径）：红圈=该策略目标动作；点大小=n；"
                 "点线=各策略自身基线" % mode, fontsize=13)
    ax.legend(fontsize=9.5, loc="lower right")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "C_scatter_effect_exposure_%s.png" % mode), dpi=135, bbox_inches="tight")
    plt.close(fig)
log("C 散点完成（2 张）")

# ================================================================ E 目标命中度
rng = np.random.default_rng(20260920)
hit_all = {}
for mode in MODES:
    recs = []
    for s in STRATS:
        sub = df[df.strategy == s]
        tg = [t for t in IDS if is_target(s, t)]
        if mode == "primary":
            flag = sub.primary.isin(tg).values
        else:
            flag = sub[["o_" + t for t in tg]].astype(bool).any(axis=1).values
        d = sub.delta_pp.values
        obs = d[flag].mean() - d[~flag].mean()
        B = 20000
        perm = np.empty(B)
        for b in range(B):
            f = rng.permutation(flag)
            perm[b] = d[f].mean() - d[~f].mean()
        p_row = (1 + np.sum(np.abs(perm) >= abs(obs))) / (1 + B)
        # 动作级（等权，仅 n>=5 的动作）
        T = MAIN[mode]
        g = T[(T.strategy == s) & (T.n >= 5)]
        means = g.set_index("action").mean_pp
        tgt = [t for t in means.index if is_target(s, t)]
        oth = [t for t in means.index if not is_target(s, t)]
        obs_a = means[tgt].mean() - means[oth].mean()
        combos = list(itertools.combinations(means.index, len(tgt)))
        diffs = [means[list(c)].mean() - means[[x for x in means.index if x not in c]].mean()
                 for c in combos]
        p_act = np.mean(np.abs(diffs) >= abs(obs_a) - 1e-12)
        recs.append(dict(strategy=s, n_target=int(flag.sum()), n_non=int((~flag).sum()),
                         target_actions="、".join(NAMES[t] for t in tg),
                         mean_target=d[flag].mean(), mean_non=d[~flag].mean(), diff=obs,
                         p_perm_row=p_row, diff_act_eq=obs_a, p_act_enum=p_act,
                         n_combos=len(combos)))
        log("E[%s] %-10s 目标 %s" % (mode, s, "、".join(NAMES[t] for t in tg)))
        log("        行级：目标 %+.2f pp (n=%d) vs 非目标 %+.2f pp (n=%d) → 差 %+.2f pp，置换 p=%.4f"
            % (d[flag].mean(), flag.sum(), d[~flag].mean(), (~flag).sum(), obs, p_row))
        log("        动作级等权：差 %+.2f pp，枚举 p=%.4f（%d 种组合）" % (obs_a, p_act, len(combos)))
    H = pd.DataFrame(recs)
    hit_all[mode] = H
    fig, ax = plt.subplots(figsize=(11.6, 5.6))
    xs = np.arange(len(STRATS))
    ax.bar(xs - 0.19, H.mean_target, 0.38, color="#C0392B", label="目标动作（行级均值）")
    ax.bar(xs + 0.19, H.mean_non, 0.38, color="#3B6FB6", label="非目标动作（行级均值）")
    ax.axhline(0, color="#222", lw=1.3)
    for i, r in H.iterrows():
        ax.annotate("差 %+.1f pp\np=%.3f" % (r["diff"], r.p_perm_row), (i, max(r.mean_target, r.mean_non)),
                    fontsize=8.6, ha="center", va="bottom",
                    bbox=dict(fc="white", ec="#999", lw=0.6, alpha=0.85))
    ax.set_xticks(xs)
    ax.set_xticklabels(["%s\n（目标：%s）" % (r.strategy, r.target_actions) for _i, r in H.iterrows()],
                       fontsize=9)
    ax.set_ylabel("Δ score (pp)", fontsize=11)
    ax.set_title("E. 目标命中度：目标动作 vs 非目标动作的效应差（%s 口径，行级 20000 次置换检验）" % mode,
                 fontsize=12.5)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "E_target_hit_%s.png" % mode), dpi=135, bbox_inches="tight")
    plt.close(fig)
log("E 完成（2 张）")

# ================================================================ D 分层稳健性
FAM = sorted(df.family.unique())
for mode in MODES:
    # D1 按评测族
    TF = cells(df, mode, by=("family",))
    TF.to_csv(os.path.join(R, "strat_family_%s.csv" % mode), index=False, encoding="utf-8-sig")
    fig, axes = plt.subplots(len(STRATS), 1, figsize=(19, 4.0 * len(STRATS)))
    for ax, s in zip(axes, STRATS):
        g = TF[TF.strategy == s]
        M = np.full((len(FAM), len(IDS)), np.nan)
        Q = np.full_like(M, np.nan)
        for i, f in enumerate(FAM):
            gi = g[g.family == f].set_index("action")
            for j, t in enumerate(IDS):
                M[i, j], Q[i, j] = gi.loc[t, "mean_pp"], gi.loc[t, "q_strat"]
        im = ax.imshow(M, cmap=CBAR, vmin=VMIN, vmax=VMAX, aspect="auto")
        ax.set_xticks(range(len(IDS)))
        ax.set_xticklabels([NAMES[t] for t in IDS], fontsize=8.5)
        ax.set_yticks(range(len(FAM)))
        ax.set_yticklabels(FAM, fontsize=8.5)
        for i in range(len(FAM)):
            for j in range(len(IDS)):
                ax.text(j, i, "%.0f%s" % (M[i, j], stars(Q[i, j])), ha="center", va="center",
                        fontsize=7.2, color="#111")
        for j, t in enumerate(IDS):
            if is_target(s, t):
                ax.add_patch(plt.Rectangle((j - .5, -.5), 1, len(FAM), fill=False, ec="k", lw=2.2))
        ax.set_title("%s（黑框列=目标动作）" % s, fontsize=12, fontweight="bold")
    cb = fig.colorbar(im, ax=axes, pad=0.008, fraction=0.02)
    cb.set_label("Δ score (pp)", fontsize=10)
    fig.suptitle("D1. 按评测族分层：族 × 动作 的 Δ（%s 口径），* q<0.10 ** q<0.05（族内 11 格 BH）" % mode,
                 fontsize=15)
    fig.savefig(os.path.join(FIG, "D1_family_%s.png" % mode), dpi=130, bbox_inches="tight")
    plt.close(fig)

    # D2 按难度（plain 高低的头寸三分位）
    TD = cells(df, mode, by=("hr_tercile",))
    TD.to_csv(os.path.join(R, "strat_difficulty_%s.csv" % mode), index=False, encoding="utf-8-sig")
    rows_ord = ["plain低", "plain中", "plain高"]
    fig, axes = plt.subplots(1, len(STRATS), figsize=(30, 4.6), sharey=True)
    for ax, s in zip(axes, STRATS):
        g = TD[TD.strategy == s]
        M = np.full((3, len(IDS)), np.nan)
        for i, f in enumerate(rows_ord):
            gi = g[g.hr_tercile == f].set_index("action")
            for j, t in enumerate(IDS):
                M[i, j] = gi.loc[t, "mean_pp"]
        im = ax.imshow(M, cmap=CBAR, vmin=VMIN, vmax=VMAX, aspect="auto")
        ax.set_xticks(range(len(IDS)))
        ax.set_xticklabels([NAMES[t] for t in IDS], fontsize=7.6, rotation=45, ha="right")
        ax.set_yticks(range(3))
        ax.set_yticklabels(rows_ord, fontsize=9)
        for i in range(3):
            for j in range(len(IDS)):
                if np.isfinite(M[i, j]):
                    ax.text(j, i, "%.0f" % M[i, j], ha="center", va="center", fontsize=7.2)
        for j, t in enumerate(IDS):
            if is_target(s, t):
                ax.add_patch(plt.Rectangle((j - .5, -.5), 1, 3, fill=False, ec="k", lw=2.2))
        ax.set_title(s, fontsize=12, fontweight="bold")
    cb = fig.colorbar(im, ax=axes, pad=0.008, fraction=0.02)
    cb.set_label("Δ score (pp)", fontsize=10)
    fig.suptitle("D2. 按难度分层（plain 分数三分位）：行=plain低/中/高，列=动作，%s 口径" % mode, fontsize=15)
    fig.savefig(os.path.join(FIG, "D2_difficulty_%s.png" % mode), dpi=130, bbox_inches="tight")
    plt.close(fig)

    # D3 扣除难度余量的线性校正（delta ~ plain，每策略一条回归线）
    adj = []
    fig, axes = plt.subplots(1, len(STRATS), figsize=(30, 7.6), sharey=True)
    for ax, s in zip(axes, STRATS):
        sub = df[df.strategy == s]
        x = sub.plain_pp.values
        y = sub.delta_pp.values
        b1, b0 = np.polyfit(x, y, 1)
        pred = b0 + b1 * x
        r = y - pred
        r2 = 1 - np.sum(r ** 2) / np.sum((y - y.mean()) ** 2)
        sub = sub.assign(resid=r)
        g = MAIN[mode][MAIN[mode].strategy == s].set_index("action")
        pslope = stats.linregress(x, y).pvalue
        ys = np.arange(len(IDS))[::-1]
        ax.axvline(0, color="#222", lw=1.5)
        for i, t in enumerate(IDS):
            yv = ys[i]
            raw = g.loc[t, "mean_pp"]
            ad = sub.loc[sub.primary == t, "resid"].mean() if mode == "primary" else \
                sub.loc[sub["o_" + t].astype(bool), "resid"].mean()
            col = "#C0392B" if is_target(s, t) else "#3B6FB6"
            ax.plot([raw, ad], [yv, yv], "-", color="#999", lw=1.6, zorder=2)
            ax.scatter(raw, yv, s=42, color=col, zorder=4, edgecolors="k", lw=0.5, label="原始 Δ" if i == 0 else None)
            ax.scatter(ad, yv, s=42, marker="D", color=col, alpha=0.55, zorder=4,
                       edgecolors="k", lw=0.5, label="难度校正后" if i == 0 else None)
            adj.append(dict(strategy=s, action=t, raw_pp=raw, adjusted_pp=ad, target=is_target(s, t)))
        ax.set_yticks(ys)
        ax.set_yticklabels([NAMES[t] for t in IDS], fontsize=9)
        ax.set_title("%s（斜率 %+.2f pp/分，p=%.1e，R²=%.2f）" % (s, b1, pslope, r2), fontsize=11.5,
                     fontweight="bold")
        ax.grid(alpha=0.25, axis="x")
        ax.set_xlim(-90, 45)
        ax.set_xlabel("Δ pp（圆=原始，菱=扣除 plain 余量后）", fontsize=9.5)
    axes[0].legend(fontsize=9, loc="lower left")
    fig.suptitle("D3. 难度余量校正：以 delta ~ plain 的线性拟合残差作为「与难度无关的效应」（%s 口径）" % mode,
                 fontsize=15)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(FIG, "D3_headroom_adjust_%s.png" % mode), dpi=130, bbox_inches="tight")
    plt.close(fig)
    pd.DataFrame(adj).to_csv(os.path.join(R, "adjust_%s.csv" % mode), index=False, encoding="utf-8-sig")

    # D1 的跨族一致性汇总
    cons = []
    for s in STRATS:
        for t in IDS:
            g = TF[(TF.strategy == s) & (TF.action == t) & (TF.n >= 5)]
            cons.append(dict(strategy=s, action=t, n_families=len(g), target=is_target(s, t),
                             mean_pp=100 * np.nan if not len(g) else np.average(g.mean_pp, weights=g.n),
                             n_neg=int((g.mean_pp < 0).sum()), n_pos=int((g.mean_pp > 0).sum())))
    pd.DataFrame(cons).to_csv(os.path.join(R, "consistency_family_%s.csv" % mode), index=False,
                              encoding="utf-8-sig")
log("D 完成（6 张图 + 3 组表/口径）")

# ---------------------------------------------------------------- 落盘
for mode in MODES:
    cols = ["strategy", "action", "n", "mean_pp", "se_pp", "lo", "hi", "p", "q_strat", "q_all",
            "base_pp", "net_pp", "target"]
    MAIN[mode][cols].to_csv(os.path.join(R, "effect_table_%s.csv" % mode), index=False,
                            encoding="utf-8-sig")
    hit_all[mode].to_csv(os.path.join(R, "target_hit_%s.csv" % mode), index=False, encoding="utf-8-sig")
open(os.path.join(R, "_run_effect.log"), "w", encoding="utf-8").write("\n".join(LOG))
log("产物目录：%s" % FIG)
