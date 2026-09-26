# -*- coding: utf-8 -*-
"""Three figures: raw / difficulty-adjusted / difficulty+size-balanced.

Each figure = 5 subplots (one per re-ask strategy); rows = 12 thinking types
grouped by the three dimensions (Metacognitive / Structural / Execution);
bar length = strength of gain (right) or reduction (left), in pp.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.patches as mpatches                           # noqa: E402
import matplotlib.pyplot as plt                                 # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
LAYERS = {
    "Execution": ["Local repair", "Expression expansion", "Execution-limited"],
    "Structural": ["Routine recognition", "Full-reasoning dependent",
                   "Format preserving", "Style preserving"],
    "Metacognitive": ["Reviewable repair", "Strict verification",
                      "Long-context fidelity", "Trajectory sensitive",
                      "Plain-answer fragile"],
}
ORDER = [t for lyr in ["Metacognitive", "Structural", "Execution"] for t in LAYERS[lyr]]
LAYER_OF = {t: lyr for lyr, ts in LAYERS.items() for t in ts}
COLOR = {"Metacognitive": "#2E6DA4", "Structural": "#D98C1F", "Execution": "#8E44AD"}
THIN = 10

R = pd.read_csv(os.path.join(HERE, "out", "tt_all_versions.csv"))
OUT = os.path.join(HERE, "figs")
os.makedirs(OUT, exist_ok=True)


def panel(ax, strat, col, lim, title=None):
    g = R[R.strategy == strat].set_index("thinking_type").reindex(ORDER)
    ys = np.arange(len(ORDER))[::-1]
    for y, t, v, n in zip(ys, ORDER, g[col].values, g["n"].values):
        thin = n < THIN
        ax.barh(y, v, height=0.66, color=COLOR[LAYER_OF[t]], alpha=0.55 if thin else 0.92,
                hatch="///" if thin else None, edgecolor="white", linewidth=0.8, zorder=3)
        off = 1.5 if v >= 0 else -1.5
        ax.text(v + off, y, "%.1f" % v, va="center", ha="left" if v >= 0 else "right",
                fontsize=7.5, color="#333", zorder=4)
        ax.text(lim * 0.985, y, "n=%d" % n, va="center", ha="right", fontsize=7,
                color="#C0392B" if thin else "#888", zorder=4)
    ax.axvline(0, color="#222", lw=1.1, zorder=2)
    # layer separators + labels
    bounds = []
    i = 0
    for lyr in ["Metacognitive", "Structural", "Execution"]:
        i += len(LAYERS[lyr])
        if i < len(ORDER):
            bounds.append(len(ORDER) - i - 0.5)
    for b in bounds:
        ax.axhline(b, color="#bbb", lw=1.0, ls=(0, (4, 3)), zorder=1)
    for lyr in ["Metacognitive", "Structural", "Execution"]:
        sub = g.loc[LAYERS[lyr], col]
        mu = float(np.nanmean(sub.values))
        ax.text(lim * 0.60, ys[[ORDER.index(t) for t in LAYERS[lyr]]].mean(),
                "%s  μ=%+.1f" % (lyr, mu), fontsize=8.2, color=COLOR[lyr],
                fontweight="bold", ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=COLOR[lyr], lw=0.8, alpha=0.85))
    ax.set_yticks(ys)
    ax.set_yticklabels(ORDER, fontsize=8.8)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.7, len(ORDER) - 0.3)
    ax.set_xlabel("Score change (pp)  ← reduction   |   gain →", fontsize=9)
    tot = g["n"].sum()
    allmu = float(np.nanmean(g[col].values))
    ax.set_title("%s\n(n=%d rows, overall %+.1f pp)" % (strat, tot, allmu), fontsize=11.5, fontweight="bold")
    ax.grid(axis="x", alpha=0.28, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def legend_panel(ax, fignum, headline, note):
    ax.axis("off")
    ax.add_patch(mpatches.Rectangle((0.02, 0.02), 0.96, 0.96, transform=ax.transAxes,
                                    fc="#FAFAFA", ec="#999", lw=1.0))
    ax.text(0.06, 0.93, headline, transform=ax.transAxes, fontsize=11.5, fontweight="bold", va="top")
    ax.text(0.06, 0.80, note, transform=ax.transAxes, fontsize=9.2, va="top", wrap=True)
    y = 0.55
    for lyr in ["Metacognitive", "Structural", "Execution"]:
        ax.add_patch(mpatches.Rectangle((0.07, y), 0.05, 0.035, transform=ax.transAxes,
                                        fc=COLOR[lyr], ec="none"))
        ax.text(0.14, y + 0.017, "%s layer: %s" % (lyr, ", ".join(LAYERS[lyr])),
                transform=ax.transAxes, fontsize=8.6, va="center")
        y -= 0.075
    ax.text(0.07, y - 0.01, "Hatched + pale bar = thin cell (n < %d rows): treat as indicative only." % THIN,
            transform=ax.transAxes, fontsize=8.6, va="top", color="#C0392B")
    ax.text(0.07, y - 0.075, "n = rows behind the bar (task x strategy x model).", transform=ax.transAxes,
            fontsize=8.6, va="top", color="#555")
    ax.text(0.07, y - 0.135,
            "Reading guide: bars to the right = the re-ask helped on that kind of task;\n"
            "bars to the left = the re-ask hurt. The layer boxes report the mean of that\n"
            "dimension (Metacognitive / Structural / Execution) for the strategy.",
            transform=ax.transAxes, fontsize=8.6, va="top", color="#333")


def build(col, fname, headline, note, lam=None):
    v = R[col].values
    lim = np.ceil(max(abs(np.nanmin(v)), abs(np.nanmax(v))) / 10.0) * 10
    fig, axes = plt.subplots(2, 3, figsize=(25.5, 13.5))
    for ax, s in zip(axes.ravel()[:5], STRATS):
        panel(ax, s, col, lim)
    legend_panel(axes.ravel()[5], 1, headline, note)
    fig.suptitle(headline + "\n" + note.split("\n")[0], fontsize=15, fontweight="bold", y=0.985)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    p = os.path.join(OUT, fname)
    fig.savefig(p, dpi=125, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)
    return p


dif = pd.read_csv(os.path.join(HERE, "out", "difficulty_trend.csv"))
lines = "; ".join("%s Δ=b0%+.1f%+.2f·plain" % (r.strategy, r.b0, r.b1) for r in dif.itertuples())

build("raw", "fig1_raw.png",
      "Figure 1 — RAW: what each re-ask strategy does to each thinking type",
      "Metric: average Δ = re-ask − plain, in percentage points (pp), over all rows of that strategy × type.\n"
      "No control for task difficulty, so types that happen to be easy or hard carry that difference with them.\n"
      "Thin cells (n<10) are hatched. Bars are symmetric around 0.")

build("difficulty_adjusted", "fig2_difficulty_adjusted.png",
      "Figure 2 — DIFFICULTY-ADJUSTED: the same picture with the task-difficulty trend removed",
      "Metric: mean residual of Δ_pp after fitting Δ_pp = b0 + b1·plain_pp inside each strategy (per-strategy OLS).\n"
      "0 now means 'as expected for this strategy at the difficulty of these tasks' (not 'same as plain').\n"
      "Per-strategy lines: " + lines + ".")

build("balanced", "fig3_balanced.png",
      "Figure 3 — DIFFICULTY-ADJUSTED + SIZE-BALANCED: independent of how many samples a thinking type has",
      "Metric: the Figure-2 residuals re-averaged with equal weight per evaluation family, so a type is not\n"
      "represented by the family (or the row count) it happens to be plentiful in. 0 = strategy's own baseline.\n"
      "Cells resting on 1–2 families remain noisy by construction; see out/tt_all_versions.csv (lodo_range) for spread.")
