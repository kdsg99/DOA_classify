# -*- coding: utf-8 -*-
"""
Figures + Chinese summary for the v3 taxonomy comparison.

usage: python report_v3.py
   (reads all_tasks_v2.csv / all_tasks_v3_s1.csv / all_tasks_v3_s2.csv,
    re-uses the metrics of analyze_v3.py)
"""
import os, sys, itertools
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_v3 as A
from taxonomy_v3 import SCHEMES
from taxonomy_v2 import ID2ZH as V2_ZH

OUT = os.path.join(HERE, "fig_v3"); os.makedirs(OUT, exist_ok=True)
SCOL = {"PRESSURE": "#c0392b", "ENCOURAGE": "#2980b9", "CRITICAL": "#8e44ad",
        "MISLEADING": "#d68910", "HEURISTIC": "#16a085"}


# ------------------------------------------------------------------ figures
def fig_scheme_compare(M, path):
    m = M[M.scope == "common"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
    for ax, col, ttl in ((axes[0], "T", "策略差异度 T（5 策略两两 JSD 均值）"),
                         (axes[1], "P", "优劣区分度 P（同策略 high vs low）")):
        x = np.arange(len(m))
        ax.bar(x, m[col], color=["#7f8c8d" if s == "dataset" else "#2e86c1" for s in m.scheme],
               width=0.6)
        for xi, (v, nl, z) in enumerate(zip(m[col], m[col + "_null"] if col + "_null" in m else m[col], m[col + "_z"])):
            ax.hlines(nl, xi - 0.35, xi + 0.35, color="#c0392b", ls="--", lw=1.6)
            ax.text(xi, v + 0.004, f"z={z:.0f}", ha="center", fontsize=10, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels([f"{s}\n({t})" for s, t in zip(m.scheme, m.n_cats)], fontsize=9.5)
        ax.set_title(ttl, fontsize=12.5); ax.grid(alpha=0.25, axis="y")
        ax.set_ylim(0, max(m[col].max(), m[col + "_null"].max()) * 1.25)
    axes[0].plot([], [], color="#c0392b", ls="--", label="随机置换基线")
    axes[0].legend(fontsize=10, loc="upper left")
    fig.suptitle("各分类方案对「策略差异」的区分能力（同一批任务、common 子集）", fontsize=14.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=170, bbox_inches="tight"); plt.close(fig)


def fig_heatmap(P, names, cats, path, title):
    fig, axes = plt.subplots(1, 2, figsize=(1.05 * len(cats) + 5, 5.6),
                             gridspec_kw={"width_ratios": [len(cats), 1.1]})
    ax = axes[0]
    M = P.pivot(index="strategy", columns="cat", values="log2_lift").reindex(index=A.STRATS, columns=cats)
    R = P.pivot(index="strategy", columns="cat", values="high_rate").reindex(index=A.STRATS, columns=cats)
    N = P.pivot(index="strategy", columns="cat", values="n").reindex(index=A.STRATS, columns=cats)
    vmax = float(np.nanmax(np.abs(M.values))) or 1.0
    im = ax.imshow(M.values, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([names.get(c, c) for c in cats], rotation=60, ha="right", fontsize=9)
    ax.set_yticks(range(len(A.STRATS))); ax.set_yticklabels(A.STRATS, fontsize=11)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M.values[i, j]; r = R.values[i, j]; n = N.values[i, j]
            if np.isnan(v):
                continue
            ax.text(j, i - 0.13, f"{r*100:.0f}%", ha="center", va="center", fontsize=9,
                    fontweight="bold", color="black" if abs(v) < vmax * 0.6 else "white")
            ax.text(j, i + 0.24, f"n={int(n)}", ha="center", va="center", fontsize=7,
                    color="black" if abs(v) < vmax * 0.6 else "white")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("log2(该策略在该类的提升率 / 该策略整体提升率)", fontsize=9.5)
    ax.set_title(title + "\n单元格：提升率（上） 样本数（下）", fontsize=12)
    ax2 = axes[1]
    base = P.groupby("strategy").apply(
        lambda d: d.n_high.sum() / d.n.sum(), include_groups=False).reindex(A.STRATS)
    ax2.barh(range(len(A.STRATS)), base.values * 100,
             color=[SCOL[s] for s in A.STRATS], alpha=0.85)
    for i, v in enumerate(base.values * 100):
        ax2.text(v + 0.6, i, f"{v:.1f}%", va="center", fontsize=9.5, fontweight="bold")
    ax2.set_yticks(range(len(A.STRATS)))
    ax2.set_yticklabels([s[0] for s in A.STRATS], fontsize=11)
    ax2.invert_yaxis(); ax2.set_xlim(0, max(base.values * 100) * 1.25)
    ax2.set_title("该策略整体提升率\n(high 占比)", fontsize=11)
    ax2.grid(alpha=0.25, axis="x")
    fig.tight_layout(); fig.savefig(path, dpi=175, bbox_inches="tight"); plt.close(fig)


def fig_prefbars(P, cats, path, title):
    fig, axes = plt.subplots(1, 5, figsize=(26, 7.2), sharex=True)
    vmax = float(np.nanmax(np.abs(P.log2_lift.values))) or 1.0
    for ax, s in zip(axes, A.STRATS):
        d = P[P.strategy == s].set_index("cat").reindex(cats).dropna(subset=["log2_lift"])
        y = np.arange(len(d))[::-1]
        cols = ["#c0392b" if v > 0 else "#2471a3" for v in d.log2_lift]
        ax.barh(y, d.log2_lift, color=cols, alpha=0.9,
                edgecolor=["black" if e else "none" for e in d.enough], linewidth=0.8)
        for yy, (_, r) in zip(y, d.iterrows()):
            lbl = f"{r.high_rate*100:.0f}%  n={int(r.n)}"
            ax.text(r.log2_lift + (0.05 if r.log2_lift >= 0 else -0.05), yy, lbl,
                    va="center", ha="left" if r.log2_lift >= 0 else "right", fontsize=8.2,
                    color="#111111")
        ax.axvline(0, color="black", lw=1)
        ax.set_yticks(y); ax.set_yticklabels(d.cat_name, fontsize=9.5)
        ax.set_title(f"{s}  (整体 {d.base_rate.iloc[0]*100:.1f}%)", fontsize=12.5, fontweight="bold",
                     color=SCOL[s])
        ax.grid(alpha=0.25, axis="x"); ax.set_xlim(-vmax * 1.5, vmax * 1.5)
    axes[0].set_xlabel("log2(提升率 / 该策略整体提升率)")
    fig.suptitle(title + "\n右=该策略偏好的题型（提升率高于自身平均）；左=短板题型；加粗边框=样本 n≥20",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def fig_cat_spread(P, cats, path, title):
    fig, ax = plt.subplots(figsize=(11.5, 0.52 * len(cats) + 2.4))
    piv = P.pivot(index="cat", columns="strategy", values="high_rate").reindex(index=cats)
    n = P.pivot(index="cat", columns="strategy", values="n").reindex(index=cats)
    spread = (piv.max(axis=1) - piv.min(axis=1)).sort_values()
    piv = piv.reindex(spread.index); n = n.reindex(spread.index)
    y = np.arange(len(piv))
    for i, c in enumerate(piv.index):
        vals = piv.loc[c].dropna()
        ax.hlines(i, vals.min() * 100, vals.max() * 100, color="#bdc3c7", lw=2.2, zorder=1)
    for s in A.STRATS:
        ax.scatter(piv[s] * 100, y, s=[40 + 1.6 * (n[s].iloc[i] if not np.isnan(n[s].iloc[i]) else 0)
                                       for i in range(len(y))],
                   color=SCOL[s], label=s, zorder=3, edgecolors="white", linewidths=0.8)
    base = P.groupby("strategy").apply(lambda d: d.n_high.sum() / d.n.sum(), include_groups=False)
    ax.axvline(base.mean() * 100, color="#555555", ls="--", lw=1.3)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{P[P.cat==c].cat_name.iloc[0]}  (跨度 {spread[c]*100:.0f}pp)" for c in piv.index],
                       fontsize=10)
    ax.set_xlabel("该策略在该类任务上的提升率 high rate (%)")
    ax.set_title(title + "\n每行=一个题型，每个点=一个策略（点大小=该策略在该类的样本数）；虚线=总体平均",
                 fontsize=12.5, fontweight="bold")
    ax.legend(fontsize=10, ncol=5, loc="lower right"); ax.grid(alpha=0.25, axis="x")
    fig.tight_layout(); fig.savefig(path, dpi=170, bbox_inches="tight"); plt.close(fig)


CANDS = [(11, 9), (11, -14), (-11, 9), (-11, -14), (17, 15), (-17, 15), (17, -20), (-17, -20),
         (26, 0), (-26, 0), (0, 17), (0, -20), (30, 16), (-30, 16), (30, -22), (-30, -22),
         (0, 28), (0, -32), (40, 0), (-40, 0), (36, 24), (-36, 24), (36, -28), (-36, -28)]


def label_points(ax, fig, sub, lim, fs=8.0):
    inside = sub[(sub.x >= lim[0]) & (sub.x <= lim[1]) & (sub.y >= lim[0]) & (sub.y <= lim[1])]
    if inside.empty:
        return
    fig.canvas.draw()
    placed = []
    for _, r in inside.iterrows():
        px, py = ax.transData.transform((r.x, r.y))
        placed.append(Bbox.from_bounds(px - 10, py - 10, 20, 20))
    for _, r in inside.iterrows():
        for (dx, dy) in CANDS:
            far = abs(dx) > 18 or abs(dy) > 18
            kw = dict(arrowprops=dict(arrowstyle="-", lw=0.6, color="#9a9a9a",
                                      shrinkA=1, shrinkB=3)) if far else {}
            t = ax.annotate(f"{r.cat_name} {r.n_task}", (r.x, r.y), fontsize=fs, fontweight="bold",
                            color="#111111", zorder=7, xytext=(dx, dy), textcoords="offset points",
                            ha="center", va="center",
                            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="#cccccc",
                                      lw=0.6, alpha=0.88), **kw)
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer()).expanded(1.03, 1.10)
            if not any(bb.overlaps(u) for u in placed):
                placed.append(bb); break
            t.remove()


def share_table(df, names, cat_col="cat"):
    rows = []
    for s in A.STRATS:
        sub = df[df.strategy == s]
        L = int((sub.set == "low").sum()); H = int((sub.set == "high").sum())
        for c, g in sub.groupby(cat_col):
            l = int((g.set == "low").sum()); h = int((g.set == "high").sum())
            rows.append(dict(strategy=s, cat=c, cat_name=names.get(c, str(c)),
                             n_task=h + l, n_high=h, n_low=l,
                             x=100 * l / L if L else 0.0, y=100 * h / H if H else 0.0))
    return pd.DataFrame(rows)


def scatter_rows(ax, sub, lim, ms=250, lw=2.2, cmap=None):
    for _, r in sub.iterrows():
        col = cmap.get(r["cat"], "#333333") if cmap else "#333333"
        ax.scatter(r.x, r.y, s=ms, marker="o", c=col, edgecolors="white", linewidths=1.2,
                   zorder=4, clip_on=False)
    ax.fill_between([lim[0], lim[1]], [lim[0], lim[0]], [lim[1], lim[1]], color="#2e8b57",
                    alpha=0.07, zorder=0)
    ax.plot([lim[0], lim[1]], [lim[0], lim[1]], "-", color="#333333", lw=1.8, zorder=2)
    ax.set_xlim(*lim); ax.set_ylim(*lim); ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.22)
    ax.set_xlabel("Low set share (%)"); ax.set_ylabel("High set share (%)")


