import os
from minio import Minio
from minio.error import S3Error
from sqlalchemy import create_engine
from sqlalchemy.engine.interfaces import DBAPICursor
from dotenv import load_dotenv
from os import environ

load_dotenv()


class Attachment:
    db_id: int
    namespace: int
    url: str
    preview_url: str

    def __str__(self) -> str:
        return (
            f"Attachment(id={self.db_id}, url={self.url},"
            f"preview_url={self.preview_url})"
        )


ENDPOINT = environ["ENDPOINT"]
ACCES_KEY = environ["ACCES_KEY"]
MINIO_SECRET_KEY = environ["environ"]
MINIO_BUCKET = environ["MINIO_BUCKET"]
CERTS_PATH = environ["CERTS_PATH"]
DB_URL = environ["DB_URL"]

input_path = input("Путь для сохранения: ")
SAVE_PATH = "/var/static" if input_path == "" else input_path
print(SAVE_PATH)
mc = Minio(
    endpoint=ENDPOINT,
    access_key=ACCES_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=True,
)


def connect_db(dsn: str):
    return create_engine(
        dsn,
    ).raw_connection()


def get_attachments(cur: DBAPICursor, namespace=427425760141246465) -> list[Attachment]:
    query = """
        SELECT id, url, preview_url
        FROM compose_attachment
        WHERE rel_namespace = %s 
        AND deleted_at IS NULL
        AND name LIKE 'CortaDataHub_pravo.gov.ru_NPA.pdf'
    """
    cur.execute(query, (namespace,))
    rows = cur.fetchall()
    attachments = []
    for row in rows:
        att = Attachment()
        att.db_id = row[0]
        att.url = row[1]
        att.preview_url = row[2]
        attachments.append(att)
    return attachments


def download_minio_file(url: str, path="/var/static/compose"):

    if not os.path.isdir(path):
        raise Exception("Заданный путь сохранения файлов не существует")
    resp = mc.get_object(MINIO_BUCKET, url)
    f_path = path + "/" + url
    print(f_path)
    with open(f_path, "wb") as fh:
        for d in resp.stream(32 * 1024):
            fh.write(d)


def update_attachment_path(
    cur: DBAPICursor, att_id: int, new_url: str, new_preview_url: str
):
    query = """
        UPDATE compose_attachment
        SET url = %s ,
        preview_url = %s 
        WHERE id = %s
    """
    cur.execute(query, (new_url, new_preview_url, att_id))


def сheck_object_existense(mc: Minio, key: str) -> bool:
    try:
        mc.stat_object(MINIO_BUCKET, key)
        return True
    except S3Error:
        return False
    except Exception:
        return False


def main():
    db = connect_db(DB_URL)
    try:
        cur = db.cursor()
        attachments = get_attachments(cur)
        # print(attachments)
        for att in attachments:
            print(f"Processing attachment: {att}")
            if сheck_object_existense(mc, "compose/" + att.url):
                print(f"File found in MinIO: {att.url}, downloading...")
                # download_minio_file("compose/" + att.url, SAVE_PATH)
                print(SAVE_PATH, att.url)
                new_url = SAVE_PATH + "/compose/" + att.url
                new_preview_url = SAVE_PATH + "/compose/" + att.preview_url
                # update_attachment_path(cur, att.db_id, new_url, new_preview_url)
                # db.commit()

            else:
                print(f"File: {att.url}, not exist. skipping download.")
    except Exception as e:
        db.close()
        raise e
    finally:
        db.close()


main()
