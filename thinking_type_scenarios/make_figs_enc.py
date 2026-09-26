# -*- coding: utf-8 -*-
"""Same three tt3 figures, but every bar now shows the three dimensions that compose its thinking type.

  dimension 1  operation level (L1/L2/L3)  ->  bar COLOUR
  dimension 2  target of intervention      ->  bar PATTERN (K none, R slashes, E cross, F backslashes)
  dimension 3  nature of the gain          ->  bar 虚实: Offensive = solid fill, Defensive = hollow
                                               fill with a dashed outline
  (n < 15 = thin cell: the bar is drawn paler and its right-hand label turns red, as before)

Everything else (metrics, layout, marginals, notes) is unchanged from make_figs.py.
"""
import json
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
TARGET_COLOR = {"K": "#6A4C93", "R": "#C0392B", "E": "#E08A1E", "F": "#0E7C7B"}
TARGET_HATCH = {"K": None, "R": "///", "E": "xxx", "F": "\\\\\\"}
NATURE_EN = {"Offensive": "Offensive  (rescues more than it breaks)",
             "Defensive": "Defensive  (breaks more than it rescues)"}
THIN = 15
PAD = 22.0

R = pd.read_csv(os.path.join(HERE, "out", "cells_3dims.csv"))
M = pd.read_csv(os.path.join(HERE, "out", "marginals_3dims.csv"))
S = pd.read_csv(os.path.join(HERE, "out", "spread_by_strategy.csv"))
META = json.load(open(os.path.join(HERE, "out", "meta.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "figs_enc")
os.makedirs(OUT, exist_ok=True)


def axis_limit(values, thin):
    v = np.abs(np.asarray(values)[~np.asarray(thin)])
    lim = max(float(np.nanmax(v)) if len(v) else float(np.nanmax(np.abs(values))), 10.0)
    return float(np.ceil(lim * 1.30 / 5.0) * 5)


def bar(ax, y, v, lim, level, target, nature, thin, zorder=3, label=None):
    """one bar = one thinking type: colour=level, hatch=target, solid/hollow=nature."""
    clip = (not np.isnan(v)) and abs(v) > lim
    v_draw = np.sign(v) * lim * 0.97 if clip else v
    offensive = (nature == "Offensive")
    if offensive:
        fc, ec, ls, alpha = LEVEL_COLOR[level], "white", "solid", 0.55 if thin else 0.95
    else:
        fc, ec, ls, alpha = LEVEL_COLOR[level], LEVEL_COLOR[level], (0, (3, 2)), 0.22 if thin else 0.30
    ax.barh(y, v_draw, height=0.68, color=fc, alpha=alpha, hatch=TARGET_HATCH.get(target),
            edgecolor=ec, linewidth=1.0, linestyle=ls, zorder=zorder)
    if np.isnan(v):
        return
    txt = (label if label else "%.1f" % v) + (" \u21af" if clip else "")
    if clip:
        ax.text(v_draw * 0.97, y, txt, va="center", ha="right" if v > 0 else "left",
                fontsize=7.2, color="white", zorder=5, fontweight="bold")
    else:
        ax.text(v + (1.0 if v >= 0 else -1.0), y, txt, va="center", ha="left" if v >= 0 else "right",
                fontsize=7.2, color="#333", zorder=4)


def type_panel(ax, strat, col, lim, mode):
    other = col[:-4] if col.endswith("_rel") else col + "_rel"
    g = R[R.strategy == strat].set_index("thinking_type").reindex(ORDER)
    ys = np.arange(len(ORDER))[::-1]
    for y, t in zip(ys, ORDER):
        row = g.loc[t]
        bar(ax, y, row[col], lim, ID2LEVEL[t], ID2TARGET[t], row["nature"], bool(row["thin"]),
            label="%.1f" % row[col])
        ax.text(lim + PAD * 0.99, y, "lvl %+.1f \u00b7 n=%d \u00b7 %d%%" % (
            row[other], row["n"], round(100 * row["gain_rate"])),
            va="center", ha="right", fontsize=6.3,
            color="#C0392B" if row["thin"] else "#777", zorder=4)
    ax.axvline(0, color="#222", lw=1.2, zorder=2)
    for i in range(len(ORDER) // 4 - 1):
        ax.axhline(len(ORDER) - 4 * (i + 1) - 0.5, color="#bbb", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(["%s  %s" % (t, ID2EN[t]) for t in ORDER], fontsize=8.0)
    ax.set_xlim(-(lim + PAD), lim + PAD)
    ax.set_ylim(-0.7, len(ORDER) - 0.3)
    ax.set_xlabel("pp  \u2190 worse than usual   |   better than usual \u2192" if mode == "rel"
                  else "Score change vs plain (pp)", fontsize=8.4)
    sp = S[(S.strategy == strat) & (S.version == col)].iloc[0]
    star = "  \u2605 reference (flattest)" if strat == "PRESSURE" else ""
    ax.set_title("%s%s" % (strat, star), fontsize=11.0, fontweight="bold", loc="left")
    ax.text(0.0, 1.012, "level mean %+.1f pp   |   spread SD %.1f / range %.0f" % (sp["mean"], sp.sd, sp.rng),
            transform=ax.transAxes, fontsize=8.0, color="#555")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def marginal_panel(ax, strat, ver, lim):
    m = M[(M.strategy == strat) & (M.version == ver)]
    sub = R[(R.strategy == strat)]
    items = ([("L%d  %s" % (i + 1, LEVEL_EN[l]), l, LEVEL_COLOR[l], "Level") for i, l in enumerate(LEVELS)] +
             [("%s  %s" % (t, TARGET_EN[t]), t, TARGET_COLOR[t], "Target") for t in TARGETS] +
             [(n, n, "#7F8C8D", "Nature") for n in ("Offensive", "Defensive")] +
             [("All types", "all", "#555555", "Overall")])
    ys = np.arange(len(items))[::-1]
    plain = []
    for y, (lab, key, colr, dim) in zip(ys, items):
        if dim == "Nature":
            g = sub[sub.nature == key]
            if len(g):
                val, gr, nt = float(np.nanmean(g[ver].values)), float(np.nanmean(g.gain_rate.values)), len(g)
            else:
                val, gr, nt = np.nan, np.nan, 0
            bar(ax, y, val, lim, "L2", None, "Offensive", False)
        elif dim == "Overall":
            g = sub
            val, gr, nt = float(np.nanmean(g[ver].values)), float(np.nanmean(g.gain_rate.values)), len(g)
            bar(ax, y, val, lim, "L1", None, "Offensive", False)
        else:
            row = m[(m.dimension == dim) & (m.value == key)]
            val, gr, nt = float(row["mean"].iloc[0]), float(row["gain_rate"].iloc[0]), int(row["n_types"].iloc[0])
            bar(ax, y, val, lim, "L1" if dim == "Level" else "L2", key if dim == "Target" else None,
                "Offensive", False)
        ax.text(lim + PAD * 0.99, y, ("%d%% (%d types)" % (round(100 * gr), nt)) if nt else "no such type",
                va="center", ha="right", fontsize=6.4, color="#777", zorder=4)
        plain.append(y)
    ax.axvline(0, color="#222", lw=1.2, zorder=2)
    ax.axhline(0.5, color="#bbb", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.axhline(3.5, color="#bbb", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.axhline(5.5, color="#bbb", lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([i[0] for i in items], fontsize=8.0)
    ax.set_xlim(-(lim + PAD), lim + PAD)
    ax.set_ylim(-0.6, len(items) - 0.4)
    ax.set_xlabel("Dimension marginal (pp), one type = one vote", fontsize=8.4)
    ax.set_title("%s \u2014 dimension profile" % strat, fontsize=10.5, loc="left")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def spread_panel(ax, ver):
    sub = S[S.version == ver].set_index("strategy").loc[STRATS]
    order = sub.sort_values("sd").index.tolist()
    ys = np.arange(len(order))[::-1]
    for y, s in zip(ys, order):
        c = "#C0392B" if s == "PRESSURE" else "#7F8C8D"
        ax.barh(y, sub.loc[s, "sd"], height=0.55, color=c, alpha=1.0 if s == "PRESSURE" else 0.78, zorder=3)
        ax.text(sub.loc[s, "sd"] + 0.25, y, "SD %.1f   (range %.0f)" % (sub.loc[s, "sd"], sub.loc[s, "rng"]),
                va="center", fontsize=8.2, color="#333", zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels(order, fontsize=9.5)
    ax.set_xlim(0, sub.sd.max() * 1.8)
    ax.set_xlabel("Spread of the 12 type values (pp) \u2014 smaller = more even", fontsize=8.6)
    ax.set_title("How evenly does each strategy behave?", fontsize=11.5, fontweight="bold", loc="left")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def sample(ax, x, y, w, h, level, target, nature):
    offensive = (nature == "Offensive")
    if offensive:
        fc, ec, ls, alpha = LEVEL_COLOR[level], "white", "solid", 0.95
    else:
        fc, ec, ls, alpha = LEVEL_COLOR[level], LEVEL_COLOR[level], (0, (3, 2)), 0.30
    ax.add_patch(mpatches.Rectangle((x, y), w, h, transform=ax.transAxes, fc=fc, alpha=alpha,
                                    hatch=TARGET_HATCH.get(target), ec=ec, lw=1.0, ls=ls))


def notes_panel(ax, headline, note):
    ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0.02, 0.02), 0.96, 0.96, transform=ax.transAxes,
                                    fc="#FAFAFA", ec="#999", lw=1.0))
    ax.text(0.06, 0.96, headline, transform=ax.transAxes, fontsize=10.2, fontweight="bold", va="top")
    ax.text(0.06, 0.845, note, transform=ax.transAxes, fontsize=8.5, va="top", linespacing=1.45)
    # legend of the three dimensions
    ax.text(0.06, 0.47, "Every bar carries the three dimensions of its thinking type:",
            transform=ax.transAxes, fontsize=8.8, fontweight="bold", va="top")
    x0, w, h = 0.08, 0.055, 0.028
    yy = 0.425
    for lyr in LEVELS:
        sample(ax, x0, yy, w, h, lyr, None, "Offensive")
        ax.text(x0 + w + 0.012, yy + h / 2, "%s %s  \u2014 colour" % (lyr, LEVEL_EN[lyr]),
                transform=ax.transAxes, fontsize=8.2, va="center")
        yy -= 0.042
    yy -= 0.012
    for t in TARGETS:
        sample(ax, x0, yy, w, h, "L1", t, "Offensive")
        ax.text(x0 + w + 0.012, yy + h / 2, "%s %s  \u2014 pattern" % (t, TARGET_EN[t]),
                transform=ax.transAxes, fontsize=8.2, va="center")
        yy -= 0.042
    yy -= 0.012
    for n in ("Offensive", "Defensive"):
        sample(ax, x0, yy, w, h, "L2", "R", n)
        ax.text(x0 + w + 0.012, yy + h / 2, NATURE_EN[n] + "  \u2014 solid/hollow", transform=ax.transAxes,
                fontsize=8.0, va="center")
        yy -= 0.042
    ax.text(0.06, yy - 0.01, "Colour and pattern are task labels; the solid/hollow split is derived from the\n"
            "data (rescued rows vs broken rows of that strategy in that type): solid + white pattern =\n"
            "offensive, hollow + dashed outline = defensive (avoid-loss).\n"
            "Pale bars with a red right-hand label = thin cell (n < %d): indicative only.\n"
            "\u21af = bar clipped to the axis limit." % THIN,
            transform=ax.transAxes, fontsize=8.0, va="top", color="#C0392B", linespacing=1.4)


def build(col, ver_geom, fname, headline, note, mode="rel", suptitle=None):
    v = R[col].dropna().values
    thin = R["thin"].values
    lim = axis_limit(v, thin)
    fig = plt.figure(figsize=(34, 14.5))
    gs = fig.add_gridspec(2, 6, width_ratios=[1, 1, 1, 1, 1, 1.15], hspace=0.3, wspace=0.33)
    for j, s in enumerate(STRATS):
        type_panel(fig.add_subplot(gs[0, j]), s, col, lim, mode)
        marginal_panel(fig.add_subplot(gs[1, j]), s, ver_geom, lim)
    spread_panel(fig.add_subplot(gs[0, 5]), ver_geom)
    notes_panel(fig.add_subplot(gs[1, 5]), headline, note)
    if suptitle:
        fig.suptitle(suptitle, fontsize=17, fontweight="bold", y=0.985)
    fig.savefig(os.path.join(OUT, fname), dpi=110, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.join(OUT, fname))


REL_NOTE = ("Bar = baseline-relative: the value of that thinking type minus the strategy's own average over the "
            "12 types,\nso a positive bar marks a type where the strategy does comparatively well and a negative "
            "bar a type to avoid.\nIn brackets, the absolute value versus plain (\"lvl\" = pp change against the "
            "no-strategy run); at the right margin, rows and empirical gain rate.")

if __name__ == "__main__":
    build("raw_rel", "raw", "fig1_raw.png",
          "Metric: mean \u0394 (re-ask \u2212 plain, all rows), centred on each strategy's own average.",
          REL_NOTE + "\nNo difficulty correction. 24% of all rows are already perfect before re-asking "
          "(PRESSURE 7%,\nCRITICAL 20%, MISLEADING 23%, ENCOURAGE 26%, HEURISTIC 36%) and those rows can only lose.",
          suptitle="Figure 1 \u2014 RAW profile: which thinking types does each re-ask strategy do comparatively "
                   "well / badly on?")
    build("std_rel", "std", "fig2_difficulty.png",
          "Metric: score change of that thinking type, difficulty-corrected by the ORIGINAL score and centred on "
          "each strategy's own average.",
          REL_NOTE + "\nDifficulty correction: rows are restricted to the headroom band 5 \u2264 original score \u2264 95 "
          "and re-weighted to the\nsame difficulty mix in every cell (bins " +
          ", ".join("bin%s=%.0f%%" % (k, 100 * v) for k, v in META["reference_mix"].items()) +
          "), so a cell full of already-perfect\ntasks is no longer dragged down mechanically.",
          suptitle="Figure 2 \u2014 DIFFICULTY-CORRECTED by the original score: each strategy against its own "
                   "baseline (PRESSURE stays flat at 0)")
    build("std_fam_rel", "std_fam_rel", "fig3_balanced.png",
          "Metric: Figure-2 value re-averaged with equal weight per evaluation family (one family = one vote), "
          "centred on each strategy's own average.",
          REL_NOTE + "\nSize balance: every evaluation family counts once, so a value does not depend on how many rows "
          "a type\nhappens to have or on being concentrated in one benchmark.",
          suptitle="Figure 3 \u2014 DIFFICULTY-CORRECTED + SIZE-BALANCED profile (one evaluation family = one vote)")
    build("raw", "raw", "fig1_raw_levels.png",
          "Metric: mean \u0394 (re-ask \u2212 plain, all rows), absolute values.",
          REL_NOTE + "\nAbsolute view: only PRESSURE is close to 0; the other four are negative nearly everywhere.",
          mode="lvl", suptitle="Figure 1L \u2014 RAW absolute levels (reference view)")
    build("std", "std", "fig2_difficulty_levels.png",
          "Metric: absolute score change, difficulty-corrected by the ORIGINAL score.",
          REL_NOTE + "\nAbsolute view after the difficulty correction: PRESSURE \u22120.2 pp and flat; the other four "
          "stay negative.", mode="lvl",
          suptitle="Figure 2L \u2014 DIFFICULTY-CORRECTED absolute levels (reference view)")
