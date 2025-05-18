import os
import time
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from agents.agent_loader import AgentLoader
from agents.routes import router as agent_router
from ingestion.index_builder import load_index
from ingestion.routes import router as ingestion_router
from logging_config import setup_logging
from utils.logger import get_logger

load_dotenv()
setup_logging()
logger = get_logger(__name__)

# TODO: DOCS FOLDER & SQL -> S3 BUCKET
DEFAULT_DOCS_FOLDER = os.getenv("DEFAULT_DOCS_FOLDER")
SQL_DB_PATH = os.getenv("SQL_DB_PATH")


# Executed once at app startup and once at shutdown for setup and teardown operations
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        index = load_index()
        if index is None:
            logger.warning("⚠️ No documents loaded into index.")
        else:
            logger.info("✅ Vector index loaded or created.")
    except Exception as e:
        logger.exception("❌ Failed to load or create vector index: %s", e)

    try:
        AgentLoader()
        logger.info("🧠 Preloaded GraphBuilder agent at startup.")
    except Exception as e:
        logger.exception("❌ Failed to preload agent: %s", e)

    yield
    logger.info("🔚 Application shutdown complete.")


# FastAPI app with lifespan context manager
app = FastAPI(title="LangGraph Agent API", version="1.0", lifespan=lifespan)

# Route registrations
app.include_router(ingestion_router, prefix="/vectordb")
app.include_router(agent_router, prefix="")


# HTTP request timing middleware
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
