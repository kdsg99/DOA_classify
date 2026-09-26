# -*- coding: utf-8 -*-
"""
One figure per strategy; each point = one thinking type.
  x = Low set share  (%)  = strategy's low-count of that type / ALL strategies' low-count of that type
  y = High set share (%)  = strategy's high-count of that type / ALL strategies' high-count of that type
Diagonal y = x is the plain baseline.

Each point encodes THREE dimensions of the thinking type via
  colour  = cognitive level
  marker  = intervention target
  fill    = nature of gain (hollow = defensive/保稳, solid = offensive/拔高)

Two taxonomies are supported:
  v2  : the redesigned 12 types (L1-K ... L3-F)
  old : the previous 12 types (LR/ES/RV/... from new_painting/reasoning_style.py, fixed 3-dim table)
"""
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
SE = os.path.dirname(HERE)
STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]

# ============================================================
# taxonomy config
# ============================================================
# ---- v2 ----
sys.path.insert(0, HERE)
from taxonomy_v2 import TYPE_IDS, ID2EN, ID2LEVEL, ID2TARGET

V2_ORDER = TYPE_IDS
LEVEL_COLOR = {"L1": "#1f77b4", "L2": "#2ca02c", "L3": "#d62728"}      # 蓝/绿/红
TARGET_MARKER = {"K": "o", "R": "^", "E": "s", "F": "D"}                 # 圆/三角/方/菱
LEVEL_LABEL = {"L1": "L1 执行层 Execution", "L2": "L2 结构层 Structure", "L3": "L3 元认知层 Metacognition"}
TARGET_LABEL = {"K": "K 知识 Knowledge", "R": "R 推理 Reasoning",
                "E": "E 表达 Expression", "F": "F 格式 Format"}

# ---- old (from new_painting/reasoning_style.py; table is fixed) ----
OLD_ABBR = {
    "Local repair": "LR", "Execution-limited": "ES", "Reviewable repair": "RV",
    "Expression expansion": "EE", "Routine recognition": "RR", "Full-reasoning dependent": "FR",
    "Strict verification": "SV", "Format preserving": "FP", "Style preserving": "SP",
    "Long-context fidelity": "LC", "Trajectory sensitive": "TP", "Plain-answer fragile": "PF",
}
OLD_DIMS = {  # label: (level, target, is_stable)
    'LR': (1, 1, True), 'ES': (1, 2, True), 'RV': (3, 3, False),
    'EE': (1, 1, False), 'RR': (2, 2, False), 'FR': (2, 2, True),
    'SV': (3, 3, True), 'FP': (2, 3, True), 'SP': (2, 3, True),
    'LC': (3, 1, False), 'TP': (3, 2, False), 'PF': (3, 3, True),
}
OLD_LEVEL_COLOR = {1: "#1f77b4", 2: "#2ca02c", 3: "#d62728"}
OLD_TARGET_MARKER = {1: "o", 2: "^", 3: "s"}
OLD_LEVEL_LABEL = {1: "L1 执行层", 2: "L2 结构层", 3: "L3 元认知层"}
OLD_TARGET_LABEL = {1: "目标知识", 2: "过程逻辑", 3: "结果质量"}


def compute_shares(df, type_col):
    """returns DataFrame[strategy, thinking_type, level, target, n_high, n_low, high_share, low_share]"""
    df = df.copy()
    df["is_high"] = df["set"] == "high"
    D_high = df[df.is_high].groupby(type_col).size()
    D_low = df[~df.is_high].groupby(type_col).size()
    out = []
    for s in STRATS:
        sub = df[df.strategy == s]
        for t in sorted(df[type_col].dropna().unique()):
            g = sub[sub[type_col] == t]
            h = int(g.is_high.sum()); l = int((~g.is_high).sum())
            dh = int(D_high.get(t, 0)); dl = int(D_low.get(t, 0))
            out.append(dict(strategy=s, thinking_type=t, n_high=h, n_low=l,
                            D_high=dh, D_low=dl,
                            high_share=100 * h / dh if dh else 0.0,
                            low_share=100 * l / dl if dl else 0.0))
    return pd.DataFrame(out), D_high, D_low


