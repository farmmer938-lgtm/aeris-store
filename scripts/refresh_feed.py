#!/usr/bin/env python3
"""Keep the machine-readable surface of the store honest, every day, with nobody watching.

Runs on GitHub Actions (free, no secrets). Three jobs, in order:

  1. FEED    - parse index.html (the only place live buy URLs exist) and rewrite
               agents/catalog.json from it. Refuses to write when it parses zero offers, so a
               parse break cannot turn a selling store into "nothing for sale".
  2. HEALTH  - HEAD/GET every buy link and count the dead ones. A dead buy button is the only
               storefront failure that is AF's own fault, so it must be measured, not assumed.
  3. SUBMIT  - push every sitemap URL at IndexNow. A 200 is a receipt, not an index, so the
               result is recorded rather than claimed as reachability.

Writes agents/status.json either way; the workflow commits when anything changed.

Usage: python3 scripts/refresh_feed.py   (from the repo root)
"""
from __future__ import annotations

import concurrent.futures as cf
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SITE = "https://farmmer938-lgtm.github.io/aeris-store/"
HOST = "farmmer938-lgtm.github.io"
INDEXNOW_KEY = "20008340a440f10c1c89d03b5d985719"
UA = {"User-Agent": "af-feed-refresh/1.0"}
TIERS = ["basic", "premium", "sync"]
TIER_NAMES = {"basic": "Basic License", "premium": "Premium License", "sync": "Sync License"}

CARD_RE = re.compile(
    r'<h2>(?P<title>.*?)</h2>\s*'
    r'<div class="meta">(?P<meta>.*?)</div>\s*'
    r'<div class="desc">(?P<desc>.*?)</div>\s*'
    r'<audio[^>]*src="(?P<preview>[^"]+)"[^>]*>\s*</audio>\s*'
    r'<div class="buy">(?P<buy>.*?)</div>', re.S)
LINK_RE = re.compile(r'<a(?P<cls>[^>]*)href="(?P<href>[^"]+)"[^>]*>(?P<label>.*?)</a>', re.S)


def strip(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def status_of(url: str) -> object:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return "ERR:%s" % type(e).__name__


def parse(page: str) -> list[dict]:
    products = []
    for m in CARD_RE.finditer(page):
        stripe, usdc = [], []
        for a in LINK_RE.finditer(m.group("buy")):
            (usdc if "fluxapay" in a.group("href") else stripe).append(a.group("href"))
        products.append({
            "slug": m.group("preview").split("/")[-2],
            "title": strip(m.group("title")),
            "meta": strip(m.group("meta")),
            "description": strip(m.group("desc")),
            "preview": SITE + m.group("preview").lstrip("/"),
            "stripe": stripe,
            "usdc": usdc,
        })
    return products


def price_of(card_url: str, page: str) -> str | None:
    m = re.search(re.escape(card_url) + r'">[^<]*<span>([^<]+)</span>', page)
    return strip(m.group(1)) if m else None


def build(page: str) -> dict:
    products = parse(page)
    for p in products:
        p["offers"] = []
        for i, tier in enumerate(TIERS):
            card = p["stripe"][i] if i < len(p["stripe"]) else None
            p["offers"].append({
                "tier": tier, "name": TIER_NAMES[tier],
                "price_text": price_of(card, page) if card else None,
                "card_url": card,
                "usdc_url": p["usdc"][i] if i < len(p["usdc"]) else None,
            })
    return {
        "schema": "af.aeris_catalog.v1",
        "provider": "AERIS MUSIC",
        "storefront": SITE,
        "paid_catalog_status": "OPEN" if products else "CLOSED",
        "track_count": len(products),
        "offer_count": sum(len(p["stripe"]) + len(p["usdc"]) for p in products),
        "rails": {"card": "Stripe hosted checkout", "usdc": "Base (USDC) via agent wallet"},
        "delivery": "Instant. The checkout redirects to a license page whose URL holds the "
                    "decryption key; the master decrypts in the buyer's browser.",
        "license_terms": "Non-exclusive worldwide licence for the tier purchased. Redistribution, "
                         "resale and NFT use of the track itself are not permitted.",
        "generated_from": SITE,
        "catalog": products,
    }


def indexnow(urls: list[str]) -> object:
    body = json.dumps({"host": HOST, "key": INDEXNOW_KEY,
                       "keyLocation": "%s%s.txt" % (SITE, INDEXNOW_KEY),
                       "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8",
                                          "User-Agent": UA["User-Agent"]})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return "ERR:%s" % type(e).__name__


def main() -> int:
    index = Path("index.html")
    if not index.exists():
        print("refusing: no index.html in the working directory")
        return 2
    page = index.read_text(encoding="utf-8", errors="replace")

    catalog = build(page)
    print("tracks=%d offers=%d status=%s"
          % (catalog["track_count"], catalog["offer_count"], catalog["paid_catalog_status"]))
    if catalog["offer_count"] == 0:
        print("refusing: parsed zero offers — keeping the previous feed rather than claiming CLOSED")
        return 1

    Path("agents").mkdir(exist_ok=True)
    Path("agents/catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    urls = [u for p in catalog["catalog"] for u in p["stripe"] + p["usdc"]]
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda u: (u, status_of(u)), urls))
    dead = [(u, s) for u, s in res if not (isinstance(s, int) and 200 <= s < 400)]
    print("buy links: %d checked, %d dead" % (len(urls), len(dead)))

    sm = Path("sitemap.xml")
    pages = re.findall(r"<loc>([^<]+)</loc>", sm.read_text(encoding="utf-8")) if sm.exists() else []
    in_result = indexnow(pages) if pages else "no sitemap"
    print("indexnow: %s urls -> %s" % (len(pages), in_result))

    status = {
        "schema": "af.aeris_status.v1",
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "track_count": catalog["track_count"],
        "offer_count": catalog["offer_count"],
        "buy_links_checked": len(urls),
        "buy_links_dead": len(dead),
        "dead": dead,
        "sitemap_urls": len(pages),
        "indexnow_result": in_result,
        "note": "indexnow 200 is a submission receipt, not proof of indexing",
    }
    Path("agents/status.json").write_text(json.dumps(status, ensure_ascii=False, indent=1) + "\n",
                                          encoding="utf-8")
    return 0 if not dead else 1


if __name__ == "__main__":
    sys.exit(main())
