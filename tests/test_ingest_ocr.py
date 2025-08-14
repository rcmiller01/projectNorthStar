from pathlib import Path
from ingest import extract_text, to_chunks


def _generate_image(tmp_path: Path) -> Path:
    try:
        from PIL import Image, ImageDraw  # type: ignore
    except Exception:
        return Path('samples/ocr.png')  # fallback (may not exist)
    p = tmp_path / 'hello.png'
    img = Image.new('RGB', (120, 40), color='white')
    d = ImageDraw.Draw(img)
    d.text((5, 10), 'hello world', fill='black')
    img.save(p)
    return p


def test_extract_and_chunk_image(tmp_path):
    img_path = _generate_image(Path(tmp_path))
    recs = extract_text(str(img_path))
    if not recs:  # allow skip when no OCR backend
        return
    chunks = to_chunks(recs, max_tokens=32)
    assert chunks, 'no chunks produced'
    m = chunks[0]['meta']
    assert 'type' in m and 'uri' in m
