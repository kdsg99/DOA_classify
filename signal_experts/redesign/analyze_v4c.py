# -*- coding: utf-8 -*-
"""
v4c 分析：把因变量从 high/low 二值换成连续分差 Δscore（建议 1）。

口径与 analyze_v4.py 完全一致，只换因变量：
  v4  : y = 该 (策略, 任务) 上 high 的比例 >= 0.5  → 0/1        （阈值化）
  v4c : y = 该 (策略, 任务) 上 delta = reask_minmax - plain_minmax 的均值（连续）
族内平衡加权、置换检验（族内打乱标签）、BH-FDR 全部沿用。

新增产物：
  v4c_preference_cont.csv     55 个 (策略 × 思维动作) 单元格的连续版效应
  v4c_vs_binary.csv           连续 vs 二值 逐单元格对比（含灵敏度统计）
  v4c_target_match.csv        目标思维命中检验（连续版 + 二值版并列）
  v4c_scheme_interaction_cont.csv  各分类尺的连续版"交互残差 RMS"与 z
  fig_v4c/*.png
  summary_v4c.md
"""
import os, sys, math
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
from taxonomy_v4 import IDS, NAMES, TARGET, DESC

STRATS = A.STRATS
OUT = os.path.join(HERE, "fig_v4c"); os.makedirs(OUT, exist_ok=True)
FCOL = ["o_" + i for i in IDS]
COLS = [NAMES[i] for i in IDS]


# ------------------------------------------------------------------ data
def load_v4():
    df = pd.read_csv(os.path.join(HERE, "all_tasks_v4.csv"))
    df["cat"] = df["primary"]
    df["_key"] = list(zip(df.dataset_id, df.task_id))
    return df


def task_table_cont(df):
    """每 (策略, 数据集, 任务) 一行：连续 y = mean(delta)，同时保留二值口径便于并列展示"""
    g = df.groupby(["strategy", "dataset_id", "task_id"])
    tt = g.agg(delta_mean=("delta", "mean"), delta_med=("delta", "median"),
               n_runs=("delta", "size")).reset_index()
    rate = (g["set"].apply(lambda x: (x == "high").mean())
              .reset_index().rename(columns={"set": "rate"}))
    tt = tt.merge(rate, on=["strategy", "dataset_id", "task_id"])
    tt["helped"] = (tt.rate >= 0.5).astype(int)
    fl = df.drop_duplicates(["dataset_id", "task_id"])[["dataset_id", "task_id"] + FCOL]
    return tt.merge(fl, on=["dataset_id", "task_id"], how="left")


# ------------------------------------------------------------------ core stats
def bal_delta(y, F, ds, minn=3, standardize=False):
    """族内平衡的 Δ（每族先算 on-off 差，再按 min(n_on,n_off) 加权平均）。
    standardize=True 时用族内合并标准差归一（Cohen's d 式）。"""
    res = np.full(F.shape[1], np.nan); wsum = np.zeros(F.shape[1])
    for gg in np.unique(ds):
        m = ds == gg
        yy = y[m]
        sd = None
        if standardize:
            sd = yy.std(ddof=0)
            if not np.isfinite(sd) or sd < 1e-12:
                continue
        for j in range(F.shape[1]):
            f = F[m, j]
            a = yy[f]; b = yy[~f]
            if len(a) >= minn and len(b) >= minn:
                w = min(len(a), len(b))
                d = (a.mean() - b.mean()) / (sd if standardize else 1.0)
                res[j] = (res[j] if not np.isnan(res[j]) else 0.0) + w * d
                wsum[j] += w
    return res / np.where(wsum == 0, np.nan, wsum), wsum


def _bh(p):
    p = np.asarray(p, float); n = len(p)
    o = np.argsort(p); q = np.empty(n); prev = 1.0
    for rank, idx in enumerate(o[::-1]):
        i = n - rank
        prev = min(prev, p[idx] * n / i)
        q[idx] = prev
    return q


def _welch_p(a, b):
    """Welch t 的正态近似 p 值（n 都在几十以上，够用）"""
    if len(a) < 2 or len(b) < 2:
        return np.nan
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    if se < 1e-12:
        return 1.0
    z = abs(a.mean() - b.mean()) / se
    return math.erfc(z / math.sqrt(2))


