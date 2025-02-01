# %%
import json
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from spacy.lang.nl import Dutch
import spacy
from bs4 import BeautifulSoup
import re
import logging
from itertools import chain
import xmltodict
from markdownify import markdownify as md
from markdownify import MarkdownConverter

logging.basicConfig(
    filename="logs/embedding.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
# nlp = Dutch()
nlp = spacy.load("nl_core_news_sm")
nlp.add_pipe(factory_name="sentencizer")

regex_feasability = re.compile(
    pattern=r"(?:uitvoerbaarheid|haalbaarheid|uitvoeringsaspecten|financieel)"
)


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
    for heading in soup.find_all(heading_tag, string=heading_text):
        next_sibling = heading.next_sibling
        if next_sibling and next_sibling.name == "p":
            paragraphs.append(next_sibling)

    return paragraphs


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


def contains_feasability(s) -> bool:
    return bool(regex_feasability.search(string=s.lower()))


# %%
toelichting_files = list(Path("../data/plan_documents").iterdir())
toelichting_htmls = [f for f in toelichting_files if f.suffix == ".html"]
feasability_HTML_contents = {}
for fp in tqdm(toelichting_htmls):
    IMRO = fp.stem
    with open(fp, "r", encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")
    div_tags = soup.find_all("div")
    div_ids = [div["id"] for div in div_tags if "id" in div.attrs]
    feasability_divs = [i for i in div_ids if contains_feasability(i)]
    sents = []
    for div in feasability_divs:
        target_div = soup.find("div", id=div)
        contents = MarkdownConverter().convert_soup(target_div)
        contents = [x.strip() for x in contents.split("\n") if x.strip() != ""]
        for c in contents:
            sents += [sent.text for sent in nlp(c).sents]
    feasability_HTML_contents[IMRO] = sents

cleaned_sents = {}
for k in tqdm(feasability_HTML_contents.keys()):
    correct_sents = []
    for item in feasability_HTML_contents[k]:
        doc = nlp(item)
        if "#" in item:
            correct_sents.append(item)
            continue
        for sent in doc.sents:
            if sent[0].is_title and sent[-1].is_punct:
                tokens = {token.pos_ for token in sent}
                if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
                    "VERB" in tokens
                ):
                    correct_sents.append(item)
    cleaned_sents[k] = list(set(correct_sents))
# %%
with open("../data/HTML_feasability_sections.json", "w") as f:
    f.write(json.dumps(cleaned_sents, indent=4))
# %%
