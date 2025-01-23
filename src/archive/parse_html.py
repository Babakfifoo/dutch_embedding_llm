# %%

from pathlib import Path
import re
import logging
import json
from bs4 import BeautifulSoup

import pymupdf
from markdownify import markdownify as md
from icecream import ic


logging.basicConfig(
    filename="pdf_parsing.log", 
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s')
# %%

def check_string(s:str):
    
    hoofdstuk_match = re.match(r"^hoofdstuk", s)
    num_match = re.match(r'^\d+', s)
    heading_match = re.match(r'^#', s)
    uitvoerbaarheid_match = re.search(r"uitvoerbaarheid", s)
    haalbaarheid_match = re.search(r"haalbaar.*", s)
    Financi_match1 = re.search(r"financiele", s)
    Financi_match1 = re.search(r"fina.*", s)
    Economische = re.search(r"economische", s)
    return (
            (
                bool(hoofdstuk_match) or 
                bool(num_match) or
                bool(heading_match) 
                ) and 
            (
                bool(uitvoerbaarheid_match) or
                bool(haalbaarheid_match) or
                bool(Financi_match1) or
                bool(Economische)
                )
        )
def extract_sections(file):
    # Fetch the content
    with open(file, 'r') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all heading tags
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # Extract text content from headings
    heading_text = [heading.get_text(strip=True) for heading in headings]
    selected_headings = [h for h in heading_text if check_string(h.lower())]
    sections = []
    for heading in selected_headings:
        section = {}
        for i, h in enumerate(headings):
            # Extract paragraphs after this heading
            if h.get_text(strip=True) != heading:
                continue
            section["heading"] = heading
            section["paragraphs"] = []
            for sibling in h.next_siblings:
                
                if sibling.name == 'h' and sibling.get('class') != h.get('class'):
                    break
                
                if sibling.name == 'p':
                    paragraph_text = sibling.get_text(strip=True).encode("utf-8").decode("latin-1")
                    section["paragraphs"].append(paragraph_text)
            
            # Skip the next heading if it's the same level
            if i + 1 < len(headings) and headings[i+1].name == h.name:
                continue
            
        section['paragraphs'] = [split_paragraph(x) for x in section['paragraphs'] if x != ""]
        sections.append(section)
    return sections


def split_paragraph(s:str):
    s = [(x + ".").replace("..", ".") for x in s.split(". ")]
    return(s)


def extract_paragraphs(heading:str):
    pass


# %%

directories =list(Path('./plans_need_processing_htmls').iterdir())
# %%
parsed_htmls = {}
for d in directories:
    toelichting_file = [f for f in list(d.iterdir()) if "t_" in f.name]
    if len(toelichting_file) == 0:
        continue
    if toelichting_file[0].suffix == ".html":
        logging.info(d.name + " -> Parsed")
        sections = extract_sections(toelichting_file[0])
        parsed_htmls[toelichting_file[0].name] = sections
# %%
with open("./htmls_parsed.json", "w", encoding="latin-1") as f:
    f.write(json.dumps(parsed_htmls, indent=4))

# %%
