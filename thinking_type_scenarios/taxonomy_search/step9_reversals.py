# -*- coding: utf-8 -*-
"""Step 9 - which of the reversals are trustworthy? per-pair detail + split-half stability."""
import hashlib
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screen2 as S2                                            # noqa: E402
import step3_choose as S3                                       # noqa: E402
import step6_genre as S6                                        # noqa: E402

FOCAL = S2.FOCAL
MIN_CELL = 25


def detail(C, lab, tag):
    M = S3.contrast_matrix(C, lab, min_n=MIN_CELL)
    rows = []
    for a, b in itertools.combinations(FOCAL, 2):
        da = M[M.strategy == a].set_index("type")
        db = M[M.strategy == b].set_index("type")
        j = da.index.intersection(db.index)
        if len(j) < 2:
            continue
        diff = da.loc[j, "contrast"] - db.loc[j, "contrast"]
        se = np.sqrt(da.loc[j, "se"] ** 2 + db.loc[j, "se"] ** 2)
        z = (diff / se)
        pos = [t for t in j if z[t] > 1.5]
        neg = [t for t in j if z[t] < -1.5]
        rows.append(dict(cand=tag, pair="%s vs %s" % (a[:4], b[:4]), n_types=len(j),
                         mean_diff=round(float(diff.mean()), 1),
                         max_pos=round(float(diff.max()), 1), at=[t for t in j if diff[t] == diff.max()][0],
                         max_neg=round(float(diff.min()), 1), at2=[t for t in j if diff[t] == diff.min()][0],
                         flip="YES" if (pos and neg) else "-",
                         sig_pos=str(pos), sig_neg=str(neg)))
    return pd.DataFrame(rows)


def stability(C, lab, tag, z_thr=1.2):
    idx = np.array(C.index)
    h = np.array([int(hashlib.md5(str(s).encode()).hexdigest(), 16) % 2 for s in idx])
    out = []
    for a, b in itertools.combinations(FOCAL, 2):
        d = {}
        for half in (0, 1):
            Ch = C[h == half]
            M = S3.contrast_matrix(Ch, lab.reindex(np.array(C.index)[h == half]), min_n=10)
            da = M[M.strategy == a].set_index("type")
            db = M[M.strategy == b].set_index("type")
            j = da.index.intersection(db.index)
            if len(j) == 0:
                continue
            diff = da.loc[j, "contrast"] - db.loc[j, "contrast"]
            d[half] = diff
        if len(d) < 2:
            continue
        j = d[0].index.intersection(d[1].index)
        if len(j) < 2:
            continue
        same_sign = float((np.sign(d[0][j]) == np.sign(d[1][j])).mean())
        r = float(np.corrcoef(d[0][j].rank(), d[1][j].rank())[0, 1]) if len(j) >= 3 else np.nan
        out.append(dict(cand=tag, pair="%s vs %s" % (a[:4], b[:4]), types=len(j),
                        sign_agree=round(same_sign, 2), rank_corr=round(r, 2) if r == r else np.nan,
                        h0=[round(float(x), 1) for x in d[0][j]], h1=[round(float(x), 1) for x in d[1][j]]))
    return pd.DataFrame(out)


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 260)
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    lvl = feat.thinking_type.str[:2].astype(str)
    fmt = feat.has_fmt.map({True: "fmt", False: "free"}).astype(str)
    g = S6.genres(feat)
    import step4_search as S4
    auto = S4.build_candidates(feat)
    cands = {"GENRE x output-constraint": g + "|" + fmt,
             "GENRE x level": g + "|" + lvl,
             "agg8 x level": auto["agg8 x level"],
             "GENRE x level x output-constraint": g + "|" + lvl + "|" + fmt}
    for tag, lab in cands.items():
        lab = pd.Series(lab, index=feat.index).astype(str)
        print("\n=== %s" % tag)
        print(detail(C, lab, tag).to_string(index=False))
        print("-- split-half stability of the pairwise differences")
        print(stability(C, lab, tag).to_string(index=False))
