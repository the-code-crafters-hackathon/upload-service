from pathlib import Path
from typing import List, Tuple
import os
import shutil
import subprocess
import zipfile
import boto3
from fastapi import UploadFile, HTTPException


class VideoProcessingGateway:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.uploads_dir = base_dir / "uploads"
        self.outputs_dir = base_dir / "outputs"
        self.temp_dir = base_dir / "temp"

        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, upload_file: UploadFile, timestamp: str) -> Path:
        filename = f"{timestamp}_{upload_file.filename}"
        dest = self.uploads_dir / filename

        env = os.getenv("APP_ENV", "development")

        if env != "production":
            try:
                with open(dest, "wb") as buffer:
                    shutil.copyfileobj(upload_file.file, buffer)
            finally:
                upload_file.file.close()

            return dest

        bucket = os.getenv("AWS_S3_BUCKET")
        if not bucket:
            try:
                upload_file.file.close()
            except Exception:
                pass
            raise HTTPException(status_code=500, detail="S3 bucket not configured")

        s3_key = f"uploads/{filename}"

        try:
            s3_client = boto3.client(
                "s3",
                region_name=os.getenv("AWS_REGION"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
            )

            try:
                upload_file.file.seek(0)
            except Exception:
                pass

            s3_client.upload_fileobj(upload_file.file, bucket, s3_key)
        except Exception as e:
            try:
                upload_file.file.close()
            except Exception:
                pass
            raise HTTPException(status_code=500, detail=f"Erro ao enviar arquivo para S3: {e}")

        try:
            upload_file.file.close()
        except Exception:
            pass

        return f"s3://{bucket}/{s3_key}"
