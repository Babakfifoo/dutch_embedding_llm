# %%
import json
from rapidfuzz import fuzz
from tqdm import tqdm
import logging
from ollama import chat
from typing import Literal
from pydantic import BaseModel

logging.basicConfig(
    filename="./logs/08.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# The output format
class Answer(BaseModel):
    ans: Literal[True, False]


def find_topic(s, q, threshold=90) -> bool:
    # This ignores the sentences that contain examples to prevent bias.
    if "example" in s:
        return False
    for query in q:
        score = fuzz.partial_ratio(s1=s, s2=query)
        if score > threshold:
            return True
    return False


def ask_LLM(entry, prompt):
    return chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"],
                ),
            }
        ],
        options=dict(
            temperature=0.0,  # reducing the variability of the answer
            seed=2025,  # Setting the Seed for prediction and reproducability
            num_predict=10,  # max number of tokens to predict
            top_k=10,  # More conservative answer
            min_p=0.9,  # minimum probability of token to be considered.
        ),
        format=Answer.model_json_schema(),
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
        if find_topic(
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
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/new/LLM_answers/{TOPIC}.json", "w") as f:
    f.write(json.dumps(topic_1, indent=4))
# %%
