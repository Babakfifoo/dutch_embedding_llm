# %%
import sqlite3
from tqdm import tqdm
import logging
from Tools import ask_LLM, bool_cleaner, BoolAnswer
from ollama import chat
from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

logging.basicConfig(
    filename="./logs/P03.log",
    encoding="utf-8",
    level=logging.WARNING,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
# %%


prompt: str = """
    
    # CONTEXT:
    
    ## ECONOMIC FEASIBILITY SECTION IN DUTCH:
    
    {feas_nl}
    
    ## ECONOMIC FEASIBILITY SECTION IN ENGLIGH:
    
    {feas_en}
    
    # INSTRUCTIONS
    
    Based on the provided context, is explicitely mentioned that operating plan or exploitatieplan are not made, is unnecessary, or cannot be made?
    
    Answer onely based on the context provided.
    You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "ans": <true_or_false>
        }}
    Where <true_or_false> is either the boolean `true` or `false`.
    Do not include any other text or explanation.

    """

# %%


conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
cursor.execute(
    f"select imro from {TABLE_LU} where length(feasability_en) > 10 order by imro"
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

    respond: str = bool_cleaner(
        ask_LLM(
            prompt=passsed_prompt,
            model="gemma3:4b",
            response_format=BoolAnswer.model_json_schema(),
        )["message"]["content"]
    )

    sql_upsert = f"""
    UPDATE {TABLE_LU}
    SET dcp_unnecessary = '{respond}'
    WHERE imro = '{imro}';
    """
    cursor.execute(sql_upsert)
    conn.commit()

conn.close()

# %%
