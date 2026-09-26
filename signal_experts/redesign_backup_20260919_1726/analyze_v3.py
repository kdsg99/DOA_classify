# -*- coding: utf-8 -*-
"""
Compare the existing v2 taxonomy with the two new v3 taxonomies and pick the one that
separates the five strategies best (see design notes in summary_v3.md).

Metrics (all bounded, so schemes with different class counts stay comparable)
  T  策略差异度 : mean pairwise Jensen-Shannon divergence between the five strategies'
                 category profiles of their HIGH rows.
  P  优劣区分度 : mean JSD between each strategy's own HIGH profile and LOW profile.
  V  Cramer's V : association between strategy and category on the HIGH rows.
Scopes
  all    所有 2801 行
  common 只保留 5 个策略都覆盖的任务（245 个），去掉"任务组合不同"这个混淆因素
Significance: strategy labels are permuted *inside each dataset*, 400 draws.
"""
import os, sys, itertools
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy_v3 import SCHEMES
from taxonomy_v2 import ID2ZH as V2_ZH

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
N_PERM = 400
RNG = np.random.default_rng(20260918)


# --------------------------------------------------------------------- loading
def load_all():
    v2 = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
    v2["cat"] = v2["thinking_type"]
    out = {"v2": dict(df=v2, names=V2_ZH, title="v2 认知层级×对象 (12类，原有)")}
    for tag in ["s1", "s2"]:
        f = os.path.join(HERE, f"all_tasks_v3_{tag}.csv")
        if not os.path.exists(f):
            print("!! missing", f); continue
        d = pd.read_csv(f)
        d["cat"] = d["type"]
        out[tag] = dict(df=d, names=SCHEMES[tag]["names"],
                        title=f"{tag} {SCHEMES[tag]['title']} ({len(SCHEMES[tag]['ids'])}类，新)")
    d = v2.copy(); d["cat"] = d["dataset_id"]
    out["dataset"] = dict(df=d, names={}, title="数据集/主题 (6类，基线)")
    for v in out.values():
        v["df"]["_key"] = list(zip(v["df"].dataset_id, v["df"].task_id))
    return out


def common_keys(v2):
    keys = set(zip(v2.dataset_id, v2.task_id))
    for s in STRATS:
        keys &= set(zip(v2[v2.strategy == s].dataset_id, v2[v2.strategy == s].task_id))
    return keys


# ------------------------------------------------------------------ fast core
def prep(df, cats, only=None):
    d = df if only is None else df[df["_key"].isin(only)]
    d = d[d["cat"].notna()]
    cmap = {c: i for i, c in enumerate(cats)}
    return dict(s=np.array([STRATS.index(x) for x in d.strategy], dtype=int),
                c=d["cat"].map(cmap).values.astype(int),
                h=(d["set"] == "high").values.astype(int),
                ds=pd.factorize(d.dataset_id)[0],
                C=len(cats), n=len(d))


def _jsd(p, q):
    p = p / max(p.sum(), 1e-12); q = q / max(q.sum(), 1e-12)
    m = 0.5 * (p + q)
    def kl(a, b):
        k = a > 0
        return float(np.sum(a[k] * np.log2(a[k] / np.maximum(b[k], 1e-12))))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def profs(P, s=None):
    s = P["s"] if s is None else s
    C = P["C"]
    hi = np.zeros((5, C)); lo = np.zeros((5, C))
    for k in range(5):
        m = s == k
        hi[k] = np.bincount(P["c"][m & (P["h"] == 1)], minlength=C).astype(float)
        lo[k] = np.bincount(P["c"][m & (P["h"] == 0)], minlength=C).astype(float)
    return hi, lo


def stats(hi, lo):
    T = np.mean([_jsd(hi[a], hi[b]) for a, b in itertools.combinations(range(5), 2)])
    Pp = np.mean([_jsd(hi[k], lo[k]) for k in range(5)])
    return float(T), float(Pp)


