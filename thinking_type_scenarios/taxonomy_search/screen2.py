# -*- coding: utf-8 -*-
"""Step 2 - with the CORRECT task identity (dataset|task_id), screen many candidate classifications.

Interaction is estimated within tasks: c_s(task) = dpp_s - mean(four focal strategies), so task
level, difficulty, benchmark and wording cancel.  For every candidate classification we report
  inter   : mean over strategies of the SD across types of the type-mean contrast (pp)
  p_perm  : label-permutation p-value for that statistic
  rel     : split-half reproducibility of the type profiles (Spearman, tasks split by hash)
  rev     : how many of the 6 strategy pairs flip their order between types
  best    : which strategy wins how many types
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
OPS = ["T1_RECALL", "T2_CHAIN", "T3_PLAN", "T4_CONSTRAINT", "T5_INTEGRATE", "T6_VERIFY",
       "T7_RESIST", "T8_EXPLORE", "T9_REFRAME", "T10_PRAGMA", "T11_SUSTAIN"]


def load():
    d = pd.read_csv(DATA)
    d["dpp"] = 100 * d.delta
    d["key"] = d.dataset_id.astype(str) + "|" + d.task_id.astype("string").fillna("NA")
    piv = d.pivot_table(index="key", columns="strategy", values="dpp", aggfunc="mean")
    feat = d.drop_duplicates("key").set_index("key")[
        ["dataset_id", "task", "instruction", "problem", "category", "subject", "primary_tag",
         "primary_group", "level_label", "metadata_skill", "metadata_domain", "thinking_type",
         "target", "second_turn"]].copy()
    v4 = pd.read_csv(V4)
    v4["key"] = v4.dataset_id.astype(str) + "|" + v4.task_id.astype("string").fillna("NA")
    v4 = v4.drop_duplicates("key").set_index("key")
    for c in ["primary"] + ["o_" + o for o in OPS]:
        if c in v4:
            feat[c] = v4[c].reindex(feat.index)
    feat["n_ops"] = feat[["o_" + o for o in OPS if "o_" + o in feat]].fillna(0).sum(axis=1)
    feat["skill0"] = feat.metadata_skill.fillna("[]").astype(str).str.strip("[]").str.split(",").str[0].str.strip('" ')
    feat["domain0"] = feat.metadata_domain.fillna("[]").astype(str).str.strip("[]").str.split(",").str[0].str.strip('" ')
    txt = feat.task.fillna("").astype(str) + " " + feat.problem.fillna("").astype(str)
    feat["tlen"] = txt.str.len()
    feat["has_fmt"] = txt.str.contains(r"json|csv|latex|table|format|bullet|markdown", case=False, regex=True)
    feat["txt"] = txt
    return piv, feat


def contrasts(piv, strategies):
    F = piv.reindex(columns=strategies)
    ok = F.notna().sum(axis=1) >= 2
    return F[ok].sub(F[ok].mean(axis=1), axis=0)


def v_matrix(C, lab, strategies):
    df = C.copy()
    df["t"] = lab.reindex(df.index).astype(str)
    out, cnt = {}, {}
    for s in strategies:
        g = df.dropna(subset=[s])
        out[s] = g.groupby("t")[s].mean()
        cnt[s] = g.groupby("t")[s].size()
    return pd.DataFrame(out), pd.DataFrame(cnt)


def interaction(V, N, min_n=20):
    Vm = V.where(N.fillna(0) >= min_n)
    sd = Vm.std(axis=0, ddof=1)
    return (float(np.nanmean(sd.values)) if np.isfinite(sd.values).any() else np.nan), sd


def perm_test(C, lab, strategies, obs, n_perm=300, min_n=20, seed=0):
    rng = np.random.default_rng(seed)
    labs = lab.reindex(C.index).astype(str).values
    null = []
    for _ in range(n_perm):
        V, N = v_matrix(C, pd.Series(rng.permutation(labs), index=C.index), strategies)
        i, _ = interaction(V, N, min_n)
        null.append(i)
    null = np.array(null)
    return float(np.nanmean(null >= obs)), float(np.nanmean(null)), float(np.nanstd(null))


def split_half(C, lab, strategies, min_n=12, seed=7):
    idx = np.array(C.index)
    h = np.array([int(hashlib.md5((str(s) + str(seed)).encode()).hexdigest(), 16) % 2 for s in idx])
    corrs = []
    for s in strategies:
        Va, Na = v_matrix(C[h == 0], lab.reindex(idx[h == 0]), [s])
        Vb, Nb = v_matrix(C[h == 1], lab.reindex(idx[h == 1]), [s])
        va = Va[s].where(Na[s].fillna(0) >= min_n)
        vb = Vb[s].where(Nb[s].fillna(0) >= min_n)
        j = va.dropna().index.intersection(vb.dropna().index)
        if len(j) >= 3:
            corrs.append(float(np.corrcoef(va[j].rank(), vb[j].rank())[0, 1]))
    return (float(np.nanmean(corrs)) if corrs else np.nan), len(corrs)


def reversal_stats(V, N, strategies, min_n=20):
    Vm = V.where(N.fillna(0) >= min_n)
    disc = []
    for a, b in itertools.combinations(strategies, 2):
        d = (Vm[a] - Vm[b]).dropna()
        if len(d) < 3:
            continue
        pos, neg = int((d > 0).sum()), int((d < 0).sum())
        disc.append((a, b, pos, neg, float(d.mean())))
    argmax = Vm.dropna(how="all").idxmax(axis=1).value_counts().to_dict()
    return len([x for x in disc if x[2] and x[3]]), argmax, disc


def evaluate(C, lab, min_n=20, n_perm=300):
    V, N = v_matrix(C, lab, FOCAL)
    obs, sd = interaction(V, N, min_n)
    p, m0, s0 = perm_test(C, lab, FOCAL, obs, n_perm=n_perm, min_n=min_n)
    rel, nrel = split_half(C, lab, FOCAL, min_n=max(12, min_n // 2))
    rev, argmax, pairs = reversal_stats(V, N, FOCAL, min_n)
    nmin = float(np.nanmin(N.where(N > 0).values)) if np.isfinite(N.values).any() else np.nan
    nmed = float(np.nanmedian(N.values))
    return dict(inter=obs, null=m0, sd_null=s0, p=p, rel=rel, n_rel_types=nrel, reversals=rev,
                n_types=V.shape[0], cells_min=nmin, cells_med=nmed,
                argmax=str([a for a, _ in sorted(argmax.items(), key=lambda kv: -kv[1])][:4])), V, N


def candidates(piv, feat):
    C = contrasts(piv, FOCAL)
    txt = feat.txt
    out = {}
    out["family (6)"] = feat.dataset_id
    out["v2 12 types"] = feat.thinking_type
    out["operation level (3)"] = feat.thinking_type.str[:2]
    out["target (4)"] = feat.target
    out["v4 primary action (~11)"] = feat["primary"].fillna("NA")
    out["category (8)"] = feat.category.fillna("NA")
    out["primary_tag (9)"] = feat.primary_tag.fillna("NA")
    out["primary_group (4)"] = feat.primary_group.fillna("NA")
    out["skill0 (7+other)"] = feat.skill0.where(feat.skill0.isin(feat.skill0.value_counts().head(7).index), "other")
    out["domain0 (6+other)"] = feat.domain0.where(feat.domain0.isin(feat.domain0.value_counts().head(6).index), "other")
    out["n_ops (3)"] = pd.cut(feat.n_ops, [-0.1, 1, 2, 20], labels=["1", "2", "3+"]).astype(str)
    out["task length tercile (3)"] = pd.qcut(feat.tlen, 3, labels=["short", "mid", "long"]).astype(str)
    out["needs format (2)"] = feat.has_fmt.map({True: "fmt", False: "free"}).astype(str)
    for op in OPS:                                     # single content-operation contrast
        c = "o_" + op
        if c in feat:
            out["%s vs rest" % op] = feat[c].fillna(0).map({1: "yes", 0: "no"}).astype(str)
    out["family x target"] = feat.dataset_id.astype(str) + "|" + feat.target.astype(str)
    out["family x level"] = feat.dataset_id.astype(str) + "|" + feat.thinking_type.str[:2].astype(str)
    out["family x v4primary"] = feat.dataset_id.astype(str) + "|" + feat["primary"].fillna("NA").astype(str)
    out["v2 12 types x has_fmt"] = feat.thinking_type.astype(str) + "|" + feat.has_fmt.map({True: "fmt", False: "free"}).astype(str)
    return C, out


def text_clusters(feat, ks=(4, 6, 8, 12)):
    """data-driven, content-only clustering of the prompts (TF-IDF + k-means, no outcome used)."""
    try:
        from sklearn.cluster import KMeans
        from sklearn.feature_extraction.text import TfidfVectorizer
    except Exception as e:                                          # noqa: BLE001
        print("sklearn unavailable:", e)
        return {}
    X = TfidfVectorizer(max_features=4000, stop_words="english", ngram_range=(1, 2)).fit_transform(
        feat.txt.fillna("").astype(str))
    res = {}
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
        res["kmeans text (k=%d)" % k] = pd.Series(km.labels_.astype(str), index=feat.index)
    return res


def main():
    np.seterr(all="ignore")
    import warnings
    warnings.filterwarnings("ignore")
    piv, feat = load()
    C, cands = candidates(piv, feat)
    cands.update(text_clusters(feat))
    print("tasks in the paired sample: %d (of %d)" % (len(C), len(piv)))
    rows = []
    for name, lab in cands.items():
        lab = pd.Series(lab, index=feat.index)
        m, V, N = evaluate(C, lab)
        m["partition"] = name
        rows.append(m)
    R = pd.DataFrame(rows)
    R["score"] = R.inter * R.rel.clip(lower=0)
    R = R.sort_values("score", ascending=False)
    cols = ["partition", "n_types", "inter", "null", "sd_null", "p", "rel", "reversals", "argmax",
            "cells_min", "cells_med", "score"]
    pd.set_option("display.width", 260)
    print(R[cols].round(2).to_string(index=False))
    R.to_csv(os.path.join(HERE, "out", "screen2_partitions.csv"), index=False)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    main()
