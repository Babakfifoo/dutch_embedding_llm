# %%

import sqlite3
from tqdm import tqdm
import logging
from tools import promptTools
from tools.promptsLandPrice import LandPriceYN
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

logging.basicConfig(
    filename="./logs/P12.log",
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
    context = f"""
    
    ** Land use document **:
    
    {feasability_text}
    
     ** summary **:
    
    {brief}
    """
    answer: bool = promptTools.bool_cleaner(
        promptTools.ask_LLM(
            context=context,
            prompt=LandPriceYN.prompt,
            response_format=LandPriceYN.schema,
        )["message"]["content"]
    )

    try:
        sql_upsert = f"""
        UPDATE {TABLE_LU}
        SET land_price_used = {answer}
        WHERE imro = '{imro}';
        """
        cursor.execute(sql_upsert)
        conn.commit()

    except Exception as e:
        logging.warning(imro, ": could not detect agreement :", e)

# %%
