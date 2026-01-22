# %%
import json
from transformers import pipeline
from tqdm import tqdm
import re

translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=6,
    truncation=True,
)
regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel)"
)


def contains_feasability(s) -> bool:
    return bool(regex_feasability.search(string=s.lower()))


def get_existing_index(item):
    res = {
        item.get("IMRO"): len(item.get("ids"))
    }
    return(res)


# %%
with open("../data/plan_documents/clean_sentences/html_fuzzy_sents.json") as f:
    data = json.loads(f.read())
# %%
translated_results = []
for plan in tqdm(data):
    sents = []
    ids = []
    for item in plan["sentences"]:
        para = str(item.get("para_num"))
        ids += [para + ":" + str(x) for x in list(item.get("sentences").keys())]
        sents += list(item.get("sentences").values())

    translations = [x.get("translation_text") for x in translator(sents)]
    entry = {
        "IMRO": plan.get("IMRO"),
        "ids": ids,
        "nl": sents,
        "en": translations,
    }
    translated_results.append(entry)

with open("../data/plan_documents/translations/html_translated.json", "w") as f:
    f.write(json.dumps(translated_results, indent=4))

# %%

with open("../data/plan_documents/clean_sentences/pdf_fuzzy_sents.json") as f:
    data = json.loads(f.read())

translated_results = []

for i, plan in tqdm(enumerate(data)):
    sents = []
    ids = []
    for item in plan["sentences"]:
        page = str(item.get("page"))
        block = str(item.get("block"))
        ids += [
            page + "." + block + ":" + str(x)
            for x in list(item.get("sentences").keys())
        ]
        sents += list(item.get("sentences").values())
    conds = [i for i, s in enumerate(sents) if contains_feasability(s)]
    if len(conds) == 0:
        idx = 0
    else:
        # Reducing the feasability index by 1 so actual feasability heading is obtained.
        # Some text where extracting wrong feasability index.
        idx = max(0, conds[round(len(conds) / 2) - 1])
    selected_sents = sents[idx:]
    selected_ids = ids[idx:]
    translations = [
        x.get("translation_text") for x in translator(selected_sents, max_length=400)
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "ids": selected_ids,
        "nl": selected_sents,
        "en": translations,
    }
    translated_results.append(entry)

with open("../data/plan_documents/translations/pdf_translated.json", "w") as f:
    f.write(json.dumps(translated_results, indent=4))
# %%
