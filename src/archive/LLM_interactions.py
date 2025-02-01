# %%
from markdownify import markdownify as md
from icecream import ic
from tqdm import tqdm
from pathlib import Path

from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Model

import re, logging
import torch
import chromadb
import numpy as np


logging.basicConfig(
    filename="pdf_parsing.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

# %%

# Embedding db
client = chromadb.PersistentClient(path="../data/test_sentences_html.db")
collections = client.list_collections()
collections = [c.name for c in collections]

# Embedding function
JINA = "jinaai/jina-embeddings-v3"
model_sentenseTransformer = SentenceTransformer(
    model_name_or_path=JINA,
    trust_remote_code=True, 
    device='cuda'
)

# %%

# TODO:
# A Function to extract all text -> Sentences
# setup for HTML, PDF and XML
def check_string(s: str):
    s = s.lower()
    hoofdstuk_match = re.match(r"^hoofdstuk", s)
    num_match = re.match(r"^\d+", s)
    heading_match = re.match(r"^#", s)
    uitvoerbaarheid_match = re.search(r"uitvoerbaarheid", s)
    haalbaarheid_match = re.search(r"haalbaar.*", s)
    Financi_match1 = re.search(r"fina.*", s)
    Economische = re.search(r"economische", s)
    return (bool(hoofdstuk_match) or bool(num_match) or bool(heading_match)) and (
        bool(uitvoerbaarheid_match)
        or bool(haalbaarheid_match)
        or bool(Financi_match1)
        or bool(Economische)
    )


def parse_html_to_sentenses(html_path: str) -> list[str]:
    with open(file=html_path, mode="r", encoding="utf-8") as html:
        html_txt = html.read()
        text = md(html_txt, strip=["a"])
        try:
            text = text.encode("latin-1").decode("utf-8", "ignore")
        except:
            text = text.encode("utf-8").decode("utf-8", "ignore")
    text = [s.strip() for s in text.split("\n") if s.strip() != ""]
    # text = [s for s in text if bool(re.match(pattern=r'[A-Z]', string=s))]
    # text = [s for s in text if s[-1] == "."]

    return text


def split_feasability(sentenses):
    sent_arr = np.array(sentenses)
    mask = np.fromiter((check_string(xi) for xi in sent_arr), np.bool)
    checked = sent_arr[mask]
    checked = [x for x in checked if x[1] == "#"]
    if len(checked) == 0:
        return sent_arr
    (i,) = np.where(sent_arr == checked[0])
    result = sent_arr[i[0] :]
    if len(result) != 0:
        return result
    else:
        return sent_arr

# %%

directories = list(Path("../data/plans_need_processing_htmls").iterdir())
toelichting_files = []
for d in directories:
    toelichting = [f for f in list(d.iterdir()) if "t_" in f.name]
    if len(toelichting) != 0:
        toelichting_files.append(toelichting[0])

toelichting_files = [f for f in toelichting_files if f.suffix == ".html"]


# %%
for plan_html in tqdm(toelichting_files):
    name = plan_html.stem.replace("t_NL.IMRO.", "")
    if name in collections:
        continue
    collection = client.get_or_create_collection(name=name)
    sentenses = parse_html_to_sentenses(plan_html)
    sentenses = split_feasability(sentenses).tolist()
    sentenses = [s for s in sentenses if s[-1] == "."]
    sentenses = [s for s in sentenses if bool(re.match(pattern=r"[A-Z]", string=s))]
    
    embeddings = model_sentenseTransformer.encode(sentenses, show_progress_bar=False)
    ids = [str(i) for i in range(len(embeddings))]
    if len(ids) == 0:
        continue
    collection.add(documents=sentenses, embeddings=embeddings, ids=ids)
    logging.info(name + " -> Collected")

# %%
