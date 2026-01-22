# %%
import logging
from tqdm import tqdm
from pathlib import Path
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
import os
# %%

logging.basicConfig(
    filename="./PDFparsing.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

config = {
    # 1. Output & Languages
    "output_format": "markdown",
    "languages": "nl",
    
    # 2. Vision Acceleration (The Speed Boost)
    "batch_multiplier": 2,                    # Global multiplier for all batches
    "layout_batch_size": 8,                   # Process 8 pages of layout at once
    "detection_batch_size": 8,                # Process 8 pages of text detection at once
    
    # 3. Lean Processing (Skipping Heavy AI)
    "ocr_engine": "None",
    "disable_ocr": True,
    "skip_math_processing": True,             # Skips Texify model
    "skip_table_processing": True,            # Skips Table-Transformer
    "detect_tables": False,
    "extract_images": False,
    "disable_image_extraction": True,
    "use_llm": False,
    "mode":"fast",
    # 4. Corrected Processors List
    "processors": [
        "marker.processors.text.TextProcessor",
        "marker.processors.layout.LayoutProcessor" 
    ],
    
    # 5. Content Filtering
    "BAD_SPAN_TYPES": ["PageFooter", "PageHeader", "Caption"],
}

# %%
os.environ["LOKY_MAX_CPU_COUNT"] = "4"        # Increase slightly for parallel image prep
os.environ["COMPILE_LAYOUT"] = "true"         # Enables Surya layout model compilation
# ATTENTION: run this script in Terminal and not the notebook setting. 
# There are issues with how ipykernel handels processes that causes issues with 
# marker-pdf
if __name__ == "__main__":
    config_parser = ConfigParser(config)
    converter = PdfConverter(
        artifact_dict=create_model_dict(), 
        config=config_parser.generate_config_dict()
    )
    toelichting_files = list(Path("./data/plan_documents/pdf").iterdir())

    for fp in tqdm(iterable=toelichting_files):
        IMRO = fp.stem
        if Path(f"./data/plan_documents/md/{IMRO}.md").exists():
            continue
        try:
            document = converter(filepath=str(fp))

            logging.info(f"\t{IMRO}: Converted to markdown.")
            with open(f"./data/plan_documents/md/{IMRO}.md", "w", encoding="utf-8") as f:
                f.write(document.markdown)
            logging.info(f"\t{IMRO}: Done!")

        except Exception as e:
            logging.error(f"\t{IMRO}: Conversion Failed: {e}")

# %%