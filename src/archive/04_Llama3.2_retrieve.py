
# %%
from ollama import chat
from ollama import ChatResponse

from tqdm import tqdm

import logging
import json

logging.basicConfig(
    filename="pdf_parsing.log", 
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s')


with open("../data/translations_html.json", "r") as file:
    data = json.loads(file.read())

# %%

Llama3_prompt_template = """
Act as an urban planner answering the questions about contents of a land-use plan in the Netherlands. 
The terms operator, initiator, developer are the same.
Do not create answers. Use the provided context only.
Answers must be ONLY in form of "yes", "no" and "None".
Do not comment on the answers.
Put the answers in quotes.

Context:

The user is asking about this string of text:

{plan_string}

Questions:

    01- Is municipality the landowner of the planned area?
    02- Is developer the landowner of the planned area?
    03- Is the initiator the landowner of the area?
    04- Is plan area on municipal land?
    05- Is the municipality responsible for the costs?
    06- Is the landowner responsible for costs?
    07- Is the private sector responsible for costs?
    08- Is the initiator responsible for costs?
    09- Is costs covered by land sales?
    11- Is costs covered by cost recovery?
    12- Is there a need for expoitation plan?
    13- Is it mentioned that exploitation plan is NOT needed?
    14- Is it mentioned that operating plan is NOT needed?
    15- Is municipality going to sell land?
    16- Is municipality agreement mentioned?
    17- Do municipality and initiator have an agreement?
    18- Is the plan for housing construction?
    19- Is land require preparation?
    20- Is municipality taking care of land preperation?
    21- Is the initiator taking care of land preparation?
    22- Is there joint venture mentioned?
    23- Is there a name of a company mentioned?
    24- Is there a company owned by the municipality?
    25- Is there PPP, PPS or Public Private Participation mentioned?


Output:
Reply in a formatted JSON.
Use the question number for the keys in JSON without modification.
Use the answers as value in JSON.
"""

Llama_answers = {}

for i, (IMRO, plan_string) in tqdm(enumerate(data.items())):
    if plan_string == []:
        continue
    Llama_response: ChatResponse = chat(
        model='llama3.2:3b',
        messages=[{
            'role': 'user',
            'content': Llama3_prompt_template.format(plan_string=plan_string[0]["text"]),
            }]
        )
    Llama_answer = Llama_response['message']["content"]
    Llama_answers[IMRO] = Llama_answer
    logging.info(msg=f"{IMRO} --> Llama3.2 Answered")
    if (i+1) % 100 == 0:
        with open(f"../data/01_Llama3.2/{i+1}.json", "w") as file:
            file.write(json.dumps(Llama_answers, indent=4))
            Llama_answers = {}
        logging.info(msg=f"{i+1} plans stored")
# %%
with open("../data/Llama3.2_answers.json", "w") as file:
    file.write(json.dumps(Llama_answers, indent=4))
# %%
wrong_answers = []
for k in Llama_answers.keys():
    try:
        if Llama_answers[k][-1] != "}":
            Llama_answers[k] = json.loads(Llama_answers[k] + "}")
        else: 
            Llama_answers[k] = json.loads(Llama_answers[k])
    except:
        print("IMRO Answer is not formated correctly: ", k)
        wrong_answers.append(k)

with open("../data/Llama3.2_answers.json", "w") as file:
    file.write(json.dumps(Llama_answers, indent=4))
# %%
