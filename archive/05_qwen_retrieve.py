
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
    format='%(asctime)s:%(levelname)s:qwen:4b:%(message)s')


with open("../data/translations_html.json", "r") as file:
    data = json.loads(file.read())

# %%

qwen_prompt_template = """
Act as an urban planner answering the questions about contents of a land-use plan in the Netherlands. 
Do not create answers. Use the provided context only.
Answers must be ONLY one of these:
    - "Yes"
    - "No"
    - "Not mentioned"

Do not comment on the answers.

Context:

The user is asking about this string of text:

{plan_string}

Questions:

    01) Is municipality the landowner of the planned area?
    02) Is developer the landowner of the planned area?
    03) Is the initiator the landowner of the area?
    04) Is plan area on municipal land?
    05) Is the municipality responsible for the costs?
    06) Is the landowner responsible for costs?
    07) Is the private sector responsible for costs?
    08) Is the initiator responsible for costs?
    09) Is costs covered by land sales?
    11) Is costs covered by cost recovery?
    12) Is there a need for expoitation plan?
    13) Is it mentioned that exploitation plan is NOT needed?
    14) Is it mentioned that operating plan is NOT needed?
    15) Is municipality going to sell land?
    16) Is municipality agreement mentioned?
    17) Do municipality and initiator have an agreement?
    18) Is the plan for housing construction?
    19) Is land require preparation?
    20) Is municipality taking care of land preperation?
    21) Is the initiator taking care of land preparation?
    22) Is there joint venture mentioned?
    23) Is there a name of a company mentioned?
    24) Is there a company owned by the municipality?
    25) Is there PPP, PPS or Public Private Participation mentioned?


Output:
Reply in a formatted JSON.
Use the question number for the keys in JSON without modification.
Use the answers as value in JSON.
"""

qwen_answers = {}

for i, (IMRO, plan_string) in tqdm(enumerate(data.items())):
    if plan_string == []:
        continue
    qwen_answer: ChatResponse = chat(
        model='qwen:4b',
        messages=[{
            'role': 'user',
            'content': qwen_prompt_template.format(plan_string=plan_string[0]["text"]),
            }]
        )
    qwen_answers[IMRO] = qwen_answer['message']["content"]
    logging.info(msg=f"{IMRO} --> mistral Answered")
    if (i+1) % 100 == 0:
        with open(f"../data/03_qwen/qwen.json", "w") as file:
            file.write(json.dumps(qwen_answers, indent=4))
        logging.info(msg=f"{i+1} plans stored")

# %%
