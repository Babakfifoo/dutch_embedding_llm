# %%
import logging
import json
import re
# %%
with open("../data/translations_pdf_20250107.json", "r") as f:
    data=json.loads(f.read())
# %%
sentences = "\n".join(list(data["t_NL.IMRO.0063.140503-VA01"][0].values())).split("\n")
# %%
sentences
# %%
pattern = r"(?:uitvoerbaarheid|haalbaarheid|economische|Uitvoeringsaspecten)"
regex = re.compile(pattern)

def contains_feasability(s):
    return bool(regex.search(s.lower()))
# %%
sentences