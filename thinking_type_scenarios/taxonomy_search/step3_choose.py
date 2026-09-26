# -*- coding: utf-8 -*-
"""Step 3 - for the leading candidate classifications: level matrix, within-task contrast matrix with
standard errors, split-half stability per cell, and a significance-filtered reversal table.

Level  (what the user wants to see in the bars): difficulty-standardised score change vs plain,
       i.e. restrict to the headroom band 5-95 and re-weight every cell to the same original-score mix.
Contrast (where strategy-versus-strategy differences live): within-task centring over the four
       non-PRESSURE strategies, so the shared task effect cancels.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screen2 as S2                                            # noqa: E402

EDGES = [5, 25, 45, 65, 95]
FOCAL = S2.FOCAL
ALLS = ["PRESSURE"] + FOCAL


def rows_band():
    d = pd.read_csv(os.path.join(HERE, "..", "data", "rows_v2.csv"))
    d["dpp"] = 100 * d.delta
    d["p"] = 100 * d.plain_minmax
    d["key"] = d.dataset_id.astype(str) + "|" + d.task_id.astype("string").fillna("NA")
    band = d[(d.p >= 5) & (d.p <= 95)].copy()
    band["bin"] = pd.cut(band.p, EDGES, labels=False, include_lowest=True)
    d["bin"] = pd.cut(d.p, EDGES, labels=False, include_lowest=True)
    W = band.groupby("bin").size() / len(band)
    return d, band, W


def std_value(g, W):
    if len(g) == 0:
        return np.nan, 0.0, 0
    mb = g.groupby("bin").dpp.mean()
    w = W.reindex(mb.index).fillna(0.0)
    cov = float(w.sum())
    if cov <= 0:
        return np.nan, 0.0, len(g)
    return float((mb * w).sum() / cov), cov, len(g)


def level_matrix(d, lab):
    out = []
    for s in ALLS:
        g = d[d.strategy == s].copy()
        g["t"] = lab.reindex(g.key).values
        for t, gg in g.groupby("t"):
            v, cov, n = std_value(gg, W)
            out.append(dict(strategy=s, type=t, level=v, n=n, coverage=cov,
                            gain_rate=float((gg.dpp > 0).mean()), sat=float((gg.p >= 99.9).mean())))
    return pd.DataFrame(out)


def contrast_matrix(C, lab, min_n=20):
    df = C.copy()
    df["t"] = lab.reindex(df.index).astype(str)
    rec = []
    for s in FOCAL:
        g = df.dropna(subset=[s])
        for t, gg in g.groupby("t"):
            if len(gg) < min_n:            # thin cells are not credible for strategy comparisons
                continue
            rec.append(dict(strategy=s, type=t, contrast=float(gg[s].mean()),
                            se=float(gg[s].std(ddof=1) / np.sqrt(len(gg))), n=len(gg)))
    return pd.DataFrame(rec)


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    d, band, W = rows_band()
    _, cands = S2.candidates(piv, feat)
    cands.update(S2.text_clusters(feat))
    keep = ["kmeans text (k=12)", "primary_group (4)", "family (6)", "task length tercile (3)",
            "family x level", "v2 12 types"]
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    for name in keep:
        lab = pd.Series(cands[name], index=feat.index).astype(str)
        L = level_matrix(d, lab)
        M = contrast_matrix(C, lab)
        L.to_csv(os.path.join(HERE, "out", "level_%s.csv" % name.replace(" ", "_").replace("(", "").replace(")", "")),
                 index=False)
        M.to_csv(os.path.join(HERE, "out", "contrast_%s.csv" % name.replace(" ", "_").replace("(", "").replace(")", "")),
                 index=False)
        # level view
        Lm = L[L.n >= 20].pivot(index="type", columns="strategy", values="level")[ALLS]
        Nm = L.pivot(index="type", columns="strategy", values="n")[ALLS]
        print("\n=== %s  |  LEVEL (pp vs plain, difficulty-standardised, cells with n>=20)" % name)
        print(pd.concat([Lm.round(1), Nm.astype("Int64")], axis=1, keys=["level", "n"]).to_string())
        # contrast view + reversal table
        Mm = M.pivot(index="type", columns="strategy", values="contrast")[FOCAL]
        print("--- within-task contrast (pp; positive = better than the other three on the same tasks)")
        print(Mm.round(1).to_string())
        pairs = []
        for i, a in enumerate(FOCAL):
            for b in FOCAL[i + 1:]:
                da = M[M.strategy == a].set_index("type")
                db = M[M.strategy == b].set_index("type")
                j = da.index.intersection(db.index)
                diff = (da.loc[j, "contrast"] - db.loc[j, "contrast"])
                se = np.sqrt(da.loc[j, "se"] ** 2 + db.loc[j, "se"] ** 2)
                z = diff / se
                sig_pos = [t for t in j if z[t] > 1.5]
                sig_neg = [t for t in j if z[t] < -1.5]
                if sig_pos and sig_neg:
                    pairs.append((a, b, [(t, round(float(diff[t]), 1), round(float(z[t]), 1)) for t in j
                                         if abs(z[t]) > 1.5]))
        print("--- significant reversals (|z|>1.5 in both directions across types): %d of 6 pairs" % len(pairs))
        for p in pairs:
            print("    %-11s vs %-11s : %s" % (p[0], p[1], p[2]))
