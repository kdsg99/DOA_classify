# -*- coding: utf-8 -*-
r"""tt7 figures: tt3 layout + three *demand* dimensions on every bar.

Thinking type = dim1 x dim2, both are properties of the *task*:
  dimension 1  operation level -> bar COLOUR   (blue / green / red)
  dimension 2  target          -> bar PATTERN  (K none, R ///, E xxx, F \\\)
  dimension 3  starting state  -> bar SOLID/HOLLOW:
               solid = continuation (>=30 % of the type's items build on a previous turn),
               hollow + dashed edge = from scratch
  thin cell (n < 15)           -> paler bar + red "n=" in the right margin

Difficulty (headroom) is deliberately NOT a bar dimension: it is a property of the model-task
pair at measurement time, not a cognitive demand, and it is exactly what fig 2/3 correct for.

Data: tt3_analysis.py output (out/cells_3dims.csv, out/spread_by_strategy.csv).
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.patches as mpatches                           # noqa: E402
import matplotlib.pyplot as plt                                 # noqa: E402
from taxonomy_v2 import (TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET,  # noqa: E402
                         LEVELS, TARGETS, LEVEL_EN, TARGET_EN)

matplotlib.rcParams["hatch.linewidth"] = 1.6

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
ORDER = TYPE_IDS
LEVEL_COLOR = {"L1": "#1F77B4", "L2": "#2CA02C", "L3": "#D62728"}
TARGET_HATCH = {"K": None, "R": "///", "E": "xxx", "F": "\\\\\\"}
THIN = 15
PAD = 20.0

# ------------------------------------------------- dimension 3: starting state (continuation?)
ROWS = pd.read_csv(os.path.join(HERE, "data", "rows_v2.csv"))
ROWS = ROWS[ROWS.thinking_type.isin(TYPE_IDS)]
CONT_SHARE = ROWS.groupby("thinking_type").apply(
    lambda x: float((x.dataset_id == "mt_bench").mean()), include_groups=False)
CONT_EDGE = 0.30
ID2D3 = {t: ("Continuation" if CONT_SHARE.get(t, 0.0) >= CONT_EDGE else "FromScratch")
         for t in TYPE_IDS}
ID2CONT = {t: float(CONT_SHARE.get(t, np.nan)) for t in TYPE_IDS}
D3_LABEL = {"Continuation": "continuation  (\u2265 30 % of items)",
            "FromScratch": "from scratch  (< 30 %)"}

R = pd.read_csv(os.path.join(HERE, "out", "cells_3dims.csv"))
S = pd.read_csv(os.path.join(HERE, "out", "spread_by_strategy.csv"))
OUT = os.path.join(HERE, "figs_tt7")
os.makedirs(OUT, exist_ok=True)


def axis_limit(values, thin):
    v = np.abs(np.asarray(values)[~np.asarray(thin)])
    lim = max(float(np.nanmax(v)) if len(v) else float(np.nanmax(np.abs(values))), 10.0)
    return float(np.ceil(lim * 1.25 / 5.0) * 5)


def bar(ax, y, v, lim, level, target, d3, thin, zorder=3):
    """one bar = one thinking type: colour = level, hatch = target, solid/hollow = starting state."""
    clip = (not np.isnan(v)) and abs(v) > lim
    v_draw = np.sign(v) * lim * 0.97 if clip else v
    if d3 == "Continuation":
        fc, ec, ls, alpha = LEVEL_COLOR[level], "white", "solid", 0.55 if thin else 0.95
    else:
        fc, ec, ls, alpha = LEVEL_COLOR[level], LEVEL_COLOR[level], (0, (3, 2)), 0.20 if thin else 0.28
    ax.barh(y, v_draw, height=0.68, color=fc, alpha=alpha, hatch=TARGET_HATCH.get(target),
            edgecolor=ec, linewidth=1.0, linestyle=ls, zorder=zorder)
    if np.isnan(v):
        return
    txt = "%.1f" % v + (" \u21af" if clip else "")
    if clip:
        ax.text(v_draw * 0.97, y, txt, va="center", ha="right" if v > 0 else "left",
                fontsize=7.0, color="white", zorder=5, fontweight="bold")
    else:
        ax.text(v + (1.0 if v >= 0 else -1.0), y, txt, va="center", ha="left" if v >= 0 else "right",
                fontsize=7.0, color="#333", zorder=4)


def type_panel(ax, strat, col, lim, xlabel):
    g = R[R.strategy == strat].set_index("thinking_type").reindex(ORDER)
    ys = np.arange(len(ORDER))[::-1]
    for y, t in zip(ys, ORDER):
        row = g.loc[t]
        bar(ax, y, row[col], lim, ID2LEVEL[t], ID2TARGET[t], ID2D3[t], bool(row["thin"]))
        ax.text(lim + PAD * 0.99, y, "n=%d" % row["n"], va="center", ha="right", fontsize=6.6,
                color="#C0392B" if row["thin"] else "#999", zorder=4)
    ax.axvline(0, color="#222", lw=1.2, zorder=2)
    for i in range(len(ORDER) // 4 - 1):
        ax.axhline(len(ORDER) - 4 * (i + 1) - 0.5, color="#c9c9c9", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(["%s  %s" % (t, ID2EN[t]) for t in ORDER], fontsize=8.0)
    ax.set_xlim(-(lim + PAD), lim + PAD)
    ax.set_ylim(-0.7, len(ORDER) - 0.3)
    ax.set_xlabel(xlabel, fontsize=8.4)
    sp = S[(S.strategy == strat) & (S.version == col)].iloc[0]
    star = "  \u2605" if strat == "PRESSURE" else ""
    ax.set_title("%s%s" % (strat, star), fontsize=11.0, fontweight="bold", loc="left")
    ax.text(0.0, 1.012, "mean %+.1f   SD %.1f   range %.0f" % (sp["mean"], sp.sd, sp.rng),
            transform=ax.transAxes, fontsize=7.8, color="#666")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def marginal_panel(ax, strat, col, lim):
    g = R[R.strategy == strat]
    items = [("L%d %s" % (i + 1, LEVEL_EN[l]), g[g.level == l], LEVEL_COLOR[l]) for i, l in enumerate(LEVELS)]
    items += [("%s %s" % (t, TARGET_EN[t]), g[g.target == t], LEVEL_COLOR["L1"]) for t in TARGETS]
    items += [("continuation", g[[ID2D3[t] == "Continuation" for t in g.thinking_type]], "#7F8C8D"),
              ("from scratch", g[[ID2D3[t] == "FromScratch" for t in g.thinking_type]], "#7F8C8D"),
              ("All types", g, "#555555")]
    ys = np.arange(len(items))[::-1]
    for y, (lab, sub, colr) in zip(ys, items):
        v = float(np.nanmean(sub[col].values)) if len(sub) else np.nan
        ax.barh(y, v, height=0.6, color=colr, alpha=0.9, zorder=3)
        if not np.isnan(v):
            ax.text(v + (1.0 if v >= 0 else -1.0), y, "%.1f" % v, va="center",
                    ha="left" if v >= 0 else "right", fontsize=7.0, color="#333", zorder=4)
    ax.axvline(0, color="#222", lw=1.2, zorder=2)
    for cut in (0.5, 3.5, 5.5):
        ax.axhline(cut, color="#c9c9c9", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([i[0] for i in items], fontsize=8.0)
    ax.set_xlim(-(lim + PAD), lim + PAD)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_xlabel("marginal, one type = one vote (pp)", fontsize=8.2)
    ax.set_title("%s \u2014 marginals" % strat, fontsize=10.0, loc="left")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def spread_panel(ax, col):
    sub = S[S.version == col].set_index("strategy").loc[STRATS]
    order = sub.sort_values("sd").index.tolist()
    ys = np.arange(len(order))[::-1]
    for y, s in zip(ys, order):
        c = "#C0392B" if s == "PRESSURE" else "#7F8C8D"
        ax.barh(y, sub.loc[s, "sd"], height=0.55, color=c, alpha=1.0 if s == "PRESSURE" else 0.78, zorder=3)
        ax.text(sub.loc[s, "sd"] + 0.2, y, "SD %.1f" % sub.loc[s, "sd"], va="center", fontsize=8.2,
                color="#333", zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels(order, fontsize=9.5)
    ax.set_xlim(0, sub.sd.max() * 1.55)
    ax.set_xlabel("spread over the 12 types (pp)", fontsize=8.6)
    ax.set_title("Evenness across types", fontsize=11.0, fontweight="bold", loc="left")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def swatch(ax, x, y, w, h, level="L2", target=None, d3="Continuation"):
    if d3 == "Continuation":
        fc, ec, ls, alpha = LEVEL_COLOR[level], "white", "solid", 0.95
    else:
        fc, ec, ls, alpha = LEVEL_COLOR[level], LEVEL_COLOR[level], (0, (3, 2)), 0.28
    ax.add_patch(mpatches.Rectangle((x, y), w, h, transform=ax.transAxes, fc=fc, alpha=alpha,
                                    hatch=TARGET_HATCH.get(target), ec=ec, lw=1.0, ls=ls))


def notes_panel(ax, headline, lines):
    ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0.02, 0.02), 0.96, 0.96, transform=ax.transAxes,
                                    fc="#FAFAFA", ec="#999", lw=1.0))
    ax.text(0.06, 0.962, headline, transform=ax.transAxes, fontsize=10.5, fontweight="bold", va="top")
    y = 0.878
    for ln in lines:
        ax.text(0.06, y, ln, transform=ax.transAxes, fontsize=8.4, va="top", color="#333")
        y -= 0.055
    y -= 0.026
    ax.text(0.06, y, "Every bar carries the three dimensions of its thinking type:",
            transform=ax.transAxes, fontsize=9.6, fontweight="bold", va="top")
    y -= 0.062
    for l in LEVELS:
        swatch(ax, 0.075, y - 0.024, 0.055, 0.030, level=l)
        ax.text(0.144, y, "%s %s  \u2014 colour" % (l, LEVEL_EN[l]), transform=ax.transAxes,
                fontsize=8.4, va="top")
        y -= 0.052
    y -= 0.012
    for t in TARGETS:
        swatch(ax, 0.075, y - 0.024, 0.055, 0.030, level="L1", target=t)
        ax.text(0.144, y, "%s %s  \u2014 pattern" % (t, TARGET_EN[t]), transform=ax.transAxes,
                fontsize=8.4, va="top")
        y -= 0.052
    y -= 0.012
    for d3 in ("Continuation", "FromScratch"):
        swatch(ax, 0.075, y - 0.024, 0.055, 0.030, level="L2", d3=d3)
        ax.text(0.144, y, "%s  \u2014 %s" % (D3_LABEL[d3], "solid" if d3 == "Continuation" else "hollow"),
                transform=ax.transAxes, fontsize=8.4, va="top")
        y -= 0.052
    y -= 0.026
    ax.text(0.06, y, "solid / hollow = starting state: share of the type's items that build on a "
            "previous turn (MT-Bench 2nd turns).", transform=ax.transAxes, fontsize=8.0, va="top",
            color="#777")
    y -= 0.05
    ax.text(0.06, y, "\u21af = clipped to the axis limit.   n = rows behind the cell "
            "(red + paler bar = n < %d, indicative only)." % THIN, transform=ax.transAxes,
            fontsize=8.0, va="top", color="#C0392B")


def build(col, fname, headline, lines, xlabel, suptitle):
    v = R[col].dropna().values
    lim = axis_limit(v, R["thin"].values)
    fig = plt.figure(figsize=(30, 13.5))
    gs = fig.add_gridspec(2, 6, width_ratios=[1, 1, 1, 1, 1, 1.05], hspace=0.32, wspace=0.34)
    for j, s in enumerate(STRATS):
        type_panel(fig.add_subplot(gs[0, j]), s, col, lim, xlabel)
        marginal_panel(fig.add_subplot(gs[1, j]), s, col, lim)
    spread_panel(fig.add_subplot(gs[0, 5]), col)
    notes_panel(fig.add_subplot(gs[1, 5]), headline, lines)
    fig.suptitle(suptitle, fontsize=16, fontweight="bold", y=0.985)
    fig.savefig(os.path.join(OUT, fname), dpi=110, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.join(OUT, fname))


COMMON = ["values in pp; \u0394 = re-ask \u2212 plain (both min-max 0-100).",
          "figures 1-3 show the profile: each value minus the strategy's own mean over the 12 types."]

if __name__ == "__main__":
    build("std_rel", "fig2_difficulty.png",
          "Fig 2 \u2014 difficulty-corrected profile",
          COMMON + ["correction: keep 5 \u2264 baseline \u2264 95, re-weight every cell to one common baseline mix."],
          "pp vs the strategy's own mean",
          "Figure 2 \u2014 difficulty-corrected profile: which thinking types does each re-ask do "
          "comparatively well / badly on?")
    build("std_fam_rel", "fig3_balanced.png",
          "Fig 3 \u2014 difficulty-corrected + size-balanced profile",
          COMMON + ["size balance: figure-2 value re-averaged with one evaluation family = one vote."],
          "pp vs the strategy's own mean",
          "Figure 3 \u2014 difficulty-corrected and size-balanced profile")
    build("raw_rel", "fig1_raw.png",
          "Fig 1 \u2014 raw profile (no correction)",
          COMMON + ["no difficulty correction: cells full of already-perfect items can only lose."],
          "pp vs the strategy's own mean",
          "Figure 1 \u2014 raw profile, before any difficulty correction")
    build("std", "fig2_difficulty_levels.png",
          "Fig 2L \u2014 difficulty-corrected, absolute level",
          COMMON + ["absolute level: PRESSURE stays near 0, the other four are negative nearly everywhere."],
          "pp vs plain",
          "Figure 2L \u2014 difficulty-corrected absolute level (reference view)")
    print("dim3 split:", {t: ("cont" if ID2D3[t] == "Continuation" else "scratch")
                          for t in ORDER})
    print("continuation share:", {t: round(ID2CONT[t], 2) for t in ORDER})
