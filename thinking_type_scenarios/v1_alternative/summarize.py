# -*- coding: utf-8 -*-
"""Per-strategy scenario summary (English) from the three estimates."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

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
SCENARIO = {
    "Local repair": "patch a concrete error / bug / hallucination",
    "Expression expansion": "write long-form, creative or expansive text",
    "Execution-limited": "simple but labour-heavy routines (arithmetic, sudoku, lookup chains)",
    "Routine recognition": "classification, matching, pattern recognition",
    "Full-reasoning dependent": "multi-step maths / physics / logic proofs",
    "Format preserving": "strict output formats (JSON, CSV, table, LaTeX)",
    "Style preserving": "persona, tone and voice maintenance",
    "Reviewable repair": "review / critique / give feedback on someone else's answer",
    "Strict verification": "fact-checking and correctness validation",
    "Long-context fidelity": "long documents, summarise while keeping consistency",
    "Trajectory sensitive": "keep the reasoning path / step order intact",
    "Plain-answer fragile": "short factual answers without reasoning",
}

R = pd.read_csv(os.path.join(HERE, "out", "tt_all_versions.csv"))
L = R[R.thinking_type.isin(ORDER)]

out = ["# Re-ask strategy × thinking-type scenarios", "",
       "Values are score changes in pp (re-ask − plain). `balanced` = difficulty-adjusted and",
       "re-averaged with equal weight per evaluation family (independent of sample sizes).", ""]

for ver, col in [("raw", "raw"), ("difficulty-adjusted", "difficulty_adjusted"), ("balanced", "balanced")]:
    out += ["## Layer means (%s)" % ver, "",
            "| Strategy | Metacognitive | Structural | Execution | Overall |", "|---|---|---|---|---|"]
    for s in STRATS:
        g = L[L.strategy == s]
        m = [np.nanmean(g[g.layer == l][col].values) for l in ["Metacognitive", "Structural", "Execution"]]
        out.append("| %s | %+.1f | %+.1f | %+.1f | %+.1f |" % (s, *m, np.nanmean(g[col].values)))
    out.append("")

out += ["## Per-strategy reading (balanced, with the raw value for reference)", ""]
for s in STRATS:
    g = L[L.strategy == s].dropna(subset=["balanced"]).sort_values("balanced", ascending=False)
    out += ["### %s" % s, ""]
    for tag, sub in [("Helps", g.head(3)), ("Hurts", g.tail(3)[::-1])]:
        out.append("%s:" % tag)
        for r in sub.itertuples():
            out.append("  - %s [%s] — %+.1f pp balanced (raw %+.1f, n=%d, families=%d) → %s"
                       % (r.thinking_type, r.layer, r.balanced, r.raw, r.n, r.n_families, SCENARIO[r.thinking_type]))
        out.append("")
    mixed = g[(g.lodo_range.notna())]
    if len(mixed):
        out.append("Most family-dependent cell: %s (leave-one-family-out spread %.1f pp)"
                   % (mixed.sort_values("lodo_range", ascending=False).iloc[0].thinking_type,
                      mixed.lodo_range.max()))
        out.append("")

open(os.path.join(HERE, "scenarios.md"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out[:46]))
print("\n... written to scenarios.md")
