# %%
import json
import re
from pathlib import Path
from tqdm import tqdm
import logging
from rapidfuzz import fuzz

logging.basicConfig(
    filename="logs/04.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel|financiële|exploitatie|u i t v o e r b a a r h e i d|F i n a n c i e e l)"
)


def set_heading_formatting(s):
    if s[0] == "#":
        return s
    if ("hoofdstuk" in s.lower()) and ("|" not in s) and len(s) < 120:
        return "# " + s
    return s


search_terms = [
    "uitvoerbaarheid",
    "haalbaarheid",
    "uitvoeringsaspecten",
    "financieel",
    "financiële",
    "exploitatie",
    "u i t v o e r b a a r h e i d",
    "F i n a n c i e e l",
]


def contains_feasability(s) -> bool:
    if bool(regex_feasability.search(string=s.lower())):
        return True
    for k in search_terms:
        score = fuzz.partial_ratio(s, k)
        if score > 90:
            return True
    return False


def is_heading(s):
    return (s.strip()[0] == "#") or (s.strip().lower()[:2] == "**")


def is_digit_heading(s):
    if (len(s) < 120) and s.strip()[0].isdigit():
        return int(s.strip()[0])
    return False


# %%
files = list(Path("../data/plan_documents/md/").iterdir())
problematic = []
results = {}
for fp in tqdm(files):
    IMRO = fp.stem

    with open(fp, "r", encoding="utf-8") as f:
        text = [s.strip() for s in f.read().split("\n") if len(s.strip()) != 0]
        text = [set_heading_formatting(s) for s in text]
    feasability_h1 = [
        i
        for i, s in enumerate(text)
        if contains_feasability(s) and len(s) < 120 and (i > 100) and ("|" not in s)
    ]
    if len(feasability_h1) == 0:
        problematic.append(str(fp))
        logging.warning(f"{fp} -> Heading not found")
        continue
    feas_h_text = [text[h] for h in feasability_h1]
    feas_with_hash = [h for h in feas_h_text if "#" in h]
    if len(feas_with_hash) == 0:
        heading_num = [
            int(s.replace("*", "").strip()[0])
            for s in feas_h_text
            if s.strip()[0].isdigit()
        ]
        if len(heading_num) == 0:  # No numeric nor # headings
            problematic.append(str(fp))
            logging.warning(f"{fp} -> No numeric nor # headings")
            continue
        next_num_heading_idx = min(
            [
                i
                for i, s in enumerate(text)
                if (is_digit_heading(s) == (heading_num[0] + 1))
            ]
            + [len(text)]
        )

        results[IMRO] = text[feasability_h1[0]: next_num_heading_idx]
        continue
    else:
        count_hash = min([s.replace(" ", "").count("#") for s in feas_h_text])
        h1 = [
            i
            for i, s in enumerate(text)
            if (i >= min(feasability_h1)) and (count_hash == s.count("#"))
        ]

        if len(h1) == 1:
            h1.append(-1)

        results[IMRO] = text[h1[0]: h1[1]]

with open("../data/plan_documents/feasability_chapter.json", "w") as f:
    f.write(json.dumps(results, indent=4))

with open("../data/plan_documents/feasability_chapter_problematic.json", "w") as f:
    f.write(json.dumps(problematic, indent=4))
# %%
