# %%

from functools import lru_cache
from transformers import pipeline, TranslationPipeline
import spacy


translation_model_name: str = "Helsinki-NLP/opus-mt-nl-en"
translator: TranslationPipeline = pipeline(
    task="translation",
    model=translation_model_name,
    device=0,
    batch_size=6,
    truncation=True,
)

nlp = spacy.load("nl_core_news_lg")
nlp.add_pipe(factory_name="sentencizer")


@lru_cache(maxsize=10000)
def translate_sentence(s: str) -> str:
    return translator(s)[0].get("translation_text")


def translate_para(sentences):
    sentences_to_translate = list(sentences.values())
    sents = [translate_sentence(s) for s in sentences_to_translate]
    return {"id": list(sentences.keys()), "nl": list(sentences.values()), "en": sents}


def extract_sentences(s: str, para: int):
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


# %%
