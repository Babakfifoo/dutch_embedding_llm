# %%
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import chromadb
import logging
import pymupdf
import re
import json
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from spacy.lang.nl import Dutch
import ollama

logging.basicConfig(
    filename="logs/embedding.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
nlp = Dutch()
nlp.add_pipe(factory_name="sentencizer")

regex_toc = re.compile(pattern=r"(?:inhoudsopgave|inleiding|ianleiding)")
regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel)"
)


def contains_feasability(s) -> bool:
    return bool(regex_feasability.search(s.lower()))


def get_the_y_bounds(df, para_font_size, para_font, common_width):
    dy_stats = df.loc[
        (df["size"] == para_font_size)
        & (df["font"] == para_font)
        & (df["line_w"] >= common_width)
    ]
    Max_allowed_y0 = dy_stats.y1.max()
    Min_allowed_y1 = dy_stats.y0.min()
    return (Max_allowed_y0, Min_allowed_y1)


def extract_paragraph_texts(df):
    para_font = df.font.mode()[0]
    para_font_size = df["size"].mode()[0]
    common_width = df["line_w"].mean()
    Max_allowed_y0, Min_allowed_y1 = get_the_y_bounds(
        df, para_font_size, para_font, common_width
    )
    paragraph_text = df.loc[
        (df["size"] == para_font_size)
        & (df["font"] == para_font)
        & (df["text"].str.len() >= 7)
        & (df["y0"] <= Max_allowed_y0)
        & (df["y1"] >= Min_allowed_y1),
        ["text", "page_number", "block_number"],
    ].reset_index(drop=True)
    return paragraph_text


def correct_hyphenation(s):
    if s[-1] == "-":
        return s[:-1]
    else:
        return s + " "


def contains_table_of_contents(s) -> bool:
    return bool(regex_toc.search(s.lower()))


def extract_sentences(PDFf):
    doc = pymupdf.open(PDFf)
    pages = list(doc.pages())
    IMRO = PDFf.stem

    for j, page_f in enumerate(pages):
        page_text = page_f.get_text()
        if contains_table_of_contents(page_text) or contains_feasability(page_text):
            break

    all_lines = pd.DataFrame()
    for i, page in enumerate(pages[(j + 1) :], start=(j + 1)):
        page_text = page.get_text()
        blocks_dict = page.get_text("dict").get("blocks")

        df = pd.json_normalize(blocks_dict)
        if "lines" not in df.columns:
            continue
        df = df.explode("lines").dropna(subset="lines")
        df["lines"] = df["lines"].str["spans"]
        df = df.explode("lines")
        lines_df = pd.DataFrame(df["lines"].to_list())
        lines_df["block_number"] = df["number"].values
        lines_df["page_width"] = page.rect[2]
        lines_df["page_height"] = page.rect[3]
        lines_df["page_number"] = page.number
        all_lines = pd.concat([all_lines, lines_df], ignore_index=True)

    all_lines[["x0", "y0", "x1", "y1"]] = pd.DataFrame(all_lines.bbox.to_list())
    all_lines["line_w"] = all_lines.x1 - all_lines.x0
    all_lines["line_h"] = all_lines.y1 - all_lines.y0
    all_lines["size"] = all_lines["size"].round(1)
    paragraphs = extract_paragraph_texts(all_lines)
    paragraphs = paragraphs.loc[
        (paragraphs.text.str.strip().str.len() > 3), :
    ].reset_index(drop=True)
    paragraphs.text = paragraphs.text.str.strip().apply(correct_hyphenation)
    sents_df = pd.DataFrame()
    for p, g in paragraphs.groupby("page_number"):
        test_s = "".join(g.text.to_list())
        sents = [sent.text for sent in nlp(test_s).sents]
        sents = pd.DataFrame({"sents": sents, "page": p})
        sents["w_start"] = sents["sents"].str[0].str.islower()
        sents["w_end"] = sents["sents"].str[-1] != "."
        sents_df = pd.concat([sents_df, sents])
    sents_df["IMRO"] = IMRO
    logging.info(f"{IMRO} is done!")
    return sents_df


def QA(prompt):
    response = ollama.chat(
        model=OllamaModel,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={"seed": 2025, "temperature": 0},
    )
    return (response['message']['content'])


def extract_and_embed_sentences(fp, collection):
    sentences_df = extract_sentences(fp).reset_index(drop=True)
    if len(sentences_df) == 0:
        return None
    documents = sentences_df.sents.to_list()
    embeddings = emb_model.encode(
        sentences=sentences_df.sents.to_list(), show_progress_bar=False
    )
    ids = sentences_df.index.astype(str).to_list()
    collection.add(
        embeddings=embeddings,
        documents=documents,
        ids=ids)


def search_and_translate(embed_question, collection):
    query_embeddings = emb_model.encode(
        sentences=embed_question,
        show_progress_bar=False
        )
    results = collection.query(query_embeddings=query_embeddings, n_results=5)
    translations = translator(results["documents"], max_length=350)
    return ("\n".join([t[0]["translation_text"] for t in translations]))

# %%

#  Run this when extracting sentences ...
# parallel_processing(items=toelichting_PDFs, max_workers=10)
# %%
OllamaModel = "llama3.2:3b-instruct-q5_K_M"

emb_model = SentenceTransformer(
    model_name_or_path="jinaai/jina-embeddings-v3",
    trust_remote_code=True,
    device="cuda",
)

translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=5,
    truncation=True,
)

# %%
prompt = """
#### INSTRUCTIONS
    Answer the questions based on the provided context.
    Choose answer from ["yes", "no", "not mentioned"].

#### CONTEXT:
    {context}
#### QUESTION
    {question}

#### OUTPUT:
a json with question number as keys, and answer as values. 
Do not provide any additional text.

#### Example:
{{
    "1": "no",
    "2": "yes",
}}
"""

def get_answers_from_file(fp, questions):
    IMRO = fp.stem
    logging.info(f"Embedding {IMRO} ... ")
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(IMRO)
    extract_and_embed_sentences(fp, collection)

    context = search_and_translate(
        embed_question=questions["embed_question"], 
        collection=collection
        )
    answer = QA(
        prompt=prompt.format(context=context, question=questions["rag_question"])
    )   
    return {
        "context": context,
        "answer": answer
    }

# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_PDFs = [f for f in toelichting_files if f.suffix == ".pdf"]

questions = {
    "embed_question": "who is the land or plot owner?",
    "rag_question":"""
1. Does municipality own land?
2. Does initiator, private party or developer own land?
"""}



# %%
all_pdf_answers = {}
for fp in tqdm(iterable=toelichting_PDFs):
    logging.info(f"{fp} Processed")
    all_pdf_answers[fp.stem] = get_answers_from_file(fp, questions)

# %%
