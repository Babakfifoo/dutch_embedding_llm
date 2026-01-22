# %%

import sqlite3
import logging
from typing import List, Set, Tuple
from tqdm import tqdm
from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset
from transformers import pipeline, TranslationPipeline
import spacy
from itertools import groupby

SQLITE_DB_PATH = "../data/database.db"
translation_model_name: str = "Helsinki-NLP/opus-mt-nl-en"
translator: TranslationPipeline = pipeline(
    task="translation",
    model=translation_model_name,
    device=0,
    batch_size=6,
    truncation=True,
    no_repeat_ngram_size=3,
)
nlp = spacy.load("nl_core_news_lg")
nlp.add_pipe(factory_name="sentencizer")


logging.basicConfig(
    filename="./logs/P01.log",
    encoding="utf-8",
    level=logging.WARNING,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


conn = sqlite3.connect(SQLITE_DB_PATH)
cursor: sqlite3.Cursor = conn.cursor()
cursor.execute(
    f"select imro from landuse where feasability_text IS NOT NULL and feasability_en is NULL ORDER BY imro"
)
imro_list: List[str] = [row[0] for row in cursor.fetchall()]


def find_sents(s: spacy.tokens.span.Span) -> bool:
    tokens: Set[str] = {token.pos_ for token in s}
    return any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]])


def extract_sentences(paragraphs: List[str]) -> Tuple[List[str | int], ...]:
    sent_nl: List[str] = []
    paragraph_ids: List[int] = []
    for i, para in enumerate(paragraphs):
        doc: spacy.Doc = nlp(para)
        sents: List[str] = [sent.text.strip() for sent in doc.sents if find_sents(sent)]
        sent_nl += sents
        paragraph_ids += [i] * len(sents)
    return (paragraph_ids, sent_nl)


def translate_dataset(dataset) -> List[str]:
    sents_en: List[str] = []
    for out in translator(KeyDataset(dataset, "text"), batch_size=6):
        sents_en.append(
            out[0]
            .get("translation_text")
            .replace("story", "recovery")
            .replace("operating plan", "exploitation plan")
            .replace("Operating plan", "Exploitation plan")
        )
    return sents_en


# %%
logging.info("Initiating the Extraction")
for imro in tqdm(imro_list):
    cursor.execute(
        f"SELECT feasability_text FROM landuse WHERE imro = ? AND feasability_en is NULL",
        (imro,),
    )
    result = cursor.fetchone()
    if result is None:
        print("no value for ", imro)
        continue
    context = result[0]

    paragraphs: List[str] = [
        s.strip().replace("Ã«", "ë") for s in context.split("\n") if s.strip() != ""
    ]
    data_nl: Tuple[List[int | str], ...] = extract_sentences(paragraphs)

    # Translating the sentences:
    hf_dataset = Dataset.from_dict({"text": data_nl[1]})
    sents_en: List[str] = translate_dataset(hf_dataset)
    data: List[List[int | str]] = list(zip(data_nl[0], sents_en))

    # putting the paragraphs back together.
    translation: List[str] = []
    for _, group in groupby(data, key=lambda x: x[0]):
        paragraph_en: str = " ".join([item[1] for item in group])
        translation.append(paragraph_en)

    translation: str = (
        "\n\n".join(translation)
        .replace("\x00", "")
        .replace("\xa0", "")
        .replace("'", "''")
        .replace("”", '"')
    )

    sql_upsert: str = """
        UPDATE landuse
        SET feasability_en = ?
        WHERE imro = ?;
    """
    cursor.execute(sql_upsert, (translation, imro))

    conn.commit()

# %%
