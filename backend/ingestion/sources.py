import os
import sqlite3
import tempfile
from urllib.parse import urlparse

import boto3
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.readers.web import SimpleWebPageReader

from utils.logger import get_logger

logger = get_logger(__name__)
s3 = boto3.client("s3")


def download_s3_file(s3_uri: str) -> str:
    """
    Download file from S3 to a temporary local file and return its path.
    """
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    temp_dir = tempfile.mkdtemp()
    filename = os.path.basename(key)
    local_path = os.path.join(temp_dir, filename)

    with open(local_path, "wb") as f:
        s3.download_fileobj(bucket, key, f)

    logger.info(f"📥 Downloaded file from S3: {s3_uri} → {local_path}")
    return local_path


def list_s3_documents(bucket: str, prefix: str = "uploads/") -> list[str]:
    """
    List all S3 object paths under a prefix, returning full S3 URIs.
    """
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get("Contents", [])
        file_paths = [
            f"s3://{bucket}/{obj['Key']}"
            for obj in contents
            if not obj["Key"].endswith("/")  # Exclude folder markers
        ]
        logger.info(f"📥 Found {len(file_paths)} documents in s3://{bucket}/{prefix}")
        return file_paths
    except Exception as e:
        logger.warning(f"❌ Failed to list S3 documents: {e}")
        return []


def get_documents(source_type, source_path):
    if source_type == "website":
        logger.info("🌐 Fetching content from website...")
        return SimpleWebPageReader().load_data(urls=[source_path])

    elif source_type == "docs":
        logger.info("📂 Loading document files...")
        if source_path.startswith("s3://"):
            local_file_path = download_s3_file(source_path)
            local_dir = os.path.dirname(local_file_path)
            return SimpleDirectoryReader(local_dir).load_data()
        else:
            return SimpleDirectoryReader(source_path).load_data()

    elif source_type == "sql":
        logger.info("🗄️ Reading FAQ entries from SQLite...")
        if source_path.startswith("s3://"):
            local_db_path = download_s3_file(source_path)
        else:
            local_db_path = source_path

        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT question, answer FROM faq")
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error: {e}")
            raise
        finally:
            conn.close()

        return [
            Document(text=f"Q: {q.strip()}\nA: {a.strip()}") for q, a in rows if q and a
        ]

    else:
        raise ValueError(f"❌ Unsupported source type: {source_type}")