def make_figures(sh, meta, outdir, tag, gain_solid):
    os.makedirs(outdir, exist_ok=True)
    labels = list(meta.keys())
    vmax = float(np.ceil(max(sh.high_share.max(), sh.low_share.max()) / 5) * 5) + 3

    def draw(ax, s):
        sub = sh[sh.strategy == s]
        ax.fill_between([0, vmax], [0, vmax], [vmax, vmax], color="#2e8b57", alpha=0.07, zorder=0)
        ax.fill_between([0, vmax], [0, 0], [0, vmax], color="#c0392b", alpha=0.07, zorder=0)
        ax.plot([0, vmax], [0, vmax], "-", color="#333333", lw=2.0, zorder=2)   # plain baseline
        for _, r in sub.iterrows():
            m = meta[r.thinking_type]
            col = m["color"]; mk = m["marker"]
            solid = m["solid"] if m.get("solid") is not None else gain_solid[r.thinking_type]
            fc = col if solid else "none"
            ax.scatter(r.low_share, r.high_share, s=210, marker=mk, c=fc,
                       edgecolors=col, linewidths=2.0, zorder=3)
            ax.annotate(m["label"], (r.low_share, r.high_share), fontsize=8.5,
                        fontweight="bold", color="#222222", zorder=5,
                        xytext=(7, 4), textcoords="offset points")
        ax.set_xlim(0, vmax); ax.set_ylim(0, vmax)
        ax.set_xlabel("Low set share (%)", fontsize=12)
        ax.set_ylabel("High set share (%)", fontsize=12)
        ax.grid(True, alpha=0.25)
        ax.set_aspect("equal", adjustable="box")

    for s in STRATS:
        fig, ax = plt.subplots(figsize=(9, 8.2))
        draw(ax, s)
        ax.set_title(f"{s}\n(对角线 y = x 为 plain 基准)", fontsize=13, fontweight="bold")
        h = []
        for lv, c in meta_level_colors(meta).items():
            h.append(Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                            markeredgecolor=c, markersize=11, label=lv))
        for tg, mk in meta_target_markers(meta).items():
            h.append(Line2D([0], [0], marker=mk, color="w", markerfacecolor="none",
                            markeredgecolor="#333333", markeredgewidth=2, markersize=10, label=tg))
        h.append(Line2D([0], [0], marker="o", color="w", markerfacecolor="none",
                        markeredgecolor="#333333", markeredgewidth=2, markersize=11,
                        label="保稳 Defensive (空心)"))
        h.append(Line2D([0], [0], marker="o", color="w", markerfacecolor="#333333",
                        markeredgecolor="#333333", markersize=11, label="拔高 Offensive (实心)"))
        ax.legend(handles=h, loc="lower right", fontsize=8.5, framealpha=0.92, ncol=1)
        fig.tight_layout()
        p = os.path.join(outdir, f"{tag}_{s}.png")
        fig.savefig(p, dpi=180, bbox_inches="tight"); plt.close(fig)
        print("saved", p)

    # combined 1x5
    fig, axes = plt.subplots(1, 5, figsize=(30, 7), sharex=True, sharey=True)
    for ax, s in zip(axes, STRATS):
        draw(ax, s)
        ax.set_title(s, fontsize=16, fontweight="bold")
    fig.suptitle(f"Thinking-type Low/High share per strategy  [{tag}]   "
                 f"(colour=Level, marker=Target, fill=Nature of Gain; diagonal=plain)", fontsize=15)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    p = os.path.join(outdir, f"{tag}_ALL.png")
    fig.savefig(p, dpi=150, bbox_inches="tight"); plt.close(fig)
    print("saved", p)


def meta_level_colors(meta):
    d = {}
    for t, m in meta.items():
        d[m["level_label"]] = m["color"]
    return d


def meta_target_markers(meta):
    d = {}
    for t, m in meta.items():
        d[m["target_label"]] = m["marker"]
    return d


def main():
    # ---------------- v2 ----------------
    v2 = pd.read_csv(os.path.join(HERE, "all_tasks_v2.csv"))
    sh2, Dh2, Dl2 = compute_shares(v2, "thinking_type")
    meta_v2 = {}
    for t in TYPE_IDS:
        lv = ID2LEVEL[t]; tg = ID2TARGET[t]
        solid = bool(Dh2.get(t, 0) > Dl2.get(t, 0))   # 该类型整体更常被提升 => 拔高(实心)
        meta_v2[t] = dict(label=t, color=LEVEL_COLOR[lv], marker=TARGET_MARKER[tg],
                          level_label=LEVEL_LABEL[lv], target_label=TARGET_LABEL[tg],
                          solid=solid)
    sh2.to_csv(os.path.join(HERE, "threestyle_v2_shares.csv"), index=False)
    make_figures(sh2, meta_v2, os.path.join(HERE, "fig_threestyle_v2"), "v2",
                 {t: meta_v2[t]["solid"] for t in TYPE_IDS})

    # ---------------- old ----------------
    owd = os.path.join(SE, "all_tasks_with_thinking_type.csv")
    od = pd.read_csv(owd, usecols=lambda c: c in ("set", "strategy", "thinking_type"))
    od = od.dropna(subset=["thinking_type"])
    sh1, Dh1, Dl1 = compute_shares(od, "thinking_type")
    sh1["abbr"] = sh1.thinking_type.map(OLD_ABBR)
    meta_old = {}
    for t, ab in OLD_ABBR.items():
        lvl, tgt, stab = OLD_DIMS[ab]
        meta_old[t] = dict(label=ab, color=OLD_LEVEL_COLOR[lvl], marker=OLD_TARGET_MARKER[tgt],
                           level_label=OLD_LEVEL_LABEL[lvl], target_label=OLD_TARGET_LABEL[tgt],
                           solid=(not stab))     # solid = 拔高(offensive)
    sh1.to_csv(os.path.join(HERE, "threestyle_old_shares.csv"), index=False)
    make_figures(sh1, meta_old, os.path.join(HERE, "fig_threestyle_old"), "old", None)

    # ---------------- print ----------------
    print("\n==== v2 shares (%) ====")
    print(sh2.pivot(index="thinking_type", columns="strategy",
                    values=["low_share", "high_share"]).round(1).to_string())
    print("\n==== old shares (%) ====")
    print(sh1.pivot(index="abbr", columns="strategy",
                    values=["low_share", "high_share"]).round(1).to_string())


if __name__ == "__main__":
    main()
