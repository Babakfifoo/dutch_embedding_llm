# %%
import logging
from tqdm import tqdm
from pathlib import Path
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser

logging.basicConfig(
    filename="logs/02.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

config = {
    "output_format": "markdown",
    "languages": "nl",
    "disable_image_extraction": True,
    "processors": "marker.processors.text.TextProcessor",
    "LOKY_MAX_CPU_COUNT": 8,
}

config_parser = ConfigParser(config)
converter = PdfConverter(
    artifact_dict=create_model_dict(), config=config_parser.generate_config_dict()
)

# %%
toelichting_files = list(Path("../data/plan_documents/pdf").iterdir())

for fp in tqdm(iterable=toelichting_files[2755:]):
    IMRO = fp.stem
    try:
        document = converter(filepath=str(fp))

        logging.info(f"\t{IMRO}: Converted to markdown.")
        with open(f"../data/plan_documents/md/{IMRO}.md", "w", encoding="utf-8") as f:
            f.write(document.markdown)
        logging.info(f"\t{IMRO}: Done!")

    except Exception as e:
        logging.error(f"\t{IMRO}: Conversion Failed: {e}")

# %%
