import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
FIELDS = {"_id": 0, "brand": 1, "product_name": 1, "size_g": 1, "search_text": 1,
          "protein_g": 1, "price_per_100g": 1, "kcal": 1, "embedding": 1}

client = MongoClient("mongodb://localhost:27017/")
collection = client["nutrition_db"]["products"]
model = SentenceTransformer(MODEL_NAME)


def show(title, results):
    print(f"\n=== {title} ===")
    if not results:
        print("  (no results)")
    for doc, score in results:
        name = f"{doc['brand']} {doc['product_name']} ({doc['size_g']:g}g)"
        print(f"  {score:.3f}  {name[:50]:<50} "
            f"{doc['protein_g']}g protein  ${doc['price_per_100g']}/100g  {doc['kcal']} kcal")


def to_matrix(docs):
    return np.array([doc["embedding"] for doc in docs])

def keep_cheapest(docs):
    cheapest = {}
    for doc in docs:
        text = doc["search_text"]
        if text not in cheapest or doc["price_per_100g"] < cheapest[text]["price_per_100g"]:
            cheapest[text] = doc
    return list(cheapest.values())

def rank(query, docs, k=5):
    docs = keep_cheapest(docs)
    if not docs:
        return []
    matrix = to_matrix(docs)
    query_vector = model.encode(query, normalize_embeddings=True)
    scores = matrix @ query_vector
    top = np.argsort(scores)[::-1][:k]
    return [(docs[i], scores[i]) for i in top]


def build_filter(min_protein_g=None, max_price_per_100g=None, max_kcal=None):
    mongo_filter = {"embedding": {"$exists": True}}
    if min_protein_g is not None:
        mongo_filter["protein_g"] = {"$gte": min_protein_g}
    if max_price_per_100g is not None:
        mongo_filter["price_per_100g"] = {"$lte": max_price_per_100g}
    if max_kcal is not None:
        mongo_filter["kcal"] = {"$lte": max_kcal}
    return mongo_filter


# ------------------------------------------------------------
# Experiment 1: pull the vectors back out of MongoDB
# ------------------------------------------------------------
all_docs = list(collection.find(build_filter(), FIELDS))
print(f"Products with embeddings: {len(all_docs)}")
print(f"Matrix shape: {to_matrix(all_docs).shape}")

# ------------------------------------------------------------
# Experiment 2: semantic search only (meaning, no numbers)
# ------------------------------------------------------------
for query in ["cheap high protein breakfast", "hearty dinner", "sweet snack"]:
    show(f"semantic only: '{query}'", rank(query, all_docs))

# ------------------------------------------------------------
# Experiment 3: numeric filter only (numbers, no meaning)
# ------------------------------------------------------------
print("\n=== filters on their own ===")
for kwargs in [{}, {"min_protein_g": 10}, {"min_protein_g": 10, "max_price_per_100g": 1.5}]:
    mongo_filter = build_filter(**kwargs)
    print(f"  {kwargs} -> {collection.count_documents(mongo_filter)} products")
    print(f"      filter sent to MongoDB: { {k: v for k, v in mongo_filter.items() if k != 'embedding'} }")

# ------------------------------------------------------------
# Experiment 4: hybrid = filter first, then rank the survivors
# ------------------------------------------------------------
query = "cheap high protein breakfast"
filtered_docs = list(collection.find(build_filter(min_protein_g=10, max_price_per_100g=1.5), FIELDS))
show(f"semantic only: '{query}'", rank(query, all_docs))
show(f"hybrid (protein >= 10g, price <= $1.50/100g): '{query}'", rank(query, filtered_docs))

# ------------------------------------------------------------
# Experiment 5: where embeddings fall short
# ------------------------------------------------------------
show("numbers in the text: 'food under 50 cents per 100g'", rank("food under 50 cents per 100g", all_docs))
show("negation: 'breakfast without dairy'", rank("breakfast without dairy", all_docs))