def permute_within(P, rng):
    s = P["s"].copy()
    for g in np.unique(P["ds"]):
        idx = np.where(P["ds"] == g)[0]
        s[idx] = rng.permutation(s[idx])
    return s


def cramers_v(P):
    from scipy.stats import chi2_contingency
    tab = np.zeros((5, P["C"]))
    for k in range(5):
        tab[k] = np.bincount(P["c"][(P["s"] == k) & (P["h"] == 1)], minlength=P["C"])
    tab = tab[:, tab.sum(axis=0) > 0]
    if tab.shape[1] < 2:
        return 0.0
    chi2 = chi2_contingency(tab)[0]
    n = tab.sum()
    return float(np.sqrt(chi2 / (n * (min(tab.shape) - 1))))


def measure(df, cats, only=None, n_perm=N_PERM, rng=None):
    rng = rng or np.random.default_rng(7)
    P = prep(df, cats, only)
    hi, lo = profs(P)
    T, Pp = stats(hi, lo)
    nT = []; nP = []
    for _ in range(n_perm):
        h2, l2 = profs(P, permute_within(P, rng))
        a, b = stats(h2, l2)
        nT.append(a); nP.append(b)
    nT = np.array(nT); nP = np.array(nP)
    return dict(n=P["n"], n_cats=len(cats), T=T, T_null=float(nT.mean()),
                T_z=float((T - nT.mean()) / max(nT.std(), 1e-9)),
                P=Pp, P_null=float(nP.mean()), P_z=float((Pp - nP.mean()) / max(nP.std(), 1e-9)),
                V=cramers_v(P))


# --------------------------------------------------------------- preferences
def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    r = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def preference_table(df, names, min_n=20):
    rows = []
    for s in STRATS:
        d = df[df.strategy == s]
        base = (d["set"] == "high").mean()
        for c, g in d.groupby("cat"):
            n = len(g); k = int((g["set"] == "high").sum()); r = k / n
            lo, hi_ = wilson(k, n)
            rows.append(dict(strategy=s, cat=c, cat_name=names.get(c, str(c)), n=n, n_high=k,
                             high_rate=r, base_rate=float(base),
                             lift=r / base if base else np.nan,
                             log2_lift=float(np.log2((r + 1e-6) / (base + 1e-6))),
                             ci_lo=lo, ci_hi=hi_, sig=bool(hi_ < base or lo > base),
                             enough=bool(n >= min_n)))
    return pd.DataFrame(rows)


def main():
    schemes = load_all()
    keys = common_keys(schemes["v2"]["df"])
    print("common tasks (all 5 strategies):", len(keys), "\n")
    met = []
    for tag, v in schemes.items():
        df = v["df"]; cats = sorted(df["cat"].dropna().unique())
        if tag in SCHEMES:
            cats = [c for c in SCHEMES[tag]["ids"] if c in set(df["cat"].dropna().unique())]
        for scope in ["all", "common"]:
            r = measure(df, cats, None if scope == "all" else keys)
            met.append(dict(scheme=tag, title=v["title"], scope=scope, **r))
            print(f"{tag:8s} {scope:6s} cats={r['n_cats']:2d} rows={r['n']:4d}  "
                  f"T={r['T']:.3f} (null {r['T_null']:.3f}, z={r['T_z']:5.1f})   "
                  f"P={r['P']:.3f} (z={r['P_z']:5.1f})   V={r['V']:.3f}")
    M = pd.DataFrame(met)
    M.to_csv(os.path.join(HERE, "scheme_metrics.csv"), index=False)
    cm = M[M.scope == "common"].set_index("scheme")
    cand = cm.drop(index=["dataset"], errors="ignore")
    best = cand["T"].idxmax()
    print(f"\n>>> 区分度最高的方案 (common scope, T): {best} = {cand.loc[best,'T']:.3f}")
    return schemes, M, keys, best


if __name__ == "__main__":
    main()
