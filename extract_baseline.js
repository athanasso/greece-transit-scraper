const fs = require('fs');
const path = require('path');

const srcPath = 'd:/Projects/RN/published/GreeceTransit/lib/transit-lines.ts';
let content = fs.readFileSync(srcPath, 'utf8').replace(/\r\n/g, '\n');

function extractArray(startMarker, endMarker) {
  const startIdx = content.indexOf(startMarker);
  if (startIdx === -1) throw new Error('Cannot find startMarker: ' + startMarker);
  const arrayStart = content.indexOf('[', startIdx);
  const endIdx = content.indexOf(endMarker, arrayStart);
  if (endIdx === -1) throw new Error('Cannot find endMarker: ' + endMarker);
  
  // Cut the array text
  const arrayCode = content.substring(arrayStart, endIdx + 1);
  return eval(arrayCode);
}

const athensStations = extractArray('const athensStations: TransitStation[] =', '];\n\nconst athensLines');
const athensLines = extractArray('const athensLines: TransitLine[] =', '];\n\n// =============================================================================\n// THESSALONIKI');
const thessStations = extractArray('const thessalonikiStations: TransitStation[] =', '];\n\nconst thessalonikiLines');
const thessLines = extractArray('const thessalonikiLines: TransitLine[] =', '];\n\n// =============================================================================\n// EXPORT');

console.log('Parsed Athens stations:', athensStations.length, 'lines:', athensLines.length);
console.log('Parsed Thessaloniki stations:', thessStations.length, 'lines:', thessLines.length);

// Also add Athens Line 4 stations & line
const line4Stations = [
  { id: "l4-alsos-veikou", name: "Alsos Veikou", nameEl: "Άλσος Βεΐκου", latitude: 38.0163, longitude: 23.7547, lineIds: ["line4"], status: "construction" },
  { id: "l4-galatsi", name: "Galatsi", nameEl: "Γαλάτσι", latitude: 38.0105, longitude: 23.7490, lineIds: ["line4"], status: "construction" },
  { id: "l4-elikonos", name: "Elikonos", nameEl: "Ελικώνος", latitude: 38.0051, longitude: 23.7439, lineIds: ["line4"], status: "construction" },
  { id: "l4-kypseli", name: "Kypseli", nameEl: "Κυψέλη", latitude: 37.9996, longitude: 23.7410, lineIds: ["line4"], status: "construction" },
  { id: "l4-dikastiria", name: "Dikastiria", nameEl: "Δικαστήρια", latitude: 37.9918, longitude: 23.7423, lineIds: ["line4"], status: "construction" },
  { id: "l4-alexandras", name: "Alexandras", nameEl: "Αλεξάνδρας", latitude: 37.9892, longitude: 23.7402, lineIds: ["line4"], status: "construction" },
  { id: "l4-exarcheia", name: "Exarcheia", nameEl: "Εξάρχεια", latitude: 37.9868, longitude: 23.7348, lineIds: ["line4"], status: "construction" },
  { id: "l4-akadimia", name: "Akadimia", nameEl: "Ακαδημία", latitude: 37.9804, longitude: 23.7340, lineIds: ["line4", "line2"], isInterchange: true, status: "construction" },
  { id: "l4-kolonaki", name: "Kolonaki", nameEl: "Κολωνάκι", latitude: 37.9774, longitude: 23.7410, lineIds: ["line4"], status: "construction" },
  { id: "l4-evangelismos", name: "Evangelismos", nameEl: "Ευαγγελισμός", latitude: 37.9760, longitude: 23.7485, lineIds: ["line4", "line3"], isInterchange: true, status: "construction" },
  { id: "l4-kaisariani", name: "Kaisariani", nameEl: "Καισαριανή", latitude: 37.9712, longitude: 23.7554, lineIds: ["line4"], status: "construction" },
  { id: "l4-panepistimioupoli", name: "Panepistimioupoli", nameEl: "Πανεπιστημιούπολη", latitude: 37.9698, longitude: 23.7661, lineIds: ["line4"], status: "construction" },
  { id: "l4-ilisia", name: "Ilisia", nameEl: "Ιλίσια", latitude: 37.9745, longitude: 23.7658, lineIds: ["line4"], status: "construction" },
  { id: "l4-zografou", name: "Zografou", nameEl: "Ζωγράφου", latitude: 37.9768, longitude: 23.7712, lineIds: ["line4"], status: "construction" },
  { id: "l4-goudi", name: "Goudi", nameEl: "Γουδή", latitude: 37.9825, longitude: 23.7725, lineIds: ["line4"], status: "construction" }
];

const line4Line = {
  id: "line4",
  name: "Line 4 (Orange)",
  nameEl: "Γραμμή 4 (Πορτοκαλί)",
  color: "#F68B1F",
  type: "metro",
  status: "construction",
  coordinates: line4Stations.map(s => [s.longitude, s.latitude])
};

const allAthensStations = [...athensStations, ...line4Stations];
const allAthensLines = [...athensLines, line4Line];

const master = {
  version: "2026.11.1",
  updatedAt: new Date().toISOString(),
  schematicMaps: {
    athens: "https://raw.githubusercontent.com/athanasso/greece-transit-scraper/main/assets/maps/athens_schematic.jpg",
    thessaloniki: "https://raw.githubusercontent.com/athanasso/greece-transit-scraper/main/assets/maps/thessaloniki_schematic.jpg"
  },
  athens: {
    stations: allAthensStations,
    lines: allAthensLines
  },
  thessaloniki: {
    stations: thessStations,
    lines: thessLines
  }
};

fs.writeFileSync('d:/Projects/RN/published/greece-transit-scraper/data/transit_network_master.json', JSON.stringify(master, null, 2), 'utf8');
console.log('Saved data/transit_network_master.json');
