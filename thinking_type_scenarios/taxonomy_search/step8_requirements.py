# -*- coding: utf-8 -*-
"""Step 8 - score every candidate classification on the four measurable requirements and save the table.

Requirements (a classification is "good" when ...)
  R1 divergence   : strategy x type ordering flips (reversal pairs, 0-6) and the within-task contrast
                    profiles swing (c_inter)
  R2 PRESSURE     : absolute level near zero but positive on average (p_mean > 0) and flat (small p_sd),
                    on >= 60% of types
  R3 the other four: swing between types (o_sd), and only one or two types are tolerable (o_specialty
                    small) while the mean is clearly negative
  R4 trust        : split-half reproducibility of the type profiles (rel) - the guard against picking
                    noise; plus a floor of min 25 tasks per cell
"""
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
import step4_search as S4                                       # noqa: E402
import step6_genre as S6                                        # noqa: E402

FOCAL = S2.FOCAL
ALLS = ["PRESSURE"] + FOCAL
MIN_CELL = 25


def rev_pairs(C, lab, min_n=MIN_CELL, z_thr=1.5):
    M = S3.contrast_matrix(C, lab, min_n=min_n)
    n, det = 0, {}
    for a, b in itertools.combinations(FOCAL, 2):
        da = M[M.strategy == a].set_index("type")
        db = M[M.strategy == b].set_index("type")
        j = da.index.intersection(db.index)
        if len(j) == 0:
            det["%s-%s" % (a[:4], b[:4])] = (np.nan, [])
            continue
        diff = da.loc[j, "contrast"] - db.loc[j, "contrast"]
        se = np.sqrt(da.loc[j, "se"] ** 2 + db.loc[j, "se"] ** 2)
        z = (diff / se).dropna()
        if (z > z_thr).any() and (z < -z_thr).any():
            n += 1
        det["%s-%s" % (a[:4], b[:4])] = (round(float(diff.mean()), 1),
                                         [t for t in z.index if abs(z[t]) > z_thr])
    return n, det


def main():
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 260)
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    d, band, W = S3.rows_band()
    S3.W = W
    lvl = feat.thinking_type.str[:2].astype(str)
    fmt = feat.has_fmt.map({True: "fmt", False: "free"}).astype(str)
    g = S6.genres(feat)

    auto = S4.build_candidates(feat)
    cands = {k: v for k, v in auto.items()}
    cands.update({
        "GENRE (5)": g,
        "GENRE x level": g + "|" + lvl,
        "GENRE x output-constraint": g + "|" + fmt,
        "GENRE x level x output-constraint": g + "|" + lvl + "|" + fmt,
        "v2 operation level (3)": lvl,
        "v2 target (4)": feat.target.astype(str),
        "v2 12 types": feat.thinking_type.astype(str),
    })
    rows = []
    for name, lab in cands.items():
        lab = pd.Series(lab, index=feat.index).astype(str)
        rep, mats = S6.evaluate(feat, lab, C, d, W, name)
        rp, det = rev_pairs(C, lab)
        rep.update(rev_pairs=rp, partition=name,
                   kind="random" if name.startswith("random") else ("reference" if name in
                        ("v2 12 types", "v2 operation level (3)", "v2 target (4)", "family") else "content"))
        rep["score"] = (0.45 * (rp / 6.0) + 0.25 * min(max(rep["c_inter"] / 10.0, 0), 1)
                        + 0.15 * min(max(rep["o_sd"] / 20.0, 0), 1)
                        + 0.15 * (min(max(rep["p_mean"], 0), 5) / 5.0) * min(max(rep["p_pos"], 0), 1)
                        - 0.20 * min(max(rep["p_sd"] / 20.0, 0), 1))
        rep["R1"] = round(0.5 * rp / 6 + 0.5 * min(rep["c_inter"] / 6.0, 1), 3)
        rep["R2"] = round(0.5 * min(max(rep["p_mean"], 0) / 3.0, 1) * min(rep["p_pos"] / 0.6, 1)
                          + 0.5 * min(max(1 - rep["p_sd"] / 8.0, 0), 1), 3)
        rep["R3"] = round(0.5 * min(rep["o_sd"] / 8.0, 1) + 0.5 * min(max(1 - rep["o_specialty"] / 3.0, 0), 1), 3)
        rep["R4"] = round(min(max(rep["rel"], 0), 1) if rep["rel"] == rep["rel"] else 0.0, 3)
        rows.append(rep)
    R = pd.DataFrame(rows)
    R["total"] = (R.R1 + R.R2 + R.R3 + R.R4) / 4.0
    R = R.sort_values("total", ascending=False)
    cols = ["partition", "kind", "n_types", "R1", "R2", "R3", "R4", "total", "c_inter", "rev_pairs",
            "p_mean", "p_sd", "p_pos", "o_mean", "o_sd", "o_specialty", "rel", "score"]
    print(R[cols].round(2).to_string(index=False))
    R.to_csv(os.path.join(HERE, "out", "requirements_all.csv"), index=False)
    print("\n--- per requirement the best candidate")
    for r in ["R1", "R2", "R3", "R4"]:
        b = R.loc[R[r].idxmax()]
        print("  %s : %-38s %.2f" % (r, b.partition, b[r]))


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    main()
