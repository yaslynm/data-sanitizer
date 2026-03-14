# Data Sanitizer

This project detects and redacts sensitive text, then serves a report through an AWS-backed API.

## Repository Layout

```text
data-sanitizer/
	README.md
	client/
		client.py
	lambda/
		pii_detector.py
		process_function.py
		report_generator.py
	sample_data/
		sample1.txt
		sample2.txt
```

## Frontend

The frontend lives in `client/client.py` (NiceGUI).

It supports two flows:
1. Upload a `.txt` file and process it.
2. Look up results for an already-processed filename.

The page displays:
- risk level
- total findings
- findings by type
- sanitized text
- download link for the sanitized file

### Run the Frontend Locally

Install dependencies:

```bash
pip install nicegui requests
```

Run:

```bash
python client/client.py
```

Open:

```text
http://localhost:8080
```

## Backend Integration

Frontend API base URL:

- `https://riwzsm6apd.execute-api.us-east-2.amazonaws.com/prod`

Endpoints used by the frontend:

- `POST /upload-url`
- `GET /report?filename=<filename>`
- `GET /download?filename=<filename>`

Expected response fields:

- `/report`: `risk_level`, `total_findings`, `findings_by_type`, `sanitized_text`
- `/download`: `download_url`

## Sample Input Files

Use `sample_data/sample1.txt` and `sample_data/sample2.txt` for local testing.
