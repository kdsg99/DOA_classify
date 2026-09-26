# -*- coding: utf-8 -*-
"""Step 1 - screen candidate content-based classifications for strategy x type INTERACTION.

Design note
-----------
Every row is one (task, strategy) run.  Strategies are *not* run on the same tasks everywhere
(227 tasks, 5 strategies, pairwise overlap 84-129 tasks), so a cell mean can differ between two
strategies simply because they were run on different tasks.  The interaction question
("does strategy A beat strategy B on type 1 but lose on type 2?") is therefore estimated
WITHIN tasks: for every task the four non-PRESSURE strategies are centred on their own task mean,

    c_s(task) = dpp_s(task) - mean over available focal strategies

so everything task-specific (difficulty, benchmark, wording, model) cancels.  A classification
produces interaction if the type means v[s, t] of these contrasts differ across types.  Significance
is a label-permutation test (same type sizes, tasks re-assigned at random), and stability is a
split-half correlation (tasks split by hash).
"""
import hashlib
import itertools
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "rows_v2.csv")
V4 = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign\all_tasks_v4.csv"
FOCAL = ["CRITICAL", "ENCOURAGE", "MISLEADING", "HEURISTIC"]
ALLS = ["PRESSURE"] + FOCAL
OPS = ["T1_RECALL", "T2_CHAIN", "T3_PLAN", "T4_CONSTRAINT", "T5_INTEGRATE", "T6_VERIFY",
       "T7_RESIST", "T8_EXPLORE", "T9_REFRAME", "T10_PRAGMA", "T11_SUSTAIN"]


def load():
    d = pd.read_csv(DATA)
    d["dpp"] = 100 * d.delta
    d["key"] = d.dataset_id.astype(str) + "|" + d.task_id.astype(str) + "|" + d["model"].astype(str)
    d = d.drop_duplicates(["key", "strategy"])
    piv = d.pivot_table(index="key", columns="strategy", values="dpp", aggfunc="mean")
    feat = d.drop_duplicates("key").set_index("key")[
        ["dataset_id", "task", "instruction", "category", "subject", "primary_tag", "primary_group",
         "level_label", "metadata_skill", "metadata_domain", "thinking_type", "target", "second_turn"]].copy()
    v4 = pd.read_csv(V4)
    v4["key"] = v4.dataset_id.astype(str) + "|" + v4.task_id.astype(str) + "|" + v4["model"].astype(str)
    v4 = v4.drop_duplicates("key").set_index("key")
    for c in ["primary"] + ["o_" + o for o in OPS]:
        if c in v4:
            feat[c] = v4[c].reindex(feat.index)
    feat["primary"] = feat["primary"].fillna("NA")
    feat["n_ops"] = feat[["o_" + o for o in OPS if "o_" + o in feat]].notna().sum(axis=1)
    feat["skill0"] = feat.metadata_skill.fillna("[]").str.strip("[]").str.split(",").str[0].str.strip('" ')
    feat["domain0"] = feat.metadata_domain.fillna("[]").str.strip("[]").str.split(",").str[0].str.strip('" ')
    feat["tlen"] = feat.task.fillna("").str.len()
    feat["has_fmt"] = feat.task.fillna("").str.contains(
        r"json|JSON|csv|CSV|latex|LaTeX|table|format|bullet|markdown", regex=True)
    return piv, feat


def contrasts(piv, strategies):
    """within-task centring over the given strategies; needs >=2 available."""
    F = piv.reindex(columns=strategies)
    ok = F.notna().sum(axis=1) >= 2
    return F[ok].sub(F[ok].mean(axis=1), axis=0)


def v_matrix(C, lab, strategies):
    """type means of the within-task contrasts; also counts."""
    df = C.copy()
    df["t"] = lab.reindex(df.index)
    out, cnt = {}, {}
    for s in strategies:
        g = df.dropna(subset=[s])
        out[s] = g.groupby("t")[s].mean()
        cnt[s] = g.groupby("t")[s].size()
    V = pd.DataFrame(out)
    N = pd.DataFrame(cnt)
    return V, N


def interaction(V, N, min_n=8):
    """magnitude of strategy x type interaction: mean SD across the strategies of the type profile
    (equal type weight, only cells with enough tasks)."""
    Vm = V.where(N.fillna(0) >= min_n)
    sd = Vm.std(axis=0, ddof=1)                        # per strategy: how much it varies by type
    val = float(np.nanmean(sd.values)) if np.isfinite(sd.values).any() else np.nan
    return val, sd.dropna().to_dict()


