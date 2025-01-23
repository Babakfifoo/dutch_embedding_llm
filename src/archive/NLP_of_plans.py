# %%
from sentence_transformers import SentenceTransformer
import json
from itertools import chain
from torch._tensor import Tensor
from tqdm import tqdm
model = SentenceTransformer(
    model_name_or_path='fine-tuned/dutch-legal-c',
    trust_remote_code=True
)

def generate_doc_from_string(sentence:str, id:str) -> dict[str, str | Tensor]:
    embedding = model.encode(sentence)
    return(dict(
        documents = sentence,
        ids = id,
        embeddings = embedding
    ))


# %%

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# chroma_client = chromadb.PersistentClient("./chromadb")
chroma_client = chromadb.Client()
collection_name = "html_plans"
ollama_ef = OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)

try:
    collection = chroma_client.create_collection(
        name=collection_name, 
        embedding_function=ollama_ef
    )
    
except:
    collection = chroma_client.get_collection(
        name=collection_name,
        embedding_function=ollama_ef
        )


# %%

with open("./htmls_parsed.json", "r") as file:
    plan_data = json.loads(file.read())

documents = []
for plan_IMRO in tqdm(list(plan_data.keys())[0:100]):
    plan = plan_data[plan_IMRO]
    plan_name = ".".join(plan_IMRO.split(".")[2:4])
    sentenses = list(chain(*[content['paragraphs'] for content in plan]))
    sentenses = list(chain(*sentenses))
    for i, sentence in enumerate(iterable=sentenses):
        doc = generate_doc_from_string(
            sentence=sentence,
            id = (plan_name + ":" + str(i))
        )
        documents.append(doc)
# %%

collection.add(
    documents=[x["documents"] for x in documents],
    ids=[x["ids"] for x in documents],
    embeddings=[x["embeddings"] for x in documents]
)
# %%


# %%
collection.query(
    query_texts=[" municipality owns the land"]
)
# %%
print(len([x["documents"] for x in documents]))
print(len([x["embeddings"] for x in documents]))
print(len([x["ids"] for x in documents]))
# %%
