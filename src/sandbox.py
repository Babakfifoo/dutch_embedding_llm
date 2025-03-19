# %%

import json
import pandas as pd
# %%
with open("../data/plan_documents/manual_answers/html_manual - 20250226.json") as f:
    manual_data = json.loads(f.read())
# %%
df = pd.DataFrame(manual_data).T
# %%
new_dict = df.loc[df["Anterior Agreement"], "Anterior Agreement"].to_dict()
# %%
df.columns
# %%
df[df['Operating Agreement'] == True]
# %%
