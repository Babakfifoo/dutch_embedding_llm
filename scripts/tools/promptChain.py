from . import prompts
from pydantic import BaseModel


class Answer(BaseModel):
    ans: bool


CostBrief: prompts.PromptConfig = prompts.PromptConfig(
    topic="General Agreement",
    description="Generating simplified explaination of how costs are covered-",
    threshold=0,
    prompt="""
        **Context**:

        {context}

        Based on the provided context, briefely explain how the costs are covered.
        answer in tree sentences max.
    """,
)

AgreementPrompt: prompts.PromptConfig = prompts.PromptConfig(
    topic="Agreement_yes_no",
    description="Validating if an agreement is made from the cost recovery briefing",
    threshold=0,
    prompt="""
        **Context**:

        {context}

        Based on the provided context, Is there are agreement made?
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "answer": <true_or_false>
        }}
        Where <true_or_false> is either the boolean `true` or `false`.
        Do not include any other text or explanation.
    """,
    schema=Answer.model_json_schema(),
)

AgreementType: prompts.PromptConfig = prompts.PromptConfig(
    topic="agreement_type",
    description="Extracting the name of the agreements from the briefing",
    threshold=0,
    prompt="""
        **Context**:

        {context}

        Based on the provided context, list the name of the agreements.
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "answer": <agreement_name_list>
        }}
        Where <agreement_name_list> is a list of agreement names.

    """,
    schema="json",
)
