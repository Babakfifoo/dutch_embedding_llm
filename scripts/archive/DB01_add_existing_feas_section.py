# %%
import sqlite3
import json
from tqdm import tqdm

from DB00_setup_db import TABLE_LU, SQLITE_DB_PATH

# %%
EXISTING_FEAS_JSON_FP = (
    "../data/plan_documents/Dashboard_outputs/D02_validated_feasability_section.json"
)

with open(EXISTING_FEAS_JSON_FP, mode="r", encoding="utf-8") as f:
    existing = json.loads(f.read())

conn = sqlite3.connect("../data/landuse.db")
cursor = conn.cursor()
# %%
for k, v in existing.items():
    feasability_text = v.get("feasability text").replace("'", "''").replace("\x00", "")
    if feasability_text == "":
        continue
    sql_upsert = f"""
        INSERT INTO {TABLE_LU} (imro, feasability_text) VALUES ('{k.replace("t_", "")}', '{feasability_text}')
        ON CONFLICT(imro) DO UPDATE SET feasability_text=('{feasability_text}')
        """
    cursor.execute(sql_upsert)
    conn.commit()

# %%
EXISTING_COST_BRIEF = "../data/Answers/C01_cost_recovery_detection.json"
with open(EXISTING_COST_BRIEF, mode="r", encoding="utf-8") as f:
    existing = json.loads(f.read())
for item in tqdm(existing):
    cost_recovery = item.get("cost_recovery").replace("'", "''").replace("\x00", "")
    sql_upsert = sql_upsert = f"""
        UPDATE {TABLE_LU}
        SET llm_cost_brief = '{cost_recovery}'
        WHERE imro = '{item.get("imro").replace("t_", "")}';
        """
    cursor.execute(sql_upsert)
    conn.commit()
# %%


## Correcting MD formatting of feasability section:

import mdformat

conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()
cursor.execute(f"select imro from {TABLE_LU}")
imro_list = [row[0] for row in cursor.fetchall()]


for i, imro in tqdm(enumerate(imro_list, 1), total=len(imro_list)):
    cursor.execute(
        f"SELECT feasability_text FROM {TABLE_LU} WHERE imro = ?",
        (imro,),
    )
    (feasability_text,) = cursor.fetchone()
    break
# %%
print(feasability_text)

print(mdformat.text(feasability_text))
# %%
