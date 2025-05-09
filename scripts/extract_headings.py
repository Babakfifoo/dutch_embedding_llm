# %%
from pathlib import Path
from rapidfuzz import fuzz
from tqdm import tqdm
import json

ECONOMIC_FEAS_STR = [
    "financieel",
    "financiële",
    "economiche",
    "F i n a n c i e e l",
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


def find_next_heading(level, s):# -> Any:
    return (s.count("#") == level.count("#")) and (s.count("*") == level.count("*"))

# %%
mds = list(Path("../data/plan_documents/md").iterdir())
# %%
result = {}
problematics = []
for fp in tqdm(mds):
    with open(fp, "r", encoding="utf-8") as f:
        text = [x for x in f.read().split("\n") if x.strip() != ""][200:]

    headings = {i: h for i, h in enumerate(iterable=text) if (h[0] == "#")}
    
    feas_h = [
        (i, h)
        for i, h in headings.items()
        if find_topic(s=h.lower(), q=ECONOMIC_FEAS_STR, threshold=80)
        and find_topic(s=h.lower(), q=FEAS_STR, threshold=80)
        and (not find_topic(s=h.lower(), q=EX_STR, threshold=80))  # Excluding social feasibility section
    ]
    if len(feas_h) == 0:
        problematics.append(fp)
        continue
    feas_h_level = feas_h[0][1]
    feas_text = text[feas_h[0][0]:]
    feas_text_loc = [i for i, s in enumerate(feas_text) if find_next_heading(feas_h_level, s)]
    if len(feas_text_loc) > 1:
        res = feas_text[:feas_text_loc[1]] if (feas_text_loc[1] > 1) else feas_text
    if len(res) > 20: # This checks if too much text is selected by mistake. if so, it trims it to 10 paragraphs.
        res = res[:20]
    result[fp.stem] = res
# %%

with open("../data/new/texts/feasability_section.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(result, indent=4))
# %%
