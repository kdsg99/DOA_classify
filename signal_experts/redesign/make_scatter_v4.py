# -*- coding: utf-8 -*-
"""v4 分类尺（11 个思维动作）下的「策略 × 思维动作」High/Low set share 散点图。

口径按用户 2026-09-20 的更正（= 旧版 plot_ownset.py 的 own-set 归一化）：
    x = Low set share  = 该策略在此动作上的 low 行数 / 该策略的 low 总数 × 100
    y = High set share = 该策略在此动作上的 high 行数 / 该策略的 high 总数 × 100

分母是"该策略自己的 low / high 总数"，不是全体五策略的合计。于是每个策略的
两个轴各自加总 100%；没有类型特异效应（plain 式）的策略，high 与 low 会按同一
比例分布在各动作上 → y = x，落在对角线上。所以对角线 = plain 基准，
偏离方向 = 该策略在该动作上的特异效应（上方=提升占优，下方=下降占优）。

两种标注口径都出图：
  primary    —— 每道题只算它的主标签
  multilabel —— 一道题同时计入它的所有动作（v4 的原貌，份额可突破动作本身的构成占比）
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy_v4 import IDS, NAMES, TARGET  # noqa: E402

OUT = os.path.join(HERE, "fig_v4ownset")
os.makedirs(OUT, exist_ok=True)

STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]
C_OTH = "#4C72B0"      # 非目标动作
C_TGT = "#C0392B"      # 该策略想要诱导的目标动作（v4 的 TARGET 映射）
C_LINE = "#333333"

df = pd.read_csv(os.path.join(HERE, "all_tasks_v4.csv"))
df["is_high"] = df["set"] == "high"
COLS = {t: "o_" + t for t in IDS}


def build_shares(mode: str) -> pd.DataFrame:
    """mode: 'primary' 或 'multilabel'。分母 = 该策略自己的 low/high 总数。"""
    rows = []
    for s in STRATS:
        sub = df[df.strategy == s]
        if mode == "primary":
            L = int((~sub.is_high).sum())
            H = int(sub.is_high.sum())
            for t in IDS:
                g = sub[sub.primary == t]
                h, l = int(g.is_high.sum()), int((~g.is_high).sum())
                rows.append(dict(strategy=s, action=t, n_high=h, n_low=l, n_total=h + l,
                                 D_high=H, D_low=L,
                                 high_share=100 * h / H if H else 0.0,
                                 low_share=100 * l / L if L else 0.0))
        else:
            H = int(sub.is_high.sum())
            L = int((~sub.is_high).sum())
            for t in IDS:
                m = sub[COLS[t]].astype(bool)
                h, l = int((m & sub.is_high).sum()), int((m & ~sub.is_high).sum())
                rows.append(dict(strategy=s, action=t, n_high=h, n_low=l, n_total=h + l,
                                 D_high=H, D_low=L,
                                 high_share=100 * h / H if H else 0.0,
                                 low_share=100 * l / L if L else 0.0))
    sc = pd.DataFrame(rows)
    sc["net"] = sc.high_share - sc.low_share          # >0 表示该动作上提升占优
    sc["is_target"] = [a in TARGET[s]["ops"] for s, a in zip(sc.strategy, sc.action)]
    return sc


def draw(ax, sc, s, vmax, fs=8.5, fig=None, annotate=True):
    ax.fill_between([0, vmax], [0, vmax], [vmax, vmax], color="#2e8b57", alpha=0.07, zorder=0)
    ax.fill_between([0, vmax], [0, 0], [0, vmax], color="#c0392b", alpha=0.07, zorder=0)
    ax.plot([0, vmax], [0, vmax], "-", color=C_LINE, lw=2.0, zorder=2)
    sub = sc[sc.strategy == s].reset_index(drop=True)
    for _, r in sub.iterrows():
        ax.scatter(r.low_share, r.high_share, s=60 + r.n_total * 1.1,
                   c=C_TGT if r.is_target else C_OTH, edgecolors="black",
                   linewidths=1.2 if r.is_target else 0.7, alpha=0.9, zorder=4)
    ax.set_xlim(0, vmax)
    ax.set_ylim(0, vmax)
    ax.grid(True, alpha=0.25)
    if annotate:
        ax.set_xlabel("Low set share (%)  =  该动作的 low 数 / 该策略 low 总数", fontsize=10.5)
        ax.set_ylabel("High set share (%)  =  该动作的 high 数 / 该策略 high 总数", fontsize=10.5)
    return sub


OFFS = [(10, 7), (-10, 7), (10, -16), (-10, -16), (16, 16), (-16, 16), (16, -26), (-16, -26),
        (30, 7), (-30, 7), (0, 15), (0, -23), (34, -18), (-34, -18)]


def place(ax, fig, sub, fs=8.5):
    """避让式贴标签（沿用旧版 fig_ownset 的做法）。"""
    fig.canvas.draw()
    used = []
    for _, r in sub.iterrows():
        for dx, dy in OFFS:
            t = ax.annotate("%s %s (n=%d)" % (r.action, NAMES[r.action], r.n_total),
                            (r.low_share, r.high_share), fontsize=fs, color="#111111", zorder=6,
                            xytext=(dx, dy), textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.72))
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
            if not any(bb.overlaps(u) for u in used):
                used.append(bb)
                break
            t.remove()


def legend(ax, tgt, fs=9.0):
    h = [Line2D([0], [0], marker="o", color="w", markerfacecolor=C_TGT, markersize=11,
                markeredgecolor="k", label="目标动作: " + "、".join(NAMES[x] for x in tgt)),
         Line2D([0], [0], marker="o", color="w", markerfacecolor=C_OTH, markersize=10,
                markeredgecolor="k", label="其他动作"),
         Line2D([0], [0], color=C_LINE, ls="-", lw=2.2, label="对角线 y = x = plain 基准")]
    ax.legend(handles=h, loc="lower right", fontsize=fs, framealpha=0.93)


def main():
    tables = {}
    vmax = 0.0
    for mode in ("primary", "multilabel"):
        sc = build_shares(mode)
        tables[mode] = sc
        sc.round(3).to_csv(os.path.join(HERE, "v4ownset_shares_%s.csv" % mode), index=False)
        vmax = max(vmax, float(np.ceil(max(sc.high_share.max(), sc.low_share.max()) / 5) * 5) + 3)
    print("共享坐标上限 VMAX =", vmax)

    for mode in ("primary", "multilabel"):
        sc = tables[mode]
        print("\n=== %s 口径：每策略 own-set 归一化 ===" % mode)
        for s in STRATS:
            g = sc[sc.strategy == s]
            print("  %-11s above=%2d below=%2d corr=%+.2f  xmax=%5.1f ymax=%5.1f maxdev=%5.1f (D_high=%d D_low=%d)"
                  % (s, int((g.high_share > g.low_share).sum()), int((g.high_share < g.low_share).sum()),
                     np.corrcoef(g.low_share, g.high_share)[0, 1], g.low_share.max(), g.high_share.max(),
                     (g.high_share - g.low_share).abs().max(), int(g.D_high.iloc[0]), int(g.D_low.iloc[0])))

        for s in STRATS:
            fig, ax = plt.subplots(figsize=(10, 8.6))
            sub = draw(ax, sc, s, vmax)
            place(ax, fig, sub)
            ax.set_aspect("equal", adjustable="box")
            ax.set_title("策略 %s —— v4 分类尺（11 个思维动作）High/Low set share  [%s 口径]\n"
                         "x = Low set share、y = High set share，各自除以该策略的 low/high 总数；对角线 = plain 基准"
                         % (s, mode), fontsize=12)
            legend(ax, TARGET[s]["ops"])
            fig.tight_layout()
            fn = os.path.join(OUT, "v4ownset_%s_%s.png" % (mode, s))
            fig.savefig(fn, dpi=190, bbox_inches="tight")
            plt.close(fig)
            print("saved", fn)

        fig, axes = plt.subplots(1, 5, figsize=(34, 7.8), sharex=True, sharey=True)
        for ax, s in zip(axes, STRATS):
            sub = draw(ax, sc, s, vmax, annotate=False)
            ax.set_aspect("equal", adjustable="box")
            place(ax, fig, sub, fs=7)
            ax.set_title("%s  目标: %s" % (s, "、".join(NAMES[x] for x in TARGET[s]["ops"])), fontsize=14,
                         fontweight="bold")
        axes[0].set_ylabel("High set share (%)", fontsize=11)
        for ax in axes:
            ax.set_xlabel("Low set share (%)", fontsize=10)
        fig.suptitle("v4 分类尺（11 个思维动作）× 五策略 —— 每策略 own-set 的 High/Low set share  [%s 口径]\n"
                     "分母 = 该策略自己的 low/high 总数；对角线 y = x 即 plain 基准；红点 = 该策略的目标动作"
                     % mode, fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.92])
        fn = os.path.join(OUT, "v4ownset_all_%s.png" % mode)
        fig.savefig(fn, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print("saved", fn)

    print("\n=== primary 口径：各策略 net = high_share − low_share ===")
    sc = tables["primary"]
    for s in STRATS:
        sub = sc[sc.strategy == s].sort_values("net", ascending=False)
        print("\n[%s] 目标动作 %s" % (s, "、".join(NAMES[x] for x in TARGET[s]["ops"])))
        for _, r in pd.concat([sub.head(3), sub.tail(3)]).iterrows():
            print("   %-12s net=%+6.2f (high %.2f / low %.2f, n=%d)%s"
                  % (NAMES[r.action], r.net, r.high_share, r.low_share, r.n_total,
                     "  <= 目标" if r.is_target else ""))
    print("\n=== multilabel 口径：目标动作 ===")
    sc = tables["multilabel"]
    for s in STRATS:
        r = sc[(sc.strategy == s) & sc.is_target]
        print("  %-11s" % s, " | ".join("%s net=%+.2f (h%.2f/l%.2f n=%d)"
                                        % (NAMES[x.action], x.net, x.high_share, x.low_share, x.n_total)
                                        for _, x in r.iterrows()))


if __name__ == "__main__":
    main()
