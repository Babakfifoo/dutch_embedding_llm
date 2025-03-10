# %%
# %%
import logging
import json
import re
from markdownify import markdownify as md
from tqdm import tqdm
from pathlib import Path
from rapidfuzz import fuzz
import pandas as pd
import spacy
from transformers import pipeline
from ollama import chat


translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=4,
    truncation=True,
)

nlp = spacy.load("nl_core_news_lg")
nlp.add_pipe(factory_name="sentencizer")
logging.basicConfig(
    filename="logs/21.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

FUZZY_THRESHOLD=90
regex_ownership = re.compile(pattern=r"(?:eigenaar|eigendom)")


def contains_ownership(s) -> bool:
    return bool(regex_ownership.search(string=s.lower()))


def find_ownership(s: str) -> bool:
    for k in ["eigenaar", "eigendom"]:
        score = fuzz.partial_ratio(s, k)
        if score > FUZZY_THRESHOLD:
            return True

    return False


def clean_sentences(s:str) -> str:
    sents = nlp(s)
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
            s.encode("latin-1").decode("utf-8")
            for s in correct_sents
            if "..." not in s.text
        ]
    except Exception as e:
        logging.warning(e)
        correct_sents = [s.text for s in correct_sents if find_ownership(s.text)]
    
    return correct_sents

# %%
toelichting_files = list(Path("../data/plan_documents/html").iterdir())
# %%

entries = []
for fp in tqdm(iterable=toelichting_files):
    IMRO = fp.stem
    with open(fp, "r", encoding="latin-1") as f:
        html_content = f.read()

    md_text = md(html=html_content, strip=["a"]).split("\n")
    md_text = [x for x in md_text if (len(x) > 5)]

    df = pd.DataFrame({"text": md_text})
    df["text"] = df["text"].str.strip()
    df = df[df.text.str.len() > 5].reset_index(drop=True)
    ownership = df[df["text"].apply(find_ownership)]

    sents = clean_sentences("\n".join(ownership["text"].to_list()))
    if len(sents) == 0:
        continue
    ids = []
    translations = []
    for i, item in enumerate(iterable=sents):
        ids += [i]
        translations.append(translator(item)[0].get("translation_text"))

    entry = {
        "IMRO": IMRO,
        "ids": ids,
        "nl": sents,
        "en": translations,
    }

    entries.append(entry)

with open("../data/plan_documents/texts/html_ownership.json", "w") as f:
    f.write(json.dumps(entries))
# %%
prompt = """
    Analyze the following text and instrauctions:
    **Instructions**:
    Answer the question in one sentence only based on the provided text.
    If answer to the question is not in the text, reply "None" only.
    **question**:
    {question}
    
    **Text**:
    {text}

    """


owner_answers = {}
for i, plan in tqdm(enumerate(entries)):
    if plan.get('en', None) == []:
        continue
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    text="\n".join(plan.get('en', None)),
                    question="Who is the owner?"
                    ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )

    owner_answers[plan.get("IMRO")]= answer["message"]["content"]
    if (i + 1) % 100 == 0:
        with open("../data/plan_documents/answered/html_owner_answers.json", "w") as file:
            file.write(json.dumps(owner_answers, indent=4))
        logging.info(msg=f"{i + 1} plans stored")
# %%
municipality_owner = {}
for imro, v in owner_answers.items():
    if "none" in v.lower():
        municipality_owner[imro] = None
        continue
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    text=v,
                    question="Reply in yes or no. Is municipality the owner?"
                    ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    municipality_owner[imro] = answer["message"]["content"]

with open("../data/plan_documents/answered/html_gem_owner_answers.json", "w") as file:
    file.write(json.dumps(municipality_owner, indent=4))
logging.info(msg=f"{i + 1} plans stored")
