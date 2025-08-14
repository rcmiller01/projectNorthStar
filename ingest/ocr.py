"""OCR / PDF text extraction.

Strategy:
 1. PDF: extract text per page (pymupdf) first.
 2. Empty page: rasterize + OCR (pytesseract) if available.
 3. Images (png/jpg/jpeg): OCR directly if available.

Records: {doc_id,type,uri,page,text,meta}
Types: pdf, image, image_ocr (OCR used on page/image).
"""
from __future__ import annotations
from typing import List, Dict, Any
import hashlib
from pathlib import Path

_SUPPORTED_IMG = {".png", ".jpg", ".jpeg"}

try:  # optional imports
    import fitz  # type: ignore  # pymupdf
except Exception:  # pragma: no cover
    fitz = None  # type: ignore
try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore
try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore


def _hash_file(path: Path) -> str:
    h = hashlib.sha1()
    data = path.read_bytes()
    h.update(data)
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16] + ":" + path.name


def extract_text(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    ext = p.suffix.lower()
    uri = p.as_uri() if p.exists() else path
    doc_id = _hash_file(p) if p.exists() else f"missing:{p.name}"
    records: List[Dict[str, Any]] = []

    if ext == ".pdf" and fitz:
        try:
            doc = fitz.open(p)  # type: ignore
        except Exception:  # pragma: no cover
            return records
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            text = (page.get_text() or "").strip()
            page_type = "pdf"
            if not text and pytesseract and Image:  # fallback OCR
                pix = page.get_pixmap()
                img = Image.frombytes(
                    "RGB", (pix.width, pix.height), pix.samples
                )
                try:
                    ocr_txt = pytesseract.image_to_string(img).strip()
                except Exception:  # pragma: no cover
                    ocr_txt = ""
                if ocr_txt:
                    text = ocr_txt
                    page_type = "image_ocr"
                elif not pytesseract:
                    print(
                        "OCR fallback unavailable (pytesseract not installed)."
                    )
            if text:
                records.append(
                    {
                        "doc_id": doc_id,
                        "type": page_type,
                        "uri": uri,
                        "page": page_index + 1,
                        "text": text,
                        "meta": {
                            "filename": p.name,
                            "page": page_index + 1,
                            "ocr": page_type == "image_ocr",
                        },
                    }
                )
        return records

    if ext in _SUPPORTED_IMG:
        img_type = "image"
        text = ""
        if pytesseract and Image:
            try:
                img = Image.open(p)
                text = pytesseract.image_to_string(img).strip()
                if text:
                    img_type = "image_ocr"
            except Exception:  # pragma: no cover
                text = ""
        else:
            print(
                "OCR fallback unavailable (pytesseract not installed)."
            )
        if text:
            records.append(
                {
                    "doc_id": doc_id,
                    "type": img_type,
                    "uri": uri,
                    "page": 1,
                    "text": text,
                    "meta": {
                        "filename": p.name,
                        "page": 1,
                        "ocr": img_type == "image_ocr",
                    },
                }
            )
    return records
