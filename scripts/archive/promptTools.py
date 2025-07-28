# %%
from rapidfuzz import fuzz
from ollama import ChatResponse, chat
from pydantic import BaseModel
from typing import List

LLM_MODEL: str = "gemma3n:e4b"
# "llama3.2:3b-instruct-q5_K_M"


class Answer(BaseModel):
    ans: bool


def find_topic(s: str, q: List[str], threshold=90) -> bool:
    """A fuzzy matching function that evaluates a string against a list of strings.
    Complexity level is O(N).

    Parameters
    ----------
    s : str
        String to compare against queries
    q : List[str], list of strings
        list of strings that we are looking for
    threshold : int, optional
        Threshold of matching, by default 90

    Returns
    -------
    bool
        If fuzzy score for any element of the list is more then threshold, returns True
    """
    # This ignores the sentences that contain examples to prevent bias.
    if "example" in s:
        return False
    for query in q:
        score = fuzz.partial_ratio(s1=s, s2=query)
        if score > threshold:
            return True
    return False


def ask_LLM(
    prompt: str,
    response_format="json",
    model: str = LLM_MODEL,
) -> ChatResponse:
    return chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options=dict(
            temperature=0.0,  # reducing the variability of the answer
            seed=2025,  # Setting the Seed for prediction and reproducability
            top_k=10,  # More conservative answer
            min_p=0.9,  # minimum probability of token to be considered.
            main_gpu=2,
            num_thread=4,
        ),
        format=response_format,
    )


def bool_cleaner(s: str) -> bool | None:
    # Validates and corrects the answer to Bool. None values are also returned False.
    if not isinstance(s, str):
        return None
    if "true" in s.lower():
        return True
    if "false" in s.lower():
        return False
    return None
