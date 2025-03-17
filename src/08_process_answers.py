# %%
import json
import pandas as pd
# %%


def bool_cleaner(s):
    if "true" in s.lower():
        return True
    False


# %%
with open(
    "../data/plan_documents/manual_answers/html_manual - 20250226.json", "r"
) as f:
    manual_html = json.loads(f.read())
# %%
manual_df = pd.DataFrame(manual_html).T.rename(
    columns={
        "Anterior Agreement": "anterior_manual",
        "Operating Agreement": "operating_manual",
    }
)

with open("../data/plan_documents/translated_selected_sents.json", "r") as f:
    all_plans = json.loads(f.read())
    plan_df = pd.DataFrame(
        {"IMRO": [x.get("IMRO") for x in all_plans if len(x.get("id")) != 0]}
    )

with open("../data/plan_documents/answered/anterior agreement.json", "r") as f:
    data = json.loads(f.read())
    anterior = pd.DataFrame(data)
    anterior["anterior"] = anterior["answer"].apply(bool_cleaner)

with open("../data/plan_documents/answered/operating agreement.json", "r") as f:
    data = json.loads(f.read())
    operating = pd.DataFrame(data)
    operating["operating"] = operating["answer"].apply(bool_cleaner)

with open("../data/plan_documents/answered/plan damage agreement.json", "r") as f:
    data = json.loads(f.read())
    plan_damage = pd.DataFrame(data)
    plan_damage["plan_damage"] = plan_damage["answer"].apply(bool_cleaner)

with open("../data/plan_documents/answered/realisation agreement.json", "r") as f:
    data = json.loads(f.read())
    realisation = pd.DataFrame(data)
    realisation["realisation"] = realisation["answer"].apply(bool_cleaner)

with open("../data/plan_documents/answered/cooperation agreement.json", "r") as f:
    data = json.loads(f.read())
    cooperation = pd.DataFrame(data)
    cooperation["cooperation"] = cooperation["answer"].apply(bool_cleaner)

with open("../data/plan_documents/answered/purchase agreement.json", "r") as f:
    data = json.loads(f.read())
    purchase = pd.DataFrame(data)
    purchase["purchase"] = purchase["answer"].apply(bool_cleaner)

plan_df = (
    plan_df.merge(anterior[["IMRO", "anterior"]], on="IMRO", how="left")
    .merge(operating[["IMRO", "operating"]], on="IMRO", how="left")
    .merge(plan_damage[["IMRO", "plan_damage"]], on="IMRO", how="left")
    .merge(realisation[["IMRO", "realisation"]], on="IMRO", how="left")
    .merge(cooperation[["IMRO", "cooperation"]], on="IMRO", how="left")
    .merge(purchase[["IMRO", "purchase"]], on="IMRO", how="left")
    .set_index("IMRO")
    .fillna(2)
    .astype(int)
)

# %%
anterior_check = manual_df[["anterior_manual"]].join(plan_df).query("anterior != 2")
anterior_check = anterior_check.loc[
    anterior_check.anterior_manual, ["anterior_manual", "anterior"]
]
anterior_check.anterior.value_counts()
# %%
operating_check = manual_df[["operating_manual"]].join(plan_df, how="inner").query("operating != 2").dropna()
operating_check = operating_check.loc[
    operating_check.operating_manual, ["operating_manual", "operating"]
]
operating_check.operating_manual.value_counts()
# %%
