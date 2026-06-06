import boto3
import json
import uuid
import os
from datetime import datetime
from botocore.config import Config


BUCKET = os.environ["UPLOADS_BUCKET"]

s3 = boto3.client(
    "s3",
    region_name="eu-central-1",
    endpoint_url="https://s3.eu-central-1.amazonaws.com",
    config=Config(signature_version="s3v4")
)

print("BUCKET:", BUCKET)
print("REGION (client):", s3.meta.region_name)
print("S3 SERVICE:", s3.meta.service_model.service_name)


def lambda_handler(event, context):

    seller_id = "emanuele-test"

    params = event.get("queryStringParameters") or {}

    content_type = params.get("content_type", "image/jpeg")

    allowed_types = (
        "image/jpeg",
        "image/png",
        "image/webp"
    )

    if content_type not in allowed_types:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Unsupported file type"
            })
        }

    image_id = str(uuid.uuid4())

    extension = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp"
    }[content_type]

    key = f"uploads/{seller_id}/{image_id}.{extension}"

    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET,
            "Key": key,
            "ContentType": content_type
        },
        ExpiresIn=300
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "upload_url": url,
            "image_id": image_id,
            "key": key,
            "expires_in": 300,
            "bucket": BUCKET,
            "region": "eu-central-1",
            "generated_at": datetime.utcnow().isoformat()
        })
    }