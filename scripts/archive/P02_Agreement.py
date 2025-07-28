# %%
import json
from tqdm import tqdm
import logging
from ollama import ChatResponse
import json
import sqlite3
import spacy
from typing import List, Dict, Any
from tools import promptTools
from tools.promptsDA import DA_general
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
# %%


cursor.execute(f"select agreement_type from {TABLE_LU}")
agreement_list = [row[0] for row in cursor.fetchall() if row[0] != "None"]

nlp = spacy.load("nl_core_news_sm")
logging.basicConfig(
    filename="./logs/D02.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# %%

# LOADING FEASIBILITY TEXTS.

FEAS_TEXT: str = (
    "../data/plan_documents/Dashboard_outputs/D02_validated_feasability_section.json"
)
# Loading the context information
with open(file=FEAS_TEXT, mode="r", encoding="utf-8") as f:
    texts = json.loads(f.read())
CONTEXTS_COUNT: int = len(texts.keys())


# %%

# identifying the existing prompts.
# ATTENTION: renew the file if you are re-running the prompting from scratch!
# Make it a database recording with semi-structured data (SQLite + JSON)


if True:
    DA_detection_result: List[Any] = []
    OUTPUT: str = "../data/Answers/DA_if_detection.json"
    for i, (imro, plan) in tqdm(
        iterable=enumerate(iterable=texts.items()), total=CONTEXTS_COUNT
    ):
        entry: Dict[str, Any] = {"imro": imro, "if_agreement": None}
        if plan["feasability text"].lower() == "":
            continue
        if promptTools.find_topic(
            s=plan["feasability text"].lower(),
            q=DA_general.term_queries,
            threshold=DA_general.threshold,
        ):
            answer: ChatResponse = promptTools.ask_LLM(
                context=plan["feasability text"], prompt=DA_general.prompt
            )
            entry["if_agreement"] = promptTools.bool_cleaner(
                s=answer["message"]["content"]
            )

        DA_detection_result.append(entry)

        if (i + 1) % 10 == 0:
            with open(file=OUTPUT, mode="w", encoding="utf-8") as f:
                f.write(json.dumps(DA_detection_result, indent=4))
# %%
