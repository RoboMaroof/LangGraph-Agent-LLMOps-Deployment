from fastapi import FastAPI, Request
import uvicorn
from contextlib import asynccontextmanager
from ingestion.routes import router as ingestion_router
from agents.routes import router as agent_router
from ingestion import create_index, qdrant_collection_exists

import os
import time
from dotenv import load_dotenv
import logging
from logging_config import setup_logging
from agents.agent_loader import preload_agent 

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

VECTORDB_PATH = os.getenv("VECTORDB_PATH")
DEFAULT_DOCS_FOLDER = os.getenv("DEFAULT_DOCS_FOLDER")
SQL_DB_PATH = os.getenv("SQL_DB_PATH")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if qdrant_collection_exists():
        logger.info("📦 Qdrant vector index already exists. Skipping index creation.")
    else:
        logger.info("🆕 No vector index found in Qdrant. Creating a new one...")
        sources_ingested = []

        if DEFAULT_DOCS_FOLDER and os.path.exists(DEFAULT_DOCS_FOLDER):
            try:
                logger.info(f"📁 Creating index from local documents in: {DEFAULT_DOCS_FOLDER}")
                create_index("docs", DEFAULT_DOCS_FOLDER)
                sources_ingested.append("docs")
            except Exception as e:
                logger.error(f"❌ Failed to index documents: {e}")

        if SQL_DB_PATH and os.path.exists(SQL_DB_PATH):
            try:
                logger.info(f"🗄️ Creating index from FAQ database at: {SQL_DB_PATH}")
                create_index("sql", SQL_DB_PATH)
                sources_ingested.append("sql")
            except Exception as e:
                logger.error(f"❌ Failed to index FAQ database: {e}")

        if not sources_ingested:
            logger.warning("⚠️ No data sources found to index at startup.")
        else:
            logger.info(f"✅ Indexed sources at startup: {', '.join(sources_ingested)}")

    try:
        preload_agent()
        logger.info("🧠 Preloaded GraphBuilder agent at startup.")
    except Exception as e:
        logger.exception("❌ Failed to preload agent at startup: %s", e)

    yield

    logger.info("🔚 Application shutdown complete.")

app = FastAPI(title="LangGraph Agent API", version="1.0", lifespan=lifespan)

app.include_router(ingestion_router, prefix="/vectordb")
app.include_router(agent_router, prefix="")

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info("%s %s took %.2fs", request.method, request.url.path, duration)
    logger.debug("📥 Request received: %s %s", request.method, request.url)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)