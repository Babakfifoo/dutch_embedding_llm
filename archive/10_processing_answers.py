#%%
import pandas as pd
from tqdm import tqdm
import logging
import json
import re
from pathlib import Path
logging.basicConfig(
    filename="pdf_parsing.log", 
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s')


def extract_between_curly_braces(text):
    pattern = r'{([^{}]+)}'
    return re.findall(pattern, text)


def extract_digits(s):
    return re.findall(r'\d+', s)


def find_no(s):
    return re.find(r'no', s)


def find_yes(s):
    return re.find(r'yes', s)


def find_yes_no(s):
    if s is None:
        return None
    if bool(re.search(r'\byes\b', s.lower())):
        return "yes"
    if bool(re.search(r'\bno\b', s.lower())):
        return "no"
    return "Not Mentioned"


def process_entries(entry):
    if "\n" in v:
        test = pd.DataFrame(data={"entry": v.split("\n")})
        
    test[["question", "answer"]] = test["entry"].str.split(":", expand=True, n=1)
    test = test.dropna().reset_index(drop=True)
    test.question = test.question.apply(extract_digits).str[0]
    test.answer = (
        test.answer
        .str.replace('"', "")
        .str.replace(',', "")
        .replace("Not mentioned", None)
        .str.strip()
        )
    return test.set_index("question")[["answer"]].T.reset_index(drop=True)


# %%
parsed_pdfs = list(Path("../data/html_answers").iterdir())
Q_names=[("Q" + str(i).zfill(2)) for i in range(1,26) if i != 10] # there is no question 10
cleaned_answers=[]
for fp in tqdm(parsed_pdfs):
    with open(file=fp, mode="r") as f:
        data = json.loads(f.read())
    for k,v in data.items():
        try:
            if "\n" in v:
                delim = "\n"
            else:
                delim= ","
            if v.count("[") == 0:
                if v.count("{") == 1:
                    v = v.split("{")[1].split("}")[0]
                q_a = [k.split(":") for k in v.split(delim)]
                q_a = [i for i in q_a if len(i) == 2]
                q_a = dict(zip(Q_names,[find_yes_no(a) for (_,a) in q_a]))
            else:
                q_a = dict(zip(Q_names,[find_yes_no(k) for k in v.split(delim)]))
            q_a["IMRO"] = k
            q_a["model"] = fp.stem
            q_a["invalid"] = False
            cleaned_answers.append(q_a)
        except:
            cleaned_answers.append({"invalid": True, "IMRO": k})
# %%
answers_df = pd.DataFrame(cleaned_answers)
answers_df = answers_df[answers_df.columns.sort_values()]
# %%
model_names = {
    'gemma2': 'gemma2:2b',
    'gemma2_500': 'gemma2:2b',
    'granite_html': 'granite3.1-dense:2b',
    'llama3.2_html': 'llama3.2:3b',
    'mistral_html': 'mistral:7b-instruct',
    'qwen2.5_html': 'qwen2.5:3b',
}
answers_df.model = answers_df.model.replace(model_names).astype("category")
answers_df.dropna().to_parquet("../data/HTML_cleaned_answers.parquet")
# %%

(
    answers_df
    .drop(columns=["invalid", "model"])
    .dropna()
    .melt("IMRO")
    .value_counts()
    .reset_index()
    .pivot_table(index=["IMRO","variable"], columns=["value"])
    )
# %%
