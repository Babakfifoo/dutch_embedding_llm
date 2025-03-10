# %%
from pathlib import Path
import pandas as pd
import shutil

# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
# %%
IMROs = [s.stem for s in toelichting_files]
# %%
plan_df = pd.DataFrame({"IMRO": IMROs, "paths": toelichting_files})
# %%
plan_df["municipality"] = plan_df.IMRO.str.split(".").str[2]
plan_df["extension"] = plan_df["paths"].apply(lambda s: s.suffixes[-1])
# %%
(
    plan_df.query("extension == '.pdf'")
    .groupby("municipality")
    .first()
    .paths.apply(lambda x: shutil.copy(src=x, dst="../data/sample plans/pdf/"))
)
(
    plan_df.query("extension == '.html'")
    .groupby("municipality")
    .first()
    .paths.apply(lambda x: shutil.copy(src=x, dst="../data/sample plans/html/"))
)

# %%
