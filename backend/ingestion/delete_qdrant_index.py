import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Qdrant configuration
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langgraph-rag-vectordb")

def delete_qdrant_index():
    if not QDRANT_HOST or not QDRANT_API_KEY:
        print("❌ QDRANT_HOST or QDRANT_API_KEY not set. Please check your .env file.")
        return

    client = QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)

    if client.collection_exists(QDRANT_COLLECTION):
        confirm = input(f"⚠️ Are you sure you want to delete collection '{QDRANT_COLLECTION}'? This cannot be undone. (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("❌ Deletion aborted.")
            return

        client.delete_collection(QDRANT_COLLECTION)
        print(f"✅ Qdrant collection '{QDRANT_COLLECTION}' deleted successfully.")
    else:
        print(f"ℹ️ Collection '{QDRANT_COLLECTION}' does not exist.")

if __name__ == "__main__":
    delete_qdrant_index()
