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
    
    The context is the economic feasibility section of land use plan in the Netherlands in Dutch and its english translation. 
    Based on the provided context, write in simple language what is done. 
    Make sure to include these information if they are mentioned:
    
        - The entity responsible for costs
        
        - whether land exploitation is used
        
        - whether exploitatieplan is prepared, or is unnecessary
        
        - the land ownership
        
        - agrrements that are made, or will be made
        
        - type of the plan
        
        - name of the entities if mentioned
        
        - description of planning damages
        
    Answer onely based on the context provided. 
    Do not include the information that explains the laws and examples.
    
    """

# %%


conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
cursor.execute(
    f"select imro from {TABLE_LU} where length(feasability_text) > 10 AND llm_simplified IS NULL order by imro"
)
imro_list = [row[0] for row in cursor.fetchall()]


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
        model="gemma3:1b",
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
    SET llm_simplified = '{sanitised_respond}'
    WHERE imro = '{imro}';
    """
    cursor.execute(sql_upsert)
    conn.commit()

conn.close()
# %%
