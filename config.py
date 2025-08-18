import json
from datetime import datetime
from google.cloud import secretmanager
from google.oauth2 import service_account

today = datetime(2024, 9, 1)

def access_secret_version(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    secret_string = response.payload.data.decode("UTF-8")
    return secret_string

# 你 GCP 專案 ID
PROJECT_ID = "gen-lang-client-0700041250"

access_token = access_secret_version(PROJECT_ID, "LINE_CHANNEL_ACCESS_TOKEN")
secret = access_secret_version(PROJECT_ID, "LINE_CHANNEL_SECRET")

SERVICE_ACCOUNT_JSON_str = access_secret_version(PROJECT_ID, "SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_JSON_dict = json.loads(SERVICE_ACCOUNT_JSON_str)
# 直接建立憑證物件
SERVICE_ACCOUNT_JSON = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_JSON_dict,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

)
