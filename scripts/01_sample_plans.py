# %%
from pathlib import Path
import pandas as pd
import shutil

# %%
toelichting_files = [p for p in Path("../data/plan_documents").iterdir() if p.suffix in [".pdf", ".html"]]
# %%
IMROs = [s.stem for s in toelichting_files]
# %%
for fp in toelichting_files:
    if fp.suffix == '.pdf':
        shutil.move(src=fp, dst="../data/plan_documents/pdf/")
    if fp.suffix == '.html':
        shutil.move(src=fp, dst="../data/plan_documents/html/")
# %%
