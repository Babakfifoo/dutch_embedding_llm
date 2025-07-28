# %%
import sqlite3
import json

from tqdm import tqdm
import logging
from tools import promptTools
from tools.promptChain import CostBrief
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

logging.basicConfig(
    filename="./logs/P10.log",
    encoding="utf-8",
    level=logging.WARNING,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
cursor.execute(
    f"select imro from {TABLE_LU} where feasability_text IS NOT NULL and llm_cost_brief is NULL"
)
imro_list = [row[0] for row in cursor.fetchall()]

# %%
if True:
    logging.info("Initiating the Extraction")
    for imro in tqdm(imro_list[1:]):
        cursor.execute(
            f"SELECT feasability_text FROM {TABLE_LU} WHERE imro = ?",
            (imro,),
        )
        (context,) = cursor.fetchone()
        # The prompt asks the LLM to include the information about the agreements.
        prompt: str = CostBrief.prompt.format(context=context.replace("#", ""))

        brief: str = str(
            promptTools.ask_LLM(
                prompt=prompt,
                response_format="json",
                model="gemma3:4b",
            )["message"]["content"]
            .replace("\x00", "")
            .replace("\xa0", "")
            .replace("'", "''")
            .replace("”", '"')
        )
        try:
            sql_upsert = f"""
            UPDATE {TABLE_LU}
            SET llm_cost_brief = '{brief}'
            WHERE imro = '{imro}';
            """
            cursor.execute(sql_upsert)
            conn.commit()

        except Exception as e:
            logging.warning(f"Could not generate summary for {imro}: {e}")
# %%

conn.commit()
conn.close()

# %%
