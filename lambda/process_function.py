#
# Lambda function to process a text file and detect sensitive information.
#
# The text file is passed to the function in the body of the request, in
# JSON format:
#
#  {
#    "name": "example.txt",
#    "content": "My email is user@example.com and my # is 999-999-9999"
#  }
#
# The function scans the content for personally identifiable information
# (PII) including email addresses, phone numbers, SSNs, and credit card
# numbers using detect_pii() from pii_detector.py.

# The response is an object in JSON format, with status code of 
# 200 (success) or 500 (server-side error). The data contains
# the detected findings with their positions in the text.
#
# Example response format:
#
#     { 
#       "message": "success",
#       "data": [
#                 { "type": "email", "start": 12, "end": 27 },
#                 { "type": "phone", "start": 41, "end": 52 }
#               ]
#     }
#
#

import json
import uuid
import boto3
from pii_detector import detect_pii

def lambda_handler(event, context):
    try:
        print("**Call to process...")

        print("**Accessing request body...")

        if "body" not in event:
            raise Exception("request has no body")

        body = json.loads(event["body"])

        if "name" not in body:
            raise Exception("request has no key 'name'")
        if "content" not in body:
            raise Exception("request has no key 'content'")

        name = body["name"]
        content = body["content"]

        print("name: ", name)
        print("content: ", content)

        print("**Uploading file to S3...")
        
        # generating a unique string for the bucketkey
        unique_str = str(uuid.uuid4())
        key = f"original/{unique_str}_{name}"
        bucket_name = "data-sanitizer-app"
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content.encode("utf-8")
        )

        print("uploaded to: ", unique_str)


        print("**Detecting sensitive data...")
        
        findings = detect_pii(content)

        body = {
            "message": "success",
            "data": findings
        }

        return {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    except Exception as e:
        print("**ERROR")
        print("**Message: ", str(e))

        body = {
            "message": str(e),
            "data": []
        }

        return {
            "statusCode": 500,
            "body": json.dumps(body)
        }