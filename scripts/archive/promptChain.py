from . import prompts
from pydantic import BaseModel


class Answer(BaseModel):
    ans: bool


CostBrief: prompts.PromptConfig = prompts.PromptConfig(
    topic="General Agreement",
    description="Generating simplified explaination of how costs are covered-",
    threshold=0,
    prompt="""
# Context:

{context}

# Instructions:

Based on the provided context, summarise explain how the costs are covered. 
Include information about any agreements or plans that are made.

Only use the provided context.

Do not hallucinate.

    """,
)
