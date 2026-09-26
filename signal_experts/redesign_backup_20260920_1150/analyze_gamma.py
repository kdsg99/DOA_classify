# -*- coding: utf-8 -*-
"""
「策略偏好」的可测量版本 —— 策略 x 题型的交互项 gamma。

对每个单元格 (策略 s, 题型 c) 用经验 logit 表示该策略在这类题上的"提升优势"：
    logit P(high | s,c) ≈ mu + alpha_s + beta_c + gamma_sc
用加权最小二乘（权 = n*p*(1-p)）拟合 mu/alpha/beta，gamma 就是净交互项：
gamma>0 表示"该策略相对自己的平均水平，在这类题上格外有效"，gamma<0 则是短板。
统计量 = 加权 RMS(gamma)，其显著性与方案间比较由置换检验给出（在每个数据集内部打乱策略标签）。
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

RNG = np.random.default_rng(5)
N_PERM = 500


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


def fit_gamma(K, N):
    """weighted-LS additive fit on empirical log-odds -> (gamma matrix, weights, mu/a/b)"""
    mask = N > 0
    p = (K + 0.5) / (N + 1.0)
    emp = np.log(p / (1 - p))
    w = N * p * (1 - p)
    idx = np.argwhere(mask)
    y = emp[mask]; ww = w[mask]
    X = np.zeros((len(idx), 1 + 5 + N.shape[1]))
    X[:, 0] = 1.0
    for r, (i, j) in enumerate(idx):
        X[r, 1 + i] = 1.0
        X[r, 1 + 5 + j] = 1.0
    sw = np.sqrt(ww)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    fit = X @ beta
    gamma = np.zeros_like(emp)
    gamma[mask] = emp[mask] - fit
    rms = float(np.sqrt(np.sum(ww * gamma[mask] ** 2) / np.sum(ww)))
    return gamma, w, emp, mask, rms


def perm_test(df, cats, n_perm=N_PERM):
    K, N = cell_table(df, cats)
    _, _, _, _, obs = fit_gamma(K, N)
    ds = pd.factorize(df.dataset_id)[0]
    s = np.array([A.STRATS.index(x) for x in df.strategy])
    null = np.empty(n_perm)
    for t in range(n_perm):
        s2 = s.copy()
        for g in np.unique(ds):
            ix = np.where(ds == g)[0]; s2[ix] = RNG.permutation(s2[ix])
        null[t] = fit_gamma(*cell_table(df.assign(strategy=[A.STRATS[i] for i in s2]), cats))[4]
    z = (obs - null.mean()) / max(null.std(), 1e-9)
    return obs, float(null.mean()), float(null.std()), float(z)


def main():
    sch = A.load_all()
    rows = []; gammas = {}
    for tag, v in sch.items():
        d = v["df"]
        cats = sorted(d["cat"].dropna().unique())
        if tag in SCHEMES:
            cats = [c for c in SCHEMES[tag]["ids"] if c in set(d["cat"].dropna().unique())]
        d = d[d["cat"].notna()]
        K, N = cell_table(d, cats)
        gamma, w, emp, mask, obs = fit_gamma(K, N)
        _, nm, ns, z = perm_test(d, cats)
        gammas[tag] = dict(gamma=gamma, w=w, emp=emp, mask=mask, cats=cats)
        rows.append(dict(scheme=tag, title=v["title"], n_cats=len(cats),
                         gamma_rms=obs, null_mean=nm, null_sd=ns, z=z))
        print(f"{tag:8s} cats={len(cats):2d}  gamma-RMS={obs:.3f}  null={nm:.3f}+-{ns:.3f}  z={z:5.1f}")
    M = pd.DataFrame(rows)
    M.to_csv(os.path.join(HERE, "scheme_interaction.csv"), index=False)

    # print the gamma tables in log-odds and in percentage-point terms
    for tag in ["s1", "s2", "v2", "dataset"]:
        if tag not in gammas:
            continue
        g = gammas[tag]
        print(f"\n===== {tag} : gamma (净交互，log-odds) ")
        lab = {c: (V2_ZH.get(c, c) if tag == "v2" else
                   (SCHEMES[tag]["names"].get(c, c) if tag in SCHEMES else c)) for c in g["cats"]}
        print(pd.DataFrame(g["gamma"], index=A.STRATS, columns=[lab[c] for c in g["cats"]]).round(2).to_string())
    print("\nsaved -> scheme_interaction.csv")


if __name__ == "__main__":
    main()
