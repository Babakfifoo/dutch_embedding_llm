# %%
import sqlite3
import re
import pandas as pd
import json
from typing import List

EXPERIMENT = False
PLAN_DIR_MDS: str = "../data/plan_documents/md"
SQLITE_DB_PATH: str = "../data/database.db"
SEED: int = 2025
TABLE_LU: str = "landuse" if not EXPERIMENT else "sample"
EXISTING_FEAS_JSON_FP: str = (
    "../data/plan_documents/Dashboard_outputs/D02_validated_feasability_section.json"
)


# %%
def clean_context(s: str) -> str:
    s_lst: List = s.split("\n")
    s_lst: List = [line.strip() for line in s_lst if line.count("|") < 5]
    s_lst: List = [line for line in s_lst if "---" not in line]
    s_lst: List = [line for line in s_lst if "..." not in line]
    s_lst: List = [line for line in s_lst if line.strip() != ""]
    return "\n\n".join(s_lst)


def remove_span(s: str) -> str:
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string


def create_db() -> None:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    with open(file="./sql/00_init_db.sql", mode="r") as q:
        cursor.executescript(q.read())
        conn.commit()


def migrate_manual_extractions() -> None:
    with open(EXISTING_FEAS_JSON_FP, mode="r", encoding="utf-8") as f:
        existing = json.loads(f.read())

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    for k, v in existing.items():
        feasability_text = (
            v.get("feasability text").replace("'", "''").replace("\x00", "")
        )
        if feasability_text == "":
            continue
        sql_upsert = f"""
            INSERT INTO landuse (imro, feasability_text) VALUES ('{k.replace("t_", "")}', '{feasability_text}')
            ON CONFLICT(imro) DO UPDATE SET feasability_text=('{feasability_text}')
            """
        cursor.execute(sql_upsert)
        conn.commit()


def generate_sample() -> None:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # dropping the existing sample table to recreate it.
    cursor.execute("DROP TABLE IF EXISTS sample;")
    conn.commit()

    cursor.execute(
        "SELECT imro FROM landuse WHERE LENGTH(feasability_text) > 10"
    )  # making sure only plans with extracted feasibility text are included.
    imro_list = [row[0] for row in cursor.fetchall()]
    df = pd.DataFrame({"imro": imro_list})
    df["GM"] = df.imro.str.split(".").str[2]
    df["GM_n"] = df.groupby("GM")["imro"].transform("count")

    sample_list = (
        df.query("GM_n > 1")
        .groupby("GM")
        .sample(2, random_state=SEED)["imro"]
        .to_list()
        + df.query("GM_n == 1")["imro"].to_list()
    )
    query = f"""
        UPDATE landuse
        SET selected_sample = 1
        WHERE imro IN ({",".join(["?"] * len(sample_list))})
    """
    cursor.execute(query, sample_list)
    conn.commit()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS sample AS SELECT * FROM landuse WHERE selected_sample = 1"
    )  # Creating a separate table for testing the pipeline.
    conn.close()


# %%

if __name__ == "__main__":
    create_db()
    migrate_manual_extractions()
    if EXPERIMENT:
        generate_sample()


# %%

# %%