def perm_contrast(y, f, ds, n_perm, rng, standardize=False, minn=3):
    """单个对比（f 为 bool 向量）的族内平衡效应 + 置换 p"""
    obs, w = bal_delta(y, f[:, None], ds, minn=minn, standardize=standardize)
    nt = np.full(n_perm, np.nan)
    for t in range(n_perm):
        fp = f.copy()
        for gg in np.unique(ds):
            m = np.where(ds == gg)[0]
            fp[m] = f[rng.permutation(m)]
        v, _ = bal_delta(y, fp[:, None], ds, minn=minn, standardize=standardize)
        nt[t] = v[0]
    nv = nt[~np.isnan(nt)]
    p = np.nan
    if not np.isnan(obs[0]) and len(nv):
        p = (1 + np.sum(np.abs(nv) >= abs(obs[0]))) / (1 + len(nv))
    return dict(effect=float(obs[0]), w=float(w[0]), p=float(p))


def flag_analysis_cont(tt, n_perm=400, seed=3):
    """v4 flag_analysis 的连续版：同族内平衡 / 同置换 / 同 BH"""
    rng = np.random.default_rng(seed)
    recs = []
    for s in STRATS:
        d = tt[tt.strategy == s].reset_index(drop=True)
        y = d.delta_mean.values.astype(float)
        ymed = d.delta_med.values.astype(float)
        ybin = d.helped.values.astype(float)
        F = d[FCOL].values.astype(bool)
        ds = pd.factorize(d.dataset_id)[0]
        # 未平衡的原始均值差
        raw = np.array([(y[F[:, j]].mean() - y[~F[:, j]].mean())
                        if F[:, j].any() and (~F[:, j]).any() else np.nan
                        for j in range(F.shape[1])])
        bal, wsum = bal_delta(y, F, ds)
        bal_std, _ = bal_delta(y, F, ds, standardize=True)
        bal_med, _ = bal_delta(ymed, F, ds)
        bal_bin, _ = bal_delta(ybin, F, ds)
        null = np.full((n_perm, F.shape[1]), np.nan)
        null_std = np.full((n_perm, F.shape[1]), np.nan)
        null_med = np.full((n_perm, F.shape[1]), np.nan)
        null_bin = np.full((n_perm, F.shape[1]), np.nan)
        for t in range(n_perm):
            Fp = F.copy()
            for gg in np.unique(ds):
                m = np.where(ds == gg)[0]
                Fp[m] = F[rng.permutation(m)]
            null[t], _ = bal_delta(y, Fp, ds)
            null_std[t], _ = bal_delta(y, Fp, ds, standardize=True)
            null_med[t], _ = bal_delta(ymed, Fp, ds)
            null_bin[t], _ = bal_delta(ybin, Fp, ds)
        pv = np.full(F.shape[1], np.nan)
        pv_std = np.full(F.shape[1], np.nan)
        pv_med = np.full(F.shape[1], np.nan)
        pv_bin = np.full(F.shape[1], np.nan)
        for j in range(F.shape[1]):
            for arr, out, obs in ((null, pv, bal[j]), (null_std, pv_std, bal_std[j]),
                                  (null_med, pv_med, bal_med[j]), (null_bin, pv_bin, bal_bin[j])):
                v = arr[:, j][~np.isnan(arr[:, j])]
                if not np.isnan(obs) and len(v):
                    out[j] = (1 + np.sum(np.abs(v) >= abs(obs))) / (1 + len(v))
        for j, i in enumerate(IDS):
            on = y[F[:, j]]; off = y[~F[:, j]]
            recs.append(dict(strategy=s, op=i, op_name=NAMES[i],
                             n_on=int(F[:, j].sum()), n_off=int((~F[:, j]).sum()),
                             dscore_on=float(on.mean()) if len(on) else np.nan,
                             dscore_off=float(off.mean()) if len(off) else np.nan,
                             dscore_raw=raw[j], dscore_bal=bal[j], w=wsum[j],
                             dscore_std=bal_std[j], dscore_med_bal=bal_med[j],
                             dpp_bal=bal_bin[j],
                             p=pv[j], p_std=pv_std[j], p_med=pv_med[j], p_bin=pv_bin[j],
                             p_tt=_welch_p(on, off),
                             target=int(i in TARGET[s]["ops"])))
    R = pd.DataFrame(recs)
    for col, qcol in (("p", "q"), ("p_med", "q_med"), ("p_std", "q_std"), ("p_bin", "q_bin")):
        ok = R[col].notna()
        R.loc[ok, qcol] = _bh(R.loc[ok, col].values)
    R["sig"] = R["q"] < 0.05
    R["sig_med"] = R["q_med"] < 0.05
    R["sig_std"] = R["q_std"] < 0.05
    R["sig_bin"] = R["q_bin"] < 0.05
    return R


