# %%

import sqlite3
import json

from tqdm import tqdm
import logging
from tools import promptTools
from tools.promptsDA import AgreementPrompt, AgreementType, AGREEMENT_LIST
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

logging.basicConfig(
    filename="./logs/P11.log",
    encoding="utf-8",
    level=logging.WARNING,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()

cursor.execute(f"select imro from {TABLE_LU} where length(llm_cost_brief) > 10")
imro_list = [row[0] for row in cursor.fetchall()]


# %%
for i, imro in tqdm(enumerate(imro_list, start=1), total=len(imro_list)):
    cursor.execute(
        f"SELECT feasability_text, llm_cost_brief FROM {TABLE_LU} WHERE imro = ?",
        (imro,),
    )
    (feasability_text, brief) = cursor.fetchone()

    answer: bool = promptTools.bool_cleaner(
        promptTools.ask_LLM(
            prompt=AgreementPrompt.prompt.format(context=brief),
            response_format=AgreementPrompt.schema,
        )["message"]["content"]
    )
    if answer:
        context = f"""
        ## Land use document text:
        
        {feasability_text}
        
        ## Summary:
        
        {brief}
        
        
        
        """
        agreement_type: str = (
            promptTools.ask_LLM(
                context=feasability_text,  # here extracting agreement names from the original text.
                prompt=AgreementType.prompt,
                response_format=AgreementType.schema,
            )["message"]["content"]
            .replace("'", "''")
            .replace("\x00", "")
        )
    else:
        agreement_type = None

    try:
        sql_upsert = f"""
        UPDATE {TABLE_LU}
        SET agreement = '{answer}', agreement_type='{agreement_type}'
        WHERE imro = '{imro}';
        """
        cursor.execute(sql_upsert)
        conn.commit()

    except Exception as e:
        logging.warning(imro, ": could not detect agreement :", e)


# %%