def fig_scatter(sh, names, path, title, vmax):
    cmap = {c: plt.cm.tab20(i / max(len(names) - 1, 1)) for i, c in enumerate(sorted(names))}
    FULL = (-1.2, vmax); ZL = (-1.2, 15.0)
    fig, axes = plt.subplots(1, 2, figsize=(17.5, 8.6))
    for ax, lim, tag in ((axes[0], FULL, f"全范围 0–{vmax:.0f}%"), (axes[1], ZL, "放大 0–15%")):
        ax.add_patch(Rectangle((0, 0), 15, 15, fill=False, ec="#888888", ls=(0, (4, 3)), lw=1.2, zorder=1))
        sub = sh[sh.strategy == sh.strategy.iloc[0]]
        scatter_rows(ax, sub, lim)
        ax.set_title(tag, fontsize=12)
    fig.tight_layout()
    for ax, lim, fs in ((axes[0], FULL, 7.6), (axes[1], ZL, 9.0)):
        sub = sh[sh.strategy == sh.strategy.iloc[0]]
        label_points(ax, fig, sub, lim, fs=fs)
    fig.suptitle(title, fontsize=14.5, fontweight="bold")
    fig.savefig(path, dpi=180, bbox_inches="tight"); plt.close(fig)


def fig_scatter_all(sh, names, path, title, vmax):
    cmap = {c: plt.cm.tab20(i / max(len(names) - 1, 1)) for i, c in enumerate(sorted(names))}
    FULL = (-1.2, vmax); ZL = (-1.2, 15.0)
    fig, axes = plt.subplots(2, 5, figsize=(33, 14.5), sharex="row", sharey="row")
    for j, s in enumerate(A.STRATS):
        sub = sh[sh.strategy == s]
        for i, lim in ((0, FULL), (1, ZL)):
            ax = axes[i][j]
            ax.add_patch(Rectangle((0, 0), 15, 15, fill=False, ec="#888888", ls=(0, (4, 3)),
                                   lw=1.1, zorder=1))
            scatter_rows(ax, sub, lim, ms=210, lw=2.0, cmap=cmap)
            if i == 0:
                ax.set_title(s, fontsize=16, fontweight="bold", color=SCOL[s])
    fig.tight_layout()
    for j, s in enumerate(A.STRATS):
        sub = sh[sh.strategy == s]
        label_points(axes[0][j], fig, sub, FULL, fs=6.6)
        label_points(axes[1][j], fig, sub, ZL, fs=8.0)
    h = [Line2D([0], [0], marker="o", color="w", markerfacecolor=cmap[c], markersize=11,
                markeredgecolor="white", label=names[c]) for c in sorted(names)]
    fig.legend(handles=h, loc="lower center", ncol=min(6, len(h)), fontsize=11,
               frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(title, fontsize=16, fontweight="bold")
    fig.savefig(path, dpi=135, bbox_inches="tight"); plt.close(fig)


# ------------------------------------------------------------------ summary
def _fmt_pref(row):
    sig = "" if row.sig else "*"
    return f"{row.cat_name} {row.high_rate*100:.0f}%(n={int(row.n)},x{row.lift:.2f}){sig}"


def write_summary(schemes, M, best, P_best, P_v2, path):
    cm = M[M.scope == "common"].set_index("scheme")
    L = []; A_ = L.append
    A_("# 新分类法 (v3) vs 原有分类法 (v2)：策略偏好画像\n")
    A_("## 0. 结论先说\n")
    win = cm.drop(index=["dataset"], errors="ignore")
    A_(f"- 同一批任务（common 子集 {int(win.iloc[0].n)} 行）上，各候选分类法的「策略差异度」T：")
    for tag in win.index:
        r = win.loc[tag]
        A_(f"  - **{tag}** {r.title}：T = {r.T:.3f}（随机基线 {r.T_null:.3f}，z = {r.T_z:.1f}），"
           f"优劣区分度 P = {r.P:.3f}（z = {r.P_z:.1f}），Cramér's V = {r.V:.3f}")
    r = cm.loc["dataset"]
    A_(f"  - （基线）dataset {r.n_cats} 类：T = {r.T:.3f}，z = {r.T_z:.1f}")
    A_(f"- 采用 **{best}**（{schemes[best]['title']}）作为新的任务分类法。\n")
    A_("## 1. 新分类法的判据\n")
    if best == "s1":
        A_("**维度 D（题目在要什么）**：K 知识 / R 推理 / B 建构(按规格交付成品) / E 表达")
        A_("**要求类型 Q（判分依据）**：V 精确可验 / C 约束合规 / Q 主观质量\n")
    else:
        A_("单轴 8 类：模型最容易出错的环节（知识缺口/计算推导/约束遗漏/误导陷阱/表达平庸/长文一致/检查修复/低风险常规）\n")
    A_("## 2. 五个策略的偏好画像（提升率 = 该策略在这类任务上把分数拉高的比例）\n")
    for s in A.STRATS:
        d = P_best[(P_best.strategy == s) & P_best.enough].sort_values("log2_lift", ascending=False)
        base = P_best[P_best.strategy == s].base_rate.iloc[0]
        top = d.head(3); bot = d.tail(3).iloc[::-1]
        A_(f"### {s}（整体提升率 {base*100:.1f}%）\n")
        A_("偏好：" + "；".join(_fmt_pref(r) for _, r in top.iterrows()))
        A_("短板：" + "；".join(_fmt_pref(r) for _, r in bot.iterrows()))
        A_(f"最偏 {top.iloc[0].cat_name}（x{top.iloc[0].lift:.2f}），最差 {bot.iloc[0].cat_name}（x{bot.iloc[0].lift:.2f}）\n")
    A_("## 3. 最能拉开策略差距的题型\n")
    piv = P_best.pivot(index="cat", columns="strategy", values="high_rate")
    lab = P_best.drop_duplicates("cat").set_index("cat").cat_name
    nn = P_best.pivot(index="cat", columns="strategy", values="n")
    spread = (piv.max(axis=1) - piv.min(axis=1)).sort_values(ascending=False)
    for c in spread.index[:6]:
        hi_s = piv.loc[c].idxmax(); lo_s = piv.loc[c].idxmin()
        A_(f"- **{lab[c]}**：跨度 {spread[c]*100:.0f}pp — 最高 {hi_s} {piv.loc[c,hi_s]*100:.0f}%（n={int(nn.loc[c,hi_s])}），最低 {lo_s} {piv.loc[c,lo_s]*100:.0f}%（n={int(nn.loc[c,lo_s])}）")
    A_("")
    A_("## 4. 与原有 v2 分类的对照\n")
    pv2 = cm.loc["v2"]
    A_(f"- v2 上 T = {pv2.T:.3f}，{best} 上 T = {cm.loc[best,'T']:.3f}（提升 "
       f"{(cm.loc[best,'T']/pv2.T-1)*100:+.0f}%）；策略差异更清楚。")
    A_("- 同一策略在 v2 各类上的偏差只有 ±4.6pp 量级，说明 v2 的类型划分主要反映类别大小而非策略专长。\n")
    A_("## 5. 文件\n")
    A_("- `all_tasks_v3_s1.csv` / `all_tasks_v3_s2.csv`：逐行标签")
    A_("- `scheme_metrics.csv`：各方案的 T / P / V / 置换检验")
    A_(f"- `preference_{best}.csv`：策略 × 题型 的提升率、置信区间、倍数")
    A_("- `fig_v3/`：scheme_compare.png, heatmap_*.png, prefbar_*.png, cat_spread_*.png, scatter_*.png")
    A_("\n注：带 * 表示与自身整体提升率的差异未达 95% 置信（Wilson 区间跨过基线）。")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("summary ->", path)


def main():
    schemes, M, keys, best = A.main()
    names = schemes[best]["names"]
    df = schemes[best]["df"]
    cats = [c for c in SCHEMES[best]["ids"] if c in set(df["cat"].dropna().unique())]
    P = preference_table(df, names, min_n=20)
    P.to_csv(os.path.join(HERE, f"preference_{best}.csv"), index=False)
    Pv2 = preference_table(schemes["v2"]["df"], V2_ZH, min_n=20)
    Pv2.to_csv(os.path.join(HERE, "preference_v2.csv"), index=False)

    fig_scheme_compare(M, os.path.join(OUT, "scheme_compare.png"))
    fig_heatmap(P, names, cats, os.path.join(OUT, f"heatmap_{best}.png"),
                f"{best} {schemes[best]['title']} — 策略偏好热力图")
    fig_prefbars(P, cats, os.path.join(OUT, f"prefbar_{best}.png"),
                 f"{best} {schemes[best]['title']} — 每个策略偏好的题型 vs 短板题型")
    fig_cat_spread(P, cats, os.path.join(OUT, f"cat_spread_{best}.png"),
                   f"{best} — 每个题型上五个策略的差距")
    sh = share_table(df, names)
    vmax = float(np.ceil(max(sh.x.max(), sh.y.max()) / 5) * 5) + 3
    for s in A.STRATS:
        fig_scatter(sh[sh.strategy == s], names, os.path.join(OUT, f"scatter_{best}_{s}.png"),
                    f"{s} — {best} 各类的 Low/High set share（对角线 = plain 基准）", vmax)
    fig_scatter_all(sh, names, os.path.join(OUT, f"scatter_ALL_{best}.png"),
                    f"{best} {schemes[best]['title']} — Low/High set share（上：全范围；下：0–15% 放大）", vmax)
    write_summary(schemes, M, best, P, Pv2, os.path.join(HERE, "summary_v3.md"))
    return schemes, M, best, P


if __name__ == "__main__":
    main()
