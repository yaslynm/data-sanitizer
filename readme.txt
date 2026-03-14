Data Sanitizer - Setup and Run Guide

Course: CS310
Authors: Yaslyn Mohammed, Kailyn Mohammed, Reem Khalid

This project has:
- Server side (AWS): Lambda + S3 + API Gateway
- Client side: NiceGUI app in client/client.py

1) Requirements
- Python 3.10+
- AWS account and permissions for Lambda, S3, API Gateway, IAM
- pip

2) Install Python packages (local machine)
From the project root:

pip install nicegui requests boto3

3) Server setup (AWS)
A) S3
- Create a bucket for uploads and outputs (example: data-sanitizer-app).
- Use folders/keys like:
  - uploads/
  - sanitized/
  - reports/

B) Lambda
- Create Lambda function for processing S3 uploads.
- Upload code from lambda/process_function.py, lambda/pii_detector.py, lambda/report_generator.py.
- Runtime: Python 3.11 (or similar).
- Set execution role permissions for S3 read/write.
- Configure S3 trigger for object-created events on uploads/ prefix.

C) API Gateway
- Expose endpoints used by the client:
  - POST /upload-url
  - GET /report?filename=...
  - GET /download?filename=...
- Integrate these endpoints with your backend Lambda logic.
- Deploy API and copy the base URL.

4) Client setup
- Open client/client.py.
- Set API_BASE_URL to your deployed API Gateway URL if needed.

5) Run client locally
From project root:

python client/client.py

Then open:
http://localhost:8080

6) Basic work flow of our app
- Upload a .txt file using the Upload & Process card.
- Wait for completion and auto-loaded report.
- Or use Look Up Results with an existing filename.

Notes
- This client does not require local AWS credentials; all file access is through API endpoints and presigned URLs.
- If your API endpoint names differ, you must update client/client.py accordingly.
