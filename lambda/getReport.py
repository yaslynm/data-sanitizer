#
# Lambda function to retrieve a processed report JSON from S3.
#
# Endpoint intent:
# - GET /report?filename=<filename>
#
# Query parameter:
# - filename (required)
#
# Reads from:
# - reports/<filename>.json
#
# Success response:
# - Returns the report JSON body directly.
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

        key = f"reports/{filename}.json"
        response = s3.get_object(Bucket=BUCKET, Key=key)
        report_text = response["Body"].read().decode("utf-8")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": report_text
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }
