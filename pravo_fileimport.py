import os
from minio import Minio
from minio.error import S3Error
from sqlalchemy import create_engine
from sqlalchemy.engine.interfaces import DBAPICursor
from dotenv import load_dotenv
from os import environ
from corta_classes import Record, Attachment
from typing import List
import requests
from time import sleep
import time
import base64
import json

load_dotenv()


ENDPOINT = environ["ENDPOINT"]
ACCES_KEY = environ["ACCES_KEY"]
MINIO_SECRET_KEY = environ["MINIO_SECRET_KEY"]
MINIO_BUCKET = environ["MINIO_BUCKET"]
CERTS_PATH = environ["CERTS_PATH"]
DB_URL = environ["DB_URL"]

input_path = ""
SAVE_PATH = "/var/static/compose" if input_path == "" else input_path


AUTH_URL = environ.get("AUTH_URL", "http://127.0.0.1/auth/oauth2/token")
AUTH_BASIC = environ.get(
    "AUTH_BASIC",
    "Basic NDc4NzMwNTk0OTMzMjc2NjczOlM1Zml6VnVYOGRPSUxYemJ4RTZjOGJHbkpseE5VMUsyaWVadGM3em9HTFZZdnBzUlcyYkE3eVc3ZHM3WjQzZzY=",
)
AUTH_SCOPE = environ.get("AUTH_SCOPE", "profile api discovery openid")
TOKEN_REFRESH_SKEW_SECONDS = int(environ.get("TOKEN_REFRESH_SKEW_SECONDS", "30"))

_token_cache = {
    "access_token": None,
    "expires_at": 0,  # unix timestamp
}



base_path = "."
# base_path = "/var/static/compose"

def get_auth_token():
    url = AUTH_URL

    scope_encoded = AUTH_SCOPE.replace(" ", "%20")
    payload = f"grant_type=client_credentials&scope={scope_encoded}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": AUTH_BASIC,
    }
    response = requests.post(url, headers=headers, data=payload, timeout=30)
    if not response.ok:
        raise Exception("Ошибка получения токена", response.content)
    
    return response.json()


def _jwt_get_exp_unverified(access_token: str):
    try:
        parts = access_token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8")).decode(
            "utf-8"
        )
        payload = json.loads(payload_json)
        return int(payload.get("exp")) if payload.get("exp") is not None else None
    except Exception:
        return None


def refresh_access_token(force: bool = False) -> str:
    now = int(time.time())
    if not force and _token_cache["access_token"] and now < int(_token_cache["expires_at"]):
        return _token_cache["access_token"]

    token_data = get_auth_token()
    access_token = token_data.get("access_token")
    if not access_token:
        raise Exception("Токен не получен (нет access_token)", token_data)

    exp = _jwt_get_exp_unverified(access_token)
    expires_in = token_data.get("expires_in")

    if exp is not None:
        expires_at = int(exp) - TOKEN_REFRESH_SKEW_SECONDS
    elif expires_in is not None:
        expires_at = now + int(expires_in) - TOKEN_REFRESH_SKEW_SECONDS
    else:
        expires_at = now + 60

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = expires_at
    return access_token


def get_auth_headers(extra: dict | None = None, force_refresh: bool = False) -> dict:
    token = refresh_access_token(force=force_refresh)
    headers = {"Authorization": f"Bearer {token}"}
    if extra:
        headers.update(extra)
    return headers


def authed_request(method: str, url: str, **kwargs):
    headers = kwargs.pop("headers", None) or {}
    merged_headers = get_auth_headers(headers, force_refresh=False)

    resp = requests.request(method, url, headers=merged_headers, timeout=60, **kwargs)
    if resp.status_code == 401:
        merged_headers = get_auth_headers(headers, force_refresh=True)
        resp = requests.request(method, url, headers=merged_headers, timeout=60, **kwargs)
    return resp
def clear_state_file(f):
    f.seek(0)
    f.truncate()


def download_file(project_id, attachment_id):
    url = f"http://publication.pravo.gov.ru/file/pdf?eoNumber={project_id}"
    file_name = SAVE_PATH + f"/{attachment_id}.pdf"

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)




# Получаем токен лениво (при первом запросе) или можно форсировать здесь:
refresh_access_token(force=True)
limit = 100
# base_url = f"http://127.0.0.1/api/compose/namespace/427425760141246465/module/474627738712014812014849/record/?limit={limit}"
base_url = f"https://regulation-corta.lipetsk.gov.ru/api/compose/namespace/427425760141246465/module/474627738712014849/record/?limit={limit}"
total_url = base_url + "&incPageNavigation=true&incTotal=true"
# attachment_url = "https://regulation-corta.lipetsk.gov.ru/api/compose/namespace/427425760141246465/attachment/record/478726754124300289/original/CortaDataHub_pravo.gov.ru_NPA.pdf?sign=a7e5f0769cba802a8137b66bdfb9a38abf7687d5&userID=463489013114798081&download=1"
payload = {}
headers = {}
response = authed_request("GET", total_url, headers=headers)
state_file = "latest_worked_page_cursor"
if not response.ok:
    raise Exception("Ошибка парсинга", response.content)

response = response.json()["response"]
pageNavigation = response["filter"]["pageNavigation"]

if not os.path.exists(state_file):
    created = open(state_file, "w")
    created.write("1")
    created.close()

with open(state_file, "r+") as state:
    state = int(state.readline())


with open(state_file, "w+") as f:
    cur_state = state
    try:
        print(state)
        for page in pageNavigation:
            cur_state = page["page"]
            if state > page["page"]:
                continue
            if page["cursor"] is not None:
                records_url = base_url + "&pageCursor=" + page["cursor"]

            else:
                records_url = base_url

            page_data_content = authed_request("GET", records_url, headers=headers)

            if not page_data_content.ok:
                raise Exception("Ошибка парсинга 2", page_data_content.content)

            page_data_content = page_data_content.json()["response"]["set"]

            for record in page_data_content:
                values = {item["name"]: item["value"] for item in record["values"]}
                attachment_id = values["Text"]
                project_id = values["ProjectID"]

                fileExist = os.path.exists(SAVE_PATH + f"/{attachment_id}.pdf")

                download_file(attachment_id=attachment_id, project_id=project_id)
                clear_state_file(f)
                sleep(1)
                print(
                    f"ФАЙЛ {SAVE_PATH + f'/{attachment_id}.pdf'} обработан. Ссылка на запись: https://regulation-corta.lipetsk.gov.ru/compose/ns/orvofv/pages/474627738732003329/record/{record['recordID']}"
                )
    finally:
        f.write(str(cur_state))
