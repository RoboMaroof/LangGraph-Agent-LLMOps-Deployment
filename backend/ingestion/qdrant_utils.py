import os
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")

def qdrant_collection_exists():
    client = QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY
    )
    try:
        return client.collection_exists(collection_name=QDRANT_COLLECTION)
    except UnexpectedResponse as e:
        if "404" in str(e):
            return False
        raise  
