# %%

import sqlite3
from tqdm import tqdm
import logging
from Tools import ask_LLM, bool_cleaner, BoolAnswer
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

logging.basicConfig(
    filename="./logs/P07.log",
    encoding="utf-8",
    level=logging.WARNING,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
# %%

"""
This prompt is done in two stage. One is simplifying the text on whether land exploitation is used.
Second prompt draws conclusion of weather land development is happening within the planned area. 

This indicator is necessary, as if no land development is occured, the economic feasibility could be assured using much more simplified methods such as planning fees, or the plan damage agreements. 
"""


prompt: str = """
    
    # CONTEXT:
    
    ## ECONOMIC FEASIBILITY SECTION IN DUTCH:
    
    {feas_nl}
    
    ## ECONOMIC FEASIBILITY SECTION IN ENGLIGH:
    
    {feas_en}
    
    # INSTRUCTIONS
    The context is the economic feasibility section of land use plan in the Netherlands. 
    Based on the provided context, is there land development, or land exploitation done on the planned area??

    Answer onely based on the context provided.

    """

cursor.execute(
    f"select imro from {TABLE_LU} where length(feasability_en) > 10 AND land_dev IS NULL order by imro"
)
imro_list = [row[0] for row in cursor.fetchall()]
# %%

for i, imro in tqdm(enumerate(imro_list, 1), total=len(imro_list)):
    cursor.execute(
        f"SELECT feasability_text, feasability_en FROM {TABLE_LU} WHERE imro = ?",
        (imro,),
    )

    (feas_nl, feas_en) = cursor.fetchone()

    passsed_prompt: str = prompt.format(
        feas_nl=feas_nl.replace("#", ""), feas_en=feas_en.replace("#", "")
    )

    respond: str = ask_LLM(
        prompt=passsed_prompt,
        model="gemma3:4b",
        response_format="",
    )["message"]["content"]
    sanitised_respond: str = (
        respond.replace("\x00", "")
        .replace("\xa0", "")
        .replace(r"'", r"''")
        .replace("”", '"')
        .replace("“", '"')
    )
    sql_upsert = f"""
    UPDATE {TABLE_LU}
    SET land_dev = '{sanitised_respond}'
    WHERE imro = '{imro}';
    """
    cursor.execute(sql_upsert)
    conn.commit()

conn.close()
# %%


prompt: str = """
    
    # CONTEXT:
    
    {land_dev}
    
    # INSTRUCTIONS
    The context is the economic feasibility section of land use plan in the Netherlands. 
    
    Based on the provided context, is there land development, or land exploitation done on the planned area?
    
    Answer onely based on the context provided.
    
    You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "ans": <true_or_false>
        }}
    Where <true_or_false> is either the boolean `true` or `false`.
    Do not include any other text or explanation.

    """
cursor.execute(f"select imro from {TABLE_LU} where land_dev IS NOT NULL order by imro")
imro_list = [row[0] for row in cursor.fetchall()]
for i, imro in tqdm(enumerate(imro_list, 1), total=len(imro_list)):
    cursor.execute(
        f"SELECT land_dev FROM {TABLE_LU} WHERE imro = ?",
        (imro,),
    )

    (land_dev,) = cursor.fetchone()

    passsed_prompt: str = prompt.format(land_dev=land_dev)

    respond: str = bool_cleaner(
        ask_LLM(
            prompt=passsed_prompt,
            model="gemma3:4b",
            response_format=BoolAnswer.model_json_schema(),
        )["message"]["content"]
    )

    sql_upsert = f"""
    UPDATE {TABLE_LU}
    SET land_dev_bool = '{respond}'
    WHERE imro = '{imro}';
    """
    cursor.execute(sql_upsert)
    conn.commit()

conn.close()
# %%
