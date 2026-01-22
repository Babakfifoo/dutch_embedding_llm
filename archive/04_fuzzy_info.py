# %%
from rapidfuzz import fuzz
import json
import re
from pathlib import Path
from itertools import chain
import pandas as pd
from tqdm import tqdm
from config import FUZZY_TERMS, FUZZY_THRESHOLD

search_terms = list(FUZZY_TERMS.keys())


regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel|exploitatie|u i t v o e r b a a r h e i d)"
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


with open(
    "../data/plan_documents/texts/feasability/html_feasability.json",
    "r",
    encoding="utf-8",
) as f:
    data = json.loads(f.read().encode("utf-8").decode("latin-1"))

cleaned_sections = []
for plan in data:
    texts = list(chain(*plan["texts"]["data"]))
    feas_n_hashtag_n = [contains_feasability(x) * x.count("#") for x in texts]
    heading_hash_count = [s for s in feas_n_hashtag_n if s != 0]
    if len(heading_hash_count) != 0:
        feasability_heading_count = min(heading_hash_count)
        heading_idx = [
            i for i, s in enumerate(feas_n_hashtag_n) if s == feasability_heading_count
        ]

    elif any([x for x in texts if "**" in x]):
        feas_n_hashtag_n = [contains_feasability(x) * x.count("**") for x in texts]
        feasability_heading_count = min([s for s in feas_n_hashtag_n if s != 0])
        heading_idx = [
            i for i, s in enumerate(feas_n_hashtag_n) if s == feasability_heading_count
        ]

    if len(heading_idx) > 1:
        texts_correct = texts[: heading_idx[1]]
    else:
        texts_correct = texts
    cleaned_sections.append({"IMRO": plan["IMRO"], "texts": texts_correct})

results_html = []

for plan in tqdm(cleaned_sections):
    entry = {"IMRO": plan["IMRO"]}
    matched_texts = []
    for item in plan["texts"]:
        for k in search_terms:
            score = fuzz.partial_ratio(item, k)
            if score > FUZZY_THRESHOLD:
                matched_texts.append(item)
                break
    if len(matched_texts) == 0:
        continue

    entry["selections"] = pd.DataFrame(matched_texts).drop_duplicates().to_dict()[0]

    results_html.append(entry)

with open("../data/plan_documents/fuzzy/html_fuzzy.json", mode="w") as f:
    f.write(json.dumps(results_html, indent=4))

# %%

pdfs = list(Path("../data/plan_documents/md").iterdir())
cleaned_sections = []
for fp in tqdm(pdfs):
    with open(fp, "r", encoding="utf-8") as f:
        texts = f.read().split("\n")
        texts = [s.strip() for s in texts if s.strip() != ""]
    feas_n_hashtag_n = [contains_feasability(x) * x.count("#") for x in texts]
    heading_hash_count = [s for s in feas_n_hashtag_n if s != 0]
    if len(heading_hash_count) != 0:
        feasability_heading_count = min(heading_hash_count)
        heading_idx = [
            i for i, s in enumerate(feas_n_hashtag_n) if s == feasability_heading_count
        ]

    elif any([x for x in texts if "**" in x]):
        feas_n_hashtag_n = [contains_feasability(x) * x.count("**") for x in texts]
        if len(heading_hash_count) == 0:
            continue
        feasability_heading_count = min([s for s in feas_n_hashtag_n if s != 0])
        heading_idx = [
            i for i, s in enumerate(feas_n_hashtag_n) if s == feasability_heading_count
        ]
    texts_correct = texts[heading_idx[0] :]
    if len(heading_idx) > 1:
        texts_correct = texts[: heading_idx[1]]

    cleaned_sections.append({"IMRO": fp.stem, "texts": texts_correct})

results_pdf = []
for plan in tqdm(cleaned_sections):
    entry = {"IMRO": plan["IMRO"]}
    matched_texts = []
    for item in plan["texts"]:
        for k in search_terms:
            score = fuzz.partial_ratio(item, k)
            if score > FUZZY_THRESHOLD:
                matched_texts.append(item)
                break
    if len(matched_texts) == 0:
        continue

    entry["selections"] = pd.DataFrame(matched_texts).drop_duplicates().to_dict()[0]

    results_pdf.append(entry)

with open("../data/plan_documents/fuzzy/pdf_fuzzy.json", mode="w") as f:
    f.write(json.dumps(results_pdf, indent=4))

# %%
