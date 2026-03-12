import io
import zipfile
from xml.etree import ElementTree as ET

from fastapi import FastAPI, File, HTTPException, UploadFile, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pypdf import PdfReader
import base64
from typing import Dict

from pydantic import BaseModel

class Item(BaseModel):
    content: str


def register_exception(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):

        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        print(exc_str)
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

app = FastAPI(title="Word Text Extractor API")
register_exception(app)

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


def extract_text_from_docx(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            with archive.open("word/document.xml") as document_xml:
                xml_data = document_xml.read()
    except (zipfile.BadZipFile, KeyError) as exc:
        raise ValueError("Invalid .docx file") from exc

    root = ET.fromstring(xml_data)
    namespace = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    }
    paragraphs: list[str] = []

    for paragraph in root.findall(".//w:p", namespace):
        texts = [
            node.text
            for node in paragraph.findall(".//w:t", namespace)
            if node.text
        ]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)

    return "\n".join(paragraphs)


@app.post("/extract-text-word")
async def extract_text_word(file: UploadFile = File(...)) -> Dict[str, str]:
    filename = file.filename or ""
    if not filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Only .docx files are supported",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        text = extract_text_from_docx(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"text": text}


def extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception as exc:
        raise ValueError("Invalid .pdf file") from exc

    pages_text: list[str] = []
    for page in reader.pages:
        page_text = (page.extract_text() or "").strip()
        if page_text:
            pages_text.append(page_text)

    return "\n\n".join(pages_text)


@app.post("/extract-text-pdf")
async def extract_text_pdf(file: UploadFile = File(...)) -> Dict[str, str]:
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf files are supported",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        text = extract_text_from_pdf(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"text": text}

@app.post("/extract-text-base64")
async def extract_text_base64(item: Item) -> str:
    decoded_content = base64.b64decode(item.content)

    if not decoded_content:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        text = extract_text_from_pdf(decoded_content)
        print(text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return text
