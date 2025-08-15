"""Generate synthetic assets: dashboard screenshot + demo PDF/PNG.

Requires Pillow (pip install pillow). Safe synthetic content only.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:  # pragma: no cover
    raise SystemExit("Pillow required: pip install pillow") from e

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SAMPLES = ROOT / "samples"
DOCS.mkdir(exist_ok=True)
SAMPLES.mkdir(exist_ok=True)


def _font(size: int):
    for name in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def gen_dashboard_png(path: Path) -> None:
    w, h = 1200, 760
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    title_f = _font(36)
    d.text(
        (20, 15),
        "Project NorthStar – Dashboard Preview",
        fill="black",
        font=title_f,
    )
    sub_f = _font(18)
    d.rectangle([20, 80, 580, 380], outline="black", width=2)
    d.text((30, 90), "Common Issues (synthetic)", fill="black", font=sub_f)
    rows = [
        ("login timeout", 7, "P2"),
        ("upload mismatch", 5, "P1"),
        ("session reset", 3, "P3"),
    ]
    y = 130
    for name, cnt, sev in rows:
        d.text(
            (40, y),
            f"{name:16} | count={cnt} | sev={sev}",
            fill="black",
            font=_font(14),
        )
        y += 28
    d.rectangle([620, 80, 1180, 380], outline="black", width=2)
    d.text(
        (630, 90),
        "Severity Trends (weekly synthetic)",
        fill="black",
        font=sub_f,
    )
    chart_origin = (640, 340)
    points = [
        (0, -40),
        (100, -80),
        (200, -20),
        (300, -120),
        (400, -60),
        (500, -90),
    ]
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        d.line(
            [
                chart_origin[0] + x1,
                chart_origin[1] + y1,
                chart_origin[0] + x2,
                chart_origin[1] + y2,
            ],
            fill="steelblue",
            width=3,
        )
    d.rectangle([20, 400, 1180, 740], outline="black", width=2)
    d.text((30, 410), "Duplicate Clusters (sample)", fill="black", font=sub_f)
    dup_samples = [
        (
            "Cluster #1",
            ["log:app.log:12", "pdf:demo.pdf:p1", "ocr:demo.png:p1"],
        ),
        (
            "Cluster #2",
            ["log:app.log:5", "pdf:demo.pdf:p1"],
        ),
    ]
    y = 450
    for label, members in dup_samples:
        d.text((40, y), label, fill="black", font=_font(16))
        y += 26
        for m in members:
            d.text((60, y), f"- {m}", fill="#666666", font=_font(14))
            y += 22
        y += 10
    footer = _font(12)
    d.text(
        (20, h - 20),
        f"synthetic preview generated {datetime.utcnow().isoformat()}Z",
        fill="#666666",
        font=footer,
    )
    img.save(path)


def gen_demo_png(path: Path) -> None:
    img = Image.new("RGB", (600, 400), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 590, 390], outline="black", width=2)
    d.text((30, 40), "Synthetic Data", fill="black", font=_font(42))
    d.text((30, 120), "Used for OCR ingest test", fill="black", font=_font(24))
    d.text((30, 180), "No real user content", fill="black", font=_font(24))
    img.save(path)


def gen_demo_pdf(path: Path) -> None:
    img = Image.new("RGB", (595, 842), "white")
    d = ImageDraw.Draw(img)
    d.text(
        (40, 60),
        "Project NorthStar Demo PDF",
        fill="black",
        font=_font(28),
    )
    paragraphs = [
        "Synthetic placeholder document.",
        "Contains no PII. Used to exercise PDF ingest + chunking.",
        "Version v1.0.0.",
    ]
    y = 140
    for p in paragraphs:
        d.text((40, y), p, fill="black", font=_font(16))
        y += 40
    img.save(path, "PDF")


def gen_log(path: Path) -> None:
    lines = [
        "2025-08-14T00:00:01Z [api] login timeout for user demo",
        "2025-08-14T00:00:02Z [worker] retrying batch id=42 status=timeout",
        "2025-08-14T00:00:03Z [ingest] pdf chunked pages=1 tokens=120",
        "2025-08-14T00:00:04Z [ocr] image demo.png text_len=38",
        "2025-08-14T00:00:05Z [retrieval] query='login failure' k=5",
        "2025-08-14T00:00:06Z [triage] draft plan generated evidence=3",
        "2025-08-14T00:00:07Z [verifier] playbook verification=pass",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    gen_dashboard_png(DOCS / "dashboard.png")
    gen_demo_png(SAMPLES / "demo.png")
    gen_demo_pdf(SAMPLES / "demo.pdf")
    log_path = SAMPLES / "app.log"
    if not log_path.exists():
        gen_log(log_path)
    print(
        "[gen-assets] wrote: docs/dashboard.png, "
        "samples/demo.png, samples/demo.pdf"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
