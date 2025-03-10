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


# %%

with open("../data/plan_documents/translated_selected_sents.json", "r") as f:
    texts = [x for x in json.loads(f.read())]
# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether anterior agreement is used, concluded or layed down.
If context explicitely mentions anterior agreement is used or concluded, answer 'True', otherwise 'False'.

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
        if find_topic(s.lower(), ["anterior agreement"], threshold=THRESHOLD)
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
                    questions="Is municipality concluding an anterior agreement?",
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
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether exploitation agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

'land exploitation agreements', and 'exploitation agreement' are the same agreement.
If context explicitely mentions exploitation agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

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
            ["operating agreement", "exploitation agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
        .replace("operating", "exploitation")
        .replace("Operating", "Exploitation")
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"]
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

# %%
prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether Plan Damage Agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that plan damage agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "plan damage agreement"
THRESHOLD = 95
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
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"]
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
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
THRESHOLD = 95
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
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"]
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether cooperation Agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that cooperation agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "cooperation agreement"
THRESHOLD = 95
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
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"]
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
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
THRESHOLD = 95
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
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"]
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%

prompt = """
Analyze the following context, follow instructions:
#### Instructions:
We have the "context" containing information about cost recovery of the land use plans in the Netherlands. We want to see whether agreement is concluded or will be used.
Do not provide any additional information.
Do not hallucinate.
Only use the context provided.

If the context explicitely mentions that agreement is used or concluded, answer 'True', otherwise 'False'.
Answer in single False/True.

#### context:

{context}

"""

TOPIC = "agreement"
THRESHOLD = 95
topic_1 = []
for plan in tqdm(texts):
    selected_ids = [
        i
        for i, s in enumerate(iterable=plan.get("en"))
        if find_topic(
            s.lower(),
            [" agreement"],
            threshold=THRESHOLD,
        )
    ]
    entry = {
        "IMRO": plan.get("IMRO"),
        "topic": TOPIC,
    }
    if len(selected_ids) == 0:
        entry["answer"] = None
        entry["context"] = None
        continue
    entry["context"] = (
        " ".join([plan.get("en")[x] for x in selected_ids])
        .replace("story", "recovery")
    )
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"]
                ),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )
    entry["answer"] = answer["message"]["content"]
    topic_1.append(entry)

with open(f"../data/plan_documents/answered/{TOPIC}.json", "w") as f:
    f.write(json.dumps(obj=topic_1, indent=4))

# %%
