from fastapi import APIRouter, Body, UploadFile, File
from .index_builder import create_index
from .upload_handler import save_uploaded_file
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[1]/'.env'
load_dotenv(dotenv_path=env_path)
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
UPLOADED_DOCS_FOLDER = os.getenv("UPLOADED_DOCS_FOLDER")

router = APIRouter()

@router.post("/create")
def manual_ingest(source_type: str = Body(...), source_path: str = Body(...)):
    try:
        create_index(source_type, source_path)
        return {"message": f"Ingested and indexed from {source_type}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/upload")
def upload_and_ingest(file: UploadFile = File(...)):
    try:
        saved_path = save_uploaded_file(file)

        # TODO all types
        # Assume it's a docs ingestion
        create_index("docs", UPLOADED_DOCS_FOLDER)

        return {"message": f"Uploaded and indexed file: {file.filename}"}
    except Exception as e:
        return {"error": str(e)}
