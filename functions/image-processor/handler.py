import boto3
import os
import io
import uuid
from datetime import datetime, timezone
from PIL import Image

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

s3=boto3.client("s3")

ddb=boto3.resource("dynamodb")

table=ddb.Table(
    "emanuele-artisana-image"
)

THUMBS_BUCKET=os.environ[
    "THUMBNAILS_BUCKET"
]

THUMB_SIZE=(200,200)


def lambda_handler(event,context):

    for record in event["Records"]:

        bucket=record["s3"]["bucket"]["name"]

        key=record["s3"]["object"]["key"]


        with xray_recorder.in_subsegment(
            "download-original"
        ):

            obj=s3.get_object(
                Bucket=bucket,
                Key=key
            )

            image_data=obj[
                "Body"
            ].read()


        with xray_recorder.in_subsegment(
            "create-thumbnail"
        ):

            img=Image.open(
                io.BytesIO(image_data)
            )

            img.thumbnail(
                THUMB_SIZE
            )

            buf=io.BytesIO()

            img.save(
                buf,
                format="JPEG",
                quality=85
            )

            buf.seek(0)


        parts=key.split("/")

        seller_id=parts[1]

        filename=parts[2]

        image_id=filename.split(".")[0]

        thumb_key=(
            f"thumbnails/"
            f"{seller_id}/"
            f"{image_id}.jpg"
        )


        with xray_recorder.in_subsegment(
            "upload-thumbnail"
        ):

            s3.put_object(
                Bucket=THUMBS_BUCKET,
                Key=thumb_key,
                Body=buf.getvalue(),
                ContentType="image/jpeg"
            )


        with xray_recorder.in_subsegment(
            "write-dynamodb"
        ):

            table.put_item(
                Item={

                    "PK":
                    f"SELLER#{seller_id}",

                    "SK":
                    f"IMAGE#{image_id}",

                    "seller_id":
                    seller_id,

                    "image_id":
                    image_id,

                    "original_key":
                    key,

                    "thumbnail_key":
                    thumb_key,

                    "status":
                    "processed",

                    "original_size":
                    len(image_data),

                    "thumbnail_size":
                    len(
                        buf.getvalue()
                    ),

                    "created_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat()

                }
            )

    return{
        "statusCode":200
    }