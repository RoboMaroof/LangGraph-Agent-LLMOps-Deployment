from fastapi import FastAPI, Request
import uvicorn
from contextlib import asynccontextmanager

from ingestion.routes import router as ingestion_router
from agents.routes import router as agent_router
from agents.agent_loader import preload_agent
from ingestion.index_builder import create_index
from ingestion.qdrant_utils import qdrant_collection_exists

from dotenv import load_dotenv
from logging_config import setup_logging
import logging
import os
import time

# Load environment variables and logging config
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Optional local data ingestion sources
DEFAULT_DOCS_FOLDER = os.getenv("DEFAULT_DOCS_FOLDER")
SQL_DB_PATH = os.getenv("SQL_DB_PATH")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not qdrant_collection_exists():
        logger.info("🆕 No vector index found in Qdrant. Creating a new one...")
        sources_ingested = []

        if DEFAULT_DOCS_FOLDER and os.path.exists(DEFAULT_DOCS_FOLDER):
            try:
                logger.info(f"📁 Indexing local docs at: {DEFAULT_DOCS_FOLDER}")
                create_index("docs", DEFAULT_DOCS_FOLDER)
                sources_ingested.append("docs")
            except Exception as e:
                logger.error(f"❌ Failed to index local docs: {e}")

        if SQL_DB_PATH and os.path.exists(SQL_DB_PATH):
            try:
                logger.info(f"🗄️ Indexing FAQ database at: {SQL_DB_PATH}")
                create_index("sql", SQL_DB_PATH)
                sources_ingested.append("sql")
            except Exception as e:
                logger.error(f"❌ Failed to index SQLite DB: {e}")

        if not sources_ingested:
            logger.warning("⚠️ No data sources indexed at startup.")
        else:
            logger.info(f"✅ Indexed sources: {', '.join(sources_ingested)}")
    else:
        logger.info("📦 Qdrant vector index already exists.")

    try:
        preload_agent()
        logger.info("🧠 Preloaded GraphBuilder agent at startup.")
    except Exception as e:
        logger.exception("❌ Failed to preload agent: %s", e)

    yield
    logger.info("🔚 Application shutdown complete.")


app = FastAPI(title="LangGraph Agent API", version="1.0", lifespan=lifespan)

# Route registrations
app.include_router(ingestion_router, prefix="/vectordb")
app.include_router(agent_router, prefix="")

# Request timing middleware
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info("%s %s took %.2fs", request.method, request.url.path, duration)
    logger.debug("📥 Request received: %s %s", request.method, request.url)
    return response

# Run with uvicorn manually
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
