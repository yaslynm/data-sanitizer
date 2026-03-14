#
# Lambda function to generate a presigned download URL for a sanitized file.
#
# Endpoint intent:
# - GET /download?filename=<filename>
#
# Query parameter:
# - filename (required)
#
# Reads from:
# - sanitized/<filename>
#
# Success response JSON:
# {
#   "download_url": "https://..."
# }
#

import json
import boto3

s3 = boto3.client("s3")
BUCKET = "data-sanitizer-app"

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        filename = params.get("filename")

        if not filename:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "filename is required"})
            }

        key = f"sanitized/{filename}"

        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"download_url": url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }
