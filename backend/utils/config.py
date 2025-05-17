import os

class Config:
    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "langgraph-rag-vectordb")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    DEFAULT_DOCS_FOLDER = os.getenv("DEFAULT_DOCS_FOLDER")
    SQL_DB_PATH = os.getenv("SQL_DB_PATH")
