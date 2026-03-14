# Data Sanitizer

This repository contains a data sanitization workflow for detecting and redacting sensitive information.

## Frontend (NiceGUI)

The frontend is implemented in `client/results_viewer_app.py`.

This is a single-page results viewer that calls deployed API Gateway endpoints (no AWS credentials used in the GUI).

- Enter a processed filename (example: `ancestor.txt`)
- Click `Get Results`
- Calls `GET /report` and `GET /download`
- Displays risk level, total findings, counts by type, sanitized text, and a download link

### Run Frontend Locally

1. Install dependencies:

```bash
pip install -r client/requirements.txt
```

2. Start the frontend:

```bash
python client/results_viewer_app.py
```

3. Open the app in your browser:

```text
http://localhost:8080
```

### Backend API Contract Used by Frontend

The frontend uses this API base URL:

- `https://riwzsm6apd.execute-api.us-east-2.amazonaws.com/prod`

Endpoints used:

- `GET /report?filename=<filename>`
- `GET /download?filename=<filename>`

`GET /report` example response fields shown in UI:

- `risk_level`
- `total_findings`
- `findings_by_type`
- `sanitized_text`

`GET /download` example response fields shown in UI:

- `download_url`
