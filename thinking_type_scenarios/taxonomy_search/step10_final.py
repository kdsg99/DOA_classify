# -*- coding: utf-8 -*-
"""Step 10 - final numbers for the recommended classification (GENRE x output-constraint):
   level (absolute, difficulty-standardised) and the five-way within-task contrast with CIs."""
import hashlib
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

ALLS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
FOCAL = ALLS[1:]
MIN_CELL = 25
OUT = os.path.join(HERE, "out")
GENRE_EN = {"code_format": "Code / format conversion", "prose_open": "Open prose & advice",
            "skill_short": "Skill-constrained short answer", "verify_fix": "Verification / repair",
            "quant_math": "Quantitative reasoning"}
FMT_EN = {"fmt": "output-constrained", "free": "free-form output"}


def five_way_contrast(piv, lab):
    F = piv.reindex(columns=ALLS)
    ok = F.notna().sum(axis=1) >= 3
    C = F[ok].sub(F[ok].mean(axis=1), axis=0)
    C["t"] = lab.reindex(C.index).astype(str)
    rec = []
    for s in ALLS:
        g = C.dropna(subset=[s])
        for t, gg in g.groupby("t"):
            if len(gg) < 5:
                continue
            rec.append(dict(strategy=s, type=t, contrast=float(gg[s].mean()),
                            se=float(gg[s].std(ddof=1) / np.sqrt(len(gg))), n=len(gg)))
    return pd.DataFrame(rec), C


def split_half_cells(C5, lab, min_n=8):
    idx = np.array(C5.index)
    h = np.array([int(hashlib.md5(str(s).encode()).hexdigest(), 16) % 2 for s in idx])
    out = []
    for s in FOCAL:
        rec = {}
        for half in (0, 1):
            Ch = C5[h == half]
            M = M5 = None
            df = Ch.copy()
            t = lab.reindex(df.index).astype(str)
            g = df.dropna(subset=[s]).assign(t=t)
            rec[half] = g.groupby("t")[s].agg(["mean", "size"])
        j = [t for t in rec[0].index if t in rec[1].index
             and rec[0].loc[t, "size"] >= min_n and rec[1].loc[t, "size"] >= min_n]
        if len(j) >= 3:
            a, b = rec[0].loc[j, "mean"], rec[1].loc[j, "mean"]
            out.append(dict(strategy=s, types=len(j),
                            sign_agree=round(float((np.sign(a) == np.sign(b)).mean()), 2),
                            rank_corr=round(float(np.corrcoef(a.rank(), b.rank())[0, 1]), 2)))
    return pd.DataFrame(out)


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    piv, feat = S2.load()
    C4 = S2.contrasts(piv, FOCAL)
    d, band, W = S3.rows_band()
    S3.W = W
    lab = (S6.genres(feat) + "|" + feat.has_fmt.map({True: "fmt", False: "free"}).astype(str))
    lab = pd.Series(lab, index=feat.index).astype(str)

    L = S3.level_matrix(d, lab)
    Lm = L.pivot_table(index="type", columns="strategy", values="level")[ALLS].round(1)
    Nm = L.pivot_table(index="type", columns="strategy", values="n")[ALLS].astype("Int64")
    Gm = (100 * L.pivot_table(index="type", columns="strategy", values="gain_rate")[ALLS]).round(0).astype("Int64")
    keep = (Nm.fillna(0) >= MIN_CELL).all(axis=1)
    C5, C5raw = five_way_contrast(piv, lab)
    Cm = C5.pivot_table(index="type", columns="strategy", values="contrast")[ALLS].round(1)
    Sm = C5.pivot_table(index="type", columns="strategy", values="se")[ALLS].round(1)
    Cn = C5.pivot_table(index="type", columns="strategy", values="n")[ALLS].astype("Int64")
    print("### GENRE x output-constraint  (kept level cells: %d of %d)" % (keep.sum(), len(keep)))
    print("\n-- LEVEL (pp vs plain, difficulty-standardised) / n / gain rate")
    print(pd.concat([Lm[keep], Nm[keep], Gm[keep]], axis=1, keys=["level", "n", "gain%"]).to_string())
    print("\n-- FIVE-WAY within-task contrast (pp; + = better than the average strategy on the same tasks)")
    print(pd.concat([Cm, Sm, Cn], axis=1, keys=["c", "se", "n"]).to_string())
    print("\n-- split-half stability of the focal strategies' cell values")
    print(split_half_cells(C5raw, lab).to_string(index=False))
    Lm.to_csv(os.path.join(OUT, "final_level.csv"))
    Cm.to_csv(os.path.join(OUT, "final_contrast5.csv"))
    Sm.to_csv(os.path.join(OUT, "final_contrast5_se.csv"))
    Nm.to_csv(os.path.join(OUT, "final_level_n.csv"))
    print("\nsaved out/final_*.csv")
