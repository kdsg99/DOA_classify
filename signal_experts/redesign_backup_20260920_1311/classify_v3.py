# -*- coding: utf-8 -*-
"""
Label every (dataset, task) with a v3 taxonomy scheme, producing a row-level file
identical in shape to all_tasks_v2.csv so the two schemes can be compared directly.

usage:  python classify_v3.py s1
        python classify_v3.py s2
"""
import os, sys, json, time, hashlib, re
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm

HERE = os.path.dirname(os.path.abspath(__file__))
SE = os.path.dirname(HERE)
RAW = os.path.join(SE, "raw_data")
sys.path.insert(0, HERE)
from taxonomy_v3 import SCHEMES

client = OpenAI(api_key="sk-578ed37fee7a4bbbb8770dd3f94c44f5",
                base_url="https://api.deepseek.com")
MODEL_NAME = "deepseek-v4-flash"


def build_user_prompt(row):
    return f"""【task】
{str(row.get('task',''))[:1600]}

【problem】
{str(row.get('problem',''))[:1600]}

【instruction】
{str(row.get('instruction',''))[:800]}

【来源/元数据】 dataset={row.get('dataset_id','')} | category={row.get('category','')} | group={row.get('primary_group','')} | domain={row.get('metadata_domain','')} | subject={row.get('subject','')} | level={row.get('level_label','')}
"""


def main(scheme):
    sc = SCHEMES[scheme]
    ids = sc["ids"]; prompt = sc["prompt"]
    cache_dir = os.path.join(HERE, f"cache_v3_{scheme}")
    os.makedirs(cache_dir, exist_ok=True)
    out_csv = os.path.join(HERE, f"all_tasks_v3_{scheme}.csv")

    def normalize(t):
        t = (t or "").strip()
        for tid in ids:
            if tid.lower() == t.lower():
                return tid
        for tid in ids:
            if tid.lower() in t.lower():
                return tid
        for tid, nm in sc["names"].items():
            if nm in t:
                return tid
        return None

    def classify_one(row):
        up = build_user_prompt(row)
        key = hashlib.md5((sc["tag"] + "||" + prompt + up).encode("utf-8")).hexdigest()
        p = os.path.join(cache_dir, f"{key}.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)["type"]
        for attempt in range(5):
            try:
                resp = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": up}],
                    temperature=0.0, response_format={"type": "json_object"})
                raw = resp.choices[0].message.content
                try:
                    parsed = json.loads(raw)
                except Exception:
                    mm = re.search(r"\{.*\}", raw, re.S)
                    parsed = json.loads(mm.group(0)) if mm else {}
                tid = normalize(parsed.get("type", ""))
                if not tid:
                    raise ValueError(f"unparsable: {parsed}")
                with open(p, "w", encoding="utf-8") as f:
                    json.dump({"type": tid, "reason": parsed.get("reason", ""),
                               "confidence": parsed.get("confidence")}, f, ensure_ascii=False)
                return tid
            except Exception as e:
                print(f"[retry {attempt+1}] {type(e).__name__}: {str(e)[:120]}")
                time.sleep(1.5 * (attempt + 1))
        return ids[-1]

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
    ukey = [hashlib.md5(p.encode("utf-8")).hexdigest() for p in prompts]
    uniq = uniq.assign(_k=ukey)
    base = uniq.drop_duplicates("_k").reset_index(drop=True)
    print(f"unique tasks={len(uniq)}  unique prompts={len(base)}  -> {scheme}")

    records = base.to_dict("records")
    results = [None] * len(records)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("V3_WORKERS", "10"))) as ex:
        fut = {ex.submit(classify_one, r): i for i, r in enumerate(records)}
        for f in tqdm(as_completed(fut), total=len(fut), desc=f"v3-{scheme}"):
            results[fut[f]] = f.result()
    base["v3_type"] = results

    m = dict(zip(base["_k"], results))
    kmap = dict(zip(zip(uniq.dataset_id, uniq.task_id), ukey))
    df["type"] = [m.get(kmap.get((ds, t))) for ds, t in zip(df.dataset_id, df.task_id)]
    df["type_name"] = df["type"].map(sc["names"])
    df.to_csv(out_csv, index=False)
    print("saved ->", out_csv)
    print(df["type"].value_counts().to_string())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "s1")
