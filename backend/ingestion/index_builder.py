import os
import logging
from dotenv import load_dotenv
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from .sources import get_documents

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "rag_docs")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_qdrant_client():
    return QdrantClient(
        url=QDRANT_HOST,
        api_key=QDRANT_API_KEY,
    )

def create_index(source_type, source_path):
    logger.info(f"📄 Loading documents from {source_type}: {source_path}")
    documents = get_documents(source_type, source_path)

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)

    logger.info("⚙️ Setting up Qdrant Cloud collection...")
    client = get_qdrant_client()

    if not client.collection_exists(collection_name=QDRANT_COLLECTION):
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
    )
    index = VectorStoreIndex(nodes=nodes, vector_store=vector_store)

    logger.info("✅ Index created and stored in Qdrant Cloud.")
    return index

def load_index():
    logger.info("📦 Loading index from Qdrant Cloud...")
    client = get_qdrant_client()
    vector_store = QdrantVectorStore(client=client, collection_name=QDRANT_COLLECTION)
    return VectorStoreIndex.from_vector_store(vector_store)
