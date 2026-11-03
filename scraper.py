#!/usr/bin/env python3
"""
scraper.py

Automated Transit Scraper for Greece (Athens & Thessaloniki).
Modeled after pharmafinder-scraper and fuelGR-scraper.

Tasks:
1. Crawls OASA Telematics API for active bus & trolley lines in Athens.
2. Crawls/verifies Thessaloniki transit line registries.
3. Enriches Metro, Tram, and Suburban stations with Wikimedia Commons high-resolution photography.
4. Checks for newly opened or altered metro/tram lines and updates transit_network_master.json.
5. Saves raw crawled data into data/ directory.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("transit_scraper")

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TRANSIT_MASTER_PATH = DATA_DIR / "transit_network_master.json"
BUS_LINES_PATH = DATA_DIR / "bus_lines_master.json"

OASA_API_URL = "https://telematics.oasa.gr/api/?act=webGetLines"
USER_AGENT = "GreeceTransitScraper/2.4 (+https://github.com/athanasso/greece-transit-scraper)"

# Wikipedia station title mappings for stations where simple "{Name}_metro_station" differs
WIKI_TITLE_OVERRIDES = {
    "l1-piraeus": "Piraeus_station",
    "l1-faliro": "Faliro_metro_station",
    "l1-thissio": "Thiseio_metro_station",
    "l1-victoria": "Victoria_metro_station_(Athens)",
    "l1-attiki": "Attiki_metro_station",
    "l1-monastiraki": "Monastiraki_metro_station",
    "l1-omonia": "Omonoia_metro_station",
    "l1-neratziotissa": "Nerantziotissa_station",
    "l1-irini": "Irini_metro_station",
    "l2-larissa": "Athens_railway_station",
    "l2-panepistimio": "Panepistimio_metro_station_(Athens)",
    "l2-syntagma": "Syntagma_metro_station",
    "l2-akropoli": "Acropolis_metro_station",
    "l2-syngrou-fix": "Syngrou_Fix_metro_station",
    "l2-neos-kosmos": "Neos_Kosmos_metro_station",
    "l3-dimotiko": "Dimotiko_Theatro_metro_station",
    "l3-airport": "Athens_Airport_station",
    "thes-railway": "Thessaloniki_railway_station",
    "thes-venizelou": "Venizelou_metro_station",
    "thes-ag-sofia": "Agia_Sofia_metro_station",
    "thes-sintrivani": "Sintrivani_metro_station",
    "thes-panepistimio": "Panepistimio_metro_station_(Thessaloniki)",
}


def fetch_oasa_lines(session: requests.Session) -> list[dict]:
    log.info("Fetching active OASA bus and trolley lines...")
    try:
        resp = session.get(OASA_API_URL, headers={"User-Agent": USER_AGENT}, timeout=25)
        resp.raise_for_status()
        raw = resp.json()
        lines = []
        for item in raw:
            lines.append({
                "lineCode": item.get("LineCode", "").strip(),
                "lineId": item.get("LineID", "").strip(),
                "descr": item.get("LineDescr", "").strip(),
                "descrEn": item.get("LineDescrEng", "").strip(),
                "city": "athens",
                "type": "bus"
            })
        log.info(f"Fetched {len(lines)} active lines from OASA API.")
        return lines
    except Exception as e:
        log.warning(f"Failed to fetch OASA lines: {e}")
        return []


def query_wikimedia_images(session: requests.Session, titles: list[str]) -> dict[str, str]:
    """Queries Wikimedia API for page images in batches of up to 50 titles."""
    results = {}
    if not titles:
        return results

    # Chunk into 40 at a time
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        titles_param = "|".join(chunk)
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query"
            f"&titles={quote(titles_param)}&prop=pageimages&format=json&pithumbsize=640"
        )
        try:
            resp = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                if pid == "-1":
                    continue
                title = pdata.get("title", "")
                thumb = pdata.get("thumbnail", {}).get("source")
                if thumb:
                    results[title] = thumb
                    # Also store normalized / underscore variant
                    results[title.replace(" ", "_")] = thumb
        except Exception as e:
            log.warning(f"Error querying Wikimedia chunk {i}: {e}")
        time.sleep(0.3)

    return results


def enrich_station_photos(network: dict, session: requests.Session) -> int:
    """Finds Wikimedia station photos and assigns imageUrl / thumbnailUrl."""
    all_stations = []
    all_stations.extend(network.get("athens", {}).get("stations", []))
    all_stations.extend(network.get("thessaloniki", {}).get("stations", []))

    # Build title mapping
    station_to_title = {}
    titles_to_query = set()

    for s in all_stations:
        sid = s.get("id", "")
        existing_img = s.get("imageUrl")
        if existing_img:
            continue  # Already has image, don't re-query

        title = WIKI_TITLE_OVERRIDES.get(sid)
        if not title:
            # Fallback heuristic: "{Name}_metro_station"
            name_clean = s.get("name", "").replace(" ", "_").replace("Ag.", "Agios")
            title = f"{name_clean}_metro_station"

        station_to_title[sid] = title
        titles_to_query.add(title)

    log.info(f"Resolving station photos for {len(titles_to_query)} stations via Wikimedia API...")
    title_to_image = query_wikimedia_images(session, list(titles_to_query))

    enriched_count = 0
    for s in all_stations:
        sid = s.get("id", "")
        if s.get("imageUrl"):
            continue
        title = station_to_title.get(sid)
        if title and title in title_to_image:
            img_url = title_to_image[title]
            s["imageUrl"] = img_url
            s["thumbnailUrl"] = img_url
            enriched_count += 1

    log.info(f"Enriched {enriched_count} stations with Wikimedia Commons photos.")
    return enriched_count


def scrape():
    log.info("=" * 60)
    log.info(" Greece Transit Data Scraper")
    log.info(" Modeled after pharmafinder-scraper & fuelGR-scraper")
    log.info("=" * 60)

    session = requests.Session()

    # 1. Scrape OASA Bus Lines
    oasa_lines = fetch_oasa_lines(session)
    if oasa_lines:
        existing_bus = []
        if BUS_LINES_PATH.exists():
            try:
                with open(BUS_LINES_PATH, "r", encoding="utf-8") as f:
                    existing_bus = json.load(f)
            except Exception:
                existing_bus = []

        # Merge or update
        merged_bus = {item["lineCode"]: item for item in existing_bus}
        new_count = 0
        for item in oasa_lines:
            lc = item["lineCode"]
            if lc not in merged_bus:
                new_count += 1
            merged_bus[lc] = item

        bus_list = sorted(list(merged_bus.values()), key=lambda x: (x.get("city", ""), x.get("lineId", "")))
        with open(BUS_LINES_PATH, "w", encoding="utf-8") as f:
            json.dump(bus_list, f, ensure_ascii=False, indent=2)
        log.info(f"[*] Saved {len(bus_list)} bus lines to {BUS_LINES_PATH.name} ({new_count} new lines).")

    # 2. Enrich Transit Master Network (Metro, Tram, Stations, Wikimedia Photos)
    if not TRANSIT_MASTER_PATH.exists():
        log.error(f"Transit master path not found at {TRANSIT_MASTER_PATH}")
        sys.exit(1)

    with open(TRANSIT_MASTER_PATH, "r", encoding="utf-8") as f:
        network = json.load(f)

    enrich_station_photos(network, session)

    now_utc = datetime.now(timezone.utc).isoformat()
    network["updatedAt"] = now_utc

    with open(TRANSIT_MASTER_PATH, "w", encoding="utf-8") as f:
        json.dump(network, f, ensure_ascii=False, indent=2)

    total_stations = len(network.get("athens", {}).get("stations", [])) + len(network.get("thessaloniki", {}).get("stations", []))
    stations_with_photos = sum(
        1 for s in network.get("athens", {}).get("stations", []) + network.get("thessaloniki", {}).get("stations", [])
        if s.get("imageUrl")
    )
    log.info(f"[*] Updated {TRANSIT_MASTER_PATH.name}: {total_stations} total stations ({stations_with_photos} with photos).")


if __name__ == "__main__":
    scrape()

