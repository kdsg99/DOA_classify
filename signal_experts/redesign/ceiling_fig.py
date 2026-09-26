# -*- coding: utf-8 -*-
"""D6：天花板效应盘点图（饱和行 = plain 已 100%，Δ 只能 <=0）。"""
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
from taxonomy_v4 import IDS, NAMES                              # noqa: E402

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
FIG = os.path.join(R, "fig_effect")

df = pd.read_csv(R + r"\all_tasks_v4.csv")
df["delta_pp"] = 100 * df.delta
df["plain_pp"] = 100 * df.plain_minmax
df["ceil"] = df.plain_pp >= 99.999

fig, axes = plt.subplots(2, 2, figsize=(20, 12))

ax = axes[0, 0]
b = np.arange(0, 105, 5)
ax.hist(df.loc[~df.ceil, "plain_pp"], bins=b, color="#3B6FB6", label="非饱和（还有上升空间）")
ax.hist(df.loc[df.ceil, "plain_pp"], bins=b, color="#C0392B", label="饱和 plain=100（Δ 只能 ≤0）")
ax.axvline(100, color="#C0392B", ls="--", lw=1.4)
ax.set_xlabel("plain_minmax（pp）", fontsize=11)
ax.set_ylabel("行数", fontsize=11)
ax.set_title("① 重问前得分的分布：%d/%d 行（%.0f%%）已满分，结构上不可能上升"
             % (df.ceil.sum(), len(df), 100 * df.ceil.mean()), fontsize=12.5)
ax.legend(fontsize=10)
ax.grid(alpha=0.25)

ax = axes[0, 1]
fams = ["chat_math500", "chat_wild_bench", "chat_flask", "llama_flask", "qwen_flask", "mt_bench"]
xs = np.arange(len(fams))
cs = [100 * df[df.dataset_id == f].ceil.mean() for f in fams]
ax.bar(xs, cs, color=["#C0392B" if c > 20 else "#3B6FB6" for c in cs])
for i, (f, c) in enumerate(zip(fams, cs)):
    ax.annotate("%.0f%%" % c, (i, c), ha="center", va="bottom", fontsize=10)
ax.set_xticks(xs)
ax.set_xticklabels(fams, fontsize=9.5, rotation=12)
ax.set_ylabel("饱和行占比 (%)", fontsize=11)
ax.set_title("② 各族饱和比例：chat_math500 高达 92%（0/1 判分 + plain 满分）", fontsize=12.5)
ax.grid(alpha=0.25, axis="y")

for ax, key, order, ttl in [
        (axes[1, 0], "dataset_id", fams, "按评测族"),
        (axes[1, 1], "strategy", ["PRESSURE", "CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"], "按策略")]:
    xs = np.arange(len(order))
    sat = [df[(df[key] == k) & df.ceil].delta_pp.mean() for k in order]
    uns = [df[(df[key] == k) & ~df.ceil].delta_pp.mean() for k in order]
    ax.bar(xs - 0.2, sat, 0.4, color="#C0392B", label="Δ（饱和行）")
    ax.bar(xs + 0.2, uns, 0.4, color="#3B6FB6", label="Δ（非饱和行）")
    ax.axhline(0, color="#222", lw=1.2)
    for i, (a, b_) in enumerate(zip(sat, uns)):
        ax.annotate("%.0f" % a, (i - 0.2, a), ha="center", va="top" if a < 0 else "bottom", fontsize=9)
        ax.annotate("%.0f" % b_, (i + 0.2, b_), ha="center", va="top" if b_ < 0 else "bottom", fontsize=9)
    ax.set_xticks(xs)
    ax.set_xticklabels(order, fontsize=9.5, rotation=12)
    ax.set_ylabel("Δ（pp）", fontsize=11)
    ax.set_title("③ %s：饱和行 vs 非饱和行的 Δ —— 落差几乎全在饱和行" % ttl, fontsize=12.5)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.25, axis="y")
    ax.set_ylim(-115, 130)

fig.suptitle("D6. 天花板效应：24% 的行 plain 已经 100%，这些行只可能掉分；"
             "「链式推演=崩盘」的观感主要来自 chat_math500 的 92% 饱和行（−96pp）——"
             "非饱和行里它只有 0.0pp（n=668）", fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.945])
fig.savefig(os.path.join(FIG, "D6_ceiling_effect.png"), dpi=130, bbox_inches="tight")
plt.close(fig)
print("已生成 D6_ceiling_effect.png")
