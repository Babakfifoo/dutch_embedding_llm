# %%
import logging
from tqdm import tqdm
from pathlib import Path
from markdownify import markdownify as md

logging.basicConfig(
    filename="logs/03.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

toelichting_files = list(Path("../data/plan_documents/html").iterdir())

for fp in tqdm(iterable=toelichting_files):
    IMRO = fp.stem
    try:
        with open(fp, "r", encoding="utf-8") as f:
            html_content = f.read()

        md_text = [
            x.strip()
            for x in md(html=html_content, strip=["a", "b"]).split("\n")
            if len(x.strip()) > 5
        ]
        logging.info(f"\t{IMRO}: Converted to markdown.")
        with open(f"../data/plan_documents/md/{IMRO}.md", "w", encoding="utf-8") as f:
            f.write("\n\n".join(md_text))
        logging.info(f"\t{IMRO}: Done!")
    except Exception as e:
        logging.error(f"\t{IMRO}: Conversion Failed: {e}")

# %%
