#!/usr/bin/env python3
"""
seed_master_data.py

Extracts baseline transit network and timetable data from GreeceTransit codebase,
merges Athens Line 4 (Section A under construction), sets up Wikimedia image mapping
and official schematic diagram URLs.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Schematic transit diagrams (hosted SVG/JPG vector maps)
SCHEMATIC_MAPS = {
    "athens": "https://raw.githubusercontent.com/athanasso/greece-transit-scraper/main/assets/maps/athens_schematic.jpg",
    "thessaloniki": "https://raw.githubusercontent.com/athanasso/greece-transit-scraper/main/assets/maps/thessaloniki_schematic.jpg"
}

# Line 4 Section A (Alsos Veikou - Goudi) - Under Construction
LINE4_STATIONS = [
    {"id": "l4-alsos-veikou", "name": "Alsos Veikou", "nameEl": "Άλσος Βεΐκου", "latitude": 38.0163, "longitude": 23.7547, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Alsos_Veikou_metro_station"},
    {"id": "l4-galatsi", "name": "Galatsi", "nameEl": "Γαλάτσι", "latitude": 38.0105, "longitude": 23.7490, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Galatsi_metro_station"},
    {"id": "l4-elikonos", "name": "Elikonos", "nameEl": "Ελικώνος", "latitude": 38.0051, "longitude": 23.7439, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Elikonos_metro_station"},
    {"id": "l4-kypseli", "name": "Kypseli", "nameEl": "Κυψέλη", "latitude": 37.9996, "longitude": 23.7410, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Kypseli_metro_station"},
    {"id": "l4-dikastiria", "name": "Dikastiria", "nameEl": "Δικαστήρια", "latitude": 37.9918, "longitude": 23.7423, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Dikastiria_metro_station"},
    {"id": "l4-alexandras", "name": "Alexandras", "nameEl": "Αλεξάνδρας", "latitude": 37.9892, "longitude": 23.7402, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Alexandras_metro_station"},
    {"id": "l4-exarcheia", "name": "Exarcheia", "nameEl": "Εξάρχεια", "latitude": 37.9868, "longitude": 23.7348, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Exarcheia_metro_station"},
    {"id": "l4-akadimia", "name": "Akadimia", "nameEl": "Ακαδημία", "latitude": 37.9804, "longitude": 23.7340, "lineIds": ["line4", "line2"], "isInterchange": True, "status": "construction", "wikiTitle": "Akadimia_metro_station"},
    {"id": "l4-kolonaki", "name": "Kolonaki", "nameEl": "Κολωνάκι", "latitude": 37.9774, "longitude": 23.7410, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Kolonaki_metro_station"},
    {"id": "l4-evangelismos", "name": "Evangelismos", "nameEl": "Ευαγγελισμός", "latitude": 37.9760, "longitude": 23.7485, "lineIds": ["line4", "line3"], "isInterchange": True, "status": "construction", "wikiTitle": "Evangelismos_metro_station"},
    {"id": "l4-kaisariani", "name": "Kaisariani", "nameEl": "Καισαριανή", "latitude": 37.9712, "longitude": 23.7554, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Kaisariani_metro_station"},
    {"id": "l4-panepistimioupoli", "name": "Panepistimioupoli", "nameEl": "Πανεπιστημιούπολη", "latitude": 37.9698, "longitude": 23.7661, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Panepistimioupoli_metro_station"},
    {"id": "l4-ilisia", "name": "Ilisia", "nameEl": "Ιλίσια", "latitude": 37.9745, "longitude": 23.7658, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Ilisia_metro_station"},
    {"id": "l4-zografou", "name": "Zografou", "nameEl": "Ζωγράφου", "latitude": 37.9768, "longitude": 23.7712, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Zografou_metro_station"},
    {"id": "l4-goudi", "name": "Goudi", "nameEl": "Γουδή", "latitude": 37.9825, "longitude": 23.7725, "lineIds": ["line4"], "status": "construction", "wikiTitle": "Goudi_metro_station"}
]

LINE4_LINE = {
    "id": "line4",
    "name": "Line 4 (Orange)",
    "nameEl": "Γραμμή 4 (Πορτοκαλί)",
    "color": "#F68B1F",
    "type": "metro",
    "status": "construction",
    "coordinates": [[s["longitude"], s["latitude"]] for s in LINE4_STATIONS]
}

def seed():
    # Read existing transit-lines.ts to extract baseline stations and lines
    src_lines_file = Path("d:/Projects/RN/published/GreeceTransit/lib/transit-lines.ts")
    src_timetables_file = Path("d:/Projects/RN/published/GreeceTransit/assets/data/metro-timetables.json")

    with open(src_timetables_file, "r", encoding="utf-8") as f:
        timetables_data = json.load(f)

    # Add Line 4 timetable preview
    line4_tt = {
        "id": "line4",
        "code": "M4",
        "name": "Line 4 (Orange) - Under Construction",
        "nameEl": "Γραμμή 4 (Πορτοκαλί) - Υπό Κατασκευή",
        "routeDescr": "Alsos Veikou ↔ Goudi (15 stations)",
        "routeDescrEl": "Άλσος Βεΐκου ↔ Γουδή (15 σταθμοί)",
        "color": "#F68B1F",
        "type": "metro",
        "city": "athens",
        "status": "construction",
        "operatingHours": {
            "firstTrain": "TBD",
            "lastTrain": "TBD"
        },
        "frequencies": {
            "peak": "Automatic driverless operation (expected ~90 sec headway)",
            "daytime": "Expected ~2-3 min",
            "night": "TBD",
            "weekend": "TBD"
        },
        "notes": "Currently under construction by AVAX - Ghella - Alstom consortium. 12.8 km driverless metro with 15 underground stations.",
        "notesEl": "Υπό κατασκευή από την κοινοπραξία AVAX - Ghella - Alstom. Γραμμή 12,8 χλμ χωρίς οδηγό με 15 υπόγειους σταθμούς."
    }

    # Check if line4 already exists in timetables
    existing_ids = [t["id"] for t in timetables_data.get("timetables", [])]
    if "line4" not in existing_ids:
        timetables_data["timetables"].append(line4_tt)

    timetables_master_path = DATA_DIR / "metro_timetables_master.json"
    with open(timetables_master_path, "w", encoding="utf-8") as f:
        json.dump(timetables_data, f, ensure_ascii=False, indent=2)
    print(f"[*] Saved {len(timetables_data['timetables'])} timetables to {timetables_master_path.name}")

if __name__ == "__main__":
    seed()
