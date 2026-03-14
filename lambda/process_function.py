#
# Lambda function to process an uploaded text file from S3 and detect
# sensitive information.
#
# Trigger:
# This function is triggered automatically when a text file is uploaded
# to the `uploads/` folder in the S3 bucket.
#
# Input:
# The Lambda receives an S3 event notification containing:
# - bucket name
# - object key
#
# Example S3 event structure:
# {
#   "Records": [
#     {
#       "s3": {
#         "bucket": { "name": "data-sanitizer-app" },
#         "object": { "key": "uploads/example.txt" }
#       }
#     }
#   ]
# }
#
# Processing steps:
# 1. Read uploaded file from S3
# 2. Detect PII using detect_pii() from pii_detector.py
# 3. Sanitize detected values with placeholder replacements
# 4. Generate a report using generate_report() from report_generator.py
# 5. Save the sanitized file to `sanitized/`
# 6. Save the report JSON to `reports/`
#
# Outputs:
# - sanitized/<filename>
# - reports/<filename>.json
#
# Response:
# Returns a JSON response with status code 200 on success or 500 on error.
#

import json
import boto3
import urllib.parse
from pii_detector import detect_pii
from report_generator import generate_report

s3 = boto3.client("s3")


def sanitize_text(text, findings):
    # replace from back to front so indexes don't shift
    replacements = {
        "email": "[EMAIL]",
        "phone": "[PHONE]",
        "ssn": "[SSN]",
        "credit_card": "[CREDIT_CARD]"
    }

    sanitized = text
    for item in sorted(findings, key=lambda x: x["start"], reverse=True):
        pii_type = item["type"]
        start = item["start"]
        end = item["end"]
        replacement = replacements.get(pii_type, "[REDACTED]")
        sanitized = sanitized[:start] + replacement + sanitized[end:]

    return sanitized


def lambda_handler(event, context):
    try:
        print("**Call to process...")
        print("EVENT:", json.dumps(event))

        record = event["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        print("bucket_name:", bucket_name)
        print("key:", key)

        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response["Body"].read().decode("utf-8")
        name = key.split("/")[-1]

        print("name:", name)
        print("content:", content)

        print("**Detecting sensitive data...")
        findings = detect_pii(content)

        print("**Sanitizing text...")
        sanitized_text = sanitize_text(content, findings)

        print("**Generating report...")
        report = generate_report(sanitized_text, findings)

        sanitized_key = f"sanitized/{name}"
        report_key = f"reports/{name}.json"

        print("**Writing sanitized file to S3...")
        s3.put_object(
            Bucket=bucket_name,
            Key=sanitized_key,
            Body=sanitized_text.encode("utf-8"),
            ContentType="text/plain"
        )

        print("**Writing report to S3...")
        s3.put_object(
            Bucket=bucket_name,
            Key=report_key,
            Body=json.dumps(report, indent=2).encode("utf-8"),
            ContentType="application/json"
        )

        body = {
            "message": "success",
            "original_file": key,
            "sanitized_file": sanitized_key,
            "report_file": report_key,
            "data": findings
        }

        return {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    except Exception as e:
        print("**ERROR")
        print("**Message:", str(e))

        body = {
            "message": str(e),
            "data": []
        }

        return {
            "statusCode": 500,
            "body": json.dumps(body)
        }
