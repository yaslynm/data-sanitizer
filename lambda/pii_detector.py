###################################################################
#
# detect_pii
#
# Detects personally identifiable information (PII) in a block
# of text using regular expression pattern matching. The function
# scans the text for common sensitive data types including emails,
# phone numbers, social security numbers, and credit card numbers.
#
#
# Authors:
# Yas'lyn Mohammed
# Reem Khalid
# Kai'lyn Mohammed
#
# Parameters:
# text : str (Input text that may contain sensitive information)
#
# Returns:
# findings : list of dict (A list of dictionaries describing each detected PII instance)
#
#     Each dictionary contains:
#
#       "type"  : the type of PII detected
#                 ("email", "phone", "ssn", "credit_card")
#       "start" : starting index of the match in the text
#       "end"   : ending index of the match in the text
#
# Example return structure:
# [
#   {"type": "email", "start": 12, "end": 27},
#   {"type": "phone", "start": 36, "end": 48},
#   {"type": "ssn", "start": 60, "end": 71},
#   {"type": "credit_card", "start": 84, "end": 103}
# ]
#
###################################################################

import re

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
PHONE_REGEX = r'(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
SSN_REGEX = r'\b\d{3}-\d{2}-\d{4}\b'
CC_REGEX = r'\b(?:\d[ -]*?){13,16}\b'

def detect_pii(text):
    findings = []

    for pii in re.finditer(EMAIL_REGEX, text):
        findings.append({
            "type": "email",
            "start": pii.start(),
            "end": pii.end()
        })
    
    for pii in re.finditer(PHONE_REGEX, text):
        findings.append({
            "type": "phone",
            "start": pii.start(),
            "end": pii.end()
        })
    
    for pii in re.finditer(SSN_REGEX, text):
        findings.append({
            "type": "ssn",
            "start": pii.start(),
            "end": pii.end()
        })
    
    for pii in re.finditer(CC_REGEX, text):
        findings.append({
            "type": "credit_card",
            "start": pii.start(),
            "end": pii.end()
        })

    findings.sort(key=lambda x: x["start"])
    return findings

    #findings return structure: [{'type': 'email', 'start': 12, 'end': 27}, {'type': 'phone', 'start': 36, 'end': 48}, {'type': 'ssn', 'start': 60, 'end': 71}, {'type': 'credit card', 'start': 84, 'end': 103}]