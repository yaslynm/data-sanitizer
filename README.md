# Data Sanitizer

This project detects PII in uploaded text files, creates a sanitized version, and returns a report through an AWS API.

## Repository Layout

```text
data-sanitizer/
  README.md
  client/
		client.py
  lambda/
		getUploadURL.py
		getReport.py
		getDownloadLink.py
		process_function.py
		pii_detector.py
		report_generator.py
```

## What Runs Where

- Client: `client/client.py` (NiceGUI, local web app)
- Server: AWS (Lambda + S3 + API Gateway)

## Prerequisites

- Python 3.10+
- pip
- AWS account with access to Lambda, S3, API Gateway, and IAM

## Install (Local)

From repo root:

```bash
pip install nicegui requests boto3
```

## Server Setup (AWS)

1. Create an S3 bucket.
2. Use these key prefixes:
	- `uploads/`
	- `sanitized/`
	- `reports/`
3. Deploy Lambda functions:
	- `lambda/process_function.py` (S3 trigger for uploads)
	- `lambda/getUploadURL.py` (API: presigned upload URL)
	- `lambda/getReport.py` (API: read report JSON)
	- `lambda/getDownloadLink.py` (API: presigned download URL)
4. Package helper modules with processing Lambda:
	- `lambda/pii_detector.py`
	- `lambda/report_generator.py`
5. Give Lambda IAM permissions for S3 read/write.
6. Add an S3 trigger to `process_function` for object-created events in `uploads/`.
7. Configure API Gateway endpoint integrations:
	- `POST /upload-url` -> `getUploadURL`
	- `GET /report` -> `getReport`
	- `GET /download` -> `getDownloadLink`
8. Deploy API Gateway and copy the base URL.

## Client Setup + Run

1. Open `client/client.py` and verify `API_BASE_URL` points to your deployed API.
2. Start the app:

```bash
python client/client.py
```

3. Open:

```text
http://localhost:8080
```

## How to Use

1. Upload flow:
	- Choose a `.txt` file.
	- Click `Upload & Process`.
	- App uploads to S3, waits for processing, then auto-loads report.
2. Lookup flow:
	- Enter a processed filename.
	- Click `Get Results`.

The UI displays:
- risk level
- total findings
- findings by type
- sanitized text
- download URL for sanitized output

