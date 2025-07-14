# %%
import sqlite3
import json
from tqdm import tqdm

# %%
EXISTING_FEAS_JSON_FP = (
    "../data/plan_documents/Dashboard_outputs/D02_validated_feasability_section.json"
)
TABLE_LU = "landuse"

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
