# -*- coding: utf-8 -*-
"""Step 6 - define an interpretable CONTENT genre axis (deliverable form) and evaluate genre x level."""
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
import step5_inspect as S5                                      # noqa: E402

FOCAL = S2.FOCAL
ALLS = ["PRESSURE"] + FOCAL


def genres(feat, variant="v1"):
    t = feat.txt.fillna("").astype(str)
    code = t.str.contains(r"```|def |function|json|ascii|mnist|concode|schema|regex|sql|api|compile|debug",
                          case=False, regex=True)
    math = feat.dataset_id.eq("chat_math500") | feat.subject.fillna("").str.contains("math", case=False) | \
        feat.primary_tag.fillna("").str.contains("math|quant", case=False, regex=True)
    verify = feat.second_turn.notna()
    write = feat.dataset_id.eq("chat_wild_bench") | feat.target.eq("E") | \
        feat.category.fillna("").str.contains("creativ|role|common-sense|advertis", case=False, regex=True)
    g = pd.Series("skill_short", index=feat.index)
    g[write] = "prose_open"
    g[math] = "quant_math"
    g[verify] = "verify_fix"
    g[code] = "code_format"
    if variant == "v2":                     # code/format wins over everything, math keeps its own bucket
        g[code] = "code_format"
        g[math & ~code] = "quant_math"
    return g


def evaluate(feat, lab, C, d, W, name, min_n=25):
    lab = pd.Series(lab, index=feat.index).astype(str)
    L = S3.level_matrix(d, lab)
    Lm = L.pivot_table(index="type", columns="strategy", values="level")[ALLS]
    Nm = L.pivot_table(index="type", columns="strategy", values="n")[ALLS]
    G = L.pivot_table(index="type", columns="strategy", values="gain_rate")[ALLS]
    keep = (Nm.fillna(0) >= min_n).all(axis=1)
    M = S3.contrast_matrix(C, lab, min_n=min_n)
    Mc = M.pivot(index="type", columns="strategy", values="contrast")[FOCAL]
    Ms = M.pivot(index="type", columns="strategy", values="se")[FOCAL]
    Mn = M.pivot(index="type", columns="strategy", values="n")[FOCAL]
    rep = dict(name=name, n_types=int(keep.sum()),
               p_mean=float(Lm.loc[keep, "PRESSURE"].mean()), p_sd=float(Lm.loc[keep, "PRESSURE"].std(ddof=1)),
               p_pos=float((Lm.loc[keep, "PRESSURE"] > 0).mean()),
               o_sd=float(Lm.loc[keep, FOCAL].std(axis=0, ddof=1).mean()),
               o_mean=float(Lm.loc[keep, FOCAL].values.mean()),
               o_specialty=float((Lm.loc[keep, FOCAL] > -5).sum(axis=0).mean()),
               c_inter=float(Mc.std(axis=0, ddof=1).mean()),
               rel=S4.split_half_profile(C, lab))
    return rep, dict(L=Lm.round(1), N=Nm.astype("Int64"), G=(100 * G).round(0), C=Mc.round(1),
                     se=Ms.round(1), cn=Mn.astype("Int64"), keep=keep)


if __name__ == "__main__":
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 260)
    piv, feat = S2.load()
    C = S2.contrasts(piv, FOCAL)
    d, band, W = S3.rows_band()
    S3.W = W
    lvl = feat.thinking_type.str[:2].astype(str)
    for variant in ["v1"]:
        g = genres(feat, variant)
        print("### genre sizes (tasks):", g.value_counts().to_dict())
        print("genre x family:")
        print(pd.crosstab(g, feat.dataset_id).to_string())
        for nm, lab in [("genre", g), ("genre x level", g + "|" + lvl), ("genre x fmt", g + "|" + feat.has_fmt.map({True: "fmt", False: "free"}))]:
            rep, mats = evaluate(feat, lab, C, d, W, nm)
            print("\n--- %s : %s" % (nm, {k: round(v, 2) if isinstance(v, float) else v for k, v in rep.items()}))
            keep = mats["keep"]
            print("LEVEL (pp) + n, cells kept=%d" % keep.sum())
            print(pd.concat([mats["L"][keep], mats["N"][keep]], axis=1, keys=["lvl", "n"]).to_string())
            print("gain rate (%%)")
            print(mats["G"][keep].to_string())
            print("CONTRAST (pp) / se / n  [kept cells]")
            print(pd.concat([mats["C"][keep], mats["se"][keep], mats["cn"][keep]], axis=1,
                            keys=["c", "se", "n"]).to_string())
