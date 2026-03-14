# Data Sanitizer

This repository contains a data sanitization workflow for detecting and redacting sensitive information.

## Frontend (NiceGUI)

The frontend is implemented in `client/nicegui_app.py` and focuses on:

- Uploading or pasting document text
- Calling backend APIs for detection and sanitization
- Presenting findings and report details in a user-friendly interface

### Run Frontend Locally

1. Install dependencies:

```bash
pip install -r client/requirements.txt
```

2. Start the frontend:

```bash
python client/nicegui_app.py
```

3. Open the app in your browser:

```text
http://localhost:8080
```

### Backend API Contract Used by Frontend

The frontend expects a backend endpoint:

- `POST /process`

Request body fields:

- `file_name`: original file name
- `file_content_base64`: UTF-8 text encoded in base64

Response fields used by frontend:

- `request_id`
- `sanitized_text`
- `detections` (or `findings`)
- `report`

You can change the backend base URL directly in the frontend UI.
