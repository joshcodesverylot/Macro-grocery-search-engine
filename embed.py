import numpy as np
from pymongo import MongoClient, UpdateOne
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64


def load_documents(collection):
    # Only fetch the fields we need; embeddings are large, so never pull them when you don't need them
    docs = list(collection.find({}, {"_id": 1, "search_text": 1, "product_name": 1}))
    print(f"Loaded {len(docs)} documents")
    return docs


def embed_texts(model, texts):
    # TODO: turn the list of strings into a (len(texts), 384) numpy array.
    # Hints:
    #   - model.encode(...) takes a list of strings
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=BATCH_SIZE, show_progress_bar=True)
    #   - pass batch_size=BATCH_SIZE and show_progress_bar=True
    #   - pass normalize_embeddings=True so every vector has length 1,
    #     which makes cosine similarity equal to a plain dot product (a @ b)
    return vectors

    


def save_embeddings(collection, docs, vectors):
    # TODO: build one UpdateOne per document and send them with collection.bulk_write(...)
    operations = []
    for doc, vector in zip(docs, vectors):
        operations.append(
            UpdateOne(
                {"_id": doc["_id"]},
                {"$set": {"embedding": vector.tolist(), "embedding_model": MODEL_NAME}}
            )
        )
    result = collection.bulk_write(operations)
    print(f"Saved embeddings. Matched: {result.matched_count}, Modified: {result.modified_count}")
    # Hints:
    #   - filter by {"_id": doc["_id"]}
    #   - "$set" two fields: "embedding" and "embedding_model"
    #   - MongoDB can't store numpy arrays, so convert each vector with vector.tolist()
    #   - zip(docs, vectors) pairs each document with its vector



def sanity_check(docs, vectors):
    # Checks that the vectors are normalised and that "similar" actually means similar
    norms = np.linalg.norm(vectors, axis=1)
    print(f"\nVector shape: {vectors.shape}, norms between {norms.min():.3f} and {norms.max():.3f}")
    i = 0
    for index, doc in enumerate(docs):
        if "tuna" in doc["product_name"].lower():
            i = index
            break

    scores = vectors @ vectors[i]
    ranked = np.argsort(scores)[::-1]

    print(f"\nNearest neighbours of '{docs[i]['product_name']}':")
    for j in ranked[1:6]:
        print(f"  {scores[j]:.3f}  {docs[j]['product_name']}")
    # TODO: pick one product (e.g. index 0, or search docs for one named "tuna") and print its 5 nearest neighbours.
    # Hints:
    #   - scores = vectors @ vectors[i]      -> one similarity score per product
    #   - np.argsort(scores)[::-1]           -> indices from most to least similar
    #   - skip the first result: a product is always most similar to itself (score 1.0)
    #   - print docs[j]["product_name"] and scores[j]


def run():
    client = MongoClient("mongodb://localhost:27017/")
    collection = client["nutrition_db"]["products"]

    docs = load_documents(collection)
    texts = [doc["search_text"] for doc in docs]

    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    vectors = embed_texts(model, texts)
    save_embeddings(collection, docs, vectors)
    sanity_check(docs, vectors)


if __name__ == "__main__":
    run()