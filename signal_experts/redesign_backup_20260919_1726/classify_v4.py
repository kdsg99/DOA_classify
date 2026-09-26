# -*- coding: utf-8 -*-
"""给每个 (dataset, task) 打上 v4「所需思维动作」标签（多标签 + primary），输出 all_tasks_v4.csv"""
import os, sys, json, time, hashlib, re
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from tqdm import tqdm
from openai import OpenAI

HERE = os.path.dirname(os.path.abspath(__file__))
SE = os.path.dirname(HERE)
RAW = os.path.join(SE, "raw_data")
sys.path.insert(0, HERE)
from taxonomy_v4 import IDS, NAMES, PROMPT

client = OpenAI(api_key="sk-578ed37fee7a4bbbb8770dd3f94c44f5", base_url="https://api.deepseek.com")
MODEL_NAME = "deepseek-v4-flash"

def build_user_prompt(row):
    return f"""【task】
{str(row.get('task',''))[:1600]}

【problem】
{str(row.get('problem',''))[:1600]}

【instruction】
{str(row.get('instruction',''))[:800]}
"""

def norm(t):
    t = (t or "").strip()
    for i in IDS:
        if i.lower() == t.lower():
            return i
    for i in IDS:
        if i.lower() in t.lower() or NAMES[i] in t:
            return i
    return None

def main():
    cache = os.path.join(HERE, "cache_v4")
    os.makedirs(cache, exist_ok=True)
    out_csv = os.path.join(HERE, "all_tasks_v4.csv")

    def classify_one(row):
        up = build_user_prompt(row)
        key = hashlib.md5((PROMPT + up).encode("utf-8")).hexdigest()
        p = os.path.join(cache, f"{key}.json")
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))
        for a in range(5):
            try:
                r = client.chat.completions.create(model=MODEL_NAME, temperature=0.0,
                        messages=[{"role": "system", "content": PROMPT},
                                  {"role": "user", "content": up}],
                        response_format={"type": "json_object"})
                raw = r.choices[0].message.content
                try:
                    j = json.loads(raw)
                except Exception:
                    m = re.search(r"\{.*\}", raw, re.S)
                    j = json.loads(m.group(0)) if m else {}
                ops = [x for x in (j.get("ops") or []) if norm(x)]
                ops = [norm(x) for x in ops]
                pr = norm(j.get("primary", ""))
                if pr and pr not in ops:
                    ops = [pr] + ops
                if not ops:
                    raise ValueError("no ops")
                pr = pr or ops[0]
                rec = dict(primary=pr, ops=ops[:4], why=str(j.get("why", ""))[:400])
                json.dump(rec, open(p, "w", encoding="utf-8"), ensure_ascii=False)
                return rec
            except Exception as e:
                print(f"[retry {a+1}] {type(e).__name__}: {str(e)[:120]}")
                time.sleep(1.5 * (a + 1))
        return dict(primary=IDS[0], ops=[IDS[0]], why="")

    frames = []
    for s in ["pressure", "encourage", "critical", "misleading", "heuristic"]:
        for st in ["high", "low"]:
            d = pd.read_csv(os.path.join(RAW, f"{s}_{st}.csv"))
            d["strategy"] = s.upper(); d["set"] = st
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    print("rows:", len(df))

    uniq = df.drop_duplicates(["dataset_id", "task_id"]).reset_index(drop=True)
    prompts = [build_user_prompt(r) for r in uniq.to_dict("records")]
    uniq = uniq.assign(_k=[hashlib.md5(p.encode()).hexdigest() for p in prompts])
    base = uniq.drop_duplicates("_k").reset_index(drop=True)
    print(f"unique tasks={len(uniq)}  unique prompts={len(base)}")

    recs = base.to_dict("records")
    res = [None] * len(recs)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("V4_WORKERS", "12"))) as ex:
        fut = {ex.submit(classify_one, r): i for i, r in enumerate(recs)}
        for f in tqdm(as_completed(fut), total=len(fut), desc="v4"):
            res[fut[f]] = f.result()

    base["primary"] = [r["primary"] for r in res]
    base["ops_json"] = [json.dumps(r["ops"], ensure_ascii=False) for r in res]
    base["why"] = [r["why"] for r in res]
    m = dict(zip(base["_k"], res))
    kmap = dict(zip(zip(uniq.dataset_id, uniq.task_id), uniq["_k"]))
    got = [m.get(kmap.get((ds, t))) for ds, t in zip(df.dataset_id, df.task_id)]
    df["primary"] = [g["primary"] if g else None for g in got]
    df["ops_json"] = [json.dumps(g["ops"], ensure_ascii=False) if g else None for g in got]
    for i in IDS:
        df["o_" + i] = [int(i in g["ops"]) if g else 0 for g in got]
    df.to_csv(out_csv, index=False)
    print("saved ->", out_csv)
    print(df["primary"].value_counts().to_string())
    print("\n单动作出现次数（多标签）:")
    print(df.drop_duplicates(["dataset_id", "task_id"])[["o_" + i for i in IDS]].sum().to_string())

if __name__ == "__main__":
    main()
