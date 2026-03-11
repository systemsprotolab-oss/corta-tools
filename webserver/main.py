import io
import zipfile
from xml.etree import ElementTree as ET

from fastapi import FastAPI, File, HTTPException, UploadFile
from pypdf import PdfReader


app = FastAPI(title="Word Text Extractor API")


@app.get("/health")
async def health() -> dict[str, str]:
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
async def extract_text_word(file: UploadFile = File(...)) -> dict[str, str]:
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
async def extract_text_pdf(file: UploadFile = File(...)) -> dict[str, str]:
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
