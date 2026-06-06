import json
from unittest.mock import patch

import handler

def make_event(content_type=None, seller_id="user-123"):


event = {
    "requestContext": {
        "authorizer": {
            "jwt": {
                "claims": {
                    "sub": seller_id
                }
            }
        }
    }
}

if content_type:
    event["queryStringParameters"] = {
        "content_type": content_type
    }

return event


@patch("handler.s3")
def test_returns_presigned_url(mock_s3):


mock_s3.generate_presigned_url.return_value = (
    "https://s3.amazonaws.com/fake"
)

response = handler.handler(
    make_event("image/jpeg"),
    None
)

assert response["statusCode"] == 200

body = json.loads(response["body"])

assert "upload_url" in body
assert "image_id" in body


@patch("handler.s3")
def test_rejects_unsupported_content_type(mock_s3):


response = handler.handler(
    make_event("application/pdf"),
    None
)

assert response["statusCode"] == 400


@patch("handler.s3")
def test_url_expires_in_300_seconds(mock_s3):


mock_s3.generate_presigned_url.return_value = (
    "https://s3.amazonaws.com/fake"
)

response = handler.handler(
    make_event("image/jpeg"),
    None
)

body = json.loads(response["body"])

assert body["expires_in"] == 300

