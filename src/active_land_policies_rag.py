# %%
import chromadb
import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import logging
import random

logging.basicConfig(
    filename="logs/query.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
OllamaModel = "deepseek-r1:8b"

emb_model = SentenceTransformer(
    model_name_or_path="jinaai/jina-embeddings-v3",
    trust_remote_code=True,
    device="cuda",
)

random.seed(42)
# %%


def embed_and_store(sents, ids, collection) -> None:
    if len(sents) == 0:
        return None
    embeddings = emb_model.encode(
        sentences=sents, show_progress_bar=False, normalize_embeddings=True
    )
    collection.add(embeddings=embeddings, documents=sents, ids=ids)


def search_and_translate(embed_question, collection, size=5):
    query_embeddings = emb_model.encode(
        sentences=embed_question, show_progress_bar=False, normalize_embeddings=True
    )
    query_res = collection.query(
        query_embeddings=query_embeddings,
        include=["documents", "distances"],
        n_results=size,
    )
    documents = query_res["documents"][0]
    if len(documents) == 0:
        return {}

    return dict(zip(query_res["ids"][0], query_res["documents"][0]))


def translate_nl_to_en(query_res):
    documents = list(query_res.values())
    translations = translator(documents, max_length=350)
    result = {
        "ids": list(query_res.keys()),
        "documents": documents,
        "translations": [t["translation_text"] for t in translations],
    }
    return result


def run_query_list(queries, collection, size=5):
    result = {}
    for q in queries:
        result.update(
            search_and_translate(embed_question=q, collection=collection, size=size)
        )
    return result


# %%


with open(file="../data/HTML_Sentences.json", mode="r") as f:
    pdf_plans = json.loads(s=f.read())

with open("query_params.json", "r") as f:
    queries = json.loads(f.read())

query_results = []
sample = random.sample(population=pdf_plans, k=50)
for i, plan in tqdm(enumerate(pdf_plans, start=1)):
    IMRO = plan["IMRO"]
    logging.info(f"Processing {IMRO}")
    chroma_client = chromadb.EphemeralClient()
    logging.info(f"Querying {IMRO} ... ")
    collection = chroma_client.get_or_create_collection(name=IMRO)
    embed_and_store(
        sents=list(plan["sentences"].values()),
        ids=list(plan["sentences"].keys()),
        collection=collection,
    )
    entry = {"IMRO": IMRO, "contexts": {}}
    for query in queries:
        result = {}
        for q in query.get("query"):
            query_embeddings = emb_model.encode(sentences=q, show_progress_bar=False)
            query_res = collection.query(
                query_embeddings=query_embeddings,
                include=["documents", "distances"],
                n_results=5,
            )
            query_res = dict(zip(query_res["ids"][0], query_res["documents"][0]))

            result.update(query_res)
        entry["contexts"][query.get("name")] = result
    query_results.append(entry)
    logging.info(f"Done! {IMRO}")
    if 0 == i % 50:
        with open("../data/HTML_query.json", "w", encoding="latin-1") as f:
            f.write(json.dumps(query_results))

# %%
