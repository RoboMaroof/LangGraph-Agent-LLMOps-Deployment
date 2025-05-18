import os

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langgraph-rag-vectordb")


def get_qdrant_client() -> QdrantClient:
    """
    Initializes and returns a Qdrant client instance using credentials from environment variables.
    """
    return QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)


def qdrant_collection_exists() -> bool:
    """
    Checks whether the target vector collection exists in the Qdrant instance.

    Returns:
        bool: True if the collection exists, False otherwise.
    """
    client = get_qdrant_client()
    return client.collection_exists(collection_name=QDRANT_COLLECTION)


def ensure_collection_exists():
    """
    Ensures that the target collection exists in Qdrant.
    If it does not exist, it creates (or recreates) the collection
    with a predefined vector configuration.

    Notes:
        - Vector size is hardcoded to 1536 (for OpenAI embeddings).
        - Uses cosine distance as the similarity metric.
    """
    client = get_qdrant_client()
    if not client.collection_exists(QDRANT_COLLECTION):
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )


# TODO: Remove duplicate function


def create_collection(vector_size: int = 1536):  # TODO: Make this configurable.
    """
    Ensures the target Qdrant collection exists.
    Creates it if missing, with the appropriate vector settings.
    """
    client = get_qdrant_client()
    if not client.collection_exists(collection_name=QDRANT_COLLECTION):
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
