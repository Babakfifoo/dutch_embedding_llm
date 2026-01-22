
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
    format='%(asctime)s:%(levelname)s:Llama3.2:%(message)s')


# %%
with open("../data/translations_html.json", "r") as file:
    data = json.loads(file.read())

# %%
# %%



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

Question 1: Is municipality the landowner of the planned area?
Question 2: Is developer the landowner of the planned area?
Question 3: Is the initiator responsible for costs?
Question 4: Is it mentioned that exploitation plan is NOT needed?
Question 5: Is it mentioned that operating plan is NOT needed?
Question 6: Is municipality going to sell land?
Question 7: Is municipality agreement mentioned?
Question 8: Is the landowner responsible for costs?
Question 9: Is there a company owned by the municipality?
Question 10: Is there PPP, PPS or Public Private Participation?

Output:
Reply in a formatted JSON.
Use the question number for the keys in JSON without modification.
Use the answers as value in JSON.
"""
# %%

Llama_answers = {}

for i, (IMRO, plan_string) in tqdm(enumerate(data.items())):
    Llama_response: ChatResponse = chat(
    model='mistral', 
    messages=[{
        'role': 'user',
        'content': Llama3_prompt_template.format(plan_string = plan_string),
        },]
    )
    Llama_answer = Llama_response['message']["content"]
    Llama_answers[IMRO] = Llama_answer
    if (i+1)%100 == 0:
        print(i)
    break
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

with open("../data/mistral_answers.json", "w") as file:
    file.write(json.dumps(Llama_answers, indent=4))
# %%
