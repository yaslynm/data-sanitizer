import base64
import os
from typing import Any, Dict

import httpx


class APIClientError(Exception):
    """Raised when frontend cannot complete a backend API request."""


class DataSanitizerAPIClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: float = 30.0) -> None:
        self.base_url = (base_url or os.getenv("SANITIZER_API_BASE_URL") or "http://localhost:3000").rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def process_text(self, text: str, file_name: str = "uploaded.txt") -> Dict[str, Any]:
        if not text.strip():
            raise APIClientError("No text provided. Upload a file or paste content before processing.")

        payload = {
            "file_name": file_name,
            "file_content_base64": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
        }

        url = f"{self.base_url}/process"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise APIClientError(f"Unable to connect to backend at {self.base_url}: {exc}") from exc

        if response.status_code >= 400:
            details = response.text.strip()
            message = details if details else f"HTTP {response.status_code}"
            raise APIClientError(f"Backend returned an error: {message}")

        try:
            body = response.json()
        except ValueError as exc:
            raise APIClientError("Backend response was not valid JSON.") from exc

        report = body.get("report") if isinstance(body.get("report"), dict) else {}
        detections = body.get("detections")
        if not isinstance(detections, list):
            detections = body.get("findings")
        if not isinstance(detections, list):
            detections = []

        sanitized_text = body.get("sanitized_text")
        if not isinstance(sanitized_text, str):
            sanitized_text = report.get("sanitized_text", "") if isinstance(report, dict) else ""

        return {
            "request_id": body.get("request_id", "unknown"),
            "detections": detections,
            "sanitized_text": sanitized_text,
            "report": report,
            "raw_response": body,
        }