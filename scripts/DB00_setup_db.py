# %%
import sqlite3
from pathlib import Path
import re
from tqdm import tqdm


# %%
def remove_span(s):
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string


PLAN_DIR_MDS: str = "../data/plan_documents/md"
TABLE_LU: str = "landuse"
SQLITE_DB_PATH: str = "../data/landuse.db"
# %%


def main() -> None:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    with open(file="./sql/00_init_db.sql", mode="r") as q:
        cursor.executescript(q.read())
        conn.commit()

    # %%
    plan_doc_fp = list(Path(PLAN_DIR_MDS).iterdir())

    # %%
    for fp in tqdm(plan_doc_fp):
        with open(fp, "r", encoding="utf-8") as file:
            binary_md = remove_span(file.read()).replace("'", "''").replace("\x00", "")
        imro = fp.stem.replace("t_", "")
        sql_upsert = f"""
            INSERT INTO {TABLE_LU} (imro, md_file) VALUES ('{imro}', '{binary_md}')
            ON CONFLICT(imro) DO UPDATE SET md_file=('{binary_md}')
            """
        cursor.execute(sql_upsert)
        conn.commit()


if __name__ == "__main__":
    main()
