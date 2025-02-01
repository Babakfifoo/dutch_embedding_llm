# %%
from tqdm import tqdm
import logging
import json
from pathlib import Path
from prompts import questions, Prompt

logging.basicConfig(
    filename="logs/retrieve.log", 
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s')

# %%
from dspy.retrieve.chromadb_rm import ChromadbRM
import dspy
lm = dspy.LM('ollama_chat/deepseek-r1:8b', api_base='http://localhost:11434', api_key='')
dspy.configure(lm=lm)

# %%

def get_answers(data, model, output_path, skip=0) -> None:
    answers = {}
    for i, (IMRO, plan_string) in tqdm(enumerate(data.items())):
        if i <= skip:
            continue
        if plan_string == []:
            continue
        plan_text = "\n".join(list(plan_string[0].values()))
        LLM_response: ChatResponse = chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': Prompt.format(
                    plan_string=plan_text,
                    questions=questions
                    ),
                }]
            )
        answers[IMRO] = LLM_response['message']["content"]
        logging.info(msg=f"{IMRO} --> mistral Answered")
        if (i+1) % 100 == 0:
            with open(file=output_path, mode="w") as file:
                file.write(json.dumps(obj=answers, indent=4))
            logging.info(msg=f"{model}:{i+1} plans stored")


# %%
destination = "../data/pdf_answers/"
models = {
    "llama3.2:3b": destination+"llama3.2.json",
    "mistral:7b-instruct": destination+"mistral.json",
    "qwen2.5:3b": destination+"qwen2.5.json",
    "gemma2:2b": destination+"gemma2_500.json",
    "granite3.1-dense:2b": destination+"granite3.1.json",
}
# %%
with open(file="../data/translations_pdf_20250107.json", mode="r") as file:
    data = json.loads(s=file.read())
for model, output_path in models.items():
    logging.info(msg=f"INITIATION:{model}-------------------------------------")
    get_answers(data=data, model=model, output_path=output_path, skip=0)
    logging.info(msg=f"{model} IS DONE!---------------------------------------")
# %%
