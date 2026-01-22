# %%
from pathlib import Path
import json
import requests
import dotenv
import os
from tqdm import tqdm

dotenv.load_dotenv(dotenv_path=".env")
# %%
url_download: str = "https://service.pre.omgevingswet.overheid.nl/publiek/omgevingsdocumenten/api/downloaden/v1/"
url_toepasbaaropvragen: str = "https://service.omgevingswet.overheid.nl/publiek/omgevingsdocumenten/api/toepasbaaropvragen/v7/"
API_IMRO: str = "https://ruimte.omgevingswet.overheid.nl/ruimtelijke-plannen/api/opvragen/v4/plannen/{planID}/"
API_besluitsubvlakken: str = "https://ruimte.omgevingswet.overheid.nl/ruimtelijke-plannen/api/opvragen/v4/plannen/{planID}/besluitsubvlakken"
API_enkel: str = "https://ruimte.omgevingswet.overheid.nl/ruimtelijke-plannen/api/opvragen/v4/plannen/{planID}/bestemmingsvlakken"
url_geometry: str = (
    "https://service.omgevingswet.overheid.nl/publiek/geometrie/api/valideren/v1/"
)
HEADERS: dict[str, str] = {
    "X-Api-Key": os.getenv("ruim_v4"),
}
response = requests.get(API_enkel.format(planID=""), headers=HEADERS)

# %%
imros = [x.stem.replace("t_", "") for x in Path("../data/plan_documents/md").iterdir()]
problematics = []
for IMRO in tqdm(imros):
    geom = requests.get(f"https://ruimtelijkeplannen.nl/documents/{IMRO}/{IMRO}.gml")
    try:
        with open(f"../data/plan_gmls/{IMRO}.gml", "w", encoding="latin-1") as f:
            f.write(geom.text)
    except:
        problematics.append(IMRO)

with open(f"../data/plan_gmls/problematics.json", "w", encoding="latin-1") as f:
    f.write(json.dumps(problematics, indent=4))
# %%
