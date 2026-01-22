# %%
import spacy
import json
from tqdm import tqdm
from pathlib import Path

import logging
import pymupdf
import pandas as pd

nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe(factory_name="sentencizer")

logging.basicConfig(
    filename="logs/PDF_to_text.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


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


def get_lines(pages):
    all_lines = pd.DataFrame()
    for i, page in enumerate(pages):
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
    return all_lines


# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_PDFs = [f for f in toelichting_files if f.suffix == ".pdf"]
# %%
PDF_texts = []
# %%

for i, fp in tqdm(iterable=enumerate(iterable=toelichting_PDFs[191:], start=1)):
    IMRO = fp.stem
    logging.info(f"Processing {IMRO}")
    doc = pymupdf.open(fp)
    pages = list(doc.pages())
    try:
        all_lines = get_lines(pages)

        paragraphs = extract_paragraph_texts(all_lines)
        paragraphs = paragraphs.loc[
            (paragraphs.text.str.strip().str.len() > 3), :
        ].reset_index(drop=True)
        paragraphs.text = paragraphs.text.str.strip().apply(correct_hyphenation)
        correct_sents = []
        sents = nlp(paragraphs.text.sum())
        for sent in sents.sents:
            if sent[0].is_title and sent[-1].is_punct:
                tokens = {token.pos_ for token in sent}
                if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
                    "VERB" in tokens
                ):
                    correct_sents.append(sent)
        correct_sents = [s.text for s in correct_sents if "..." not in s.text]
        result_sentences = pd.Series(correct_sents).to_dict()
        entry = {
            "IMRO": IMRO,
            "sentences": result_sentences,
        }
        PDF_texts.append(entry)
        logging.info(f"Done! {IMRO}")
        if i % 100 == 0:
            with open(file="../data/PDF_Sentences.json", mode="w") as f:
                f.write(json.dumps(PDF_texts))
    except Exception as e:
        logging.error(f"Problem {IMRO}: {e}")
# %%
