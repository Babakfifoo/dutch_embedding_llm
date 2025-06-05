# %%
from pathlib import Path
from rapidfuzz import fuzz
from tqdm import tqdm
import json
import re


def remove_span(s):
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string


ECONOMIC_FEAS_STR = [
    "financieel",
    "financiële",
    "economische",
    "f i n a n c i e e l",
    "e c o n o m i s c h e",
]

FEAS_STR = ["uitvoerbaarheid", "haalbaarheid", "H a a l b a a r h e i d"]
EX_STR = ["maatschappelijke"]


def find_topic(s, q, threshold=90) -> bool:
    # This ignores the sentences that contain examples to prevent bias.
    for query in q:
        score = fuzz.partial_ratio(s1=s, s2=query)
        if score >= threshold:
            return True
    return False


# %%
mds = list(Path("../data/plan_documents/md").iterdir())

problematics = []
result = {}
for fp in tqdm(mds):
    with open(fp, "r", encoding="utf-8") as f:
        text = [
            remove_span(x).strip()
            for x in f.read().split("\n")
            if (x.strip() != "") and ("|" not in x.strip())
        ]
        text = [s for s in text if len(s) != 0]
    headings = [
        (i, h)
        for i, h in enumerate(iterable=text)
        if find_topic(s=h.lower(), q=["hoofdstuk"], threshold=195)  # finding chapters
    ]

    # If headings do not have # in them, then the Chapter term is used
    if len(headings) == 0:
        headings = [(i, h) for i, h in enumerate(iterable=text) if (h[0] == "#")]
    feas_h = [
        (j, i, h)
        for j, (i, h) in enumerate(headings)
        if (
            find_topic(s=h.lower(), q=ECONOMIC_FEAS_STR, threshold=90)
            or find_topic(s=h.lower(), q=FEAS_STR, threshold=90)
        )
        and (
            not find_topic(s=h.lower(), q=EX_STR, threshold=90)
        )  # Excluding social feasibility section
    ]

    if len(feas_h) == 0:
        # no heading found!
        problematics.append(fp)
        continue

    up_text = feas_h[-1][1]
    feas_heading = feas_h[-1]
    if (feas_h[-1][0] + 1) == len(headings):
        down_text = len(text)
    else:
        for head in headings[(feas_h[-1][0] + 1) :]:
            # this checks if the level of next heading is similar or higher.
            if head[1].count("#") <= feas_heading[2].count("#"):
                down_text = head[0]
                break

    feas_text = text[up_text:down_text]
    if len(feas_text) > 20:
        problematics.append(fp)
        continue

    result[fp.stem] = feas_text

with open("../data/plan_documents/extracted.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(result, indent=4))
# %%
