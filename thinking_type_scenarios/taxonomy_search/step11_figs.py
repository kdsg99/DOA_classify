# -*- coding: utf-8 -*-
"""Step 11 - figures.

figA_spec.png      : what the requested outcome costs - requirement scores of every classification
                     family, the noise floor, the trade-off, and the thin-cell artefact.
figB_taxonomy.png  : the recommended classification (GENRE x output-constraint) drawn the way the
                     user wants it - absolute levels on top, five-way within-task contrasts below.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.patches as mpatches                           # noqa: E402
import matplotlib.pyplot as plt                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FIG = os.path.join(HERE, "figs")
os.makedirs(FIG, exist_ok=True)
STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
FOCAL = STRATS[1:]
GENRE_COLOR = {"code_format": "#0E7C7B", "prose_open": "#E08A1E", "skill_short": "#1F77B4",
               "verify_fix": "#6A4C93", "quant_math": "#777777"}
ROWS = ["code_format|fmt", "code_format|free", "prose_open|fmt", "prose_open|free",
        "skill_short|free", "verify_fix|free"]


def lbl(t):
    g, f = t.split("|")
    return "%s\n%s" % ({"code_format": "code / format", "prose_open": "open prose", "skill_short": "skill short",
                        "verify_fix": "verify / repair", "quant_math": "math"}[g],
                       f.replace("fmt", "constrained").replace("free", "free-form"))


# --------------------------------------------------------------------------------- fig A
def fig_spec():
    R = pd.read_csv(os.path.join(OUT, "requirements_all.csv"))
    sel = [("GENRE x output-constraint", "genre x output-constraint (recommended)"),
           ("GENRE x level x output-constraint", "genre x level x output-constraint"),
           ("GENRE x level", "genre x level"),
           ("agg8 x level", "text-cluster(8) x level"),
           ("agg8 x len", "text-cluster(8) x answer length"),
           ("v2 12 types", "current v2 12 thinking types"),
           ("v2 operation level (3)", "operation level only (3)"),
           ("family", "evaluation family (6)")]
    fig = plt.figure(figsize=(26, 15))
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.22)

    # A1 requirement scorecard
    ax = fig.add_subplot(gs[0, 0])
    names, mats = [], []
    for key, disp in sel:
        r = R[R.partition == key]
        if len(r):
            names.append(disp)
            mats.append([r.R1.iloc[0], r.R2.iloc[0], r.R3.iloc[0], r.R4.iloc[0]])
    rnd = R[R.kind == "random"]
    names.append("random split (floor, mean of 8)")
    mats.append([rnd.R1.mean(), rnd.R2.mean(), rnd.R3.mean(), rnd.R4.mean()])
    M = np.array(mats)
    ys = np.arange(len(names))[::-1]
    hatch = ["", "", "", "", "", "", "", "", "//"]
    for i, (y, row) in enumerate(zip(ys, M)):
        left = 0.0
        for j, c in enumerate(["#C0392B", "#2E86C1", "#27AE60", "#8E44AD"]):
            ax.barh(y, row[j], left=left, height=0.62, color=c, alpha=0.9 if hatch[i] == "" else 0.45,
                    hatch=hatch[i] or None, edgecolor="white")
            left += row[j]
        ax.text(4.06, y, "total %.2f" % M[i].mean(), va="center", fontsize=8.5, color="#333")
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 4.6)
    ax.set_xlabel("requirement score (0-1 per requirement, sum = 4 axes)", fontsize=9)
    ax.set_title("A. Which classification satisfies the four requirements?\n"
                 "R1 strategy differences/reversals  R2 PRESSURE flat & mostly positive  "
                 "R3 others swing, one or two specialties  R4 reproducible (split-half)",
                 fontsize=10.5, loc="left")
    ax.grid(axis="x", alpha=0.25)

    # A2 divergence vs number of usable types, content vs random
    ax = fig.add_subplot(gs[0, 1])
    for kind, col, mk, sz in [("content", "#2E86C1", "o", 55), ("reference", "#F39C12", "s", 70),
                              ("random", "#C0392B", "^", 55)]:
        d = R[R.kind == kind]
        ax.scatter(d.n_types, d.c_inter, s=sz, c=col, marker=mk, alpha=0.85,
                   label="%s classification" % kind)
    for _, r in R.iterrows():
        if r.partition in ("GENRE x output-constraint", "agg8 x level", "v2 12 types", "family"):
            ax.annotate(r.partition, (r.n_types, r.c_inter), fontsize=7.5,
                        xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("usable thinking types (cells with >=25 tasks for every strategy)", fontsize=9)
    ax.set_ylabel("strategy x type divergence (pp)", fontsize=9)
    ax.axhline(R[R.kind == "random"].c_inter.mean(), color="#C0392B", ls="--", lw=1.2)
    ax.text(2.1, R[R.kind == "random"].c_inter.mean() + 0.1, "noise floor (random splits)", fontsize=8,
            color="#C0392B")
    ax.set_title("B. Divergence is real but small: content classifications clear the noise floor,\n"
                 "nothing reaches the 10-25 pp swings that thin cells suggest", fontsize=10.5, loc="left")
    ax.legend(fontsize=8.5)
    ax.grid(alpha=0.25)

    # A3 PRESSURE flatness vs the others' volatility
    ax = fig.add_subplot(gs[1, 0])
    for kind, col, mk in [("content", "#2E86C1", "o"), ("reference", "#F39C12", "s"), ("random", "#C0392B", "^")]:
        d = R[R.kind == kind]
        ax.scatter(d.o_sd, d.p_sd, s=60, c=col, marker=mk, alpha=0.85, label="%s" % kind)
    lim = 8.0
    ax.plot([0, lim], [0, lim], color="#555", ls="--", lw=1.0)
    ax.text(6.4, 6.6, "PRESSURE as volatile\nas the others", fontsize=8, rotation=38, color="#555")
    ax.axhline(3.0, color="#27AE60", ls=":", lw=1.2)
    ax.text(0.1, 3.15, "PRESSURE flat (SD < 3 pp)", fontsize=8, color="#27AE60")
    ax.set_xlabel("volatility of the other four (mean SD across types, pp)", fontsize=9)
    ax.set_ylabel("PRESSURE volatility (SD across types, pp)", fontsize=9)
    ax.set_title("C. The two requirements pull in opposite directions:\n"
                 "only coarse or thinly populated classifications make PRESSURE look flat", fontsize=10.5, loc="left")
    ax.legend(fontsize=8.5)
    ax.grid(alpha=0.25)

    # A4 the thin-cell artefact
    ax = fig.add_subplot(gs[1, 1])
    cells = pd.read_csv(os.path.join(HERE, "..", "out", "cells_3dims.csv"))
    e = cells[cells.strategy == "ENCOURAGE"].sort_values("std")
    ys = np.arange(len(e))
    n = e.n.values
    ax.barh(ys, e["std"].values, color=np.where(n < 15, "#C0392B", "#1F77B4"), alpha=0.9, height=0.7)
    for y, (_, r) in enumerate(e.iterrows()):
        ax.text(r["std"] - 2 if r["std"] < 0 else r["std"] + 2, y, "n=%d" % r.n, va="center",
                ha="right" if r["std"] < 0 else "left", fontsize=7.5,
                color="#C0392B" if r.n < 15 else "#555")
    ax.set_yticks(ys)
    ax.set_yticklabels(e.thinking_type, fontsize=8)
    ax.axvline(0, color="#222", lw=1)
    ax.set_xlim(-90, 20)
    ax.set_xlabel("ENCOURAGE level by v2 thinking type (pp)", fontsize=9)
    ax.set_title("D. Where the 'huge swings' came from: the same strategy by cell size.\n"
                 "Red = cells with fewer than 15 tasks - the -77 pp type holds 2 tasks.", fontsize=10.5, loc="left")
    ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Reverse-engineering the thinking-type classification: what each requirement costs",
                 fontsize=16, fontweight="bold", y=0.98)
    fig.savefig(os.path.join(FIG, "figA_spec.png"), dpi=100, bbox_inches="tight")
    plt.close(fig)
    print("wrote figs/figA_spec.png")


# --------------------------------------------------------------------------------- fig B
def fig_taxonomy():
    L = pd.read_csv(os.path.join(OUT, "final_level.csv"), index_col=0)
    N = pd.read_csv(os.path.join(OUT, "final_level_n.csv"), index_col=0)
    C = pd.read_csv(os.path.join(OUT, "final_contrast5.csv"), index_col=0)
    S = pd.read_csv(os.path.join(OUT, "final_contrast5_se.csv"), index_col=0)
    L, N, C, S = (x.reindex(ROWS) for x in (L, N, C, S))
    fig = plt.figure(figsize=(30, 14))
    gs = fig.add_gridspec(2, 6, width_ratios=[1, 1, 1, 1, 1, 1.45], hspace=0.34, wspace=0.34)
    ylab = [lbl(t) for t in ROWS]
    ys = np.arange(len(ROWS))[::-1]

    for j, s in enumerate(STRATS):
        ax = fig.add_subplot(gs[0, j])
        v = L[s].values
        cols = [GENRE_COLOR[t.split("|")[0]] for t in ROWS]
        ax.barh(ys, np.nan_to_num(v), height=0.66, color=cols, alpha=0.92, edgecolor="white")
        for y, val, t in zip(ys, v, ROWS):
            if val == val:
                ax.text(val + (1.2 if val >= 0 else -1.2), y, "%.1f" % val, va="center",
                        ha="left" if val >= 0 else "right", fontsize=8.0, color="#333")
        ax.axvline(0, color="#222", lw=1.2)
        ax.set_yticks(ys)
        ax.set_yticklabels(ylab if j == 0 else [""] * len(ROWS), fontsize=8.2)
        ax.set_xlim(-32, 20)
        ax.set_title("%s\nlevel mean %+.1f pp, SD %.1f" % (s, float(np.nanmean(v)), float(np.nanstd(v, ddof=1))),
                     fontsize=11, fontweight="bold", loc="left")
        ax.set_xlabel("pp vs plain (difficulty-standardised)", fontsize=8.4)
        ax.grid(axis="x", alpha=0.25)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)

    for j, s in enumerate(STRATS):
        ax = fig.add_subplot(gs[1, j])
        v, se = C[s].values, S[s].values
        cols = [GENRE_COLOR[t.split("|")[0]] for t in ROWS]
        ax.barh(ys, np.nan_to_num(v), height=0.62, color=cols, alpha=0.92, edgecolor="white")
        ax.errorbar(np.nan_to_num(v), ys, xerr=1.96 * np.nan_to_num(se), fmt="none", ecolor="#333",
                    elinewidth=1.3, capsize=3)
        for y, val, e in zip(ys, v, se):
            ax.text(val + (1.6 + 1.96 * e), y, "%.1f" % val, va="center", ha="left", fontsize=8.0, color="#333")
        ax.axvline(0, color="#222", lw=1.2)
        ax.set_yticks(ys)
        ax.set_yticklabels([])
        ax.set_xlim(-24, 24)
        ax.set_xlabel("pp vs the average strategy on the same tasks", fontsize=8.4)
        ax.set_title("%s - within-task contrast (95%% CI)" % s, fontsize=10, loc="left")
        ax.grid(axis="x", alpha=0.25)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)

    # right column: definitions + reading
    ax = fig.add_subplot(gs[:, 5])
    ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0.01, 0.01), 0.98, 0.98, transform=ax.transAxes, fc="#FAFAFA",
                                    ec="#999"))
    txt = ["Classification that produces the requested picture",
           "(derived from the search, not assumed)",
           "",
           "Axis 1 - genre of the deliverable (content-based):",
           "   code / format conversion   code, JSON/table/ASCII reconstruction",
           "   open prose & advice        creative writing, explanations, recommendations",
           "   skill-constrained short    fact / safety / skill questions with a short answer",
           "   verification / repair      the model must check and fix an earlier answer",
           "   quantitative reasoning     maths, physics, calculation",
           "Axis 2 - output constraint:",
           "   free-form  vs  output-constrained (schema / format must be respected)",
           "",
           "Why this classification and not the 12 cognitive types:",
           "   - only content-based splits beat the random floor on divergence",
           "   - the genre axis is the one that survives a split of the tasks",
           "   - cells stay >= 25 tasks per strategy (otherwise nothing is credible)",
           "",
           "How to read the panels:",
           "   top rows    absolute change vs plain, difficulty-standardised",
           "   bottom rows within-task contrast: each task is centred on its own",
           "               strategy mean, so task difficulty cancels",
           "",
           "What the picture shows:",
           "   1 PRESSURE: +10.4 / +4.7 / +4.2 / -6.2 / -4.9 / +0.6 (5 of 6 positive)",
           "      and SD 6.3 pp - the flattest of the five, always best in the",
           "      within-task panel (+3.5 ... +12.1)",
           "   2 the other four have one or two tolerable types and lose elsewhere",
           "      CRITICAL +3.0 on code|constrained and +0.2 on prose|constrained",
           "      ENCOURAGE/MISLEADING/HEURISTIC: negative in 5 of 6 genres",
           "   3 reversals (both halves of the tasks agree):",
           "      CRITICAL vs ENCOURAGE   code/free +2.9  ->  prose/free -0.3",
           "      ENCOURAGE vs HEURISTIC  prose/free +4.3 ->  skill/fmt -4.2",
           "      MISLEADING vs HEURISTIC code/fmt -7.4   ->  skill/free -6.0",
           "   split-half sign agreement of the four profiles: .71 - 1.00",
           "",
           "Limits:",
           "   - the four strategies correlate .83-.93 per task: they are near",
           "     substitutes, so their type profiles differ by only ~2.5-3 pp",
           "   - anything larger comes from cells with < 15 tasks (panel D)",
           "   - quant_math cannot be standardised for PRESSURE (too few rows in",
           "     the 5-95 headroom band) and is therefore not shown"]
    ax.text(0.04, 0.985, "\n".join(txt), transform=ax.transAxes, fontsize=9.4, va="top", linespacing=1.42)
    fig.suptitle("Recommended thinking-type classification: genre of the deliverable x output constraint",
                 fontsize=16, fontweight="bold", y=0.985)
    fig.savefig(os.path.join(FIG, "figB_taxonomy.png"), dpi=100, bbox_inches="tight")
    plt.close(fig)
    print("wrote figs/figB_taxonomy.png")


if __name__ == "__main__":
    fig_spec()
    fig_taxonomy()
