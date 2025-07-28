# %%

import sqlite3
from tqdm import tqdm
import logging
from typing import List, Dict
import json
from rapidfuzz import process, fuzz
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH
from tools.promptsDA import AGREEMENT_LIST, AGREEMENT_FUZZ_CUTOFF_SCORE, DATypeUsed
from tools import promptTools

logging.basicConfig(
    filename="./logs/P11.log",
    encoding="utf-8",
    level=logging.WARNING,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
# %%

cursor.execute(f"select imro from {TABLE_LU} where length(llm_cost_brief) > 10")
imro_list = [row[0] for row in cursor.fetchall()]


# %%
def extract_agr_type(s: str) -> List[str] | None:
    if s is None:
        return
    try:
        return [v for v in json.loads(s).values()]
    except Exception as e:
        print(f"could not process {s} -> {e}")
        return


# %%

for i, imro in tqdm(enumerate(imro_list, 1), total=len(imro_list)):
    cursor.execute(
        f"SELECT feasability_text, llm_cost_brief FROM {TABLE_LU} WHERE imro = ?",
        (imro,),
    )
    (feasability_text, brief) = cursor.fetchone()
    results = process.extract(
        (
            feasability_text + " " + brief
        ).lower(),  # This checks both Brief and feasibility text to find agreements.
        list(AGREEMENT_LIST.keys()),
        scorer=fuzz.partial_token_sort_ratio,
        limit=3,  # Max 5 types of agreement could be mentioned in a text.
        score_cutoff=0,
    )
    if len(results) == 0:
        continue
    agreemets: Dict = dict()
    for agr in [r[0] for r in results]:
        context = f"""
        ** Feasiblity section:
        
        {feasability_text}
        
        ** Summary:
        
        {brief}
        
        """

        prompt = DATypeUsed.prompt.format(context=context, agr_type=agr)

        # prompting the LLM if it is explicitely mentioned that an agreement is made.
        agreemets[agr] = promptTools.bool_cleaner(
            promptTools.ask_LLM(
                prompt=prompt, response_format=DATypeUsed.schema, model="gemma3:1b"
            )["message"]["content"]
        )
    agreemets = {AGREEMENT_LIST.get(k) for k, v in agreemets.items() if v}
    if len(agreemets) == 0:
        continue
    try:
        sql_upsert = f"""
        UPDATE {TABLE_LU}
        SET agreement_used_list = '{json.dumps(list(agreemets))}'
        WHERE imro = '{imro}';
        """
        cursor.execute(sql_upsert)
        conn.commit()

    except Exception as e:
        logging.warning(imro, ": could not detect agreement :", e)

# %%

# %%

# Agreements


# Fees
"gemeentelijke legesverordening"


# PLD
"gronduitgifte"
"grondtransactie"
"grondcontract"
"aankoopovereenkomst"
