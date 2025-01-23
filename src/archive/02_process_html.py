# %%
import logging
import json
import spacy
import re
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from itertools import chain
from bs4 import BeautifulSoup

logging.basicConfig(
    filename="logs/02.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# %%

pattern = r"(?:economische|uitvoerbaarheid)"
regex = re.compile(pattern)


def contains_feasability(s):
    return bool(regex.search(s.lower()))


def remove_digits_and_periods(s):
    return re.sub(r"[0-9\.]", "", s)


def extract_headings(soup):
    headings = []
    for i in range(1, 5):
        tags = soup.find_all(f"h{i}")
        for tag in tags:
            heading_text = tag.get_text(strip=True)
            try:
                headings.append((i, heading_text.encode("latin-1").decode("latin-1")))
            except:
                headings.append((i, heading_text))
    return headings


def extract_content_between_headings(soup, heading_tag, heading_text):
    """Extracts content between two headings of the same level.

    Args:
        html_file (str): Path to the HTML file.
        heading_tag (str): The HTML tag of the heading (e.g., 'h2', 'h3').
        heading_text (str): The text content of the heading.

    Returns:
        list: A list of extracted content elements.
    """
    heading_tag = "h" + str(heading_tag)
    # Find the next sibling heading of the same level
    paragraphs = []
    for heading in soup.find_all(heading_tag, text=heading_text):
        next_sibling = heading.next_sibling
        if next_sibling and next_sibling.name == "p":
            paragraphs.append(next_sibling)

    return paragraphs


def process_paragraphs(paragraphs, nlp):
    if paragraphs is None:
        return None
    sentences = []
    for para in paragraphs:
        doc = nlp(para)
        for sent in doc.sents:
            sentences.append(sent.text)
    return sentences


# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_PDFs = [f for f in toelichting_files if f.suffix == ".html"]
nlp = spacy.load("en_core_web_sm")
# %%

# Example usage
plans_info = {}
for file_path in tqdm(toelichting_PDFs):
    IMRO = file_path.stem
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    headings = extract_headings(soup)
    Feasability_headings = [(i, h) for i, h in headings if contains_feasability(h)]
    contents = []
    for i, h in Feasability_headings:
        paragraphs = extract_content_between_headings(
            soup, heading_tag=i, heading_text=h
        )
        paragraphs = [s.strip() for s in chain(*paragraphs) if s.strip() != ""]
        contents.append(
            {
                "heading": h,
                "text": process_paragraphs(paragraphs, nlp),
            }
        )
    plans_info[IMRO] = {"fileType": file_path.suffix, "contents": contents}


with open("html_parsed.json", "w") as f:
    f.write(json.dumps(plans_info, indent=4))
# %%
