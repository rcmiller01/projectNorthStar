#!/usr/bin/env python3
"""Test file discovery."""

from pathlib import Path

def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p)
    return files

# Test with samples directory
root = Path("C:/Users/rober/OneDrive/Documents/GitHub/projectNorthStar/samples")
print(f"Root path exists: {root.exists()}")
print(f"Root is directory: {root.is_dir()}")

files = _iter_files(root)
print(f"Found files: {[str(f) for f in files]}")

# Test filtering for PDFs
pdf_files = [f for f in files if f.suffix.lower() == '.pdf']
print(f"PDF files: {[str(f) for f in pdf_files]}")
