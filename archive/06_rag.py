# %%

import json
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb
import logging
logging.basicConfig(
    filename="logs/06.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
# %%
embedding_model_name = "jinaai/jina-embeddings-v3"
emb_model = SentenceTransformer(
    model_name_or_path=embedding_model_name,
    trust_remote_code=True,
    device="cuda"
)

translation_model_name = "Helsinki-NLP/opus-mt-nl-en"
translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=5,
    truncation=True
)
# %%


def embed_and_store(sents, collection, ids) -> None:
    if len(sents) == 0:
        return None
    embeddings = emb_model.encode(
        sentences=sents, show_progress_bar=False
    )
    collection.add(
        embeddings=embeddings,
        documents=sents,
        ids=ids)


def search_and_translate(embed_question, collection):
    query_embeddings = emb_model.encode(
        sentences=embed_question,
        show_progress_bar=False
        )
    query_res = collection.query(
        query_embeddings=query_embeddings,
        include=["documents"],
        n_results=5
        )
    documents = query_res['documents'][0]
    if len(documents) == 0:
        return None
    translations = translator(documents, max_length=350)
    result = {
        'documents' : query_res['documents'][0],
        'translations' : [t['translation_text'] for t in translations],
        'distances': query_res['distances'][0],
    }
    return (result)
# %%


with open("query_params.json", "r") as f:
    query_questions = json.loads(f.read())

with open(
    file="../data/sample plans/cleaned_sentences/html_fuzzy_sents.json",
    mode="r",
    encoding="utf-8"
) as f:
    html_data = json.loads(f.read())
# %%
selected_paragraphs = []
for plan in tqdm(html_data):
    IMRO = plan.get("IMRO")
    chroma_client = chromadb.EphemeralClient()
    # to make sure we have separate collections for each plan
    collection = chroma_client.get_or_create_collection(name=IMRO)
    for item in plan["sentences"]:
        sents = list(item["sentences"].values())
        ids = [str(item["para_num"]) + ":" + str(x) for x in item["sentences"].keys()]
        embed_and_store(sents, collection, ids)

    result = {}
    for query in query_questions:
        paragraphs = []
        for embed_question in query["query"]:
            query_embeddings = emb_model.encode(
                    sentences=embed_question,
                    show_progress_bar=False
                    )
            query_res = collection.query(
                query_embeddings=query_embeddings,
                include=["documents"],
                n_results=5
                )
            paragraphs += list({s.split(":")[0] for s in query_res['ids'][0]})
        result[query.get("name")] = list(set(paragraphs))

    selected_paragraphs.append({
        "IMRO": IMRO, 
        "paragraph_idx": result
        })
    logging.info(f"Stored -> {IMRO}")
with open("../data/sample plans/selected_paragraphs/html_paragraphs.json", mode="w", encoding="utf-8") as f:
    f.write(json.dumps(selected_paragraphs, indent=4))
# %%
