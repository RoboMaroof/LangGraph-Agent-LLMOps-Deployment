import os
import logging
from pathlib import Path

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from ingestion.sources import get_documents, list_s3_documents
from ingestion.qdrant_utils import get_qdrant_client, ensure_collection_exists, qdrant_collection_exists

logger = logging.getLogger(__name__)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langgraph-rag-vectordb")

def create_index(source_type: str, source_path: str):
    logger.info(f"📄 Ingesting documents from {source_type}: {source_path}")
    documents = get_documents(source_type, source_path)

    if not documents:
        logger.warning("⚠️ No documents loaded for indexing.")
        return load_index()

    for i, doc in enumerate(documents[:3]):
        logger.debug(f"📄 Document {i+1} preview:\n{doc.text[:300]}...\n")

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)

    if not nodes:
        logger.warning("⚠️ No nodes created from documents.")
        return load_index()

    logger.info(f"✅ Parsed {len(nodes)} nodes from documents.")
    ensure_collection_exists()
    vector_store = QdrantVectorStore(client=get_qdrant_client(), collection_name=QDRANT_COLLECTION)

    index = VectorStoreIndex.from_vector_store(vector_store)
    index.insert_nodes(nodes)

    logger.info("✅ Documents indexed and stored in Qdrant.")
    return index

def create_empty_index():
    logger.info("📭 Creating empty vector index in Qdrant...")
    ensure_collection_exists()
    vector_store = QdrantVectorStore(client=get_qdrant_client(), collection_name=QDRANT_COLLECTION)
    return VectorStoreIndex.from_vector_store(vector_store)

def load_index():
    logger.info("📦 Loading vector index from Qdrant...")
    if not qdrant_collection_exists():
        logger.warning("⚠️ Vector index not found. Checking S3 for documents...")

        s3_files = list_s3_documents(bucket="langgraph-docs", prefix="uploads/")
        if s3_files:
            logger.info("📄 Found documents in S3. Ingesting and creating index...")
            index = None
            for path in s3_files:
                try:
                    index = create_index(source_type="docs", source_path=path)
                except Exception as e:
                    logger.warning(f"❌ Skipped {path} due to error: {e}")
            return index or create_empty_index()
        else:
            logger.info("📭 No documents found in S3. Creating empty vector index.")
            return create_empty_index()

    vector_store = QdrantVectorStore(client=get_qdrant_client(), collection_name=QDRANT_COLLECTION)
    return VectorStoreIndex.from_vector_store(vector_store)