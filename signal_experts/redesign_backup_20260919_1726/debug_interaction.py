# -*- coding: utf-8 -*-
"""Diagnostic: corrected weighted-LS additive fit for the strategy x class interaction."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign")
import analyze_v3 as A
from taxonomy_v3 import SCHEMES

np.set_printoptions(precision=2, suppress=True, linewidth=220)
RNG = np.random.default_rng(5)


def cell_table(df, cats):
    K = np.zeros((5, len(cats))); N = np.zeros((5, len(cats)))
    ci = {c: i for i, c in enumerate(cats)}
    for k, s in enumerate(A.STRATS):
        d = df[df.strategy == s]
        for c, g in d.groupby("cat"):
            j = ci.get(c)
            if j is None: continue
            N[k, j] = len(g); K[k, j] = (g["set"] == "high").sum()
    return K, N


def fit_and_rms(K, N):
    mask = N > 0
    p = (K + 0.5) / (N + 1.0)
    emp = np.log(p / (1 - p))
    w = N * p * (1 - p)
    a = np.zeros(5); b = np.zeros(K.shape[1]); mu = 0.0
    for _ in range(2000):
        for k in range(5):
            m = mask[k]
            if m.sum(): a[k] = np.sum(w[k, m] * (emp[k, m] - b[m] - mu)) / np.sum(w[k, m])
        for j in range(K.shape[1]):
            m = mask[:, j]
            if m.sum(): b[j] = np.sum(w[m, j] * (emp[m, j] - a[m] - mu)) / np.sum(w[m, j])
        mu = np.sum(w * (emp - a[:, None] - b[None, :])) / np.sum(w)
    res = np.where(mask, emp - a[:, None] - b[None, :] - mu, 0.0)
    return np.sqrt(np.sum(w * res ** 2) / np.sum(w)), res, a, b, w, emp, mask


def perm_test(df, cats, n_perm=300):
    K, N = cell_table(df, cats)
    obs, *_ = fit_and_rms(K, N)
    ds = pd.factorize(df.dataset_id)[0]
    s = np.array([A.STRATS.index(x) for x in df.strategy])
    null = []
    for _ in range(n_perm):
        s2 = s.copy()
        for g in np.unique(ds):
            ix = np.where(ds == g)[0]; s2[ix] = RNG.permutation(s2[ix])
        null.append(fit_and_rms(*cell_table(df.assign(strategy=[A.STRATS[i] for i in s2]), cats))[0])
    null = np.array(null)
    return obs, null.mean(), null.std(), (obs - null.mean()) / max(null.std(), 1e-9)


sch = A.load_all()
for tag, v in sch.items():
    d = v["df"]; cats = sorted(d["cat"].dropna().unique())
    if tag in SCHEMES:
        cats = [c for c in SCHEMES[tag]["ids"] if c in set(d["cat"].dropna().unique())]
    obs, nm, ns, z = perm_test(d[d["cat"].notna()], cats)
    print(f"{tag:8s} cats={len(cats):2d}  RMS={obs:.4f}  null={nm:.4f}+-{ns:.4f}  z={z:5.1f}")

# residual matrix for the dataset scheme
for tag in ["dataset", "s1"]:
    d = sch[tag]["df"]; cats = sorted(d["cat"].dropna().unique())
    rms, res, a, b, w, emp, mask = fit_and_rms(*cell_table(d, cats))
    print(f"\n== {tag}  RMS={rms:.3f}  a={a.round(2)}  b={b.round(2)}")
    print("weighted residual (gamma):")
    print((res).round(2))
