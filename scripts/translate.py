# %%
# %%
import json
from tqdm import tqdm
import logging
import spacy
from transformers import pipeline
from functools import lru_cache

translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=6,
    truncation=True,
)

nlp = spacy.load("nl_core_news_lg")
nlp.add_pipe(factory_name="sentencizer")

logging.basicConfig(
    filename="logs/04.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# %%
@lru_cache(maxsize=10000)
def translate_sentence(s):
    return translator(s)[0].get("translation_text")


def translate_para(sentences):
    sentences_to_translate = list(sentences.values())
    sents = [translate_sentence(s) for s in sentences_to_translate]
    return {"id": list(sentences.keys()), "nl": list(sentences.values()), "en": sents}


def extract_sentences(s: str, para):
    sents = nlp(s)
    correct_sents = []
    for sent in sents.sents:
        # if sent[0].is_title:
        tokens = {token.pos_ for token in sent}
        if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
            "VERB" in tokens
        ):
            correct_sents.append(sent.text)
    ids = [f"{para}:{i}" for i in range(len(correct_sents))]
    return dict(zip(ids, correct_sents))


# %%
with open("../data/new/texts/feasability_section.json", "r", encoding="utf-8") as f:
    feas_text = json.loads(f.read())
problematic = []
results = {}
# %%
result = []
counter = 1
for IMRO, text in tqdm(feas_text.items()):

    cleaned = [
        extract_sentences(s, para=i)
        for i, s in enumerate(text, start=1)
        if s.strip()[0].isalpha()
    ]
    sentences = {}
    for d in cleaned:
        sentences.update(d)
    translated = translate_para(sentences)
    translated["IMRO"] = IMRO
    result.append(translated)
    counter += 1
    if counter % 100 == 0:
        with open("../data/new/translations/translated.json", "w") as file:
            file.write(json.dumps(result, indent=4))

        logging.info(msg=f"{counter} plans translated")

# %%
cleaned_sents = []
for item in result:
    entry = {
        "IMRO": item.get("IMRO"),
        "id": item.get("id"),
        "nl": [s.text for s in item["nl"]],
        "en": item["en"],
    }
    cleaned_sents.append(entry)
with open("../data/plan_documents/translated_selected_sents.json", "w") as file:
    file.write(json.dumps(cleaned_sents, indent=4))
# %%
