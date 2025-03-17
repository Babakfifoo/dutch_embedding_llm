# %%
from ollama import embed
import json
import numpy as np
import seaborn as sns
from tqdm import tqdm
MODEL = "llama3.2:3b-instruct-q5_K_M"
# %%

def embed_context(entry):
    return np.array(embed(MODEL,entry.get("context")).get("embeddings")[0])

# ANTERIOR AGREEMENT:
compare_sents = [
    "anterior agreement is layed down",
    "anterior agreement is used",
    "anterior agreement is signed",
    "private law agreement is layed down",
    "private law agreement is used",
    "private law agreement is signed",
]
compare_embeddings = np.array([embed(MODEL, s).get("embeddings")[0] for s in compare_sents])
with open("../data/plan_documents/answered/anterior agreement.json") as f:
    data = json.loads(f.read())
# %%
result = []
for item in tqdm(data):
    item_embed = embed_context(item)
    item["min_dist"] = min(compare_embeddings @ item_embed)
    result.append(item)
# %%
import pandas as pd
result_df = pd.DataFrame(result).drop(columns="context")

result_df["answer"] = result_df["answer"].apply(lambda x: json.loads(x).get("answer")).astype(int)
# %%

sns.scatterplot(data = result_df, x="min_dist", y="answer")
# %%
sns.kdeplot(data=result_df, x="min_dist", hue="answer")
# %%
