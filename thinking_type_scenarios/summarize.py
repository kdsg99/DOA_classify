# -*- coding: utf-8 -*-
"""Per-strategy scenario notes (English): relative profile + absolute level behind it."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
from taxonomy_v2 import ID2EN, LEVEL_EN, TARGET_EN              # noqa: E402

STRATS = ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
VNAME = {"raw_rel": "raw", "std_rel": "difficulty-corrected", "std_fam_rel": "+size-balanced"}
SCEN = {
    "L1-K": "lookup, extraction, QA, translation",
    "L1-R": "arithmetic, unit conversion, short deduction, implementing a clearly specified step",
    "L1-E": "open-ended writing, brainstorming, first-draft prose, ad copy",
    "L1-F": "reformatting, field mapping, table/LaTeX conversion, data cleaning",
    "L2-K": "multi-source synthesis, long-document summarisation",
    "L2-R": "competition maths, proofs, algorithm design, multi-step derivations",
    "L2-E": "outlines, section structure, argument architecture, narrative arc",
    "L2-F": "strict schema output (JSON/CSV/table), long structured answers",
    "L3-K": "fact-checking, hallucination spotting, finding the error in an answer",
    "L3-R": "staying on track, resisting a misleading premise, multi-turn consistency",
    "L3-E": "tone / persona / audience consistency",
    "L3-F": "many simultaneous constraints, bug fixing, error handling, self-repair",
}
R = pd.read_csv(os.path.join(HERE, "out", "cells_3dims.csv"))
M = pd.read_csv(os.path.join(HERE, "out", "marginals_3dims.csv"))
S = pd.read_csv(os.path.join(HERE, "out", "spread_by_strategy.csv"))

out = ["# Re-ask strategy x thinking-type scenarios (three-dimension taxonomy)", "",
       "Thinking type = dimension 1 **operation level** (L1 Execution / L2 Structure / L3 Metacognition)",
       "x dimension 2 **target** (K Knowledge / R Reasoning / E Expression / F Format).",
       "Dimension 3, the **nature of gain**, is measured per (strategy, type): the share of rows that improved",
       "(`gain_rate`); >=50% = Offensive, below = Defensive.", "",
       "**Reading of the main numbers.** `relative` = the value of a thinking type minus the strategy's own",
       "average over the 12 types, so positive = a type this strategy does comparatively well on, negative = a",
       "type to avoid. `level` = the same value in absolute terms, i.e. the change against the plain (no-strategy)",
       "run: a comparative win can still be a small absolute loss.",
       "Difficulty is always the ORIGINAL (plain) score; the corrected version keeps only the headroom band",
       "5-95 and re-weights every cell to the same difficulty mix.", "",
       "## Evenness across the 12 thinking types (SD / range, smaller = flatter)", "",
       "| Strategy | raw | difficulty-corrected | +size-balanced |", "|---|---|---|---|"]
for s in STRATS:
    cells = []
    for ver in ["raw_rel", "std_rel", "std_fam_rel"]:
        r = S[(S.strategy == s) & (S.version == ver)].iloc[0]
        cells.append("%.1f / %.0f" % (r.sd, r.rng))
    out.append("| %s | %s | %s | %s |" % (s, *cells))
out += ["", "PRESSURE is the reference: the flattest in all three metrics and, after the difficulty correction,",
        "a level of -0.2 pp on average - it neither helps nor hurts anywhere. The other four swing over",
        "38-75 pp between their best and their worst thinking type.", ""]

for ver in ["std_rel", "std_fam_rel"]:
    out += ["## Relative profile - %s (positive = comparatively good, negative = to avoid)" % VNAME[ver], "",
            "| Strategy | best 3 types | worst 3 types |", "|---|---|---|"]
    for s in STRATS:
        g = R[R.strategy == s].dropna(subset=[ver]).sort_values(ver, ascending=False)
        f = lambda r: "%s %s %+.1f (lvl %+.1f, %d%%)" % (r.thinking_type, r.type_en, getattr(r, ver),
                                                         getattr(r, ver[:-4]), round(100 * r.gain_rate))
        out.append("| %s | %s | %s |" % (s, "; ".join(f(r) for r in g.head(3).itertuples()),
                                         "; ".join(f(r) for r in g.tail(3)[::-1].itertuples())))
    out.append("")

for ver in ["std", "std_fam"]:
    out += ["## Absolute level - %s (pp vs plain, one thinking type = one vote)" % VNAME.get(ver, ver), "",
            "| Strategy | L1 | L2 | L3 | K | R | E | F | Overall | gain rate |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for s in STRATS:
        m = M[(M.strategy == s) & (M.version == ver)]
        lv = [m[(m.dimension == "Level") & (m.value == l)]["mean"].iloc[0] for l in ["L1", "L2", "L3"]]
        tg = [m[(m.dimension == "Target") & (m.value == t)]["mean"].iloc[0] for t in ["K", "R", "E", "F"]]
        out.append("| %s | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f | %.0f%% |"
                   % (s, *lv, *tg, m[m.dimension == "Overall"]["mean"].iloc[0],
                      100 * m[m.dimension == "Overall"]["gain_rate"].iloc[0]))
    out.append("")

out += ["## Per-strategy reading (difficulty-corrected + size-balanced)", ""]
for s in STRATS:
    g = R[R.strategy == s].dropna(subset=["std_fam_rel"]).sort_values("std_fam_rel", ascending=False)
    m = M[(M.strategy == s) & (M.version == "std_fam_rel")]
    best_l = m[m.dimension == "Level"].sort_values("mean", ascending=False).iloc[0]
    best_t = m[m.dimension == "Target"].sort_values("mean", ascending=False).iloc[0]
    worst_t = m[m.dimension == "Target"].sort_values("mean").iloc[0]
    off = g[g.nature == "Offensive"]
    out += ["### %s" % s, "",
            "- relative profile: best level %s (%+.1f), best target %s (%+.1f), worst target %s (%+.1f);"
            % (LEVEL_EN[best_l.value], best_l["mean"], TARGET_EN[best_t.value], best_t["mean"],
               TARGET_EN[worst_t.value], worst_t["mean"]),
            "- absolute level after the difficulty correction: %+.1f pp overall, gain rate %d%%; %d/%d types Offensive"
            % (m[m.dimension == "Overall"]["mean"].iloc[0],
               100 * m[m.dimension == "Overall"]["gain_rate"].iloc[0], len(off), len(g)),
            "- comparatively good types (relative / absolute level):"] + \
        ["      %-5s %-26s %+6.1f pp  (lvl %+5.1f, n=%3d, gain %3d%%)  -> %s"
         % (r.thinking_type, r.type_en, r.std_fam_rel, r.std_fam, r.n, round(100 * r.gain_rate),
            SCEN[r.thinking_type]) for r in g.head(3).itertuples()] + \
        ["- comparatively bad types (relative / absolute level):"] + \
        ["      %-5s %-26s %+6.1f pp  (lvl %+5.1f, n=%3d, gain %3d%%)  -> %s"
         % (r.thinking_type, r.type_en, r.std_fam_rel, r.std_fam, r.n, round(100 * r.gain_rate),
            SCEN[r.thinking_type]) for r in g.tail(3)[::-1].itertuples()] + [""]

open(os.path.join(HERE, "scenarios.md"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out[:40]))
print("\n... written scenarios.md (%d lines)" % len(out))
