
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

flow = InstalledAppFlow.from_client_secrets_file(
    str(BASE_DIR / "credentials.json"),
    SCOPES,
)

credentials = flow.run_local_server(port=0)

(BASE_DIR / "token.json").write_text(
    credentials.to_json(),
    encoding="utf-8",
)

print("Gmail authorization completed.")
