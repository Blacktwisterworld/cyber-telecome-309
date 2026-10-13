# HF Dataset Range Lookup API

A Flask API that uses a JSON range index to identify
candidate files in an authorized dataset.

## Features

- Flask REST API
- 10-digit number validation
- Range-based candidate file selection
- API-key authentication
- Render deployment configuration

## Repository Structure

    hf-dataset-lookup-bot/
    ├── app.py
    ├── requirements.txt
    ├── render.yaml
    ├── file_ranges.json
    ├── README.md
    └── .gitignore

## Local Installation

1. Install Python 3.12.
2. Install dependencies:

   pip install -r requirements.txt

3. Set an API key in your environment.

   Linux/macOS:

   export API_KEY="your-long-random-secret"

   Windows PowerShell:

   $env:API_KEY="your-long-random-secret"

4. Start the application:

   python app.py

## Health Check

GET /

Example:

http://127.0.0.1:5000/

## Range Lookup

GET /lookup?number=1234567890

Include this HTTP header:

X-API-Key: your-long-random-secret

Example using curl:

curl -H "X-API-Key: your-long-random-secret" \
  "http://127.0.0.1:5000/lookup?number=1234567890"

## Render Deployment

1. Push the repository to GitHub.
2. Open Render and create a Blueprint deployment.
3. Select the repository containing render.yaml.
4. Set API_KEY to a strong secret in Render's environment settings.
5. Deploy the service.

## Important

The current implementation identifies candidate filenames only.
It does not yet search inside Parquet files.

Use only datasets you are authorized to access. Protect personal
information and restrict access to approved users.
