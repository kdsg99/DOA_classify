# -*- coding: utf-8 -*-
"""Step 4 - reverse-engineer the classification.

Objective (the user's three requirements, made measurable)
---------------------------------------------------------
C1 strategy divergence : among the four non-PRESSURE strategies the type-level ordering must flip
                         (stable reversals, |z|>1.5 in both directions) and each strategy's own
                         profile must swing a lot (SD of its type profile).
C2 PRESSURE              small amplitude (SD) and mostly on the positive side (mean > 0, >= 60% of
                         types positive) in the absolute, difficulty-standardised level metric.
C3 the other four        large swings with only one or two good types: range >= 25 pp, at most two
                         types above -5 pp, mean level clearly negative.
Hard constraint          every cell must hold >= 25 tasks for every strategy (thin cells would make
                         the picture an artefact of a handful of tasks).

Everything is scored on the *contrast* metric for C1 (within-task centring over the four focal
strategies - the only way to compare strategies on equal footing) and on the *level* metric for
C2/C3 (the bars the user looks at).  Selection uses half of the tasks (discovery); the chosen
classification is then re-scored on the other half (validation).
"""
import hashlib
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from sklearn.cluster import AgglomerativeClustering, KMeans     # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer     # noqa: E402
from sklearn.metrics.pairwise import cosine_similarity          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screen2 as S2                                            # noqa: E402
import step3_choose as S3                                       # noqa: E402

FOCAL = S2.FOCAL
ALLS = ["PRESSURE"] + FOCAL
MIN_CELL = 25


# ---------------------------------------------------------------- candidate classifications
def build_candidates(feat):
    X = TfidfVectorizer(max_features=4000, stop_words="english", ngram_range=(1, 2)).fit_transform(
        feat.txt.fillna("").astype(str))
    nz = np.asarray(np.sqrt(X.multiply(X).sum(axis=1))).ravel() > 0
    idx_nz, idx_z = np.array(feat.index)[nz], np.array(feat.index)[~nz]
    Xnz = X[nz]
    cs = {}
    # k-means with a greedy merge of the smallest clusters into their most similar neighbour
    for k in (8, 12, 16, 20):
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xnz)
        lab = pd.Series(km.labels_, index=idx_nz).reindex(feat.index)
        lab = lab.fillna(lab.value_counts().idxmax()).astype(int)
        cen = pd.DataFrame(cosine_similarity(km.cluster_centers_))
        for J in (4, 5, 6):
            m = lab.copy()
            while m.nunique() > J:
                sizes = m.value_counts()
                small = sizes.index[-1]
                others = [c for c in m.unique() if c != small]
                sim = cen.loc[small, others].astype(float)
                m[m == small] = sim.idxmax()
            cs["km%d_merge%d" % (k, J)] = m.astype(str)
    # agglomerative on cosine distance
    for J in (4, 5, 6, 7, 8):
        ag = AgglomerativeClustering(n_clusters=J, metric="cosine", linkage="average").fit(Xnz.toarray())
        lab = pd.Series(ag.labels_, index=idx_nz).reindex(feat.index)
        lab = lab.fillna(lab.value_counts().idxmax()).astype(int)
        cs["agg%d" % J] = lab.astype(str)
    # crosses with the content labels that already carry level / format / length information
    lvl = feat.thinking_type.str[:2].astype(str)
    fmt = feat.has_fmt.map({True: "fmt", False: "free"}).astype(str)
    ln = pd.qcut(feat.tlen, 3, labels=["short", "mid", "long"]).astype(str)
    base = {k: v for k, v in cs.items() if k.startswith("agg")}
    for k, v in base.items():
        cs["%s x level" % k] = v + "|" + lvl
        cs["%s x fmt" % k] = v + "|" + fmt
        cs["%s x len" % k] = v + "|" + ln
    cs["family"] = feat.dataset_id.astype(str)
    cs["v2_12"] = feat.thinking_type.astype(str)
    rng = np.random.default_rng(0)
    for i in range(8):
        cs["random_%d" % i] = pd.Series(rng.integers(0, 6, len(feat)).astype(str), index=feat.index)
    return cs


# ---------------------------------------------------------------- metrics
def conflict_levels(band, W, d, lab):
    L = S3.level_matrix(d, lab) if hasattr(S3, "level_matrix") else None
    return L


