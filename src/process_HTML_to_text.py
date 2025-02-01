# %%
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import logging
from markdownify import markdownify as md
import spacy
logging.basicConfig(
    filename="logs/HTML_to_text.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
# nlp = Dutch()
nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe(factory_name="sentencizer")
# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_htmls = [f for f in toelichting_files if f.suffix == ".html"]
# %%
HTML_texts = []
for i, fp in tqdm(iterable=enumerate(iterable=toelichting_htmls, start=1)):
    IMRO = fp.stem
    logging.info(f"Processing {IMRO}")
    with open(fp, "r", encoding="utf-8") as file:
        html_content = md(file.read(), strip="a", autolinks=False)

    correct_sents = []
    for item in html_content.split("\n"):
        doc = nlp(item)
        if "#" in item:
            continue
        for sent in doc.sents:
            if sent[0].is_title and sent[-1].is_punct:
                tokens = {token.pos_ for token in sent}
                if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
                    "VERB" in tokens
                ):
                    correct_sents.append(sent)
    correct_sents = [s.text for s in correct_sents]
    result_sentences = pd.Series(correct_sents).to_dict()
    entry = {
        "IMRO": IMRO,
        "sentences": result_sentences,
    }
    HTML_texts.append(entry)
    logging.info(f"Done! {IMRO}")
    if i % 100 == 0:
        with open(file="../data/HTML_Sentences.json", mode="w") as f:
            f.write(json.dumps(HTML_texts))
# %%