# --------------------------------------------------- 目标思维命中（任务级对比）
def target_contrast(tt, n_perm=400, seed=11):
    rng = np.random.default_rng(seed)
    rows = []
    for s in STRATS:
        d = tt[tt.strategy == s].reset_index(drop=True)
        y = d.delta_mean.values.astype(float)
        ybin = d.helped.values.astype(float)
        ops = TARGET[s]["ops"]
        f = d[["o_" + i for i in ops]].values.astype(bool).any(axis=1)
        ds = pd.factorize(d.dataset_id)[0]
        a = perm_contrast(y, f, ds, n_perm, rng)
        b = perm_contrast(ybin, f, ds, n_perm, rng)
        rows.append(dict(strategy=s, target_ops="/".join(NAMES[i] for i in ops),
                         n_on=int(f.sum()), n_off=int((~f).sum()),
                         dscore_on=float(y[f].mean()), dscore_off=float(y[~f].mean()),
                         dscore_bal=a["effect"], w=a["w"], p_cont=a["p"],
                         dpp_on=float(ybin[f].mean()), dpp_off=float(ybin[~f].mean()),
                         dpp_bal=b["effect"], p_bin=b["p"]))
    T = pd.DataFrame(rows)
    ok = T.p_cont.notna()
    T.loc[ok, "q_cont"] = _bh(T.loc[ok, "p_cont"].values)
    ok = T.p_bin.notna()
    T.loc[ok, "q_bin"] = _bh(T.loc[ok, "p_bin"].values)
    return T


# ----------------------------- 各分类尺：二值 gamma 复现 + 连续版交互（同代码同口径）
def _bin_cells(T, cats, relabel=None):
    """T: 任务级表，列 strategy/dataset_id/task_id/cat/n_high/n。
    relabel: 可选的新策略标签（置换检验用）。"""
    s = T.strategy.values if relabel is None else np.asarray(relabel)
    K = np.zeros((len(STRATS), len(cats))); N = np.zeros((len(STRATS), len(cats)))
    ci = {c: i for i, c in enumerate(cats)}
    for k, st in enumerate(STRATS):
        m = s == st
        for c, g in T[m].groupby("cat"):
            j = ci.get(c)
            if j is None:
                continue
            N[k, j] = g.n.sum(); K[k, j] = g.n_high.sum()
    return K, N


def _fit_logit_rms(K, N):
    """analyze_gamma.fit_gamma 的同口径复制：log-odds 上的加权 LS，权 = N·p(1-p)"""
    mask = N > 0
    p = (K + 0.5) / (N + 1.0)
    emp = np.log(p / (1 - p))
    w = N * p * (1 - p)
    idx = np.argwhere(mask)
    y = emp[mask]; ww = w[mask]
    X = np.zeros((len(idx), 1 + len(STRATS) + N.shape[1]))
    X[:, 0] = 1.0
    for r, (i, j) in enumerate(idx):
        X[r, 1 + i] = 1.0
        X[r, 1 + len(STRATS) + j] = 1.0
    sw = np.sqrt(ww)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    g = emp[mask] - X @ beta
    return float(np.sqrt(np.sum(ww * g ** 2) / np.sum(ww)))


def _cont_cells(T, cats, ycol, relabel=None):
    s = T.strategy.values if relabel is None else np.asarray(relabel)
    K = np.zeros((len(STRATS), len(cats))); N = np.zeros((len(STRATS), len(cats)))
    ci = {c: i for i, c in enumerate(cats)}
    for k, st in enumerate(STRATS):
        m = s == st
        for c, g in T[m].groupby("cat"):
            j = ci.get(c)
            if j is None:
                continue
            N[k, j] = g.n.sum(); K[k, j] = (g[ycol] * g.n).sum()
    return K, N


