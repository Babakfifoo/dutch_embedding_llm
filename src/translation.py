# %%
from transformers import pipeline
from tqdm import tqdm
import json
import logging
translation_model_name = "Helsinki-NLP/opus-mt-nl-en"

logging.basicConfig(
    filename="logs/translation.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=8,
    truncation=True,
)
# %%
with open("../data/HTML_query.json", "r") as f:
    data = json.loads(f.read())

result = []
for i, item in tqdm(enumerate(data, start=1)):
    logging.info(f"Processing {item.get("IMRO")}")
    sentences = {}
    context_idx = {}
    for k, v in item.get("contexts").items():
        sentences.update(v)
        context_idx[k] = list(v.keys())
    sents = list(sentences.values())
    logging.info(f"Sentence count: {len(sents)}")
    
    def data():
        for i in range(len(sents)):
            yield sents[i]
    
    translations = list(translator(data()))
    translations = [x[0].get("translation_text") for x in translations]
    translations = dict(zip(list(sentences.keys()), translations))
    entry = {
        "IMRO": item.get("IMRO"),
        "sentences": sentences,
        "translations": translations,
        "contexts": context_idx
        }
    result.append(entry)
    logging.info(f"Done! {item.get("IMRO")}")
    if 0 == i % 50:
        with open("../data/HTML_query_translations.json", "w", encoding="latin-1") as f:
            f.write(json.dumps(result))
# %%
