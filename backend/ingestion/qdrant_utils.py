import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langgraph-rag-vectordb")

def get_qdrant_client():
    return QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)

def qdrant_collection_exists() -> bool:
    client = get_qdrant_client()
    return client.collection_exists(collection_name=QDRANT_COLLECTION)

def ensure_collection_exists():
    client = get_qdrant_client()
    if not client.collection_exists(QDRANT_COLLECTION):
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )