#
# Lambda function to generate a presigned S3 upload URL.
#
# Endpoint intent:
# - POST /upload-url
#
# Request body JSON:
# {
#   "filename": "example.txt"
# }
#
# Success response JSON:
# {
#   "upload_url": "https://...",
#   "file_key": "uploads/example.txt",
#   "filename": "example.txt"
# }
#
# Notes:
# - Uses S3 presigned URL for direct browser/client upload.


import json
import boto3

s3 = boto3.client("s3")
BUCKET = "data-sanitizer-app"

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        filename = body.get("filename")

        if not filename:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "filename is required"})
            }

        key = f"uploads/{filename}"

        upload_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET,
                "Key": key,
                "ContentType": "text/plain",
            },
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "upload_url": upload_url,
                "file_key": key,
                "filename": filename
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }
