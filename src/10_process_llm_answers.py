# %%
import json
import pandas as pd
# %%
with open("../data/plan_documents/manual_answers/html_manual - 20250226.json", "r") as f:

    html_manual = pd.DataFrame(json.loads(f.read())).T
# %%
html_manual
# %%
with open("../data/plan_documents/answered/html_agreement.json", "r") as f:
    agreement_answer = json.loads(s=f.read())

cleaned_answers = []
for item in agreement_answer:
    try:
        item["ans"] = json.loads(item["ans"])
        cleaned_answers.append(item)
    except:
        pass
col_names = {
    1: "Anterior agreement",
    2: "plan damage agreement",
    3: "purchase agreement/contract",
    4: "operating agreement",
    5: "cooperation agreement",
    6: "sales agreement",
    7: "Realisation agreement",
    8: "Land Exploitation agreement",
}
agreement_answers = (
    pd.DataFrame(cleaned_answers)
    .explode("ans")
    .assign(value=True)
    .pivot_table(index="IMRO", columns="ans", values="value", aggfunc="first")
    .fillna(False)
    .rename(columns=col_names)
    )
agreement_answers = agreement_answers[~agreement_answers[9]]
agreement_answers = agreement_answers.drop(columns=[9])
# %%
agreement_answers.sum(axis=1).value_counts()
# %%
agreement_answers.sum()
# %%
