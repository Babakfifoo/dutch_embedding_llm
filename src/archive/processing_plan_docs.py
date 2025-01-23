# %%

from tqdm import tqdm
import pymupdf
from pathlib import Path
import re, logging
import json
from markdownify import markdownify as md
from icecream import ic
tqdm.pandas()

logging.basicConfig(
    filename="pdf_parsing.log", 
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s')
# %%
def check_string(s):
    
    hoofdstuk_match = re.match(r"^hoofdstuk", s)
    num_match = re.match(r'^\d+', s)
    heading_match = re.match(r'^#', s)
    
    uitvoerbaarheid_match = re.search(r"uitvoerbaar.*", s)
    haalbaarheid_match = re.search(r"haalbaar.*", s)
    Financi_match1 = re.search(r"finan.*", s)
    Economische = re.search(r"economi.*", s)
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

directories = [f for f in Path('./plans_need_processing_htmls').iterdir() if f.is_dir()]
# %%
pdf_results = {}
for pdir_ in Path('./plans_need_processing_htmls').iterdir():
    files = list(pdir_.iterdir())
    if len(files) == 0:
        continue

    toelichting = [f for f in files if 't_' in f.name][0]
    if toelichting.suffix == ".pdf":
        doc = pymupdf.open(toelichting)
        text = chr(12).join([page.get_text() for page in doc[3:]])
        
    if toelichting.suffix == ".html" or toelichting.suffix == ".xml":
        with open(toelichting, "r", encoding="utf-8") as html:
            html_txt = html.read()
            text = md(html_txt, strip=['a'])

    else:
        continue
    
    text_lst = [x for x in text.split(sep="\n") if x not in  [""]]
    try:
        index = [i for i, item in enumerate(iterable=text_lst) if check_string(s=str(object=item).lower())]
    except Exception as e:
        logging.warning(pdir_.name + f"{e}")
        continue
    
    text_lists = {}
    for idx in index:
        test_lst_2 = []
        paragraph = []
        sentense = ""
        for i, item in enumerate(iterable=text_lst[idx:(idx + 100)]):
            
            if item.strip() == "":
                if len(paragraph) != 0:
                    test_lst_2.append(paragraph)
                paragraph = [] 
                sentense = ""
                continue
                
            if len(item.strip()) == 0:
                continue
            
            sentense = sentense + item.strip()
            if item.strip()[-1] == ".":
                paragraph.append(sentense)
                sentense = ""
        text_lists[idx] = test_lst_2
    pdf_results[pdir_.name] = text_lists
    logging.info(pdir_.name + " -> Parsed")
        
# %%

with open("plan_feasability_parsed.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(pdf_results, indent=4))
# %%

    


# %%
