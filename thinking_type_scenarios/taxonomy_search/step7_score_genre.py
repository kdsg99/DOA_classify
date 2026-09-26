# -*- coding: utf-8 -*-
"""Step 7 - score the interpretable genre taxonomies with the same objective used in the search."""
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
ALLS = ["PRESSURE"] + FOCAL
MIN_CELL = 25


def rev_pairs(C, lab, min_n=MIN_CELL, z_thr=1.5):
    M = S3.contrast_matrix(C, lab, min_n=min_n)
    out = {}
    n = 0
    for a, b in itertools.combinations(FOCAL, 2):
        da = M[M.strategy == a].set_index("type")
        db = M[M.strategy == b].set_index("type")
        j = da.index.intersection(db.index)
        if len(j) == 0:
            continue
        diff = da.loc[j, "contrast"] - db.loc[j, "contrast"]
        se = np.sqrt(da.loc[j, "se"] ** 2 + db.loc[j, "se"] ** 2)
        z = (diff / se).dropna()
        if (z > z_thr).any() and (z < -z_thr).any():
            n += 1
        out["%s-%s" % (a[:4], b[:4])] = (round(float(diff.mean()), 1),
                                         str([t for t in z.index if abs(z[t]) > z_thr]))
    return n, out


def objective(rep, rp):
    score = (0.45 * (rp / 6.0) + 0.25 * min(max(rep["c_inter"] / 10.0, 0), 1)
             + 0.15 * min(max(rep["o_sd"] / 20.0, 0), 1)
             + 0.15 * (min(max(rep["p_mean"], 0), 5) / 5.0) * min(max(rep["p_pos"], 0), 1)
             - 0.20 * min(max(rep["p_sd"] / 20.0, 0), 1))
    return score


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    d, band, W = S3.rows_band()
    S3.W = W
    g = S6.genres(feat)
    lvl = feat.thinking_type.str[:2].astype(str)
    fmt = feat.has_fmt.map({True: "fmt", False: "free"}).astype(str)
    cands = {
        "genre (5)": g,
        "genre x level": g + "|" + lvl,
        "genre x fmt": g + "|" + fmt,
        "genre x level x fmt": g + "|" + lvl + "|" + fmt,
    }
    rows = []
    for name, lab in cands.items():
        rep, mats = S6.evaluate(feat, lab, C, d, W, name)
        rp, detail = rev_pairs(C, lab)
        rep["rev_pairs"] = rp
        rep["score"] = objective(rep, rp)
        rep["partition"] = name
        rows.append(rep)
        print("\n%s -> score %.2f, reversal pairs %d/6" % (name, rep["score"], rp))
        for k, v in detail.items():
            print("   %-12s mean diff %+5.1f   |z|>1.5 types: %s" % (k, v[0], v[1]))
    R = pd.DataFrame(rows)[["partition", "n_types", "p_mean", "p_sd", "p_pos", "o_mean", "o_sd",
                            "o_specialty", "c_inter", "rev_pairs", "rel", "score"]]
    print("\n" + R.round(2).to_string(index=False))
    R.to_csv(os.path.join(HERE, "out", "genre_scores.csv"), index=False)
