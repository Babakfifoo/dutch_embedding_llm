# %%
import pandas as pd
import sqlite3
import json
from Tools import DAS, INDICATORS

# %%
with sqlite3.connect("../data/database.db") as conn:
    df = pd.read_sql("SELECT * FROM landuse", conn).query("indicators.notna()")
    df["indicators"] = df["indicators"].apply(json.loads)


# %%
"""
* These factors indicate PLD:
'LI': 'Municipal land issue',
'LS': 'Municipal land/plot sale',
'LP': 'Municipal land price',
'MUL': 'Municipality land / land development',
'MDF': 'Municipality land dev. financing',
'PA': 'Private buys public land, Purchase agreement',
'LSA': 'Land sale agreement',

* These factors are Agreements:
'AA': 'Anterior agreement',
'EA': 'Exploitation agreement',
'RA': 'Realisation agreement',

* These are DCPs:
'DCP': 'Development Contributions Plans (DCP)',

* These are DCPs if not accompanied by agreements or PLDs:
'INI': 'Initiator/private party covers costs',
'PDA': 'Plan damage agreement',
'GA': 'General agreement',
'CRA': 'Cost recovery agreement',
'FEE': 'Levies and Fees',

* These are indicators of PPP:
'PPP': 'Public Private Partnership (PPP)',
'CA': 'Cooperation agreement',


* Special cases that could be used as indicators:
'PDP': 'Partly PLD', -> Accompanied by DCP or agreements
'DUO': 'Both DA and PLD',
'HS': 'Housing association', -> Housing association is a special case that can be combined with others
'SFS': 'Space-for-Space agreement', -> it is a special case.
'PPA': 'Public buys, Purchase agreement',

* These should be investigated if there are multiple projects in them:
'K10': 'Less than 10,00€ cost',
'PB': 'Public Budget',
'MUN': 'Municipality budget',
'CO': 'Conservative / no development / update plan',


"""


# %%
df_indicators = (
    df[["imro", "indicators"]]
    .explode("indicators")
    .pivot_table(index="imro", columns="indicators", aggfunc="size", fill_value=0)
)
df_indicators["PLD"] = (
    df_indicators[["LI", "LS", "LP", "MUL", "MDF", "PA", "LSA"]].sum(axis=1) > 0
).astype(int)
df_indicators["AGR"] = (df_indicators[["AA", "EA", "RA"]].sum(axis=1) > 0).astype(int)
df_indicators["PRI"] = (
    (df_indicators[["INI", "PDA", "GA", "CRA", "FEE"]].sum(axis=1) > 0)
    & (df_indicators["PLD"] == 0)
    & (df_indicators["AGR"] == 0)
).astype(int)
df_indicators["PPP"] = (df_indicators[["PPP", "CA"]].sum(axis=1) > 0).astype(int)
df_indicators["RM"] = (
    df_indicators[["K10", "PB", "MUN", "CO"]].sum(axis=1) > 0
).astype(int)

df_indicators[["PLD", "AGR", "PRI", "PPP", "DCP", "DUO", "PDP"]].value_counts()
df_indicators = df_indicators[
    ["PLD", "AGR", "PRI", "PPP", "DCP", "DUO", "PDP"]
].reset_index()
df_indicators.to_parquet("../data/OUTPUT.parquet")
# %%
