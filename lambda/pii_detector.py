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