def _fit_cont_rms(K, N):
    """连续 y 上的加权 LS 加法模型，权 = N（=单元内样本量的精度）"""
    mask = N > 0
    y = np.zeros_like(K); y[mask] = K[mask] / N[mask]
    idx = np.argwhere(mask)
    X = np.zeros((len(idx), 1 + len(STRATS) + N.shape[1]))
    X[:, 0] = 1.0
    for r, (i, j) in enumerate(idx):
        X[r, 1 + i] = 1.0
        X[r, 1 + len(STRATS) + j] = 1.0
    ww = N[mask]; sw = np.sqrt(ww)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y[mask] * sw, rcond=None)
    r = y[mask] - X @ beta
    return float(np.sqrt(np.sum(ww * r ** 2) / np.sum(ww)))


def _perm_z(T, cats, stat_fn, n_perm, rng):
    ds = pd.factorize(T.dataset_id)[0]
    obs = stat_fn(T, cats)
    null = np.empty(n_perm)
    for t in range(n_perm):
        s2 = T.strategy.values.copy()
        for gg in np.unique(ds):
            ix = np.where(ds == gg)[0]
            s2[ix] = rng.permutation(s2[ix])
        null[t] = stat_fn(T, cats, s2)
    p = (1 + np.sum(null >= obs)) / (1 + n_perm)
    return obs, float(null.mean()), float(null.std()), (obs - null.mean()) / max(null.std(), 1e-9), float(p)