def reversal_stats(V, N, strategies, min_n=8):
    """how often does the ordering of two strategies flip between types?"""
    Vm = V.where(N.fillna(0) >= min_n)
    disc, taus = 0, []
    pairs = []
    for a, b in itertools.combinations(strategies, 2):
        d = (Vm[a] - Vm[b]).dropna()
        if len(d) < 3:
            continue
        pos, neg = int((d > 0).sum()), int((d < 0).sum())
        if pos and neg:
            disc += 1
        rk = (Vm[a].rank() - Vm[b].rank()).dropna()
        pairs.append((a, b, pos, neg, float(d.mean())))
        taus.append(1 - 2 * disc / max(1, len(d)))
    argmax = Vm.dropna(how="all").idxmax(axis=1).value_counts().to_dict()
    return disc, argmax, pairs


def perm_test(C, lab, strategies, obs, n_perm=200, min_n=8, seed=0):
    rng = np.random.default_rng(seed)
    labs = lab.reindex(C.index).values
    cnt = pd.Series(labs).value_counts()
    null = []
    for _ in range(n_perm):
        sh = rng.permutation(labs)
        V, N = v_matrix(C, pd.Series(sh, index=C.index), strategies)
        i, _ = interaction(V, N, min_n)
        null.append(i)
    null = np.array(null)
    p = float((null >= obs).mean())
    return p, float(null.mean()), float(null.std())


def split_half(C, lab, strategies, min_n=6, seed=7):
    """spearman correlation of the type profiles between two disjoint halves of the tasks."""
    idx = np.array(C.index)
    h = np.array([int(hashlib.md5((str(s) + str(seed)).encode()).hexdigest(), 16) % 2 for s in idx])
    corrs = []
    a = {}
    for s in strategies:
        Va, Na = v_matrix(C[h == 0], lab.reindex(idx[h == 0]), [s])
        Vb, Nb = v_matrix(C[h == 1], lab.reindex(idx[h == 1]), [s])
        va, vb = Va[s].where(Na[s] >= min_n), Vb[s].where(Nb[s] >= min_n)
        j = va.dropna().index.intersection(vb.dropna().index)
        if len(j) >= 3:
            ca = va[j].rank().values
            cb = vb[j].rank().values
            corrs.append(float(np.corrcoef(ca, cb)[0, 1]))
        a[s] = va
    return float(np.nanmean(corrs)) if corrs else np.nan, a


def main():
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    piv, feat = load()
    C = contrasts(piv, FOCAL)
    print("tasks with >=2 focal strategies: %d of %d" % (len(C), len(piv)))
    parts = {
        "v2 12 types (current)": feat.thinking_type,
        "operation level (3)": feat.thinking_type.str[:2],
        "target (4)": feat.target,
        "eval family (6)": feat.dataset_id,
        "category (8)": feat.category,
        "primary_tag (9)": feat.primary_tag.fillna("NA"),
        "primary_group (4)": feat.primary_group.fillna("NA"),
        "skill (first, 8)": feat.skill0.where(feat.skill0.isin(
            feat.skill0.value_counts().head(8).index), "other"),
        "domain (first, 6)": feat.domain0.where(feat.domain0.isin(
            feat.domain0.value_counts().head(6).index), "other"),
        "v4 primary action (11)": feat["primary"],
        "n_ops (1/2/3+)": pd.cut(feat.n_ops, [0, 1, 2, 10], labels=["1", "2", "3+"]).astype(str),
        "task length (3)": pd.qcut(feat.tlen, 3, labels=["short", "mid", "long"]).astype(str),
        "needs format (2)": feat.has_fmt.map({True: "fmt", False: "free"}),
        "level_label (5)": feat.level_label,
        "12 types x family": feat.thinking_type + "|" + feat.dataset_id,
        "target x family": feat.target + "|" + feat.dataset_id,
        "target x level": feat.thinking_type,
    }
    rows = []
    for name, lab in parts.items():
        lab = pd.Series(lab, index=feat.index).astype(str)
        V, N = v_matrix(C, lab, FOCAL)
        obs, sd = interaction(V, N)
        p, m0, s0 = perm_test(C, lab, FOCAL, obs)
        sh, _ = split_half(C, lab, FOCAL)
        disc, argmax, _ = reversal_stats(V, N, FOCAL)
        nmin = float(np.nanmin(N.values)) if np.isfinite(N.values).any() else np.nan
        nmed = float(np.nanmedian(N.values))
        rows.append(dict(partition=name, k=V.shape[0], inter=obs, null=m0, sd_null=s0, p=p, rel=sh,
                         reversals=disc, argmax3=str(list(argmax.items())[:3]),
                         cells_min=nmin, cells_med=nmed))
    R = pd.DataFrame(rows).sort_values("inter", ascending=False)
    pd.set_option("display.width", 250)
    print(R.round(2).to_string(index=False))
    R.to_csv(os.path.join(HERE, "out", "screen_partitions.csv"), index=False)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    main()
