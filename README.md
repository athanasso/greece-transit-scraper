# Greece Transit Scraper & Dataset 🇬🇷 🚇 🚌

Automated scraper, validator, and packager for public transit data across Greece (Athens & Thessaloniki). Modeled after [pharmafinder-scraper](https://github.com/athanasso/pharmafinder-scraper) and [fuelGR-scraper](https://github.com/athanasso/fuelGR-scraper).

Built to feed real-time and offline transit metadata to the [GreeceTransit](https://github.com/athanasso/GreeceTransit) mobile app.

---

## ⚡ Direct Download CDN Links (Always Latest)

| Artifact | Direct Link | Compression | Description |
| :--- | :--- | :--- | :--- |
| **Transit Network** | [`transit_network.min.json`](https://github.com/athanasso/greece-transit-scraper/releases/latest/download/transit_network.min.json) | `.zst` / `.gz` | Metro lines (L1, L2, L3, L4 under construction), Tram (T6, T7), Suburban Rail, Thessaloniki Metro (L1, L2, West), stations, coordinates, photos. |
| **Metro Timetables** | [`metro_timetables.min.json`](https://github.com/athanasso/greece-transit-scraper/releases/latest/download/metro_timetables.min.json) | `.zst` / `.gz` | Operational schedules, peak/off-peak/weekend headway intervals, first and last train departures. |
| **Bus Routes Index** | [`bus_routes_index.min.json`](https://github.com/athanasso/greece-transit-scraper/releases/latest/download/bus_routes_index.min.json) | `.zst` / `.gz` | Live catalog of all OASA & OASTH bus routes. |

---

## 🎯 Architecture

```
GitHub Actions (Weekly / Manual Dispatch)
       │
       ▼
 1. python scraper.py
    ├─ Crawls OASA telematics (webGetLines)
    ├─ Queries Wikimedia Commons API for station photos
    └─ Syncs OpenStreetMap / STASY line polylines
       │
       ▼
 2. python package_dataset.py
    ├─ Validates schemas & GeoJSON coordinates
    ├─ Generates *.min.json mobile artifacts
    └─ Compresses with Zstandard (level 19) & Gzip
       │
       ▼
 3. gh release create $TAG --latest
    └─ Uploads release artifacts to GitHub CDN
       │
       ▼
 4. GreeceTransit Mobile App
    ├─ Checks GitHub Release metadata in background
    ├─ Ingests new lines (e.g. Line 4), stations, and updated timetables
    └─ Updates Leaflet/MapLibre vector lines and schematic diagrams dynamically
```

---

## 🛠️ Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Scraper
```bash
python scraper.py
```

### 3. Package & Compress
```bash
python package_dataset.py
```

---

## 📄 License
MIT

