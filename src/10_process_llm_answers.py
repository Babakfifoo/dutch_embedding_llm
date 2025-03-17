import json
import pandas as pd
from pathlib import Path


def bool_cleaner(s: str) -> bool:
    # validating the answer
    if not isinstance(s, str):
        return False
    if "true" in s.lower():
        return True
    return False


def get_answers(res_fp, ans_fp):
    with open(file=res_fp) as f:
        res = json.loads(f.read())
        res = (
            pd.json_normalize(res)
            .T.reset_index()
            .rename(columns={"index": "IMRO", 0: "answer_clean"})
        )

    with open(file=ans_fp) as f:
        ans = json.loads(f.read())
        ans = pd.json_normalize(ans)[["IMRO", "answer"]]
        ans["answer"] = ans["answer"].apply(bool_cleaner)

    df = res.merge(ans, on="IMRO", how="outer")
    return df


# %%

res_fp: str = "../data/plan_documents/results/result_allocation - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/Land allocation.json"

land_alloc = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_anterior - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/anterior agreement.json"

anterior = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_building_plan - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/building Plan.json"

building_plan = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_cooperation - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/cooperation agreement.json"

coop = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_land_exp_scheme - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/land exploitation scheme.json"

land_exp_scheme = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_municipality_land - 20250312.json"
ans_fp: str = "../data/plan_documents/answered/municipality ownership.json"

municipality_land = get_answers(res_fp=res_fp, ans_fp=ans_fp)


res_fp: str = "../data/plan_documents/results/result_operating - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/operating agreement.json"

operating = get_answers(res_fp=res_fp, ans_fp=ans_fp)


res_fp: str = "../data/plan_documents/results/result_plan_damage - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/plan damage agreement.json"

damage = get_answers(res_fp=res_fp, ans_fp=ans_fp)


res_fp: str = "../data/plan_documents/results/result_developer_land - 20250312.json"
ans_fp: str = "../data/plan_documents/answered/private ownership.json"

dev_land = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_purchase - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/purchase agreement.json"

purchase = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_realisation - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/realisation agreement.json"

realisation = get_answers(res_fp=res_fp, ans_fp=ans_fp)

res_fp: str = "../data/plan_documents/results/result_space_for_space - 20250311.json"
ans_fp: str = "../data/plan_documents/answered/space for space.json"

space_for_space = get_answers(res_fp=res_fp, ans_fp=ans_fp)
# %%

with open("../data/plan_documents/manual_answers/html_manual - 20250226.json") as f:
    manual = json.loads(f.read())
    manual = (
        pd.DataFrame(manual)
        .T.reset_index()
        .rename(
            columns={
                "index": "IMRO",
                "Land allocation":"alloc_man"
            }
        )
    ).reset_index(drop=True)
    
    manual = manual[manual["Invalid"] == False]
    
# %%

all_plans = pd.DataFrame(
    {"IMRO": [str(f.stem) for f in list(Path("../data/plan_documents/md/").iterdir())]}
)
# %%

land_allocation_df = (
    all_plans
    .merge(land_alloc, on="IMRO", how="left")
    .merge(manual[["IMRO", "alloc_man"]], on="IMRO", how="left")
    )

test = land_allocation_df.dropna()

test[test.answer != test.alloc_man][["IMRO"]]

# %%
