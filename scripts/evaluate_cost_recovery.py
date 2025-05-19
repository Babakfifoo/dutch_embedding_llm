# %%
import json
from tqdm import tqdm
import logging
from tools import promptTools
import re
import pandas as pd

logging.basicConfig(
    filename="logs/04.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def remove_span(s):
    pattern = r'<span\s+id=".+?">.*?</span>'
    output_string = re.sub(pattern, "", s, flags=re.DOTALL | re.IGNORECASE)
    return output_string


def process_and_translate(plan):
    nl = []
    en = []
    for i, para in enumerate(plan[1]):
        sents = promptTools.extract_sentences(s=para, para=i)
        if sents == {}:
            sents = {f"{i}:1": remove_span(para)}

        translations = promptTools.translate_para(sentences=sents)
        nl.append(" ".join(translations.get("nl", None)))
        en.append(" ".join(translations.get("en", None)))

    nl = "\n\n".join(nl)
    en = "\n\n".join(en).replace("story", "recovery")
    return {"IMRO": plan[0], "nl": nl, "en": en}


# %%
with open("../data/new/texts/feasability_section.json", "r", encoding="utf-8") as f:
    feas_text = json.loads(f.read())

TRANSLATIONS = pd.read_parquet("../data/new/translations/translations.parquet")

# %%

for plan in tqdm(feas_text.items()):
    if plan[0] not in TRANSLATIONS["IMRO"].to_list():
        translation = pd.json_normalize(process_and_translate(plan))
        TRANSLATIONS = pd.concat([TRANSLATIONS, translation], ignore_index=True)
        TRANSLATIONS.to_parquet("../data/new/translations/translations.parquet")

# %%

TOPIC = "anterior agreement"


prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether anterior agreement or contract is used, concluded or layed down.
If context explicitely mentions any form of agreement or contract is made, concluded or signed, answer 'True', otherwise 'False'.

Do not provide any additional information.
Only use the context provided.


#### context:

{context}

"""

entry = {
    "IMRO": plan[0],
    "topic": TOPIC,
    "context": TRANSLATIONS.iloc[3].to_dict().get("en"),
}
en_answer = promptTools.bool_cleaner(
    s=promptTools.ask_LLM(entry=entry, prompt=prompt)["message"]["content"]
)
entry["context"] = TRANSLATIONS.iloc[3].to_dict().get("nl")
nl_answer = promptTools.bool_cleaner(
    s=promptTools.ask_LLM(entry=entry, prompt=prompt)["message"]["content"]
)
# %%
