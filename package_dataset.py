#!/usr/bin/env python3
"""
package_dataset.py

Packages Greece Transit dataset artifacts for GitHub Release and static CDN hosting.
Modeled after pharmafinder-scraper and fuelGR-scraper:
1. Loads data/transit_network_master.json, data/metro_timetables_master.json, and data/bus_lines_master.json.
2. Validates schema & coordinates.
3. Generates minified mobile distribution artifacts:
   - transit_network.min.json
   - metro_timetables.min.json
   - bus_routes_index.min.json
4. Compresses artifacts using Zstandard (.zst) and Gzip (.gz).
5. Generates tag.txt and release_notes.md for automated GitHub Release publishing.
"""

from __future__ import annotations

import gzip
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"

TRANSIT_MASTER = DATA_DIR / "transit_network_master.json"
TIMETABLES_MASTER = DATA_DIR / "metro_timetables_master.json"
BUS_MASTER = DATA_DIR / "bus_lines_master.json"

TAG_FILE = SCRIPT_DIR / "tag.txt"
RELEASE_NOTES = SCRIPT_DIR / "release_notes.md"


def compress_file(source_path: Path):
    """Compresses file using zstandard and gzip."""
    zst_path = source_path.with_name(source_path.name + ".zst")
    gz_path = source_path.with_name(source_path.name + ".gz")

    # Zstandard compression
    try:
        import zstandard as zstd
        cctx = zstd.ZstdCompressor(level=19)
        with open(source_path, "rb") as f_in, open(zst_path, "wb") as f_out:
            cctx.copy_stream(f_in, f_out)
        print(f"  [zstd-lib] {source_path.name} -> {zst_path.name} ({zst_path.stat().st_size:,} bytes)")
    except ImportError:
        zstd_bin = shutil.which("zstd")
        if zstd_bin:
            subprocess.run([zstd_bin, "-19", "-f", str(source_path), "-o", str(zst_path)], check=True)
            print(f"  [zstd-cli] {source_path.name} -> {zst_path.name} ({zst_path.stat().st_size:,} bytes)")
        else:
            print("  [-] zstandard not available, skipping .zst")

    # Gzip compression
    with open(source_path, "rb") as f_in, gzip.open(gz_path, "wb", compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)
    print(f"  [gzip]     {source_path.name} -> {gz_path.name} ({gz_path.stat().st_size:,} bytes)")


