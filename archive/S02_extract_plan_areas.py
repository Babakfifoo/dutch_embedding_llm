# %%
import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
import os, requests
from html_to_markdown import convert
import time
import json
load_dotenv()
API_KEY: str = os.getenv("ruim_v4")

# %%
# This is to get the ENKLE codes for API query.
if False:
    plans = pd.read_parquet("../data/OUTPUT.parquet")
    Projects = gpd.read_parquet("../data/db_proj_geom_dissolved.parquet")
    enkels = gpd.read_file("../data/Enkelbestemming.gml.gz")

    enkel_selected = enkels.sjoin(Projects, how="inner")

    enkel_selected_cleaned = enkel_selected[
        [
            "PROJID",
            "bestemmingshoofdgroep",
            "naam",
            "plangebied",
            "dossierStatus",
            "planstatus",
            "typePlan",
            "datum",
            "identificatie",
            "verwijzingNaarExternPlan",
            "geometry",
        ]
    ].query("plangebied.isin(@plans.imro)")
    enkel_selected_cleaned.to_parquet("../data/db_selected_enkel.parquet")

enkel_geoms = gpd.read_parquet("../data/db_selected_enkel.parquet")
# %%

HEADERS = {
    "accept": "application/hal+json",
    "X-Api-Key": API_KEY,
}
PARAMS = {"bestemmingshoofdgroep": "", "expand": "teksten"}
ENKEL_ZOEK_EP = "https://ruimte.omgevingswet.overheid.nl/ruimtelijke-plannen/api/opvragen/v4/plannen/{planId}/bestemmingsvlakken"

for planId, g in enkel_geoms.groupby("plangebied"):
    uses = g.bestemmingshoofdgroep.unique()
    results = []
    for use in uses:
        PARAMS["bestemmingshoofdgroep"] = use
        enkel_zoek_res = requests.get(
            ENKEL_ZOEK_EP.format(planId=planId), headers=HEADERS, params=PARAMS
        ).json().get("_embedded").get("bestemmingsvlakken")
        results = results + enkel_zoek_res
    with open(f"../data/APIs/bestemmingsvlakken/{planId}.json", "w") as f:
        f.write(json.dumps(results))
    
    print(planId, " IS DONE!")
    time.sleep(0.1)


# %%

# GET ENKEL AREA (bestemmingsvlakken):


