import os

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from ingestion.sources import get_documents, list_s3_documents
from utils.logger import get_logger
from utils.qdrant_utils import create_collection, get_qdrant_client

logger = get_logger(__name__)

Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-ada-002"
)  # TODO: Make this configurable

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langgraph-rag-vectordb")


def create_index(source_type: str, source_path: str):
    """
    Ingests documents from a local or remote source, processes them into chunks (nodes),
    and indexes them into a Qdrant vector store.

    Args:
        source_type (str): Type of document source ('docs', 'sql', etc.).
        source_path (str): Path or identifier for the source.

    Returns:
        VectorStoreIndex: The index created and stored in Qdrant.
    """
    logger.info(f"📄 Ingesting documents from {source_type}: {source_path}")
    documents = get_documents(source_type, source_path)

    if not documents:
        logger.warning("⚠️ No documents loaded for indexing.")
        return load_index()

    # Preview first few documents for debugging
    for i, doc in enumerate(documents[:3]):
        logger.debug(f"📄 Document {i+1} preview:\n{doc.text[:300]}...\n")

    # Split documents into chunks (nodes) suitable for vector storage
    splitter = SentenceSplitter(
        chunk_size=512, chunk_overlap=50
    )  # TODO: Make chunk size and overlap configurable
    nodes = splitter.get_nodes_from_documents(documents)

    if not nodes:
        logger.warning("⚠️ No nodes created from documents.")
        return load_index()

    logger.info(f"✅ Parsed {len(nodes)} nodes from documents.")

    # Ensure the Qdrant collection exists before storing vectors
    create_collection()

    # Create a Qdrant-backed vector store and build the index
    vector_store = QdrantVectorStore(
        client=get_qdrant_client(), collection_name=QDRANT_COLLECTION
    )
    index = VectorStoreIndex.from_vector_store(vector_store)
    index.insert_nodes(nodes)

    logger.info("✅ Documents indexed and stored in Qdrant.")
    return index


def create_empty_index():
    """
    Creates an empty vector index in Qdrant.
    Useful as a fallback when no documents are available to index.

    Returns:
        VectorStoreIndex: An empty index connected to the Qdrant collection.
    """
    logger.info("📭 Creating empty vector index in Qdrant...")

    # Ensure the Qdrant collection exists before storing vectors
    create_collection()
    vector_store = QdrantVectorStore(
        client=get_qdrant_client(), collection_name=QDRANT_COLLECTION
    )
    return VectorStoreIndex.from_vector_store(vector_store)


def load_index():
    """
    Loads the existing vector index from Qdrant. If the collection doesn't exist,
    attempts to load documents from an S3 bucket and create a new index.

    Returns:
        VectorStoreIndex: The loaded or newly created vector index.
    """
    logger.info("📦 Loading vector index from Qdrant...")

    client = get_qdrant_client()
    if not client.collection_exists(collection_name=QDRANT_COLLECTION):
        logger.warning("⚠️ Vector index not found. Checking S3 for documents...")

        # Attempt to retrieve documents from a pre-configured S3 bucket
        s3_files = list_s3_documents(
            bucket="langgraph-docs", prefix="uploads/"
        )  # TODO: Make bucket configurable
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

    # Load the existing index from Qdrant
    vector_store = QdrantVectorStore(
        client=get_qdrant_client(), collection_name=QDRANT_COLLECTION
    )
    return VectorStoreIndex.from_vector_store(vector_store)
