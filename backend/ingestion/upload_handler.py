import os
from fastapi import UploadFile
import boto3
from pathlib import Path
from urllib.parse import quote_plus


AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# Initialize S3 client
s3 = boto3.client("s3", region_name=AWS_REGION)

def save_uploaded_file(uploaded_file: UploadFile) -> str:
    """
    Uploads the uploaded file to the configured S3 bucket and returns the s3 URI.
    """
    s3_key = f"uploads/{quote_plus(uploaded_file.filename)}"
    
    # Upload the file to S3
    s3.upload_fileobj(uploaded_file.file, S3_BUCKET, s3_key)

    # Return the S3 URI
    return f"s3://{S3_BUCKET}/{s3_key}"
