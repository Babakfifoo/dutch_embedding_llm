# %%
import chromadb
import json
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from tqdm import tqdm
import logging

logging.basicConfig(
    filename="logs/query.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
OllamaModel = "deepseek-r1:8b"
translation_model_name = "Helsinki-NLP/opus-mt-nl-en"

emb_model = SentenceTransformer(
    model_name_or_path="jinaai/jina-embeddings-v3",
    trust_remote_code=True,
    device="cuda",
)

translator = pipeline(
    task="translation_nl_to_en",
    model=translation_model_name,
    device=0,
    batch_size=8,
    truncation=True,
)

# %%

exploitation_plan_queries = [
    "neet exploitatieplan",
    "Een exploitatieplan is derhalve niet noodzakelijk",
    "een exploitatieovereenkomst ge-sloten",
    "geen exploitatieplan vast hoeft te stellen",
    "exploitatieplan vastgesteld",
    "exploitatieplan achterwege kan worden gelaten",
    "een exploitatieplan is daarom niet nodig",
    "Het opstellen van een exploitatieplan is dan ook niet noodzakelijk",
    "exploitatieplan achterwege kan blijven",
    "kan worden afgezien van vaststelling van een exploitatieplan",
    "geen exploitatieplan als bedoeld",
    "Er hoeft derhalve geen exploitatieplan opgesteld te worden",
    "De verplichting tot het opstellen van een exploitatieplan vervalt hierdoor",
    "Daarmee is het kostenverhaal verzekerd en hoeft geen exploitatieplan",
]

anterior_agreement_queries = [
    "De gemeente Initiatienemer anterieure overeenkomst gesloten",
    "gemeente en de eigenaar een anterieure overeenkomst afgesloten",
    "Met de ontwikkelaar is een anterieure overeenkomst gesloten",
    "De initiatiefnemer en de gemeente hebben samen een anterieure exploitatie-overeenkomst",
    "Tussen de gemeente en de initiatiefnemer is een anterieure overeenkomst gesloten",
    "Om de gemeentelijke kosten in verband met dit project te verhalen is een zogenaamde anterieure overeenkomst gesloten",
]

municipality_owns_land_queries = [
    "de gemeente eigenaar is van de grond",
    "De gemeente is eigenaar",
    "De gronden in het plangebied zijn in eigendom bij de gemeente",
    "De gemeente is eigenaar van alle gronden in het plangebied",
    "de gronden volledig in eigendom van de gemeen-te zijn",
    "Het eigendom van gronden in het plangebied is in gemeentelijke handen",
    "de gemeente is de initiatiefnemer",
    "De gronden van het eigendom van de provincie",
    "De gronden waarop nieuwbouw wordt gebouwd, zijn of komen in eigendom van de gemeente",
    "de gemeente overeenkomsten gesloten over de aankoop van de gronde",
    "De gemeente heeft alle gronden, nodig voor de realisatie van het plan, in eigendom. ",
]

developer_owns_land_queries = [
    "De gronden zijn in eigendom van de opdrachtgever",
    "Het plangebied betreft particulier eigendom",
    "particulier grondeigendom",
    "Het plangebied is volledig in eigendom van de initiatiefnemer",
    "Het plangebied is in eigendom van de initiatiefnemer",
    "Verder zijn de gronden eigendom van de initiatiefnemer",
]

public_land_sale_queries = [
    "Verhaal van gemeentelijke kosten geschiedt door middel van gronduitgifte",
    "De bouwkavels dienen gekocht van de gemeente",
    "Het kostenverhaal wordt middels de gronduitgifte zeker gesteld.",
    "de verkoopprijs van de grond",
]

private_is_responsible_queries = [
    "Het plan wordt gerealiseerd op particulier initiatief",
    "De realisatie van het plan geschiedt voor rekening van de initiatiefnemer",
    "Het project zal geheel worden gerealiseerd op kosten en risico van de initiatiefnemer",
    "Het plan wordt geheel door initiatiefnemer gefinancierd",
    "ontwikkelingen zullen dan ook volledig vanuit hun initiatief gerealiseerd en gefinancierd worden",
    "De ontwikkeling wordt geheel op risico van de initiatiefnemer aangegaan en is daarmee een volledig particulier initiatief",
    "De kosten voor het worden gedragen door de Initiatienemer ontwikkelaar van het plan",
    "De realisatie van het project geschiedt voor rekening van de initiatiefnemer",
]

tendering_queries_queries = ["aanbesteden uitvraag"]


def embed_and_store(sents, ids, collection) -> None:
    if len(sents) == 0:
        return None
    embeddings = emb_model.encode(sentences=sents, show_progress_bar=False)
    collection.add(embeddings=embeddings, documents=sents, ids=ids)


def search_and_translate(embed_question, collection, size=5):
    query_embeddings = emb_model.encode(
        sentences=embed_question, show_progress_bar=False
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


with open(file="../data/PDF_Sentences.json", mode="r") as f:
    pdf_plans = json.loads(s=f.read())

query_results = []
for i, plan in tqdm(enumerate(pdf_plans, start=1)):
    chroma_client = chromadb.EphemeralClient()
    IMRO = plan["IMRO"]
    logging.info(f"Querying {IMRO} ... ")
    collection = chroma_client.get_or_create_collection(name=IMRO)
    embed_and_store(
        sents=list(plan["sentences"].values()),
        ids=list(plan["sentences"].keys()),
        collection=collection,
        )
    exploitation_plan = run_query_list(
        queries=exploitation_plan_queries, collection=collection, size=5
        )
    anterior_agreement = run_query_list(
        queries=anterior_agreement_queries, collection=collection, size=5
        )
    municipality_owns_land = run_query_list(
        queries=municipality_owns_land_queries, collection=collection, size=5
        )

    developer_owns_land = run_query_list(
        queries=developer_owns_land_queries, collection=collection, size=5
        )

    public_land_sale = run_query_list(
        queries=public_land_sale_queries, collection=collection, size=5
        )

    private_is_responsible = run_query_list(
        queries=private_is_responsible_queries, collection=collection, size=5
        )

    tendering_queries = run_query_list(
        queries=tendering_queries_queries, collection=collection, size=5
        )
    all_sentences = {
        **exploitation_plan,
        **anterior_agreement,
        **municipality_owns_land,
        **developer_owns_land,
        **public_land_sale,
        **private_is_responsible,
        **tendering_queries,
        }
    translations = translate_nl_to_en(all_sentences)
    entry = {
        "IMRO": IMRO,
        "text": translations,
        "exploitation plan": list(exploitation_plan.keys()),
        "anterior agreement": list(anterior_agreement.keys()),
        "municipality_owns_land": list(municipality_owns_land.keys()),
        "developer_owns_land": list(developer_owns_land.keys()),
        "public_land_sale": list(public_land_sale.keys()),
        }
    query_results.append(entry)
    logging.info(f"Done {IMRO}.")
    if i % 50 == 0:
        with open("../data/PDF_query.json", "w") as f:
            f.write(json.dumps(query_results))


# %%
