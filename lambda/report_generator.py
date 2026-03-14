def generate_report(sanitized_text, findings):
    counts = {
        "email": 0,
        "phone": 0,
        "ssn": 0,
        "credit_card": 0
    }

    for item in findings: 
        pii_type = item["type"]
        if pii_type in counts:
            counts[pii_type] += 1

    if counts["ssn"] > 0 or counts["credit_card"] > 0:
        risk = "high"
    elif len(findings) > 0:
        risk = "medium"
    else:
        risk = "low"

    report = {
        "risk_level": risk,
        "total_findings": len(findings),
        "findings_by_type": counts,
        "sanitized_text": sanitized_text
    }

    return report


    # Return structure:
    # {
    #     "risk_level": str
    #     "total_findings": int
    #     "findings_by_type": {email, phone, ssn, credit_card counts}
    #     "sanitized_text": str
    # }