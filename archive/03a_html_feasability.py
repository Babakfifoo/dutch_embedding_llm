# %%
import json
import pandas as pd
from pathlib import Path
import re
from markdownify import markdownify as md
from tqdm import tqdm

regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel|exploitatie)"
)


def contains_feasability(s) -> bool:
    return bool(regex_feasability.search(string=s.lower()))


def is_heading(s):
    return (
        (s.strip().lower()[0] == "#")
        or (s.strip().lower()[:2] == "**")
        and (s.strip().lower()[-2:] == "**")
    )


# %%
with open("../data/plan_documents/texts/html_texts.json", "r") as f:
    data = json.loads(f.read())

toelichting_files = list(Path("../data/plan_documents/html").iterdir())
entries = []
for fp in tqdm(iterable=toelichting_files):
    IMRO = fp.stem
    with open(fp, "r", encoding="latin-1") as f:
        html_content = f.read()

    md_text = md(html=html_content, strip=["a"]).split("\n")
    md_text = [x for x in md_text if (len(x) > 5)]

    df = pd.DataFrame({"text": md_text})
    df["text"] = df["text"].str.strip()
    df = df[df.text.str.len() > 5].reset_index(drop=True)
    df["feasability"] = df["text"].apply(contains_feasability)
    df["is_heading"] = df["text"].apply(is_heading)
    df["feasability_heading"] = (
        (df["is_heading"] & df["feasability"]).astype(int).cumsum()
    )
    cut_index = df.query("feasability_heading != 0").index.min()
    result = df.loc[cut_index:, ["text"]].reset_index(drop=True)
    if len(result) == 0:
        continue
    entry = {"IMRO": IMRO, "texts": result.to_dict(orient="split")}
    entries.append(entry)

with open("../data/plan_documents/texts/feasability/html_feasability.json", "w") as f:
    f.write(json.dumps(entries))
# %%