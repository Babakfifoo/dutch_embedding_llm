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
    answer: Literal[True, False]


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


with open("../data/plan_documents/translated_selected_sents.json", "r") as f:
    texts = [x for x in json.loads(f.read())]
# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether anterior agreement or contract is used, concluded or layed down.
If context explicitely mentions anterior agreement, anterior contract, private law contract, or private law agreement is used or concluded, answer 'True', otherwise 'False'.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.


#### context:

{context}

"""

TOPIC = "anterior agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(plan.get("en"))
        if find_topic(
            s.lower(),
            ["anterior agreement", "anterieure", "(anterior)", "private law agreement"],
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
        .replace("private law", "anterior")
        .replace("private-law", "anterior")
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(topic_1, indent=4))

# %%
prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands.
We want to see whether any form of exploitation agreement is concluded or will be used.

If context explicitely mentions that any form of exploitation agreements is signed, concluded, laid down, or will be concluded, answer 'True', otherwise 'False'.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

#### context:

{context}

"""

TOPIC = "operating agreement"
THRESHOLD = 95
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            ["exploitation agreement", "operating agreement"],
            threshold=THRESHOLD,
        )
        & ("cooperation agreement" not in s.lower())
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
        .replace("operating", "exploitation")
        .replace("Operating", "exploitation")
        .replace("contract", "agreement")
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

# %%
prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether an agreement is concluded or will be used to compensate the damages or plan damage costs.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that plan damage agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "plan damage agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            ["plan damage agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%
prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether purchase Agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that purchase agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "purchase agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            ["purchase agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether any form of cooperation Agreement is concluded or will be used.
If the context explicitely mentions that any form of cooperation agreement is used, laid down, concluded, or will be concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

#### context:

{context}

"""

TOPIC = "cooperation agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            ["cooperation agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether realisation Agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that realisation agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "realisation agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            ["realisation agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether reservation Agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that reservation agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "reservation agreement"
THRESHOLD = 90
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            ["reservation agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))
# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether agreement is concluded or will be used.
If the context explicitely mentions that any type of agreement is used between the municipality and initiator or applicant, concluded, will be concluded, layed down, under an agreement, or signed, answer 'True', otherwise 'False'.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

#### context:

{context}

"""

TOPIC = "agreement"
THRESHOLD = 80
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            [
                "municipality agreement applicant",
                "municipality agreement initiator",
                "municipality agreement developer",
            ],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands.
We want to see whether agreement is concluded or will be used.
If the context explicitely mentions that there "will" be an agreement or a contract, answer 'True', otherwise 'False'.

Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

#### context:

{context}

"""

TOPIC = "will agree"
THRESHOLD = 80
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            [
                "agreement", "contract"
            ],
            threshold=THRESHOLD,
        ) and ("will" in s.lower())
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        continue
    entry["context"] = " ".join([plan.get("en")[x] for x in selected_ids]).replace(
        "story", "recovery"
    )
    answer = ask_LLM(entry, prompt)
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%
