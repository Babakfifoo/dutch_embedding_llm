# %%

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


def bool_cleaner_string(s):
    if "true" in s:
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
        ans["answer"] = ans["answer"].apply(bool_cleaner_string)

    df = res.merge(ans, on="IMRO", how="outer")
    return df


def clean_results(
    name: str, res_fp: str, ins_fp: str, ans_fp: str, output: str
) -> None:
    with open(file=ins_fp) as f:
        ins_data = json.loads(f.read())
        ins_data = pd.DataFrame({f"{name}_inspection": ins_data})

    with open(file=ans_fp) as f:
        ans_data = json.loads(f.read())
        ans_data = pd.DataFrame(ans_data).set_index("IMRO")
        ans_data[f"{name}_llm"] = ans_data["answer"].apply(bool_cleaner_string)
        ans_data = ans_data[[f"{name}_llm"]]

    with open(file=res_fp) as f:
        res_data = json.loads(f.read())
        res_data = pd.DataFrame({f"{name}_result": res_data})

    df = ans_data.join(res_data, how="left").join(ins_data, how="left")
    df.to_parquet(output)


# %%
clean_results(
    name="anterior_agreement",
    res_fp="../data/plan_documents/results/inspecting_false/result_anterior_20250317.json",
    ans_fp="../data/plan_documents/answered/anterior agreement.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_anterior_20250317.json",
    output="../data/final/01_Anterior_agreement.parquet",
)

clean_results(
    name="land_allocation",
    res_fp="../data/plan_documents/results/inspecting_false/result_allocation_20250318.json",
    ans_fp="../data/plan_documents/answered/Land allocation.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_land_allocation_20250318.json",
    output="../data/final/02_Land_allocation.parquet",
)

clean_results(
    name="municipality_land",
    res_fp="../data/plan_documents/results/inspecting_false/result_municipality_land_20250318.json",
    ans_fp="../data/plan_documents/answered/municipality ownership.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_municipality_20250318.json",
    output="../data/final/03_municipality_land.parquet",
)

clean_results(
    name="exploitation",
    res_fp="../data/plan_documents/results/inspecting_false/result_operating_20250318.json",
    ans_fp="../data/plan_documents/answered/operating agreement.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_operating_20250318.json",
    output="../data/final/04_exploitation_agreement.parquet",
)

clean_results(
    name="plan_damage",
    res_fp="../data/plan_documents/results/inspecting_false/result_plan_damage_20250318.json",
    ans_fp="../data/plan_documents/answered/plan damage agreement.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_plan_damage_20250318.json",
    output="../data/final/05_plan_damage_agreement.parquet",
)

clean_results(
    name="cooperation",
    res_fp="../data/plan_documents/results/inspecting_false/result_cooperation_20250318.json",
    ans_fp="../data/plan_documents/answered/cooperation agreement.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_coop_20250318.json",
    output="../data/final/06_cooperation_agreement.parquet",
)

clean_results(
    name="initiator_land",
    res_fp="../data/plan_documents/results/inspecting_false/result_developer_land_20250320.json",
    ans_fp="../data/plan_documents/answered/private ownership.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_private_ownership_20250320.json",
    output="../data/final/07_initiator_ownership.parquet",
)

clean_results(
    name="future_agreement",
    res_fp="../data/plan_documents/results/inspecting_false/result_agreement_timing_20250320.json",
    ans_fp="../data/plan_documents/answered/will agree.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_agreement_timing_20250320.json",
    output="../data/final/08_future_agreement.parquet",
)

clean_results(
    name="agreement",
    res_fp="../data/plan_documents/results/inspecting_false/result_agreement_20250320.json",
    ans_fp="../data/plan_documents/answered/agreement.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_agreement_20250320.json",
    output="../data/final/09_agreement.parquet",
)

clean_results(
    name="private_expences",
    res_fp="../data/plan_documents/results/inspecting_false/result_private_expences_20250321.json",
    ans_fp="../data/plan_documents/answered/private expenses.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_private_expences_20250321.json",
    output="../data/final/10_private_expences.parquet",
)

clean_results(
    name="municipality_cost",
    res_fp="../data/plan_documents/results/inspecting_false/result_municipality_land_20250318.json",
    ans_fp="../data/plan_documents/answered/municipality_costs.json",
    ins_fp="../data/plan_documents/results/manual_inspection/inspection_municipality_costs_20250326.json",
    output="../data/final/12_municipality_costs.parquet",
)


all_plans = pd.DataFrame(
    {"IMRO": [str(f.stem) for f in list(Path("../data/plan_documents/md/").iterdir())]}
)
all_plans.to_parquet("../data/final/00_all_plans.parquet")
# %%
with open("../data/plan_documents/manual_answers/Problematics_20250325.json") as f:
    problematics = json.loads(f.read())
    problematics = pd.DataFrame(problematics).T
    problematics = problematics[~problematics.Invalid.astype(bool)]
    cols = {
        'Land allocation/sale': 'land_allocation_result',
        'Agreement': 'agreement_result',
        'Anterior Agreement': 'anterior_agreement_result',
        'Operating Agreement': 'exploitation_result',
        'Plan Damage Agreement': 'plan_damage_result',
        'Cooperation Agreement/PPS': 'cooperation_result',
        'Land owned by applicant': 'initiator_land_result',
        'Future Agreement': 'future_agreement_result',
        "Invalid": "Invalid"
    }
    problematics = problematics.rename(columns=cols)[list(cols.values())]

    problematics.to_parquet("../data/final/90_problematics.parquet")

# %%
