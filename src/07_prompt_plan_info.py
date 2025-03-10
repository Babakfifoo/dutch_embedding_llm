# %%
import json
from rapidfuzz import fuzz
from tqdm import tqdm
import logging
from ollama import chat

logging.basicConfig(
    filename="./logs/08.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def find_topic(s, q, threshold=90) -> bool:
    # This ignores the sentences that contain examples to prevent bias.
    if "example" in s:
        return False
    for query in q:
        score = fuzz.partial_ratio(s1=s, s2=query)
        if score > threshold:
            return True
    return False

with open("../data/plan_documents/translated_selected_sents.json", "r") as f:
    texts = [x for x in json.loads(f.read())]


prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about type of land use plans in the Netherlands.
If this land use plan is explicitly a 'building plan', answer 'True', otherwise 'False'.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.


#### context:

{context}

"""

TOPIC = "building Plan"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(plan.get("en"))
        if "'building plan'" in s.lower()
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"],
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(topic_1, indent=4))

# %%
prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about the land use plans in the Netherlands.
If this land use plan is explicitly a 'land exploitation scheme', answer 'True', otherwise 'False'.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.


#### context:

{context}

"""

TOPIC = "land exploitation scheme"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(plan.get("en"))
        if find_topic(s.lower(), ["land exploitation scheme"], threshold=THRESHOLD)
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"],
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(topic_1, indent=4))
# %%