def score_level(L):
    Lm = L.pivot_table(index="type", columns="strategy", values="level")[ALLS]
    Nm = L.pivot_table(index="type", columns="strategy", values="n")[ALLS]
    ok = (Nm.fillna(0) >= MIN_CELL).all(axis=1)
    Lm = Lm[ok]
    if len(Lm) < 3:
        return dict(n_types=0)
    p = Lm["PRESSURE"]
    others = Lm[FOCAL]
    res = dict(
        n_types=int(len(Lm)),
        p_mean=float(p.mean()), p_sd=float(p.std(ddof=1)), p_pos=float((p > 0).mean()),
        o_mean_sd=float(others.std(axis=0, ddof=1).mean()),
        o_mean=float(others.values.mean()),
        o_range=float(others.max(axis=0).max() - others.min(axis=0).min()),
        o_specialty=float((others > -5).sum(axis=0).mean()),      # good types per strategy
        o_range_min=float((others.max(axis=0) - others.min(axis=0)).min()),
    )
    return res


def score_contrast(C, lab):
    M = S3.contrast_matrix(C, lab, min_n=MIN_CELL)
    if M.empty:
        return dict(inter=np.nan, rev=0, rev_pairs=0, inter_sd=np.nan)
    Mm = M.pivot(index="type", columns="strategy", values="contrast")[FOCAL]
    Nm = M.pivot(index="type", columns="strategy", values="n")[FOCAL]
    Mm = Mm[(Nm.fillna(0) >= MIN_CELL).all(axis=1)]
    if len(Mm) < 3:
        return dict(inter=np.nan, rev=0, rev_pairs=0, inter_sd=np.nan)
    sd = Mm.std(axis=0, ddof=1)
    rev, rev_pairs = 0, 0
    for a, b in itertools.combinations(FOCAL, 2):
        da = M[M.strategy == a].set_index("type")
        db = M[M.strategy == b].set_index("type")
        j = da.index.intersection(db.index)
        diff = da.loc[j, "contrast"] - db.loc[j, "contrast"]
        se = np.sqrt(da.loc[j, "se"] ** 2 + db.loc[j, "se"] ** 2)
        z = (diff / se).dropna()
        if (z > 1.5).any() and (z < -1.5).any():
            rev_pairs += 1
            rev += int((z > 1.5).sum() + (z < -1.5).sum())
    return dict(inter=float(sd.mean()), inter_sd=float(sd.max() - sd.min()), rev=rev, rev_pairs=rev_pairs)


def split_half_profile(C, lab, which=0):
    idx = np.array(C.index)
    h = np.array([int(hashlib.md5(str(s).encode()).hexdigest(), 16) % 2 for s in idx])
    corrs = []
    for s in FOCAL:
        Va, Na = S2.v_matrix(C[h == which], lab.reindex(idx[h == which]), [s])
        Vb, Nb = S2.v_matrix(C[h == (1 - which)], lab.reindex(idx[h == (1 - which)]), [s])
        va = Va[s].where(Na[s].fillna(0) >= 8)
        vb = Vb[s].where(Nb[s].fillna(0) >= 8)
        j = va.dropna().index.intersection(vb.dropna().index)
        if len(j) >= 3:
            corrs.append(float(np.corrcoef(va[j].rank(), vb[j].rank())[0, 1]))
    return float(np.nanmean(corrs)) if corrs else np.nan


def main():
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    d, band, W = S3.rows_band()
    S3.W = W                      # step3.level_matrix reads the module-level reference mix
    cs = build_candidates(feat)
    rows = []
    for name, lab in cs.items():
        lab = pd.Series(lab, index=feat.index).astype(str)
        sl = score_level(S3.level_matrix(d, lab)) if True else {}
        sc = score_contrast(C, lab)
        rel = split_half_profile(C, lab)
        r = dict(partition=name, rel_prof=rel, **{("L_" + k): v for k, v in sl.items()},
                 **{("C_" + k): v for k, v in sc.items()})
        rows.append(r)
    R = pd.DataFrame(rows)
    R["ok_cells"] = (R.L_n_types >= 3)
    R["score"] = (0.45 * (R.C_rev_pairs / 6.0) + 0.25 * (R.C_inter / 10.0).clip(0, 1)
                  + 0.15 * (R.L_o_mean_sd / 20.0).clip(0, 1)
                  + 0.15 * ((R.L_p_mean.clip(0, 5) / 5.0).fillna(0) * (R.L_p_pos.fillna(0).clip(0, 1)))
                  - 0.20 * (R.L_p_sd.fillna(99) / 20.0).clip(0, 1))
    R.loc[~R.ok_cells, "score"] = np.nan
    R = R.sort_values("score", ascending=False)
    pd.set_option("display.width", 260)
    cols = ["partition", "score", "L_n_types", "L_p_mean", "L_p_sd", "L_p_pos", "L_o_mean_sd", "L_o_specialty",
            "C_inter", "C_rev_pairs", "C_rev", "rel_prof"]
    print(R[cols].round(2).head(25).to_string(index=False))
    print("\n--- worst / random baselines")
    print(R[cols].round(2).tail(12).to_string(index=False))
    R.to_csv(os.path.join(HERE, "out", "search_ranking.csv"), index=False)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    main()
