#!/usr/bin/env python3
"""CI verifier asserting clean PDF authorship metadata and zero watermarks across all tracks."""
from __future__ import annotations

import glob
import json
import os
import re
import sys

import pymupdf as fitz

FORBIDDEN = [
    r"suryagentic",
    r"surya\s+academy",
    r"agent\s+academy",
    r"local\s*ai",
    r"mercury",
    r"balaji",
    r"\bprincipal\b",
    r"20\+\s*years",
    r"22\+\s*years",
    r"over\s+20\s+years",
]


def main() -> None:
    pdfs = sorted(glob.glob("track-*/*.pdf"))
    if len(pdfs) < 8:
        raise SystemExit(f"Expected >=8 PDFs across 6 tracks, found {len(pdfs)}")
    checked = []
    for p in pdfs:
        doc = fitz.open(p)
        meta = doc.metadata
        if meta.get("author") != "Nagarjuna Kamireddy":
            raise SystemExit(f"{p}: unexpected author metadata {meta!r}")
        if "weasyprint" in json.dumps(meta).lower() or "anthropic" in json.dumps(meta).lower():
            raise SystemExit(f"{p}: generator watermark leaked in metadata {meta!r}")
        txt = "\n".join(pg.get_text("text") for pg in doc)
        pages = len(doc)
        doc.close()
        for pat in FORBIDDEN:
            m = re.search(pat, txt, flags=re.I)
            if m:
                raise SystemExit(f"{p}: forbidden token {m.group(0)!r}")
        checked.append({"path": p, "pages": pages, "bytes": os.path.getsize(p), "author": meta["author"]})
    print(json.dumps({"status": "OK", "verified_pdfs": len(checked), "files": checked}, indent=2))


if __name__ == "__main__":
    main()
