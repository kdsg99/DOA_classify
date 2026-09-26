# -*- coding: utf-8 -*-
"""D3 机制图：难度余量校正到底在扣什么（以「链式推演」格为例）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
sys.path.insert(0, R)
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
FIG = os.path.join(R, "fig_effect")

df = pd.read_csv(R + r"\all_tasks_v4.csv")
df["delta_pp"] = 100 * df.delta
df["plain_pp"] = 100 * df.plain_minmax
STRATS = ["PRESSURE", "ENCOURAGE", "CRITICAL", "MISLEADING", "HEURISTIC"]


def panel(ax, s, big=False):
    sub = df[df.strategy == s]
    x, y = sub.plain_pp.values, sub.delta_pp.values
    b1, b0 = np.polyfit(x, y, 1)
    xs = np.linspace(0, 100, 50)
    ax.scatter(x, y, s=9 if not big else 13, color="#BBB", alpha=0.5, zorder=2, edgecolors="none")
    ch = sub[sub.primary == "T2_CHAIN"]
    xc = ch.plain_pp.values
    yc = ch.delta_pp.values
    ax.scatter(xc, yc, s=18 if not big else 26, color="#C0392B", alpha=0.85, zorder=4,
               edgecolors="k", linewidths=0.3, label="链式推演行")
    ax.plot(xs, b0 + b1 * xs, "-", color="#1B4F72", lw=2.2, zorder=3,
            label="拟合线 %+.2f%+.3f·plain" % (b0, b1))
    xbar = xc.mean()
    raw = yc.mean()
    pred = b0 + b1 * xbar
    ax.axvline(xbar, color="#666", ls=":", lw=1.2, zorder=1)
    ax.plot([xbar, xbar], [pred, raw], "-", color="#111", lw=2.4, zorder=6)
    ax.scatter([xbar], [pred], s=110 if big else 78, marker="o", facecolors="white",
               edgecolors="#111", linewidths=1.8, zorder=7)
    ax.scatter([xbar], [raw], s=110 if big else 78, marker="D", color="#C0392B",
               edgecolors="k", linewidths=1.0, zorder=7)
    ax.annotate("校正后 %+.1fpp\n（实际 %+.1f − 难度期望 %+.1f）" % (raw - pred, raw, pred),
                (xbar, (raw + pred) / 2), fontsize=(10.5 if big else 8.2), ha="left", va="center",
                xytext=(12, 0), textcoords="offset points",
                bbox=dict(fc="white", ec="#999", lw=0.7, alpha=0.9), zorder=8)
    ax.annotate("链式推演行 plain 均值 %.0f\n（该策略整体 %.0f）" % (xbar, x.mean()),
                (xbar, 0), fontsize=(9.5 if big else 7.6), ha="center", va="top",
                xytext=(0, -8), textcoords="offset points", color="#444", zorder=8)
    ax.axhline(0, color="#999", lw=0.9, zorder=1)
    ax.set_xlim(-2, 102)
    ax.set_ylim(-115, 115)
    ax.set_xlabel("plain_minmax（pp）：题目在「重问前」的分数", fontsize=(11 if big else 9))
    ax.grid(alpha=0.2)
    if big:
        ax.set_ylabel("delta（pp）= reask − plain", fontsize=11)
        ax.set_title("PRESSURE：为什么「难度校正后」链式推演反而更低", fontsize=14, fontweight="bold")
        ax.legend(fontsize=10, loc="upper right")
    else:
        ax.set_title(s, fontsize=12.5, fontweight="bold")


fig, ax = plt.subplots(figsize=(11.2, 8.0))
panel(ax, "PRESSURE", big=True)
fig.text(0.5, 0.015, "■ 红点=实际；○ 白点=同难度下的期望值；两点的差就是「校正后」的读数。"
                     "PRESSURE 的链式推演行落在该策略偏容易的一端（plain 56.7 vs 全体 64.6），"
                     "而此处期望本身是 +8.5pp，它只拿到 −0.4pp → 校正后 −8.9pp。",
         ha="center", fontsize=10.5, color="#333")
fig.tight_layout(rect=[0, 0.045, 1, 1])
fig.savefig(os.path.join(FIG, "D4_mechanism_pressure.png"), dpi=135, bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(1, 5, figsize=(30, 6.6), sharey=True)
for ax, s in zip(axes, STRATS):
    panel(ax, s)
fig.suptitle("D4. 难度余量校正的机制（每策略一格，链式推演格为例）："
             "红点=实际均值，白点=同难度期望，两点的垂直差就是 D3 报的「校正后」值", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig(os.path.join(FIG, "D5_mechanism_all.png"), dpi=130, bbox_inches="tight")
plt.close(fig)
print("已生成 D4_mechanism_pressure.png / D5_mechanism_all.png")
