from . import prompts
from pydantic import BaseModel
from typing import List, Dict

AGREEMENT_FUZZ_CUTOFF_SCORE = 80

AGREEMENT_LIST: Dict[str, str] = {
    "anterieure overeenskomst": "Anterior agreement",
    "anterieur overeenskomst": "Anterior agreement",
    "exploitatieovereenkoost": "Exploitation agreement",
    "planschadeverhaals overeenkomst": "Plan damage agreement",
    "overeenkomst tussen initiaatiefnemer": "General agreement",
    "overeenkomst met de eigenaar": "General agreement",
    "overeenkomst grondexploitatie": "Exploitation agreement",
    "kostenv verhaal overeenkomst": "Cost recovery agreement",
    "realisatie overeenkomst": "Realisation agreement",
    "koop overeenkomsten": "Purchase agreement",
    "grondverkopen overeenkosten": "Land sale agreement",
    "planrrealisatie overeenkomst": "Realisation agreement",
    "grondexploitatie overeenkomst": "Exploitation agreement",
    "samenwerkings overeenkomst": "Cooperation agreement",
    "ontwikkelings overeenkomst": "Development agreement",
    "grondverkopenovereenkosten": "Land sale agreement",
    "planrrealisatieovereenkomst": "Realisation agreement",
    "grondexploitatieovereenkomst": "Exploitation agreement",
    "samenwerkingsovereenkomst": "Cooperation agreement",
    "ontwikkelingsovereenkomst": "Development agreement",
    "uitvoeringsOvereenkomst": "Development agreement",
    "rood voor rood overeenkomst": "Space-for-Space agreement",
    "privaatrechtelijke overeenkomst": "Anterior agreement",
    "intentie overeenkomst": "General agreement",
    "gebieds overeenkomst": "Area agreement",
    "intentieovereenkomst": "General agreement",
    "gebiedsovereenkomst": "Area agreement",
    "gebiedsontwikkelings overeenkomst": "Area agreement",
    "anterieure privaatrechtelijke overeenkomst": "Anterior agreement",
}


class AgreementTypes(BaseModel):
    agreement: List[str]


DAGeneral: prompts.PromptConfig = prompts.PromptConfig(
    topic="General Agreement",
    description="the prompt is to identify if conclusion of an agreement is stated.",
    threshold=90,
    prompt="""
        **Context**:

        {context}

        Based on the provided context, is there explicitely mentioned that an agreement is concluded?
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "answer": <true_or_false>
        }}
        Where <true_or_false> is either the boolean `true` or `false`.
        Do not include any other text or explanation.
    """,
)

DAType: prompts.PromptConfig = prompts.PromptConfig(
    topic="Agreement type",
    description="the prompt is to identify if conclusion of an agreement is stated.",
    threshold=90,
    prompt="""
        **Context**:

        {context}

        Based on the provided context, waht is the type of agreement concluded?
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "agreement": [<list_of_types>]
        }}
        Do not include any other text or explanation.
    """,
)


DATypeUsed: prompts.PromptConfig = prompts.PromptConfig(
    topic="General Agreement",
    description="the prompt is to identify if conclusion of the selected agreement",
    threshold=90,
    prompt="""
        **Context**:

        {context}

        Based on the provided context, is it mentioned that an agreement {agr_type} is signed, made or concluded?
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "ans": <true_or_false>
        }}
        Where <true_or_false> is either the boolean `true` or `false`.
        Do not include any other text or explanation.
    """,
    schema=prompts.BoolAnswer.model_json_schema(),
)
