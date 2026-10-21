
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

client_config = {
    "installed": {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "project_id": os.getenv("GOOGLE_PROJECT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":
            "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [
            os.getenv("GOOGLE_REDIRECT_URI", "http://localhost")
        ],
    }
}

flow = InstalledAppFlow.from_client_config(
    client_config,
    SCOPES,
)

credentials = flow.run_local_server(port=0)

(BASE_DIR / "token.json").write_text(
    credentials.to_json(),
    encoding="utf-8",
)

print("Gmail authorization completed.")
