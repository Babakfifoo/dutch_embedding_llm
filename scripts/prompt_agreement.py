# %%
import json
from tqdm import tqdm
import logging
from tools import promptTools

logging.basicConfig(
    filename="./logs/08.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


with open("../data/new/translations/translated.json", "r") as f:
    texts = [x for x in json.loads(f.read())]

# %%
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

TOPIC = "agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(plan.get("en"))
        if promptTools.find_topic(
            s.lower(),
            ["agreement", "contract"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
    )
    answer = promptTools.ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/new/LLM_answers/{TOPIC}.json", "w") as f:
    f.write(json.dumps(topic_1, indent=4))
# %%
