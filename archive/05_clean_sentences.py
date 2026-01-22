# %%
import spacy
import json
from tqdm import tqdm
import logging

logging.basicConfig(
    filename="logs/05.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

nlp = spacy.load("nl_core_news_lg")
nlp.add_pipe(factory_name="sentencizer")
# %%

with open(
    "../data/plan_documents/fuzzy/html_fuzzy.json", mode="r", encoding="latin-1"
) as f:
    data = json.loads(f.read())

cleaned_data = []
for plan in tqdm(data):
    entry = {"IMRO": plan["IMRO"], "sentences": []}
    for i, item in plan["selections"].items():
        sents = nlp(item)
        correct_sents = []
        for sent in sents.sents:
            if sent[0].is_title:
                tokens = {token.pos_ for token in sent}
                if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
                    "VERB" in tokens
                ):
                    correct_sents.append(sent)
        try:
            correct_sents = [
                s.text.encode("latin-1").decode("utf-8")
                for s in correct_sents
                if "..." not in s.text
            ]
        except Exception as e:
            logging.warning(e)
            correct_sents = [s.text for s in correct_sents if "..." not in s.text]

        correct_sents = dict(enumerate(iterable=correct_sents, start=1))
        if len(correct_sents) == 0:
            continue
        cleaned_item = {"para_num": i, "sentences": correct_sents}

        entry["sentences"].append(cleaned_item)

    cleaned_data.append(entry)

with open(
    "../data/plan_documents/clean_sentences/html_fuzzy_sents.json",
    mode="w",
    encoding="utf-8",
) as f:
    f.write(json.dumps(cleaned_data, indent=4))
# %%

with open(
    "../data/plan_documents/fuzzy/pdf_fuzzy.json", mode="r", encoding="latin-1"
) as f:
    data = json.loads(f.read())

cleaned_data = []
for plan in tqdm(data):
    entry = {"IMRO": plan["IMRO"], "sentences": []}
    for i, item in plan["selections"].items():
        sents = nlp(item)
        correct_sents = []
        for sent in sents.sents:
            if sent[0].is_title:
                tokens = {token.pos_ for token in sent}
                if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
                    "VERB" in tokens
                ):
                    correct_sents.append(sent)
        try:
            correct_sents = [
                s.text.encode("latin-1").decode("utf-8")
                for s in correct_sents
                if "..." not in s.text
            ]
        except Exception as e:
            logging.warning(e)
            correct_sents = [s.text for s in correct_sents if "..." not in s.text]

        correct_sents = dict(enumerate(iterable=correct_sents, start=1))
        if len(correct_sents) == 0:
            continue
        cleaned_item = {"para_num": i, "sentences": correct_sents}

        entry["sentences"].append(cleaned_item)

    cleaned_data.append(entry)

with open(
    "../data/plan_documents/clean_sentences/pdf_fuzzy_sents.json",
    mode="w",
    encoding="utf-8",
) as f:
    f.write(json.dumps(cleaned_data, indent=4))
# %%
