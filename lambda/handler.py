#
# Lambda function to sanitize a text file.
#
# The text file is passed to the function in the body of the request, in
# JSON format:
#
#  {
#    "name": "example.txt"
#    "content": "My email is user@example.com"
#  }
#
# The response is an object in JSON format, with status code of 
# 200 (success) or 500 (server-side error). The data contains
# the following fields:
#
#    risk_level:
#         The overall severity level of the detected sensitive
#         information (low, medium, or high).
#    
#    total_findings:
#         The total number of sensitive data instances detected.
#    
#    findings_by_type:
#         A dictionary-type object summarizing the number of
#         occurrences by type (email, phone, ssn, and credit card).
#   
#    sanitized_text:
#         The processed version of the input where sensitive has
#         been replaced with placeholders (ex: [EMAIL_INFORMATION_REDACTED]).
#
#
#     { 
#       "message": "success",
#       "data":    {
#                    "risk_level": "high",
#                    "total_findings": 4,
#                    "findings_by_type": {
#                                          "email": 1,
#                                          "phone": 1,
#                                          "ssn": 1,
#                                          "credit_card": 1
#                                        }
#                    "sanitized_text": "..."
#                  }
#     }
#
#

import json
from pii_detector import detect_pii
from sanitizer import sanitize_text
from report_generator import generate_report

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
            raise Exception("request has no key 'bytes'")

        name = body["name"]
        content = body["content"]

        print("name: ", name)
        print("content: ", content)

        print("**Detecting sensitive data...")
        
        findings = detect_pii(content)
        sanitized_text = sanitize_text(content, findings)
        report = generate_report(sanitized_text, findings)

        body = {
            "message": "success",
            "data": report
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

        if str(e).startswith("request has no"):
            return {
                "statusCode": 400,
                "body": json.dumps(body)
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps(body)
            }
