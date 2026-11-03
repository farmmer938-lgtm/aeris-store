#!/usr/bin/env python3
"""Rebuild the AF Studio catalogue from the live Do.ink storefront.

Runs on GitHub Actions (free, no secrets). Source of truth is the public storefront, so the
catalogue can never drift from what customers can actually buy. Exits non-zero when the store
is down or has no products, which makes GitHub email the owner.

Usage: python3 scripts/refresh_catalog.py   (from the repo root)
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from pathlib import Path

STORE = "https://app.do.ink/stores/navintas"
OUT = Path("af-studio-m938-2/products.json")
UA = {"User-Agent": "af-catalog-refresh/1.0"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(page: str) -> list[dict]:
    cards = []
    for m in re.finditer(r'<a[^>]+href="(/stores/navintas/products/[^"]+)"(.*?)</a>', page, re.S):
        block = m.group(2)
        img = re.search(r'<img[^>]+src="([^"]+)"', block)
        txt = html.unescape(re.sub(r"<[^>]+>", " ", block))
        txt = re.sub(r"\s+", " ", txt).strip()
        price = re.search(r"Starting from (฿[\d,]+(?:\.\d{2})?)", txt)
        title = txt.split("Starting from")[0].strip()
        if ">" in title:
            title = title.split(">", 1)[1].strip()
        if title:
            cards.append({
                "href": m.group(1),
                "title": title,
                "price": price.group(1) if price else "",
                "img": img.group(1) if img else "",
            })
    return cards


def main() -> int:
    page = fetch(STORE)
    products = parse(page)
    if len(products) < 5:
        print(f"FAIL: only {len(products)} products parsed from {STORE}", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(products, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT} with {len(products)} products")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
