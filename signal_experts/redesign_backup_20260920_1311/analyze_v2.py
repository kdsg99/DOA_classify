# -*- coding: utf-8 -*-
"""
Analysis + plots for the v2 thinking-type classification.

Two complementary metrics are reported for every (strategy, thinking_type):

  raw  enrichment = log2( p_high(type) / p_low(type) )
        -> the *global* high-vs-low contrast (Goal 1: a strategy's overall style)

  adj  enrichment = dataset-stratified log2( p_high(type|ds) / p_low(type|ds) )
        -> controls for the fact that low sets are dominated by hard-math (math500);
           it surfaces the *strategy-specific* thinking-style signature (Goal 2)

Goal 1 (within-strategy separation) and Goal 2 (between-strategy difference)
are also quantified in summary_v2.txt.
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy_v2 import (TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET,
                         LEVELS, LEVEL_EN, TARGETS, TARGET_EN)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False
HERE = os.path.dirname(os.path.abspath(__file__))
STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
df = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
df["is_high"] = df["set"] == "high"
EPS = 0.02

# --------------------------------------------------------------- metrics
def raw_metrics(al):
    rows = []
    for s in STRATS:
        sub = al[al.strategy == s]
        for tid in TYPE_IDS:
            h = int(((sub.thinking_type == tid) & sub.is_high).sum())
            l = int(((sub.thinking_type == tid) & ~sub.is_high).sum())
            rows.append(dict(strategy=s, thinking_type=tid, high=h, low=l))
    m = pd.DataFrame(rows)
    m["p_high"] = m.high / m.groupby("strategy").high.transform("sum")
    m["p_low"]  = m.low  / m.groupby("strategy").low.transform("sum")
    m["delta"]  = m.p_high - m.p_low
    m["enrich_raw"] = np.log2((m.p_high + 0.005) / (m.p_low + 0.005))
    return m

def adj_metrics(al):
    """dataset-stratified composition log-odds: log2( share_in_high|ds / share_in_low|ds )"""
    rows = []
    for s in STRATS:
        sub = al[al.strategy == s]
        for tid in TYPE_IDS:
            num = den = 0.0
            for ds, g in sub.groupby("dataset_id"):
                if len(g) < 5:      # too small to stratify
                    continue
                hg, lg = g[g.is_high], g[~g.is_high]
                if len(hg) == 0 or len(lg) == 0:
                    continue
                p_h = (hg.thinking_type == tid).mean()
                p_l = (lg.thinking_type == tid).mean()
                w = len(g)
                num += w * np.log2((p_h + EPS) / (p_l + EPS))
                den += w
            rows.append(dict(strategy=s, thinking_type=tid, enrich_adj=num/den if den else 0.0))
    return pd.DataFrame(rows)

sh = raw_metrics(df).merge(adj_metrics(df), on=["strategy", "thinking_type"])
sh["level"] = sh.thinking_type.map(ID2LEVEL)
sh["target"] = sh.thinking_type.map(ID2TARGET)
sh["gain_nature"] = np.where(sh.delta > 0, "Offensive", "Defensive")
sh.to_csv(os.path.join(HERE, "shares_v2.csv"), index=False)

def agg(metric):
    out = []
    for s in STRATS:
        for key, col in [("level", "level"), ("target", "target")]:
            for k in (LEVELS if col == "level" else TARGETS):
                sub = df[(df.strategy == s) & (df[col] == k)]
                h = int(sub.is_high.sum()); l = int((~sub.is_high).sum())
                out.append(dict(strategy=s, axis=key, key=k, high=h, low=l))
    o = pd.DataFrame(out)
    o["p_high"] = o.high / o.groupby(["strategy", "axis"]).high.transform("sum")
    o["p_low"]  = o.low  / o.groupby(["strategy", "axis"]).low.transform("sum")
    o["enrich_raw"] = np.log2((o.p_high + 0.005) / (o.p_low + 0.005))
    return o
al_agg = agg(None)
al_agg.to_csv(os.path.join(HERE, "level_target_v2.csv"), index=False)

# --------------------------------------------------------------- text summary
L = []
L.append("=" * 84)
L.append("V2 THINKING-TYPE SIGNATURE  (12 types = 3 Levels x 4 Targets)")
L.append("=" * 84)
L.append("enrich_raw = global  log2(p_high/p_low)        (positive => strategy is GOOD at the type)")
L.append("enrich_adj = dataset-controlled log2 ratio      (strategy-specific signature)")
for s in STRATS:
    sub = sh[sh.strategy == s].sort_values("enrich_adj", ascending=False)
    L.append(f"\n### {s}   (high={sub.high.sum()}, low={sub.low.sum()})")
    L.append(f"{'type':32s}{'high':>6s}{'low':>6s}{'raw':>8s}{'adj':>8s}")
    for _, r in sub.iterrows():
        L.append(f"{r.thinking_type+' '+ID2EN[r.thinking_type]:32s}{r.high:6d}{r.low:6d}"
                 f"{r.enrich_raw:+8.2f}{r.enrich_adj:+8.2f}")

def kl(p, q):
    p = np.asarray(p, float) + 1e-9; q = np.asarray(q, float) + 1e-9
    return float(np.sum(p * np.log2(p / q)))

L.append("\n" + "=" * 84)
L.append("GOAL 1  —  within-strategy high vs low separation")
L.append("=" * 84)
L.append(f"{'strategy':12s}{'KL(high||low)':>15s}   level shares in HIGH   :   level shares in LOW")
for s in STRATS:
    sub = df[df.strategy == s]
    d = sub.groupby(["thinking_type", "set"]).size().unstack(fill_value=0)
    k = kl(d["high"]/d["high"].sum(), d["low"]/d["low"].sum())
    b = al_agg[(al_agg.strategy == s) & (al_agg.axis == "level")].set_index("key")
    hs = "/".join(f"{b.loc[x,'p_high']:.2f}" for x in LEVELS)
    ls = "/".join(f"{b.loc[x,'p_low']:.2f}" for x in LEVELS)
    L.append(f"{s:12s}{k:15.3f}   L1/L2/L3 = {hs}   :   {ls}")

L.append("\n" + "=" * 84)
L.append("GOAL 2  —  between-strategy difference of HIGH-set type profile (KL divergence)")
L.append("=" * 84)
prof = {s: (sh[sh.strategy == s].set_index("thinking_type").reindex(TYPE_IDS).p_high.values) for s in STRATS}
L.append(f"{'':12s}" + "".join(f"{t:>12s}" for t in STRATS))
for s1 in STRATS:
    L.append(f"{s1:12s}" + "".join(f"{kl(prof[s1],prof[s2]):12.3f}" for s2 in STRATS))

def cos(a, b):
    d = np.linalg.norm(a)*np.linalg.norm(b)
    return float(a@b/d) if d > 0 else 0.0
sig = {s: (sh[sh.strategy == s].set_index("thinking_type").reindex(TYPE_IDS).enrich_adj.values
           - sh[sh.strategy == s].enrich_adj.mean()) for s in STRATS}
L.append("\nSignature similarity (cosine, adj-enrichment, mean-centred); lower = more distinct")
L.append(f"{'':12s}" + "".join(f"{t:>12s}" for t in STRATS))
for s1 in STRATS:
    L.append(f"{s1:12s}" + "".join(f"{cos(sig[s1],sig[s2]):12.2f}" for s2 in STRATS))
txt = "\n".join(L)
open(os.path.join(HERE, "summary_v2.txt"), "w", encoding="utf-8").write(txt)
print(txt)

# --------------------------------------------------------------- plots
def heatmap(ax, mat, row_labels, col_labels, title, vlim, fmt="{:+.2f}",
            col_groups=None, ylabel=True):
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-vlim, vmax=vlim, aspect="auto")
    ax.set_xticks(range(len(col_labels))); ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels if ylabel else [""]*len(row_labels), fontsize=10)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=7,
                    color="white" if abs(v) > 0.6*vlim else "black")
    if col_groups:
        prev = 0
        for gname, gsize in col_groups:
            ax.axvline(prev + gsize - 0.5, color="k", lw=1.0)
            ax.text(prev + gsize/2 - 0.5, -0.85, gname, ha="center", va="bottom",
                    fontsize=9, fontweight="bold")
            prev += gsize
    ax.set_title(title, fontsize=12, pad=22 if col_groups else 8)
    return im

def piv(metric):
    return sh.pivot(index="strategy", columns="thinking_type", values=metric).reindex(index=STRATS, columns=TYPE_IDS)

# fig1 + fig2 : raw and adj heatmaps
for metric, fname, title in [
    ("enrich_raw", "fig1_raw_enrich_heatmap.png",
     "RAW enrichment: thinking types over-represented in each strategy's HIGH vs LOW set\n(red = strategy GOOD at type;  blue = strategy WEAK at type)"),
    ("enrich_adj", "fig2_adj_enrich_heatmap.png",
     "DATASET-CONTROLLED signature (removes the 'low = hard math' composition effect)\n(strategy-specific thinking-style profile)")]:
    fig, ax = plt.subplots(figsize=(13.5, 4.4))
    im = heatmap(ax, piv(metric).values, STRATS, TYPE_IDS, title, 1.4,
                 col_groups=[("Execution  L1", 4), ("Structure  L2", 4), ("Metacognition  L3", 4)])
    cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01); cb.set_label("log2(high / low)")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, fname), dpi=160, bbox_inches="tight"); plt.close(fig)

# fig3: diverging bars (delta)
fig, axes = plt.subplots(1, 5, figsize=(22, 6), sharey=True)
for ax, s in zip(axes, STRATS):
    sub = sh[sh.strategy == s].set_index("thinking_type").reindex(TYPE_IDS)
    colors = ["#c0392b" if v > 0 else "#2c7fb8" for v in sub.enrich_adj]
    ax.barh(range(12), sub.enrich_adj.values, color=colors)
    ax.set_yticks(range(12)); ax.set_yticklabels([f"{t} {ID2EN[t]}" for t in TYPE_IDS], fontsize=8)
    ax.invert_yaxis(); ax.axvline(0, color="k", lw=0.8)
    ax.set_title(s, fontsize=13, fontweight="bold"); ax.set_xlabel("adj enrichment")
    for i, v in enumerate(sub.enrich_adj.values):
        ax.text(v + (0.03 if v >= 0 else -0.03), i, f"{v:+.1f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=7)
    ax.margins(x=0.28)
fig.suptitle("Per-strategy thinking-style signature (dataset-controlled)\n"
             "red = strategy's strength, blue = weakness", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(os.path.join(HERE, "fig3_diverging_bars.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# fig4: level & target aggregated (raw enrich)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, axis, keys, names in [(axes[0], "level", LEVELS, [LEVEL_EN[k] for k in LEVELS]),
                              (axes[1], "target", TARGETS, [TARGET_EN[k] for k in TARGETS])]:
    m = al_agg[al_agg.axis == axis].pivot(index="strategy", columns="key", values="enrich_raw").reindex(index=STRATS, columns=keys)
    im = ax.imshow(m.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(keys))); ax.set_xticklabels(names, rotation=25, ha="right")
    ax.set_yticks(range(len(STRATS))); ax.set_yticklabels(STRATS)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ax.text(j, i, f"{m.values[i,j]:+.2f}", ha="center", va="center",
                    color="white" if abs(m.values[i,j]) > 0.6 else "black", fontsize=9)
    ax.set_title(f"{axis.capitalize()} axis (raw)")
fig.colorbar(im, ax=axes, label="log2(high/low)", fraction=0.03)
fig.suptitle("Aggregated thinking-style contrast: HIGH vs LOW", fontsize=12)
fig.savefig(os.path.join(HERE, "fig4_level_target.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# fig5: level composition high vs low stacked
fig, axes = plt.subplots(1, 5, figsize=(20, 4), sharey=True)
for ax, s in zip(axes, STRATS):
    b = al_agg[(al_agg.strategy == s) & (al_agg.axis == "level")].set_index("key").reindex(LEVELS)
    x = np.arange(2); w = 0.35
    bottom_h = bottom_l = 0
    cmap = {"L1": "#4c72b0", "L2": "#dd8452", "L3": "#55a868"}
    for k in LEVELS:
        ax.bar(0, b.loc[k, "p_high"], bottom=bottom_h, color=cmap[k], width=0.55, label=k if s == STRATS[0] else None)
        ax.bar(1, b.loc[k, "p_low"], bottom=bottom_l, color=cmap[k], width=0.55)
        ax.text(0, bottom_h + b.loc[k, "p_high"]/2, f"{k}\n{b.loc[k,'p_high']:.2f}", ha="center", va="center", fontsize=7, color="white")
        ax.text(1, bottom_l + b.loc[k, "p_low"]/2, f"{k}\n{b.loc[k,'p_low']:.2f}", ha="center", va="center", fontsize=7, color="white")
        bottom_h += b.loc[k, "p_high"]; bottom_l += b.loc[k, "p_low"]
    ax.set_xticks([0, 1]); ax.set_xticklabels(["HIGH", "LOW"]); ax.set_title(s, fontweight="bold"); ax.set_ylim(0, 1)
axes[0].legend(loc="upper left", fontsize=8, ncol=1)
fig.suptitle("Cognitive-level composition of HIGH vs LOW tasks per strategy", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.92]); fig.savefig(os.path.join(HERE, "fig5_level_composition.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# fig6: signature similarity (cosine on adj)
n = len(STRATS)
sim = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        sim[i, j] = cos(sig[STRATS[i]], sig[STRATS[j]])
fig, ax = plt.subplots(figsize=(5.6, 4.6))
im = ax.imshow(sim, cmap="viridis", vmin=0, vmax=1)
ax.set_xticks(range(n)); ax.set_xticklabels(STRATS, rotation=30, ha="right")
ax.set_yticks(range(n)); ax.set_yticklabels(STRATS)
for i in range(n):
    for j in range(n):
        ax.text(j, i, f"{sim[i,j]:.2f}", ha="center", va="center",
                color="white" if sim[i, j] < 0.55 else "black", fontsize=10)
ax.set_title("Strategy signature similarity (cosine)\nlower = more distinct thinking style")
fig.colorbar(im, ax=ax, fraction=0.045)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "fig6_signature_similarity.png"), dpi=160, bbox_inches="tight"); plt.close(fig)

# fig7: per-dataset high-rate heatmap (surfaces PRESSURE's math strength)
fig, ax = plt.subplots(figsize=(8.5, 4.4))
d = df.groupby(["strategy", "dataset_id"])["is_high"].mean().unstack().reindex(STRATS)
m = d.values
im = ax.imshow(m, cmap="RdYlGn", vmin=0, vmax=0.7, aspect="auto")
ax.set_xticks(range(d.shape[1])); ax.set_xticklabels(d.columns, rotation=30, ha="right")
ax.set_yticks(range(len(STRATS))); ax.set_yticklabels(STRATS)
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        ax.text(j, i, f"{m[i,j]:.2f}", ha="center", va="center", fontsize=9)
ax.set_title("Success rate (share of HIGH) by dataset x strategy\nPRESSURE is uniquely good on chat_math500")
fig.colorbar(im, ax=ax, fraction=0.04); fig.tight_layout()
fig.savefig(os.path.join(HERE, "fig7_dataset_successrate.png"), dpi=160, bbox_inches="tight"); plt.close(fig)

print("\nsaved plots + csv in", HERE)
