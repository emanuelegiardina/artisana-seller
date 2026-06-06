import boto3
import os
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal


s3 = boto3.client("s3")

ddb = boto3.resource("dynamodb")
table = ddb.Table("emanuele-artisana-images-test")

THUMBS_BUCKET = os.environ["THUMBNAILS_BUCKET"]

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError



def lambda_handler(event, context):

    seller_id = "emanuele-test"

   
#    resp = table.query(
#        KeyConditionExpression=
#        Key("seller_id").eq(
#            seller_id
#        ),
#        Limit=20,
#        ScanIndexForward=False
#    )
    

    resp = table.query(
        KeyConditionExpression=
        Key("PK").eq(
            f"SELLER#{seller_id}"
        ),
    Limit=20,
    ScanIndexForward=False
    )

    items=[]

    for item in resp.get("Items",[]):

        url=s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket":THUMBS_BUCKET,
                "Key":item["thumbnail_key"]
            },
            ExpiresIn=3600
        )

        items.append({
            **item,
            "thumbnail_url":url
        })

    return {
        "statusCode":200,
        "body":json.dumps(
            {
                "images":items,
                "count":len(items)
            },
            default=decimal_default
        )
    }