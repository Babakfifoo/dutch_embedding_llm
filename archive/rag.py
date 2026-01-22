# %%
import chromadb
import json
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from tqdm import tqdm

OllamaModel = "llama3.2:3b-instruct-q5_K_M"
translation_model_name = "Helsinki-NLP/opus-mt-nl-en"

emb_model = SentenceTransformer(
    model_name_or_path="jinaai/jina-embeddings-v3",
    trust_remote_code=True,
    device="cuda"
)

translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=5,
    truncation=True
)

# %%

def embed_and_store(sents, collection) -> None:
    if len(sents) == 0:
        return None
    embeddings = emb_model.encode(
        sentences=sents, show_progress_bar=False
    )
    ids = [str(i) for i in list(range(len(sents)))]
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
        include=["documents", "distances"],
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

with open(file="../data/HTML_feasability_sections.json", mode="r") as f:
    html_plans = json.loads(s=f.read())
# %%
query_final_results = {}
for IMRO, sents in tqdm(html_plans.items()):
    chroma_client = chromadb.EphemeralClient()
    # to make sure we have separate collections for each plan
    collection = chroma_client.get_or_create_collection(name=IMRO)
    embed_and_store(sents=sents, collection=collection)
    query_result = search_and_translate(
        embed_question="Is exploitatieplan needed?",
        collection=collection
        )
    query_final_results[IMRO] = query_result

with open(file="../data/HTML_query_results.json", mode="w") as f:
    f.write(json.dumps(query_final_results))
# %%
