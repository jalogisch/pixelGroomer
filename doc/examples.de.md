# Beispiel-Workflows

*[English Version](examples.en.md)*

Dieses Dokument zeigt, wie PixelGroomer-Tools zu vollständigen Workflows kombiniert werden können.

## Enduro Event Workflow

Das Script `examples/enduro-workflow.sh` demonstriert eine komplette Foto-Verarbeitungs-Pipeline für Motorrad-Enduro-Trainingsevents bei [enduroxperience.de](https://www.enduroxperience.de/).

### Anwendungsfall

- Zweitägiges Enduro-Training
- Ort: Stadtoldendorf (GPS: 51°52'30.8"N 9°38'53.2"E)
- Fotos von SD-Karte verarbeiten
- Metadaten hinzufügen (Autor, Künstler, Ort, GPS)
- RAW-Dateien mit darktable entwickeln
- Web-fertige Exporte mit Wasserzeichen erstellen
- Auf ~2MB komprimieren für einfachen Download

### Konfiguration

Das Script hat eingebaute Standardwerte, die angepasst werden können:

```bash
# Event-Ort
EVENT_LOCATION="Stadtoldendorf"
EVENT_GPS="51.875222,9.648111"

# Metadaten
AUTHOR="Jan Doberstein"
ARTIST="pixelpiste"
COPYRIGHT="Unlicense - Public Domain"

# Wasserzeichen (rechte untere Ecke)
WATERMARK="Jan Doberstein - enduroeXperience"

# Export-Einstellungen
MAX_FILE_SIZE_KB=2048  # ~2MB Zielgröße
```

### Grundlegende Verwendung

```bash
# Vollständiger Workflow von SD-Karte
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL

# Ausgabeverzeichnis angeben
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --output ~/Desktop/Event2026

# Tag 2 eines mehrtägigen Events
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --day 2
```

### Workflow-Schritte

Das Script führt diese Schritte automatisch aus:

1. **Import** - Fotos von SD-Karte in Bibliothek kopieren mit Organisation
2. **EXIF-Metadaten** - Autor, Künstler, GPS-Koordinaten setzen
3. **RAW-Entwicklung** - RAW-Dateien mit darktable zu JPG konvertieren
4. **Web-Export** - Wasserzeichen hinzufügen und für Web komprimieren
5. **Checksums** - Integritätsprüfungsdateien generieren

### Optionen

| Option | Beschreibung |
|--------|--------------|
| `-o, --output DIR` | Export-Verzeichnis (Standard: ~/Desktop/EnduroExport) |
| `-e, --event NAME` | Benutzerdefinierter Event-Name |
| `-d, --day NUMBER` | Tag-Nummer für mehrtägige Events |
| `--darktable-preset P` | Bestimmtes darktable-Preset anwenden |
| `--skip-import` | Bereits importierten Ordner verarbeiten |
| `--skip-develop` | RAW-Entwicklung überspringen |
| `--dry-run` | Vorschau ohne Änderungen |

### Beispiele

```bash
# Vorschau was passieren würde (Trockenlauf)
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --dry-run

# Bereits importierte Fotos verarbeiten
./examples/enduro-workflow.sh --skip-import ~/Pictures/PhotoLibrary/2026-01-24

# Bestimmtes darktable-Preset für Entwicklung verwenden
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --darktable-preset "Enduro Action"

# Benutzerdefinierter Event-Name
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --event "GS Trophy Training 2026"
```

### Ausgabe-Struktur

Nach Ausführung des Workflows:

```
~/Pictures/PhotoLibrary/
└── 2026-01-24/
    ├── 20260124_Endurotraining_001.cr3    # Original RAW
    ├── 20260124_Endurotraining_002.cr3
    ├── developed/
    │   ├── 20260124_Endurotraining_001.jpg  # Entwickeltes JPG
    │   └── 20260124_Endurotraining_002.jpg
    └── .checksums

~/Desktop/EnduroExport/
├── 20260124_Endurotraining_001.jpg    # Mit Wasserzeichen, komprimiert
├── 20260124_Endurotraining_002.jpg
└── .checksums
```

### Wasserzeichen

Das Wasserzeichen wird in der rechten unteren Ecke platziert mit:
- Halbtransparentem weißen Text mit dezenten Schatten
- Schriftgröße skaliert mit Bildabmessungen (1,5% der Breite)
- 2% Abstand vom Rand

### Komprimierung

Bilder werden auf die Zielgröße (~2MB) komprimiert durch:
1. Reduzierung der JPEG-Qualität (Start bei 85, bis 50)
2. Falls immer noch zu groß, Skalierung des Bildes (90%, 80%, etc.)

Dies stellt sicher, dass Fotos klein genug für einfachen Download sind, bei gleichzeitig vernünftiger Qualität.

## Eigenen Workflow erstellen

Nutze den Enduro-Workflow als Vorlage:

1. Kopiere `examples/enduro-workflow.sh` in eine neue Datei
2. Passe den Konfigurationsabschnitt für deinen Anwendungsfall an
3. Ändere oder entferne Schritte nach Bedarf
4. Füge eigene Verarbeitungsschritte hinzu

Das Script lädt die PixelGroomer-Bibliotheken, sodass alle Hilfsfunktionen verfügbar sind:

```bash
source "$PIXELGROOMER_ROOT/lib/config.sh"
source "$PIXELGROOMER_ROOT/lib/utils.sh"

# Jetzt kannst du nutzen:
log_info "Nachricht"
log_success "Fertig"
log_error "Fehlgeschlagen"
log_progress 1 10 "Verarbeitung"
```
