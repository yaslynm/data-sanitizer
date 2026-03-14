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
#         The processed version of the input where sensitive 
#     
#   { 
#     "message": "success",
#     "data":    {
#                  "risk_level": "high",
#                  "total_findings": 4,
#                  "findings_by_type": {
#                                        "email": 1,
#                                        "phone": 1,
#                                        "ssn": 1,
#                                        "credit_card": 1
#                                      }
#                  "sanitized_text": "..."
#                }
#   }
#
#

def lambda_handler(even, context):
    try:
        print("**Call to ")