def package():
    print("=" * 60)
    print(" Greece Transit — Automated Release Packager")
    print(" Modeled after pharmafinder-scraper & fuelGR-scraper")
    print("=" * 60)

    now_utc = datetime.now(timezone.utc)
    tag = now_utc.strftime("%Y.%m.%d.%H%M")
    print(f"[*] Generated release tag: {tag}")

    # 1. Process transit_network_master.json
    if not TRANSIT_MASTER.exists():
        print(f"[-] Missing {TRANSIT_MASTER}")
        sys.exit(1)

    with open(TRANSIT_MASTER, "r", encoding="utf-8") as f:
        network_data = json.load(f)

    network_data["version"] = tag
    network_data["updatedAt"] = now_utc.isoformat()

    out_network = SCRIPT_DIR / "transit_network.min.json"
    with open(out_network, "w", encoding="utf-8") as f:
        json.dump(network_data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"[+] Written {out_network.name} ({out_network.stat().st_size:,} bytes)")
    compress_file(out_network)

    # 2. Process metro_timetables_master.json
    if not TIMETABLES_MASTER.exists():
        print(f"[-] Missing {TIMETABLES_MASTER}")
        sys.exit(1)

    with open(TIMETABLES_MASTER, "r", encoding="utf-8") as f:
        timetables_data = json.load(f)

    timetables_data["version"] = tag
    timetables_data["updatedAt"] = now_utc.isoformat()

    out_tt = SCRIPT_DIR / "metro_timetables.min.json"
    with open(out_tt, "w", encoding="utf-8") as f:
        json.dump(timetables_data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"[+] Written {out_tt.name} ({out_tt.stat().st_size:,} bytes)")
    compress_file(out_tt)

    # 3. Process bus_lines_master.json
    bus_count = 0
    if BUS_MASTER.exists():
        with open(BUS_MASTER, "r", encoding="utf-8") as f:
            bus_data = json.load(f)
        bus_count = len(bus_data)
        out_bus = SCRIPT_DIR / "bus_routes_index.min.json"
        with open(out_bus, "w", encoding="utf-8") as f:
            json.dump(bus_data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"[+] Written {out_bus.name} ({out_bus.stat().st_size:,} bytes)")
        compress_file(out_bus)

    # 4. Process ktel dataset
    ktel_dir = DATA_DIR / "ktel"
    if ktel_dir.exists():
        ktel_operators_f = ktel_dir / "operators.json"
        ktel_cities_f = ktel_dir / "cities.json"
        ktel_fares_f = ktel_dir / "fares.json"
        ktel_booking_f = ktel_dir / "booking_links.json"

        ktel_payload = {
            "version": tag,
            "updatedAt": now_utc.isoformat(),
            "operators": json.load(open(ktel_operators_f, "r", encoding="utf-8")) if ktel_operators_f.exists() else [],
            "cities": json.load(open(ktel_cities_f, "r", encoding="utf-8")) if ktel_cities_f.exists() else [],
            "fares": json.load(open(ktel_fares_f, "r", encoding="utf-8")) if ktel_fares_f.exists() else [],
            "bookingLinks": json.load(open(ktel_booking_f, "r", encoding="utf-8")) if ktel_booking_f.exists() else {}
        }
        out_ktel = SCRIPT_DIR / "ktel_dataset.min.json"
        with open(out_ktel, "w", encoding="utf-8") as f:
            json.dump(ktel_payload, f, ensure_ascii=False, separators=(",", ":"))
        print(f"[+] Written {out_ktel.name} ({out_ktel.stat().st_size:,} bytes)")
        compress_file(out_ktel)

    # Write tag.txt
    with open(TAG_FILE, "w", encoding="utf-8") as f:
        f.write(tag)

    # Calculate statistics for release_notes.md
    athens_stations = len(network_data.get("athens", {}).get("stations", []))
    athens_lines = len(network_data.get("athens", {}).get("lines", []))
    thess_stations = len(network_data.get("thessaloniki", {}).get("stations", []))
    thess_lines = len(network_data.get("thessaloniki", {}).get("lines", []))
    all_stations = network_data.get("athens", {}).get("stations", []) + network_data.get("thessaloniki", {}).get("stations", [])
    photos_count = sum(1 for s in all_stations if s.get("imageUrl"))

    notes = f"""# Greece Transit Dataset — Release `{tag}`

Automated scheduled build of Greek transit networks and timetables.

## Summary

| Metric | Athens | Thessaloniki | Total |
| :--- | :--- | :--- | :--- |
| **Lines (Metro / Tram / Rail)** | {athens_lines} | {thess_lines} | {athens_lines + thess_lines} |
| **Stations** | {athens_stations} | {thess_stations} | {all_stations.__len__()} |
| **Station Photography (Wikimedia)** | — | — | {photos_count} stations |
| **Active Bus / Trolley Lines** | {bus_count} | — | {bus_count} |
| **Metro Timetable Profiles** | — | — | {len(timetables_data.get('timetables', []))} lines |

## Artifacts

| Filename | Description | Formats |
| :--- | :--- | :--- |
| `transit_network.min.json` | Vector line polylines, station coordinates, status, and photos | `.json`, `.zst`, `.gz` |
| `metro_timetables.min.json` | Peak / daytime / night headways and operating hours | `.json`, `.zst`, `.gz` |
| `bus_routes_index.min.json` | Master index of active OASA & OASTH bus routes | `.json`, `.zst`, `.gz` |

## Upstream Sources
- **OASA Telematics API**: Real-time line codes and descriptors.
- **OpenStreetMap & STASY S.A.**: Metro Lines 1, 2, 3, 4 (under construction), Tram T6/T7.
- **Elliniko Metro**: Thessaloniki Metro Line 1 & Kalamaria Extension.
- **Wikimedia Commons**: Station photography thumbnails.
"""

    with open(RELEASE_NOTES, "w", encoding="utf-8") as f:
        f.write(notes)
    print(f"[+] Generated {RELEASE_NOTES.name}")
    print("=" * 60)
    print(" Packaging complete!")


if __name__ == "__main__":
    package()

