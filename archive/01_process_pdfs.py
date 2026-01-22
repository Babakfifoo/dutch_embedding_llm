# %%
import logging
import json
import spacy
import pymupdf
import pytesseract
import numpy as np
import re
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import concurrent.futures
from itertools import chain
import os
os.environ["TESSDATA_PREFIX"] = (
    r"C:\Users\firoozb1\AppData\Local\Programs\Tesseract-OCR/tessdata"
)
logging.basicConfig(
    filename="logs/01.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
nlp = spacy.load(name="nl_core_news_sm")
FEASABILITY_TERMS = "economische", "uitvoerbaarheid"



pattern = r"(?:uitvoerbaarheid|haalbaarheid|economische|Uitvoeringsaspecten)"
regex = re.compile(pattern)


def contains_feasability(s):
    return bool(regex.search(s.lower()))


def requires_ocr(pages):
    text = ""
    for page in pages[:20]:
        text += page.get_text()
    if len(text) < 2000:
        return True
    return False


def clean_block_dict_item(block):
    line_text = ""
    line_size = 0
    if "lines" not in block:
        return block
    try:
        for l in block["lines"]:
            line_text += ("".join([s.get("text", "") for s in l["spans"]]) + " ")
            line_size = max([s.get("size", 0) for s in l["spans"]] + [line_size])
        block.pop("lines")
        block["text"] = line_text.strip()
        block["font_size"] = line_size
    except Exception as e:
        logging.error(f"\t{e}")
        return block
    return block


def Process_pdfs(PDFf):
    doc = pymupdf.open(PDFf)
    # NOTE: This scrips is designed for single column text PDFs
    IMRO = PDFf.stem
    logging.info(f"Parsing: {IMRO}")
    pages = list(doc.pages())
    if requires_ocr(pages=pages):
        logging.warning(f"{IMRO} -----------> NEEDS OCR")
        return

    starting_page = 10 # this is to skip the table of contents
    # def get_pages_with_feasability(pages)
    doc_results = {}
    for i, page in enumerate(pages[(starting_page - 1) :], start=starting_page):
        try:
            page_text = page.get_text()
            blocks_dict = page.get_text("dict").get("blocks")
            blocks_df = pd.DataFrame(map(clean_block_dict_item, blocks_dict))
            blocks_df["text"] = blocks_df["text"].fillna(" ").astype(str)
            size_stats = blocks_df["font_size"].value_counts()
            para_size = size_stats.iloc[0]
            headings = (
                blocks_df.query("font_size != @para_size")["text"]
                .sum()
                )
            if not contains_feasability(headings):
                continue
            cond = blocks_df["text"].apply(contains_feasability)

            top_heading_idx = blocks_df.loc[cond, "font_size"].idxmax()
            top_heading = blocks_df.loc[top_heading_idx, "text"]
            if not contains_feasability(top_heading[:70]):
                continue

            
            top_heading_size = blocks_df.loc[top_heading_idx, "font_size"]

            para_df = (
                blocks_df
                .iloc[top_heading_idx:, :]
                ).reset_index(drop=True)

            para_df["block_shift"] = (
                para_df["number"].diff().fillna(1) - 1
                ).cumsum()
            para_df = (
                para_df
                .query("block_shift == 0")
                .reset_index(drop=True)
                .query("text != ''")
                )
            
            result_text = " ".join(para_df["text"].to_list())
            sentences = nlp(result_text)
            sentences = [sent.text for sent in sentences.sents]
            if len(result_text) < 10:
                continue
            doc_results[i] = {}
            doc_results[i]["heading"] = top_heading
            doc_results[i]["text"] = sentences
        except Exception as e:
            logging.error(f"\tPage {i} encountered error.")
    with open(
        f"../data/pdf_plans_processed/{IMRO}.json",
        mode="w",
        encoding="latin-1"
        ) as f:
        f.write(json.dumps(doc_results, indent=4).encode("utf-8").decode("latin-1"))
        logging.info(f"{IMRO} --> Parsed")


def parallel_processing(items, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for item in items:
            future = executor.submit(Process_pdfs, item)
            futures.append(future)

        # Collect results
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"Task generated an exception: {exc}")

    return results
# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_PDFs = [f for f in toelichting_files if f.suffix == ".pdf"]
# %%
parallel_processing(items=toelichting_PDFs, max_workers=10)
# %%

parsed_pdfs = list(Path("../data/pdf_plans_processed").iterdir())
all_pdf_parsed = {}
for fp in parsed_pdfs:
    with open(fp, "r", encoding="latin-1") as f:
        data = json.loads(f.read())

    all_pdf_parsed[fp.stem] = data

problematic = {}
correct = {}
for k,v in tqdm(iterable=all_pdf_parsed.items()):
    if v == {}:
        problematic[k] = {}
    else:
        correct[k]=v

with open(file="../data/pdf_parsed.json", mode="w", encoding="latin-1") as f:
    f.write(json.dumps(all_pdf_parsed))
with open(file="../data/pdf_problematic.json", mode="w", encoding="latin-1") as f:
    f.write(json.dumps(problematic))
# %%# %%

regex_toc = re.compile(pattern=r"(?:inhoudsopgave)")

def contains_table_of_contents(s) -> bool:
    return bool(regex_toc.search(s.lower()))


regex_feasability = re.compile(pattern=r"(?:uitvoerbaarheid|haalbaarheid|Uitvoeringsaspecten)")

def contains_feasability(s) -> bool:
    return bool(regex_feasability.search(s.lower()))

def get_heading_page(toc_list, idx):
    for item in toc_list[idx:]:
        result = re.findall(r'\d+(?:\.\d+)?', item)
        if len(result) != 0:
            return (result[0])
# %%


PDFf = Path("../data/plan_documents/t_NL.IMRO.0063.140503-VA01.pdf")
doc = pymupdf.open(PDFf)
pages = list(doc.pages())
IMRO = PDFf.stem
logging.info(f"Parsing: {IMRO}")
pages = list(doc.pages())

for i, page in enumerate(pages):
    page_text = page.get_text()
    if contains_table_of_contents(page_text):
        break

headings = [t for t in page_text.split("\n") if t.strip() != ""]
mask = {h.strip():i for i,h in enumerate(headings) if contains_feasability(h)}

feasability_headings = {}
for k,i in mask.items():
    feasability_headings[k] = get_heading_page(toc_list=headings, idx=i)

pages_to_parse = []
for i, page in enumerate(pages[(page.number+1):], start = page.number+1):
    page_text = page.get_text()
    for k,v in feasability_headings.items():
        if k in page_text and v in page_text:
            pages_to_parse.append(i)
            pages_to_parse.append(i+1)
pages_to_parse = set(pages_to_parse)
# %%
text_blocks = pd.DataFrame()
for page_num in pages_to_parse:
    print(page_num)
    blocks_dict = pages[page_num].get_text("dict").get("blocks")
    df = pd.json_normalize(blocks_dict).explode("lines")
    df["lines"] = df["lines"].str["spans"]
    df = df.explode("lines")
    lines_df =  pd.DataFrame(df["lines"].to_list())
    lines_df["block"] = df["number"].values
    para_flag = lines_df["flags"].mode().values[0]
    df = (
        lines_df
        .groupby("block")
        .agg({
            "font":set,
            "flags":"max",
            "text":"sum",
            })
        .assign(text_body=lambda x: (x["flags"] != para_flag).astype(int))
        )
    text_blocks = pd.concat([df, text_blocks], ignore_index=True)
# %%
text_blocks["text"]
# %%
(
    text_blocks
    .assign(text_block=lambda x: x["text_body"].cumsum())
    .groupby("text_block")
    .agg({"text":lambda x: "\n\n".join(x)})
)
# %%
