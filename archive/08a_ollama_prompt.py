# %%
import json
from tqdm import tqdm
import logging
from ollama import chat
logging.basicConfig(
    filename="./logs/08.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


with open("../data/plan_documents/translations/html_translated.json", "r") as f:
    texts = [x for x in json.loads(f.read())]
# %%

prompt = """
    Analyze the following text and instrauctions:
    **Instructions**:
    Only output the answer in short anc consice in one phrase or sentence, and no other explaination.
    Do not hallucinate.
    {questions}
    
    **Text**:
    {text}

    """
# %%
    
questions = """
return the number of the agreement types in this list that are concluded in the text in a list of numbers:
    1. Anterior agreement
    2. plan damage agreement
    3. purchase agreement/contract
    4. operating agreement


If the information does not exist, return None.

output example:
    [1,3,4]
Do not add any extra text to the output
"""

all_answers = []
for i, plan in tqdm(enumerate(texts)):
    context = "\n".join(plan.get("en")).replace("story", "recovery")
    answer_dict = {"IMRO": plan.get("IMRO")}
    if context == []:
        continue
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(text=context, questions=questions),
            }
        ],
        options=dict(temperature=0, max_tokens=50),
    )

    answer_dict["ans"] = answer["message"]["content"]

    all_answers.append(answer_dict)
    logging.info(msg=f"{answer_dict.get('IMRO')} --> llama3.2:3b Answered")
    if (i + 1) % 100 == 0:
        with open(f"../data/plan_documents/answered/html_agreement.json", "w") as file:
            file.write(json.dumps(all_answers, indent=4))
        logging.info(msg=f"{i + 1} plans stored")
# %%

# %%

# %%
questions = """
Which one of these costs recovery methods are being used?
    1: Anterior agreement.
    2: plan damage agreement.
    3: purchase agreement/contract.
    4: operating agreement.
    5: cooperation agreement.
    6: sales agreement.
    7: Realisation agreement.
    8: Land Exploitation agreement.
    9: Land sale.
    10: Land issue.
    11: Costs born by initiator, applicant, developer or land owner.
    12: From fees.
    13: from regulations.
    14: from Land Exploitation.
    15: Municipality budget.
    16: No costs expected.
    17: municipality owned land.
    18: Land Exploitation.
    19: Land Operation.
    20: Operating plan.
    21: Exploitation Plan
    22. Selling plots, lands, or lots.

output example:
    [1, 10, 14]
Do not add any extra text to the output
"""
all_answers = []
for i, plan in tqdm(enumerate(texts)):
    context = "\n".join(plan.get("en")).replace("story", "recovery")
    answer_dict = {"IMRO": plan.get("IMRO")}
    if context == []:
        continue
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(text=context, questions=questions),
            }
        ],
        options=dict(temperature=0, max_tokens=50),
    )

    answer_dict["ans"] = answer["message"]["content"]

    all_answers.append(answer_dict)
    logging.info(msg=f"{answer_dict.get('IMRO')} --> llama3.2:3b Answered")
    if (i + 1) % 100 == 0:
        with open(f"../data/plan_documents/answered/cost_recovery_html.json", "w") as file:
            file.write(json.dumps(all_answers, indent=4))
        logging.info(msg=f"{i + 1} plans stored")
# %%
questions = """
**Question**
Who Owns the land? answer in one sentence or phrase, or just the name.
Do not add any extra text to the output
"""
all_answers = []
for i, plan in tqdm(enumerate(texts)):
    sents = [s for s in plan.get("en") if ' owns' in s]
    context = "\n\n".join(sents).replace("story", "recovery")
    answer_dict = {"IMRO": plan.get("IMRO")}
    if len(sents) != 0:
        
        if context == []:
            continue
        answer = chat(
            model="llama3.2:3b-instruct-q5_K_M",
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(text=context, questions=questions),
                }
            ],
            options=dict(temperature=0.7, max_tokens=50),
        )

        answer_dict["ans"] = answer["message"]["content"]
        all_answers.append(answer_dict)

    logging.info(msg=f"{answer_dict.get('IMRO')} --> llama3.2:3b Answered")
    if (i + 1) % 100 == 0:
        with open(f"../data/plan_documents/answered/html_landowner.json", "w") as file:
            file.write(json.dumps(all_answers, indent=4))
        logging.info(msg=f"{i + 1} plans stored")
# %%
questions = """
**Question**
Is land owned by the municipality? or is it owned by the developer/initiator/applicant?
"""
# raise ValueError("Implement the spacy noun and name detection. Se if we can find the developer names.")
all_answers = []
for i, plan in tqdm(enumerate(texts)):
    sents = [s for s in plan.get("en") if ' own' in s]
    context = "\n\n".join(sents).replace("story", "recovery")
    answer_dict = {"IMRO": plan.get("IMRO")}
    if len(sents) != 0:
        if context == []:
            continue
        answer = chat(
            model="llama3.2:3b-instruct-q5_K_M",
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(text=context, questions=questions),
                }
            ],
            options=dict(temperature=0.7, max_tokens=50),
        )

        answer_dict["ans"] = answer["message"]["content"]
        all_answers.append(answer_dict)

        logging.info(msg=f"{answer_dict.get('IMRO')} --> llama3.2:3b Answered")
    if (i + 1) % 100 == 0:
        with open(f"../data/plan_documents/answered/html_landowner_name.json", "w") as file:
            file.write(json.dumps(all_answers, indent=4))
        logging.info(msg=f"{i + 1} plans stored")
# %%
# %%

municipality_land = []
for i, plan in tqdm(enumerate(all_answers)):
    if context == []:
        continue
    answer = chat(
        model="llama3.2:3b-instruct-q5_K_M",
        messages=[
            {
                "role": "user",
                "content": prompt.format(text=context, questions="Is land owned by the municipality? answer in yes or no"),
            }
        ],
        options=dict(temperature=0.7, max_tokens=50),
    )

    answer_dict["ans"] = answer["message"]["content"]
    municipality_land.append(answer_dict)
    if (i + 1) % 100 == 0:
        with open(f"../data/plan_documents/answered/html_municipality_owns_pand.json", "w") as file:
            file.write(json.dumps(all_answers, indent=4))
        logging.info(msg=f"{i + 1} plans stored")
# %%
    