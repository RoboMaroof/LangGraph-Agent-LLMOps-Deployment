from llama_index.readers.web import SimpleWebPageReader
from llama_index.core import SimpleDirectoryReader, Document
import sqlite3
import os
import boto3
import tempfile
from urllib.parse import urlparse
from pathlib import Path

s3 = boto3.client("s3")

def download_s3_file(s3_uri: str) -> str:
    """Download file from S3 to a temporary local file and return its path."""
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')

    # Create a temporary directory and download the file into it
    temp_dir = tempfile.mkdtemp()
    filename = os.path.basename(key)
    local_path = os.path.join(temp_dir, filename)

    with open(local_path, 'wb') as f:
        s3.download_fileobj(bucket, key, f)

    return local_path

def get_documents(source_type, source_path):
    if source_type == "website":
        return SimpleWebPageReader().load_data(urls=[source_path])

    elif source_type == "docs":
        # Check if S3 path
        if source_path.startswith("s3://"):
            local_file_path = download_s3_file(source_path)
            local_dir = os.path.dirname(local_file_path)
            return SimpleDirectoryReader(local_dir).load_data()
        else:
            return SimpleDirectoryReader(source_path).load_data()

    elif source_type == "sql":
        if source_path.startswith("s3://"):
            local_db_path = download_s3_file(source_path)
        else:
            local_db_path = source_path

        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT question, answer FROM faq")
        rows = cursor.fetchall()
        conn.close()

        return [
            Document(text=f"Q: {q.strip()}\nA: {a.strip()}")
            for q, a in rows if q and a
        ]

    else:
        raise ValueError("Unsupported source type")
