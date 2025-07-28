from typing import List, Dict, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel


class BoolAnswer(BaseModel):
    ans: bool


@dataclass()
class PromptConfig:
    topic: str
    description: str
    threshold: int
    prompt: str
    term_queries: List[str] = field(default_factory=list)
    schema: Optional[Dict] = "json"


# DCP: Development contribution plan. A.K.A. Exploitation plan
noDCP: PromptConfig = PromptConfig(
    topic="no-DCP",
    description="Asking whether land use plan mentions that DCP is not needed",
    threshold=80,
    prompt="""
        Context:
        {context}

        Based on the provided context, is it explicitely mentioned that making exploitatieplan is not needed or weavered??
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "answer": <true_or_false>
        }}
        Where <true_or_false> is either the boolean `true` or `false`.
        Do not include any other text or explanation.
        """,
)

DCPMade: PromptConfig = PromptConfig(
    topic="DCPMade",
    description="Asking whether DCP is made for the plan",
    threshold=80,
    prompt="""
        Context:
        {context}

        Based on the provided context, is it explicitely mentioned that an exploitatieplan made for this plan to ensure its feasibility?
        You must respond ONLY with a JSON object that strictly adheres to the following schema:
        {{
            "answer": <true_or_false>
        }}
        Where <true_or_false> is either the boolean `true` or `false`.
        Do not include any other text or explanation.
        """,
    term_queries=["exploitatieplan", "grondexploitatie"],
)

WhyNoDCP: PromptConfig = PromptConfig(
    topic="DCPMade",
    description="Asking Why DCP is not needed",
    threshold=80,
    prompt="""
        Context:
        {context}

        Based on the provided context, briefly explain how the feasibility of the plan is ensured? answer in English in maximum three sentences.
""",
    term_queries=["exploitatieplan", "grondexploitatie"],
)
