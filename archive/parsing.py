# %%

import logging
import json
import spacy
import pymupdf
import re
from tqdm import tqdm
from pathlib import Path
import concurrent.futures
from itertools import chain
import os
import pandas as pd
os.environ["TESSDATA_PREFIX"] = (
    r"C:\Users\firoozb1\AppData\Local\Programs\Tesseract-OCR/tessdata"
)
logging.basicConfig(
    filename="logs/parsing.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
nlp = spacy.load(name="nl_core_news_sm")
# %%
regex_toc = re.compile(pattern=r"(?:inhoudsopgave)")
regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel|)"
)


def extract_alphabetic(input_string):
    input_string = re.sub(pattern=r'hoofdstuk', repl='', string=input_string.lower())

    return ' '.join(word for word in input_string.split() if re.match(pattern='^[a-zA-Z]+$', string=word))


def contains_table_of_contents(s) -> bool:
    return bool(regex_toc.search(s.lower()))


def contains_feasability(s) -> bool:
    return bool(regex_feasability.search(s.lower()))


def get_heading_page(toc_list, idx):
    for item in toc_list[idx:]:
        result = re.findall(r"\d+(?:\.\d+)?", item)
        if len(result) != 0:
            return result[0]


toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_PDFs = [f for f in toelichting_files if f.suffix == ".pdf"]

# %%
problematics = []
results_doc_dict = {}
for i, PDFf in tqdm(iterable=enumerate(iterable=toelichting_PDFs, start=1)):
    doc = pymupdf.open(PDFf)
    pages = list(doc.pages())
    IMRO = PDFf.stem
    try:
        for i, page in enumerate(pages):
            page_text = page.get_text()
            if contains_feasability(page_text):
                break

        headings = [t for t in page_text.split("\n") if t.strip() != ""]
        mask = {extract_alphabetic(h.strip()) for h in headings if contains_feasability(h)}
        regex_headings = re.compile(
            pattern=r"(?:{heading_pattern})".format(heading_pattern="|".join(mask))
        )
        max_heading_len = max( len(h) for h in mask)
        text_blocks = pd.DataFrame()
        for j, page in enumerate(pages[i+1:]):
            page_text = page.get_text()
            if not bool(regex_headings.search(page_text.lower())):
                continue
            page_width = page.rect[2]
            blocks_dict = page.get_text("dict").get("blocks")
            df = pd.json_normalize(blocks_dict).explode("lines").dropna(subset="lines")
            df["lines"] = df["lines"].str["spans"]
            df = df.explode("lines")
            lines_df = pd.DataFrame(df["lines"].to_list())
            lines_df["block"] = df["number"].values
            para_flag = lines_df["flags"].mode().values[0]
            lines_df["width"] = lines_df["bbox"].str[2] - lines_df["bbox"].str[0]
            df = (
                lines_df.groupby("block")
                .agg(
                    {
                        "font": set,
                        "flags": "max",
                        "text": "sum",
                        "width":"max"
                    }
                )
                .assign(text_body=lambda x: (x["flags"] != para_flag).astype(int))
            ).query("width > (@page_width * 0.6) | text_body == 1")
            text_blocks = pd.concat([text_blocks, df], ignore_index=True)
        text_blocks["text_body"] = text_blocks["text_body"].cumsum()
        result_text: list[str] = text_blocks.groupby("text_body").agg({
            "text": lambda x: "\n".join(x)
        })["text"].to_list()

        selected_text = [t for t in result_text if bool(regex_headings.search(t[:(max_heading_len + 20)].lower()))]
        results_doc_dict[IMRO] = result_text
    except:
        problematics.append(PDFf)
        logging.warning(f"{PDFf} is problematic")
    if i % 100:
        with open("../data/pdf_dutch_extraction.json", mode="w") as f:
            f.write(json.dumps(results_doc_dict))
# %%
