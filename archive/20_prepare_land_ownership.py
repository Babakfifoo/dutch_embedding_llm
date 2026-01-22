# %%
import pandas as pd
import geopandas as gpd
# %%

V0 = {
    120: "Public (municipality)",
    158: "Public (province)",
    203: "Public (Government, Water Board, and others)",
    253: "Person, legal entities",
    250: "Person, legal entities",
    200: "Company (developer)",
    204: "Mixed",
    216: "Company (other)",
    188: "Nature or recreation organisation",
    230: "Housing organisation or WE",
}

V1 = {
    98: "Public (municipality)",
    145: "Public (province)",
    196: "Public (Government, Water Board, and others)",
    247: "Person, legal entities",
    239: "Person, legal entities",
    62: "Company (developer)",
    204: "Mixed",
    134: "Company (other)",
    212: "Nature or recreation organisation",
    173: "Housing organisation or WE",
}

V2 = {
    144: "Public (municipality)",
    180: "Public (province)",
    217: "Public (Government, Water Board, and others)",
    234: "Person, legal entities",
    214: "Person, legal entities",
    40: "Company (developer)",
    204: "Mixed",
    101: "Company (other)",
    155: "Nature or recreation organisation",
    31: "Housing organisation or WE",
}

buildings = gpd.read_parquet("../data/PAND_GEOM.parquet")
projects = gpd.read_parquet("../data/db_proj_geom_dissolved.parquet")
projects = projects[["PROJID", "geometry"]].explode().dissolve("PROJID")
# %%
OWNERSHIP2016 = gpd.read_parquet("../data/ownership_points/PROJ_OWN_2016.parquet")
OWNERSHIP2016 = OWNERSHIP2016.sjoin(buildings.set_index("BLDID")[["geometry"]])

OWNERSHIP2016["r"] = OWNERSHIP2016["v0"].map(V0)
OWNERSHIP2016["g"] = OWNERSHIP2016["v1"].map(V1)
OWNERSHIP2016["b"] = OWNERSHIP2016["v2"].map(V2)

OWNERSHIP2016["rgb_same"] = OWNERSHIP2016[["r", "g", "b"]].apply(
    lambda x: len(set(x)) == 1, axis=1
)

OWNER2016_1 = (
    OWNERSHIP2016.query("(r.notna() & rgb_same)")[["BLDID", "r", "geometry"]]
    .rename(columns={"r": "OWNER"})
    .reset_index(drop=True)
    .pivot_table(index="BLDID", columns="OWNER", aggfunc="count", fill_value=0)
)
OWNER2016_1.columns = [x[1] for x in OWNER2016_1.columns]
OWNER2016_1["total"] = OWNER2016_1.sum(axis=1)

for col in [
    "Company (developer)",
    "Company (other)",
    "Housing organisation or WE",
    "Mixed",
    "Nature or recreation organisation",
    "Person, legal entities",
    "Public (municipality)",
    "Public (province)",
]:
    OWNER2016_1[col] = OWNER2016_1[col] / OWNER2016_1["total"]

OWNER2016_1["Company (other)"] = (
    OWNER2016_1["Company (developer)"] + OWNER2016_1["Company (other)"]
)
OWNER2016_1 = OWNER2016_1.drop("Company (developer)", axis=1)
OWNER2016_1["year"] = 2016
# %%
OWNERSHIP2020 = gpd.read_parquet("../data/ownership_points/PROJ_OWN_2020.parquet")
OWNERSHIP2020 = OWNERSHIP2020.sjoin(buildings.set_index("BLDID")[["geometry"]])
OWNERSHIP2020["r"] = OWNERSHIP2020["v0"].map(V0)
OWNERSHIP2020["g"] = OWNERSHIP2020["v1"].map(V1)
OWNERSHIP2020["b"] = OWNERSHIP2020["v2"].map(V2)
OWNERSHIP2020["rgb_same"] = OWNERSHIP2020[["r", "g", "b"]].apply(
    lambda x: len(set(x)) == 1, axis=1
)
OWNER2020_1 = (
    OWNERSHIP2020.query("(r.notna() & rgb_same)")[["BLDID", "r", "geometry"]]
    .rename(columns={"r": "OWNER"})
    .reset_index(drop=True)
    .pivot_table(index="BLDID", columns="OWNER", aggfunc="count", fill_value=0)
)
OWNER2020_1.columns = [x[1] for x in OWNER2020_1.columns]
OWNER2020_1["total"] = OWNER2020_1.sum(axis=1)

for col in [
    "Company (other)",
    "Housing organisation or WE",
    "Mixed",
    "Nature or recreation organisation",
    "Person, legal entities",
    "Public (municipality)",
    "Public (province)",
]:
    OWNER2020_1[col] = OWNER2020_1[col] / OWNER2020_1["total"]
OWNER2020_1["year"] = 2020
# %%

all_ownership = pd.concat([OWNER2020_1, OWNER2016_1])
all_ownership = all_ownership.merge(buildings[["BLDID", "geometry"]], on="BLDID")
all_ownership["cents"] = all_ownership.geometry
all_ownership = gpd.GeoDataFrame(all_ownership, geometry="cents", crs=28992)
all_ownership.cents = all_ownership.cents.centroid
all_ownership = all_ownership.sjoin(projects, how="inner")
all_ownership = all_ownership.set_geometry("geometry")
all_ownership["area"] = all_ownership.geometry.area
# %%
for col in [
    "Company (other)",
    "Housing organisation or WE",
    "Mixed",
    "Nature or recreation organisation",
    "Person, legal entities",
    "Public (municipality)",
    "Public (province)",
]:
    all_ownership[col] = all_ownership[col] * all_ownership["area"]
# %%
# %%
proj_ownership = all_ownership.groupby(["PROJID", "year"]).agg(
    {
        "Company (other)": "sum",
        "Housing organisation or WE": "sum",
        "Mixed": "sum",
        "Nature or recreation organisation": "sum",
        "Person, legal entities": "sum",
        "Public (municipality)": "sum",
        "Public (province)": "sum",
        "area": "sum",
    }
)


for col in [
    "Company (other)",
    "Housing organisation or WE",
    "Mixed",
    "Nature or recreation organisation",
    "Person, legal entities",
    "Public (municipality)",
    "Public (province)",
]:
    proj_ownership[col] = proj_ownership[col] / proj_ownership["area"]

proj_ownership = (
    proj_ownership.reset_index()
    .melt(["PROJID", "year", "area"], var_name="ownership", value_name="share")
    .query("share != 0")
    .reset_index(drop=True)
)
# %%

# %%
proj_ownership_main = (
    proj_ownership.query("share >= 0.7")
    .sort_values("share")
    .groupby(["PROJID", "year"])
    .last()
    .reset_index()
    .pivot_table(
        index=["PROJID"], values="ownership", columns="year", aggfunc="max"
    )
    .reset_index()
    .rename(columns={2016: "OWN2016", 2020: "OWN2020"})
)
proj_ownership_main.columns.name = None

classification = {
    "Company (other)": "COM",
    "Public (municipality)": "PUB",
    "Person, legal entities": "PRI",
    "Housing organisation or WE": "ASC",
    "Public (province)": "PUB",
}

proj_ownership_main["OWN2016CAT"] = proj_ownership_main["OWN2016"].map(classification)
proj_ownership_main["OWN2020CAT"] = proj_ownership_main["OWN2020"].map(classification)
# %%
proj_ownership_main.to_parquet("../data/db_proj_ownership.parquet", index=False)
# %%
proj_ownership_main.query("PROJID == 74")
# %%
