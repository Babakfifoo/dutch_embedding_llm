# %%
import json
import pandas as pd


# %%
with open(f"../data/new/LLM_answers/agreement.json", "r") as f:
    answers = json.loads(f.read())
# %%
data = pd.json_normalize(answers).drop(columns=["context"])
# %%
data["answer"] = data["answer"].apply(bool_cleaner)
# %%
data.answer.value_counts()
# %%
