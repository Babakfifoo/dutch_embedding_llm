# %%

import dspy
import json
from typing import List
from itertools import chain
from tqdm import tqdm
from config import QUESTIONS
import logging
from pathlib import Path

logging.basicConfig(
    filename="./logs/08.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def create_qa_signature():
    class QuestionAnswer(dspy.Signature):
        """Process questions and return yes/no/not mentioned answers."""

        text = dspy.InputField()
        questions = dspy.InputField()
        answers = dspy.OutputField(
            desc="Dictionary mapping question numbers to yes/no/not mentioned"
        )

    return QuestionAnswer


def setup_dspy_llm():
    lm = dspy.LM(
        model="ollama_chat/llama3.2:1b",
        api_base="http://localhost:11434",
        api_key="",
        temperature=0,
        seed=2025,
        main_gpu=1,
    )
    return lm


signature = create_qa_signature()
lm = setup_dspy_llm()
dspy.settings.configure(lm=lm)
predict_answers = dspy.Predict(signature=signature)


def extract_answers_dspy(text: str, questions: List[str]):
    prompt = f"""
    Analyze the following text and questions:
    **Text**:
    {text}

    **Questions**:
    {questions}

    For each question, return 'yes' if the information is present,
    'no' if it's explicitly contradicted, and 'not mentioned' otherwise.

    output example:

        "Q1": "yes",
        "Q2": "no",
        "Q3": "notmentioned",
        ...
    """

    result = predict_answers(text=prompt, questions=questions)

    return result.answers


# %%

questions = list(chain(*[e["questions"] for e in QUESTIONS]))

with open("../data/plan_documents/translations/html_translated.json", "r") as f:
    data = json.loads(f.read())


answers = []
for plan in tqdm(data[0:10]):

    logging.info(f"Processing {plan.get('IMRO')}")
    try:
        text = "\n".join(plan.get("en"))
        answers_dspy = extract_answers_dspy(text=text, questions=questions)
        entry = {"IMRO": plan.get("IMRO"), "answers": answers_dspy}

        logging.info(f"Done! {plan.get('IMRO')}")

    except Exception as e:
        logging.error(f"ERROR {plan.get('IMRO')} : {e}")
        entry = {"IMRO": plan.get("IMRO"), "answers": None}

    answers.append(entry)

with open("../data/plan_documents/answered/html_answers.json", "w") as file:
    file.write(json.dumps(answers, indent=4))
# %%
questions = list(chain(*[e["questions"] for e in QUESTIONS]))

with open("../data/plan_documents/translations/pdf_translated.json", "r") as f:
    data = json.loads(f.read())


sample = [x.stem for x in Path("../data/sample plans/pdf/").iterdir()]
answers = []

sample_data = [i for i in data if i.get("IMRO") in sample]

problematics = []

for plan in tqdm(sample_data):
    logging.info(f"Processing {plan.get('IMRO')}")
    try:
        text = "\n".join(plan.get("en"))
        answers_dspy = extract_answers_dspy(text=text, questions=questions)
        entry = {"IMRO": plan.get("IMRO"), "answers": answers_dspy}
        logging.info(f"Done! {plan.get('IMRO')}")
        answers.append(entry)

    except Exception as e:
        logging.error(f"ERROR {plan.get('IMRO')} : {e}")
        entry = {"IMRO": plan.get("IMRO"), "answers": None}
        problematics.append(entry)

with open("../data/plan_documents/answered/pdf_answers.json", "w") as file:
    file.write(json.dumps(answers, indent=4))
    
with open("../data/plan_documents/answered/pdf_problems.json", "w") as file:
    file.write(json.dumps(problematics, indent=4))
# %%
