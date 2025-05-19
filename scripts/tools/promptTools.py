# %%
from rapidfuzz import fuzz
from ollama import chat
from typing import Literal
from pydantic import BaseModel
from functools import lru_cache
from transformers import pipeline
import spacy

LLM_MODEL = "gemma3:4b"
# "llama3.2:3b-instruct-q5_K_M"

translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=6,
    truncation=True,
)

nlp = spacy.load("nl_core_news_lg")
nlp.add_pipe(factory_name="sentencizer")


class Answer(BaseModel):
    ans: Literal[True, False]


def find_topic(s, q, threshold=90) -> bool:
    # This ignores the sentences that contain examples to prevent bias.
    if "example" in s:
        return False
    for query in q:
        score = fuzz.partial_ratio(s1=s, s2=query)
        if score > threshold:
            return True
    return False


def ask_LLM(entry, prompt, model: str = LLM_MODEL):
    return chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt.format(
                    context=entry["context"],
                ),
            }
        ],
        options=dict(
            temperature=0.0,  # reducing the variability of the answer
            seed=2025,  # Setting the Seed for prediction and reproducability
            num_predict=10,  # max number of tokens to predict
            top_k=10,  # More conservative answer
            min_p=0.9,  # minimum probability of token to be considered.
        ),
        format=Answer.model_json_schema(),
    )


@lru_cache(maxsize=10000)
def translate_sentence(s):
    return translator(s)[0].get("translation_text")


def translate_para(sentences):
    sentences_to_translate = list(sentences.values())
    sents = [translate_sentence(s) for s in sentences_to_translate]
    return {"id": list(sentences.keys()), "nl": list(sentences.values()), "en": sents}


def extract_sentences(s: str, para):
    sents = nlp(s)
    correct_sents = []
    for sent in sents.sents:
        # if sent[0].is_title:
        tokens = {token.pos_ for token in sent}
        if any([(x in tokens) for x in ["NOUN", "PROPN", "PRON"]]) and (
            "VERB" in tokens
        ):
            correct_sents.append(sent.text)
    ids = [f"{para}:{i}" for i in range(len(correct_sents))]
    return dict(zip(ids, correct_sents))


def bool_cleaner(s: str) -> bool:
    # validating the answer
    if not isinstance(s, str):
        return False
    if "true" in s.lower():
        return True
    return False
