# %%
import json
from tqdm import tqdm
import logging
from tools import promptTools

logging.basicConfig(
    filename="./logs/DCP.log",
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
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether an exploitation plan, operating plan, or operation plan is made or drawn up, answer 'True', otherwise 'False'.

Do not provide any additional information.
Only use the context provided.


#### context:

{context}

"""

TOPIC = "DCP"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    entry["context"] = (
        " ".join(plan.get("en"))
        .replace("story", "recovery")
    )
    answer = promptTools.ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry.pop("context", None))  # removing the context when it is not filtered.

with open(f"../data/new/LLM_answers/{TOPIC}.json", "w") as f:
    f.write(json.dumps(topic_1, indent=4))
# %%
