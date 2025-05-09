# %%
import json
import pandas as pd


def bool_cleaner(s: str) -> bool:
    # validating the answer
    if not isinstance(s, str):
        return False
    if "true" in s.lower():
        return True
    return False

# %%
with open(f"../data/new/LLM_answers/agreement.json", "r") as f:
    answers = json.loads(f.read())
# %%
data = pd.json_normalize(answers).drop(columns=["context"])
# %%
data["answer"] = data["answer"].apply(bool_cleaner)
# %%