def scheme_interaction_all(sch, keys, n_perm=200, seed=5, scope="common"):
    rng = np.random.default_rng(seed)
    rows = []
    for tag, v in sch.items():
        d = v["df"]
        d = d[d["cat"].notna()].copy()
        if keys is not None:
            d = d[d["_key"].isin(keys)]
        d["high_flag"] = (d["set"] == "high").astype(float)
        T = d.groupby(["strategy", "dataset_id", "task_id"]).agg(
            y_raw=("delta", "mean"), n_high=("high_flag", "sum"),
            n=("delta", "size")).reset_index().merge(
            d.drop_duplicates(["dataset_id", "task_id"])[["dataset_id", "task_id", "cat"]],
            on=["dataset_id", "task_id"], how="left")
        T = T[T["cat"].notna()].reset_index(drop=True)
        # 数据集内 z 标准化的连续 y（按样本量加权）
        def _zsub(g):
            w = g.n.values
            m = np.average(g.y_raw.values, weights=w)
            sd = np.sqrt(np.average((g.y_raw.values - m) ** 2, weights=w)) or 1.0
            return (g.y_raw - m) / sd
        T["y_z"] = T.groupby("dataset_id", group_keys=False).apply(_zsub, include_groups=False)
        cats = sorted(T["cat"].unique())
        row = dict(scheme=tag, title=v["title"], scope=scope, n_cats=len(cats),
                   n_tasks=int(T.groupby(['dataset_id', 'task_id']).ngroups))
        b = _perm_z(T, cats, lambda t, c, r=None: _fit_logit_rms(*_bin_cells(t, c, r)), n_perm, rng)
        c1 = _perm_z(T, cats, lambda t, c, r=None: _fit_cont_rms(*_cont_cells(t, c, "y_raw", r)), n_perm, rng)
        c2 = _perm_z(T, cats, lambda t, c, r=None: _fit_cont_rms(*_cont_cells(t, c, "y_z", r)), n_perm, rng)
        row.update(gamma_rms_bin=b[0], z_bin=b[3], p_bin=b[4],
                   gamma_rms_cont_raw=c1[0], z_cont_raw=c1[3], p_cont_raw=c1[4],
                   gamma_rms_cont_z=c2[0], z_cont_z=c2[3], p_cont_z=c2[4],
                   null_bin_mean=b[1], null_bin_sd=b[2],
                   null_raw_sd=c1[2], null_z_sd=c2[2])
        rows.append(row)
        print(f"  [{tag:8s}] cats={len(cats):2d} n_tasks={row['n_tasks']:4d} | "
              f"bin: RMS={b[0]:.3f} z={b[3]:+5.2f} p={b[4]:.3f} | "
              f"cont(raw): RMS={c1[0]:.3f} z={c1[3]:+5.2f} p={c1[4]:.3f} | "
              f"cont(z): RMS={c2[0]:.3f} z={c2[3]:+5.2f} p={c2[4]:.3f}")
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ figures
def fig_heatmap(R, path):
    M = R.pivot(index="strategy", columns="op_name", values="dscore_bal").reindex(STRATS)[COLS]
    sig = R.pivot(index="strategy", columns="op_name", values="sig").reindex(STRATS).fillna(False)[COLS]
    n = R.pivot(index="strategy", columns="op_name", values="n_on").reindex(STRATS).fillna(0)[COLS]
    V = M.values * 100
    v = np.nanmax(np.abs(V))
    fig, ax = plt.subplots(figsize=(13.5, 4.4))
    im = ax.imshow(V, cmap="RdBu_r", vmin=-v, vmax=v, aspect="auto")
    ax.set_xticks(range(len(COLS))); ax.set_xticklabels(COLS, rotation=28, ha="right", fontsize=9)
    ax.set_yticks(range(len(STRATS))); ax.set_yticklabels(STRATS, fontsize=10)
    for r in range(V.shape[0]):
        for c in range(V.shape[1]):
            if np.isnan(V[r, c]):
                continue
            ax.text(c, r, f"{V[r,c]:+.2f}{'*' if sig.values[r, c] else ''}\nn={int(n.values[r,c])}",
                    ha="center", va="center", fontsize=7.6,
                    color="white" if abs(V[r, c]) > .55 * v else "#222")
    plt.colorbar(im, ax=ax, shrink=.9, label="Δscore ×100（归一化分差，族内平衡）")
    ax.set_title("连续版：策略 × 所需思维动作    Δscore（* = FDR<0.05）", fontsize=12.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def fig_vs_binary(C, path):
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.6))
    ax = axes[0]
    x = C.dpp_bal.values * 100; y = C.dscore_bal.values * 100
    ax.axhline(0, color="#bbb", lw=.8); ax.axvline(0, color="#bbb", lw=.8)
    ax.scatter(x, y, s=26, c=["#c0392b" if s else "#2c7fb8" for s in C.sig], alpha=.85)
    r = C[["dpp_bal", "dscore_bal"]].corr(method="spearman").iloc[0, 1]
    ax.set_xlabel("Δpp（二值，v4）"); ax.set_ylabel("Δscore ×100（连续，v4c）")
    ax.set_title(f"逐单元格效应：Spearman ρ = {r:.2f}", fontsize=11)
    ax.grid(alpha=.25)
    ax = axes[1]
    rows = []
    for name, p, q in (("二值 v4", C.p_bin, C.q_bin), ("连续 v4c", C.p, C.q),
                       ("连续中位数", C.p_med, C.q_med)):
        rows.append((name, int((p < .05).sum()), int((q < .05).sum())))
    idx = np.arange(len(rows)); w = .36
    ax.bar(idx - w/2, [r[1] for r in rows], w, label="p<0.05", color="#2c7fb8")
    ax.bar(idx + w/2, [r[2] for r in rows], w, label="FDR q<0.05", color="#c0392b")
    ax.set_xticks(idx); ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylabel("单元格数（共 55 个）")
    ax.set_title("灵敏度：多少单元格过线", fontsize=11)
    ax.legend(fontsize=9); ax.grid(alpha=.25, axis="y")
    for i, r in enumerate(rows):
        ax.text(i - w/2, r[1] + .6, str(r[1]), ha="center", fontsize=9)
        ax.text(i + w/2, r[2] + .6, str(r[2]), ha="center", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def fig_target(T, path):
    x = np.arange(len(T)); w = .38
    fig, ax = plt.subplots(figsize=(10.5, 4.3))
    ax.bar(x - w/2, T.dscore_bal.values * 100, w, label="目标思维", color="#c0392b")
    ax.bar(x + w/2, T.dpp_bal.values * 100, w, label="对比：二值 Δpp", color="#c7c7c7")
    ax.axhline(0, color="#444", lw=.9)
    ax.set_xticks(x); ax.set_xticklabels(T.strategy, fontsize=10)
    ax.set_ylabel("族内平衡效应 ×100")
    ax.set_title("目标思维命中检验：连续 Δscore vs 二值 Δpp", fontsize=12, fontweight="bold")
    for i, r in enumerate(T.itertuples()):
        ax.text(i - w/2, r.dscore_bal * 100 + (1.2 if r.dscore_bal >= 0 else -2.6),
                f"{r.dscore_bal*100:+.1f}\np={r.p_cont:.3f}", ha="center", fontsize=8)
    ax.legend(fontsize=9); ax.grid(alpha=.25, axis="y")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


def fig_ranking(R, path):
    fig, ax = plt.subplots(figsize=(13.2, 4.4))
    x = np.arange(len(IDS)); w = .16
    for k, s in enumerate(STRATS):
        d = R[R.strategy == s].set_index("op").reindex(IDS)
        ax.bar(x + (k - 2) * w, d.dscore_bal.values * 100, w, label=s)
    ax.axhline(0, color="#444", lw=.9)
    ax.set_xticks(x); ax.set_xticklabels(COLS, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Δscore ×100（族内平衡）")
    ax.set_title("每种思维动作上的相对赢家（连续版）", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8.5, ncol=5); ax.grid(alpha=.25, axis="y")
    fig.tight_layout(); fig.savefig(path, dpi=200); plt.close(fig)


# ------------------------------------------------------------------ main
def main():
    from summary_v4c_gen import write_summary
    v4 = load_v4()
    assert np.allclose(v4.reask_minmax - v4.plain_minmax, v4.delta), "delta != reask - plain"
    sign = np.sign(v4.delta)
    assert bool(((v4["set"] == "high") == (sign > 0)).all()), "high 不是 sign(delta)>0"
    tt = task_table_cont(v4)
    print(f"[data] rows={len(v4)}  tasks={v4.groupby(['dataset_id','task_id']).ngroups}  "
          f"(strategy x task)={len(tt)}  datasets={v4.dataset_id.nunique()}")
    print(f"[data] delta: mean={v4.delta.mean():+.4f} sd={v4.delta.std():.4f} "
          f"min={v4.delta.min():+.3f} max={v4.delta.max():+.3f}")
    print(f"[data] multi-run (strategy x task) share: {(tt.n_runs > 1).mean()*100:.1f}%")

    R = flag_analysis_cont(tt, n_perm=400, seed=3)
    R.to_csv(os.path.join(HERE, "v4c_preference_cont.csv"), index=False)

    b = pd.read_csv(os.path.join(HERE, "v4_flag_preference.csv"))
    C = R[["strategy", "op", "op_name", "n_on", "n_off", "dscore_bal", "dscore_std",
           "dscore_med_bal", "dpp_bal", "p", "p_med", "p_std", "p_bin", "p_tt",
           "q", "q_med", "q_std", "q_bin",
           "sig", "sig_med", "sig_std", "sig_bin", "target"]].merge(
        b[["strategy", "op", "dpp_bal", "p", "q", "sig"]].rename(
            columns={"dpp_bal": "dpp_bal_v4", "p": "p_v4", "q": "q_v4", "sig": "sig_v4"}),
        on=["strategy", "op"], how="left")
    C.to_csv(os.path.join(HERE, "v4c_vs_binary.csv"), index=False)

    T = target_contrast(tt, n_perm=400, seed=11)
    T.to_csv(os.path.join(HERE, "v4c_target_match.csv"), index=False)
    print("\n[target] hit-test (continuous)")
    print(T[["strategy", "dscore_bal", "p_cont", "q_cont", "dpp_bal", "p_bin"]].round(4).to_string(index=False))

    print("\n[continuity] interaction RMS by scheme (binary gamma vs continuous)")
    sch = A.load_all()
    sch["v4"] = dict(df=v4, names=NAMES, title="v4 thinking actions (11, new)")
    keys = A.common_keys(pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"),
                                     usecols=["dataset_id", "task_id", "strategy"]))
    S = pd.concat([scheme_interaction_all(sch, keys, n_perm=200, scope="common"),
                   scheme_interaction_all(sch, None, n_perm=200, seed=17, scope="all")],
                  ignore_index=True)
    S.to_csv(os.path.join(HERE, "v4c_scheme_interaction_cont.csv"), index=False)

    fig_heatmap(R, os.path.join(OUT, "cont_heatmap.png"))
    fig_vs_binary(C, os.path.join(OUT, "cont_vs_binary.png"))
    fig_target(T, os.path.join(OUT, "cont_target_match.png"))
    fig_ranking(R, os.path.join(OUT, "cont_op_ranking.png"))
    print("\n[fig] saved ->", OUT)
    write_summary(v4, tt, R, C, T, S)
    return R, C, T, S, tt


if __name__ == "__main__":
    main()
