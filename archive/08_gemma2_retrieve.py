
# %%
from ollama import chat
from ollama import ChatResponse

from tqdm import tqdm

import logging
import json

logging.basicConfig(
    filename="logs/04_LLMs.log", 
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:gemma2:2b:%(message)s')


with open("../data/translations_html.json", "r") as file:
    data = json.loads(file.read())

# %%

gemma2_prompt_template = """
**Prompt:**

You are an expert in urban planning. 
There are several questions asked about economic feasability section of a landuse plan in the Netherlands.
Answers must follow instructions carefully

**Instructions:**

- Please provide answers to the following questions about the provided text. 
- Answer each question with either "yes", "no", or "Not mentioned".
- Do not provide any additional text comments or explainations.
- Do not create answers. Use the provided context only.

**text:**

"{plan_string}"

**Questions:**

    Question 01: Is municipality the landowner of the planned area?
    Question 02: Is developer the landowner of the planned area?
    Question 03: Is the initiator the landowner of the area?
    Question 04: Is plan area on municipal land?
    Question 05: Is the municipality responsible for the costs?
    Question 06: Is the landowner responsible for costs?
    Question 07: Is the private sector responsible for costs?
    Question 08: Is the initiator responsible for costs?
    Question 09: Is costs covered by land sales?
    Question 11: Is costs covered by cost recovery?
    Question 12: Is there a need for expoitation plan?
    Question 13: Is it mentioned that exploitation plan is NOT needed?
    Question 14: Is it mentioned that operating plan is NOT needed?
    Question 15: Is municipality going to sell land?
    Question 16: Is municipality agreement mentioned?
    Question 17: Do municipality and initiator have an agreement?
    Question 18: Is the plan for housing construction?
    Question 19: Is land require preparation?
    Question 20: Is municipality taking care of land preperation?
    Question 21: Is the initiator taking care of land preparation?
    Question 22: Is there joint venture mentioned?
    Question 23: Is there a name of a company mentioned?
    Question 24: Is there a company owned by the municipality?
    Question 25: Is there PPP, PPS or Public Private Participation mentioned?


**Output:**

Please return the answers in JSON format, where:

* The keys are the question numbers.
* The values are the corresponding answers ("yes," "no," or "Not mentioned").
* do not add any other text
* the answer must be JSON in machine readable format

"""

gemma2_answers = {}

for i, (IMRO, plan_string) in tqdm(enumerate(data.items())):
    if plan_string == []:
        continue
    gemma2_answer: ChatResponse = chat(
        model='gemma2:2b',
        messages=[{
            'role': 'user',
            'content': gemma2_prompt_template.format(plan_string=plan_string[0]["text"]),
            }]
        )
    gemma2_answers[IMRO] = gemma2_answer['message']["content"]
    logging.info(msg=f"{IMRO} --> mistral Answered")
    if (i+1) % 100 == 0:
        with open(f"../data/gemma2.json", "w") as file:
            file.write(json.dumps(gemma2_answers, indent=4))
        logging.info(msg=f"{i+1} plans stored")
    if i == 3:
        break
# %%
