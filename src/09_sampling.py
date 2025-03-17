# %%
import json
import pandas as pd
from pathlib import Path

all_plans = pd.DataFrame(
    {"IMRO": [str(f.stem) for f in list(Path("../data/plan_documents/md").iterdir())]}
)
all_plans["gem"] = all_plans.IMRO.str.split(".").str[2]
# %%
sample = pd.concat([all_plans.groupby("gem").sample(1),
all_plans.groupby("gem").sample(1)], ignore_index=True).drop_duplicates()["IMRO"].to_list()
# %%
with open("../data/plan_documents/proper_sample.json", "w") as f:
    f.write(json.dumps(sample))
# %%
