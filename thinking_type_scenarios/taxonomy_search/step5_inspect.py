# -*- coding: utf-8 -*-
"""Step 5 - inspect the leading classifications: what are the types, and do the reversals survive a
split of the tasks?"""
import hashlib
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screen2 as S2                                            # noqa: E402
import step3_choose as S3                                       # noqa: E402
import step4_search as S4                                       # noqa: E402

FOCAL = S2.FOCAL
ALLS = ["PRESSURE"] + FOCAL


def describe(feat, lab, topn=12):
    X = TfidfVectorizer(max_features=4000, stop_words="english", ngram_range=(1, 2)).fit_transform(
        feat.txt.fillna("").astype(str))
    vocab = np.array(TfidfVectorizer(max_features=4000, stop_words="english", ngram_range=(1, 2)).fit(
        feat.txt.fillna("").astype(str)).get_feature_names_out())
    lab = pd.Series(lab, index=feat.index).astype(str)
    rows = []
    for t, idx in lab.groupby(lab).groups.items():
        sub = feat.loc[idx]
        m = np.asarray(X[feat.index.isin(idx)].mean(axis=0)).ravel()
        terms = ", ".join(vocab[np.argsort(-m)[:topn]])
        rows.append(dict(type=t, n=len(idx), pres=int((sub["second_turn"].notna()).sum()),
                         fam=str(sub.dataset_id.value_counts().head(3).to_dict()),
                         lvl=str(sub.thinking_type.str[:2].value_counts().head(3).to_dict()),
                         tgt=str(sub.target.value_counts().head(3).to_dict()),
                         avg_len=int(sub.tlen.mean()), terms=terms[:150]))
    return pd.DataFrame(rows)


def matrices(C, d, W, lab, min_n=25):
    L = S3.level_matrix(d, lab)
    M = S3.contrast_matrix(C, lab, min_n=min_n)
    Lm = L.pivot_table(index="type", columns="strategy", values="level")[ALLS]
    Nm = L.pivot_table(index="type", columns="strategy", values="n")[ALLS]
    return L, Nm, M, Lm, Nm


def split_reversal(C, lab, z_thr=1.5):
    idx = np.array(C.index)
    h = np.array([int(hashlib.md5(str(s).encode()).hexdigest(), 16) % 2 for s in idx])
    out = []
    for a, b in itertools.combinations(FOCAL, 2):
        for half in (0, 1):
            Ch = C[h == half]
            M = S3.contrast_matrix(Ch, lab.reindex(np.array(C.index)[h == half]), min_n=8)
            da = M[M.strategy == a].set_index("type")
            db = M[M.strategy == b].set_index("type")
            j = da.index.intersection(db.index)
            if len(j) == 0:
                continue
            diff = da.loc[j, "contrast"] - db.loc[j, "contrast"]
            se = np.sqrt(da.loc[j, "se"] ** 2 + db.loc[j, "se"] ** 2)
            z = (diff / se).dropna()
            out.append(dict(pair="%s-%s" % (a[:4], b[:4]), half=half,
                            pos=int((z > z_thr).sum()), neg=int((z < -z_thr).sum()),
                            types=str([t for t in z.index if abs(z[t]) > z_thr])))
    return pd.DataFrame(out)


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    d, band, W = S3.rows_band()
    S3.W = W
    cs = S4.build_candidates(feat)
    for name in ["agg8 x level", "agg8 x len", "agg4 x level"]:
        lab = cs[name]
        print("\n" + "=" * 110)
        print("### %s" % name)
        print(describe(feat, lab).to_string(index=False))
        L, N, M, Lm, Nm = matrices(C, d, W, lab)
        print("\n-- LEVEL (pp vs plain, difficulty-standardised)")
        print(pd.concat([Lm.round(1), Nm.astype("Int64")], axis=1, keys=["lvl", "n"]).to_string())
        Mm = M.pivot(index="type", columns="strategy", values="contrast")[FOCAL]
        Sm = M.pivot(index="type", columns="strategy", values="se")[FOCAL]
        Nc = M.pivot(index="type", columns="strategy", values="n")[FOCAL]
        print("\n-- CONTRAST (pp) / se / n")
        print(pd.concat([Mm.round(1), Sm.round(1), Nc.astype("Int64")], axis=1,
                        keys=["c", "se", "n"]).to_string())
        print("\n-- reversal stability (|z|>1.5 count in each half of the tasks)")
        print(split_reversal(C, lab).to_string(index=False))
