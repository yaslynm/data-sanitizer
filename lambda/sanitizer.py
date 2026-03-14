def sanitize_text(text, findings):
    result = text
    for item in sorted(findings, key=lambda x: x["start"], reverse=True):
        pii_type = item["type"]
        start = item["start"]
        end = item["end"]
        result = result[:start] + f"[{pii_type.upper()}_INFORMATION_REDACTED]" + result[end:]

    return result