# %%

from transformers import pipeline
from tqdm import tqdm
import logging
import json

tqdm.pandas()

logging.basicConfig(
    filename="logs/03_translation.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=4,
    truncation=True,
)
# %%
with open("../data/pdf_parsed.json", "r") as f:
    plan_info_pdf = json.loads(f.read())

translations_pdf = {}
for i, (IMRO, plan_string) in tqdm(enumerate(plan_info_pdf.items(), start = 1)):
    contents = plan_string
    translations_pdf[IMRO] = []
    for page, item in plan_string.items():
        if item["text"] is None:
            continue
        translations = [translator(s.strip(), max_length=300) for s in item["text"]]
        translations = [t[0].get("translation_text") for t in translations]
        translations = "\n".join(translations)
        translations_pdf[IMRO].append(
            {"heading": item.get("heading").replace("\t", ""), "text": translations}
            )
    logging.info(f"{IMRO} -> Translated")

    if i % 100 != 0:
        continue
    with open(file="../data/translations_pdf_20250107.json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(translations_pdf, indent=4))
    logging.info(f"{i} Plans translated.")

# %%
translations_pdf = {}
for i, (IMRO, plan_string) in tqdm(enumerate(plan_info_pdf.items(), start = 1)):
    contents = plan_string
    translations_pdf[IMRO] = []
    for page, item in plan_string.items():
        if item["text"] is None:
            continue
        translations = translator(item["text"], max_length=300)
        translations = [t.get("translation_text") for t in translations]
        translations = "\n".join(translations)
        translations_pdf[IMRO].append(
            {page:translations}
            )
    logging.info(f"{IMRO} -> Translated")

    if i % 100 != 0:
        continue
    with open(file="../data/translations_pdf_20250107.json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(translations_pdf, indent=4))
    logging.info(f"{i} Plans translated.")
# %%

# %%
