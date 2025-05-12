from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from .sources import get_documents
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[1]/'.env'
load_dotenv(dotenv_path=env_path)
VECTORDB_PATH = os.getenv("VECTORDB_PATH")

logging.basicConfig(level=logging.INFO)

def create_index(source_type, source_path):
    documents = get_documents(source_type, source_path)
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)

    if os.path.exists(VECTORDB_PATH):
        # Load existing index
        storage_context = StorageContext.from_defaults(persist_dir=VECTORDB_PATH)
        index = load_index_from_storage(storage_context)
        # Append new documents
        index.insert_nodes(nodes)
    else:
        # Create new index
        index = VectorStoreIndex(nodes=nodes)

    # Save the updated or new index
    index.storage_context.persist(persist_dir=VECTORDB_PATH)
    return index

def load_index():
    if os.path.exists(VECTORDB_PATH):
        storage_context = StorageContext.from_defaults(persist_dir=VECTORDB_PATH)
        return load_index_from_storage(storage_context)
    return None
