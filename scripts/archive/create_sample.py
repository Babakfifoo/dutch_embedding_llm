# %%
import pandas as pd
from pathlib import Path
import shutil

# %%
paths = [fp for fp in Path("../data/plan_documents/md").iterdir()]
stems = [x.stem for x in paths]
paths_df = pd.DataFrame({"fp": paths, "stem": stems})

paths_df["GM"] = paths_df.stem.str.split(".").str[2]
paths_df["GM_n"] = paths_df.groupby("GM")["stem"].transform("count")

# Keeping municipalities with at least 2 plans
paths_df = paths_df[paths_df["GM_n"] > 1].reset_index(drop=True)

sample = paths_df.groupby("GM").sample(2, random_state=2025)["fp"].to_list()

for fp in sample:
    shutil.copy(src=fp, dst="../data/sample/md/" + fp.name)

# %%
