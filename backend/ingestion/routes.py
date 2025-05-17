from fastapi import APIRouter, UploadFile, File, Body
from .index_builder import create_index
from .upload_handler import save_uploaded_file
from utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_and_index(file: UploadFile = File(...)):
    """
    Uploads a document to S3 and indexes it into Qdrant.
    """
    try:
        # Upload to S3 and get the S3 URI
        s3_uri = await save_uploaded_file(file)

        # Index using the document source from S3
        create_index("docs", s3_uri)

        return {"message": f"✅ Uploaded and indexed file: {file.filename}"}
    except Exception as e:
        logger.exception("❌ Upload and indexing failed")
        return {"error": str(e)}

@router.post("/create")
def manual_ingest(source_type: str = Body(...), source_path: str = Body(...)):
    """
    Index documents from an existing source path (S3 URI).
    """
    try:
        create_index(source_type, source_path)
        return {"message": f"✅ Ingested and indexed from {source_type}"}
    except Exception as e:
        logger.exception("❌ Manual ingestion failed")
        return {"error": str(e)}
