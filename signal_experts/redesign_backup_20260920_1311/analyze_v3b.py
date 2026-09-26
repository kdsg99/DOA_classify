# -*- coding: utf-8 -*-
"""
「策略偏好」能不能被某个分类法解释？

The composition metric (what share of a strategy's high set falls in each class) turned
out to be almost strategy-independent -- all five strategies help largely the same task
pool. What *does* differ is the LEVEL: the probability that the strategy helps, per task
type. So the metric used here is the strategy x class INTERACTION on the log-odds scale:

    logit P(high | s, c) = mu + alpha_s + beta_c + gamma_sc

gamma (the interaction) is exactly "strategy s 偏好/讨厌 类型 c".  We measure its
weighted RMS, with a permutation null (strategy labels shuffled inside each dataset), and
also cross-validated log-loss of a model with vs without the interaction block.
"""
import os, sys, itertools
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_v3 as A
from taxonomy_v3 import SCHEMES
from taxonomy_v2 import ID2ZH as V2_ZH
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

RNG = np.random.default_rng(11)
N_PERM = 200


def cell_table(df, cats):
    """(k, n) matrices over STRATS x cats"""
    K = np.zeros((5, len(cats))); N = np.zeros((5, len(cats)))
    ci = {c: i for i, c in enumerate(cats)}
    for k, s in enumerate(A.STRATS):
        d = df[df.strategy == s]
        for c, g in d.groupby("cat"):
            j = ci.get(c)
            if j is None:
                continue
            N[k, j] = len(g); K[k, j] = (g["set"] == "high").sum()
    return K, N


def interaction_rms(K, N):
    """median-polish style additive fit on empirical log-odds; returns weighted RMS of gamma"""
    mask = N > 0
    if mask.sum() < 3:
        return 0.0
    p = (K + 0.5) / (N + 1.0)
    emp = np.log(p / (1 - p))
    w = N * p * (1 - p)
    a = np.zeros(len(K)); b = np.zeros(K.shape[1])
    for _ in range(300):
        for k in range(len(K)):
            m = mask[k]
            if m.sum():
                a[k] = np.sum(w[k, m] * (emp[k, m] - b[m])) / np.sum(w[k, m])
        a -= a[mask.any(axis=1)].mean() if mask.any() else 0
        for j in range(K.shape[1]):
            m = mask[:, j]
            if m.sum():
                b[j] = np.sum(w[m, j] * (emp[m, j] - a[m])) / np.sum(w[m, j])
        b -= b[mask.any(axis=0)].mean() if mask.any() else 0
    res = np.where(mask, emp - a[:, None] - b[None, :], 0.0)
    return float(np.sqrt(np.sum(w * res ** 2) / max(np.sum(w), 1e-9)))


def permutation_z(df, cats, n_perm=N_PERM, rng=RNG):
    K, N = cell_table(df, cats)
    obs = interaction_rms(K, N)
    ds = pd.factorize(df.dataset_id)[0]
    s = np.array([A.STRATS.index(x) for x in df.strategy])
    null = []
    for _ in range(n_perm):
        s2 = s.copy()
        for g in np.unique(ds):
            idx = np.where(ds == g)[0]
            s2[idx] = rng.permutation(s2[idx])
        d2 = df.assign(strategy=[A.STRATS[i] for i in s2])
        null.append(interaction_rms(*cell_table(d2, cats)))
    null = np.array(null)
    return obs, float(null.mean()), float((obs - null.mean()) / max(null.std(), 1e-9))


def cv_logloss(df, cats, with_ds=True, interaction=True, k=5):
    """5-fold CV log-loss; features = strategy / dataset / class (+ interaction)."""
    X = pd.get_dummies(df[["strategy"] + (["dataset_id"] if with_ds else [])], dtype=float)
    if interaction:
        for s in A.STRATS:
            for c in cats:
                X[f"{s}|{c}"] = ((df.strategy == s) & (df["cat"] == c)).astype(float)
    else:
        X = pd.concat([X, pd.get_dummies(df["cat"], dtype=float)], axis=1)
    y = (df["set"] == "high").values.astype(int)
    Xc = X.values
    kf = KFold(n_splits=k, shuffle=True, random_state=3)
    tot = 0.0; n = 0
    for tr, te in kf.split(Xc):
        m = LogisticRegression(max_iter=2000, C=1.0)
        m.fit(Xc[tr], y[tr])
        pr = np.clip(m.predict_proba(Xc[te])[:, 1], 1e-9, 1 - 1e-9)
        tot += -np.sum(y[te] * np.log(pr) + (1 - y[te]) * np.log(1 - pr)); n += len(te)
    return tot / n


def main():
    schemes = A.load_all()
    rows = []
    for tag, v in schemes.items():
        df = v["df"].copy()
        cats = sorted(df["cat"].dropna().unique())
        if tag in SCHEMES:
            cats = [c for c in SCHEMES[tag]["ids"] if c in set(df["cat"].dropna().unique())]
        df = df[df["cat"].notna()]
        obs, nul, z = permutation_z(df, cats)
        ll_main = cv_logloss(df, cats, interaction=False)
        ll_int = cv_logloss(df, cats, interaction=True)
        K, N = cell_table(df, cats)
        rows.append(dict(scheme=tag, title=v["title"], n_cats=len(cats),
                         int_rms=obs, int_null=nul, int_z=z,
                         cv_logloss_main=ll_main, cv_logloss_inter=ll_int,
                         gain=ll_main - ll_int))
        print(f"{tag:8s} cats={len(cats):2d}  交互强度 RMS={obs:.3f} (null {nul:.3f}, z={z:5.1f})   "
              f"CV logloss main={ll_main:.4f} +交互={ll_int:.4f}  增益={ll_main-ll_int:+.4f}")
    M = pd.DataFrame(rows)
    M.to_csv(os.path.join(HERE, "scheme_interaction.csv"), index=False)
    best = M.set_index("scheme")["gain"].drop(index=["dataset"], errors="ignore").idxmax()
    print("\n>>> CV 增益最大的方案:", best)
    return M


if __name__ == "__main__":
    main()
