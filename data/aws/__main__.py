import os
import boto3
from mimetypes import guess_type

PDF_DIR = "./pdfs"
BUCKET_NAME = "ncsu-sg"
s3 = boto3.client("s3")

for file in os.listdir(PDF_DIR):
    if file.endswith(".pdf"):
        path = os.path.join(PDF_DIR, file)

        content_type = guess_type(path)[0] or "application/pdf"

        s3.upload_file(
            path,
            BUCKET_NAME,
            file,
            ExtraArgs={
                "ContentType": content_type,
            },
        )

        print(f"uploaded {file} to https://{BUCKET_NAME}.s3.amazonaws.com/{file}")
