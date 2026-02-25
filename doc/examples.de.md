# Beispiel-Workflows

*[English Version](examples.en.md)*

Dieses Dokument zeigt, wie PixelGroomer-Tools zu vollständigen Workflows kombiniert werden können.

## Verfügbare Beispiel-Workflows

| Script | Zweck |
|--------|-------|
| `holiday-import.sh` | Import von SD-Karte im Trip-Modus (nur Identität, ein Ordner pro Tag) |
| `daily-offload.sh` | Einfacher täglicher SD-Karten-Import für mehrtägige Events |
| `develop-album.sh` | RAW-Dateien mit einheitlichem darktable-Preset entwickeln |
| `album-export.sh` | Album-Export mit Lizenz-Metadaten und Wasserzeichen |
| `adventure-camp-workflow.sh` | Wochenend-Event-Import + RawTherapee-Entwicklung (Adventure Camp, Stadtoldendorf) |
| `enduro-workflow.sh` | Kompletter Workflow mit Entwicklung und Web-Export |

---

## Urlaubs-Import Workflow

Das Script `examples/holiday-import.sh` importiert alle Fotos von einer SD-Karte im Trip-Modus. Kein Event und Ort — nur Autor, Copyright und Credit aus der `.import.yaml` der Karte oder .env. Ein Ordner pro Tag nach EXIF-Datum; RAW und JPG landen in Unterordnern `raw/` und `jpg/` mit gepaarten Namen (`--split-by-type`). Ideal für den Import nach dem Urlaub.

### Verwendung

```bash
./examples/holiday-import.sh /Volumes/CARD [--no-delete] [--dry-run] [--output DIR]
```

Siehe [Workflow: Urlaubs-Import (SD-Karte)](workflow.de.md#urlaubs-import-sd-karte).

---

## Täglicher Offload Workflow

Das Script `examples/daily-offload.sh` bietet einen einfachen, wiederholbaren Import-Workflow für mehrtägige Events. Ideal für das tägliche Entladen von SD-Karten mit konsistenten Metadaten.

### Anwendungsfall

- Mehrtägiges Motorrad-Event (Rallye, Tour, Training)
- Tägliches SD-Karten-Offload ins Archiv
- Konsistente Metadaten über alle Tage
- Keine Entwicklung oder Export - nur sichere Archivierung

### Konfiguration

Passe den Script-Header für dein Event an:

```bash
# Event-Information
EVENT_NAME="GS Treffen 2026"           # Basis-Name für das Event
EVENT_LOCATION="Garmisch-Partenkirchen"
EVENT_GPS="47.5000,11.1000"            # GPS-Koordinaten

# Fotografen-Metadaten
AUTHOR="Jan Doberstein"
ARTIST="pixelpiste"
COPYRIGHT="Unlicense - Public Domain"
```

### Grundlegende Verwendung

```bash
# Tägliches Offload - Datum ist automatisch
./examples/daily-offload.sh /Volumes/EOS_DIGITAL

# Explizite Tag-Nummer
./examples/daily-offload.sh /Volumes/EOS_DIGITAL --day 2

# Vorschau ohne Änderungen
./examples/daily-offload.sh /Volumes/EOS_DIGITAL --dry-run
```

### Workflow-Schritte

Das Script führt diese Schritte aus:

1. **Import** - Fotos von SD-Karte mit Organisation nach Datum kopieren
2. **EXIF-Metadaten** - Autor, Künstler, GPS-Koordinaten setzen
3. **Checksums** - Integritätsprüfungsdateien generieren

### Ausgabe-Struktur

Tägliche Ausführung erstellt organisierte Ordner:

```
~/Pictures/PhotoLibrary/
├── 2026-07-10/                              # Tag 1
│   ├── 20260710_GS_Treffen_2026_001.cr3
│   ├── 20260710_GS_Treffen_2026_002.cr3
│   └── .checksums
├── 2026-07-11/                              # Tag 2
│   ├── 20260711_GS_Treffen_2026_001.cr3
│   └── .checksums
└── 2026-07-12/                              # Tag 3
    └── ...
```

### Tipps für Mehrtages-Events

1. **Vor dem Event:** `daily-offload.sh` kopieren und Konfiguration anpassen
2. **Jeden Abend:** SD-Karte einlegen, Script ausführen, Karte für nächsten Tag formatieren
3. **Nach dem Event:** `develop-album.sh` für einheitlichen Stil, dann `album-export.sh` zum Teilen

---

## Album-Entwicklungs Workflow

Das Script `examples/develop-album.sh` entwickelt RAW-Dateien stapelweise mit einem einheitlichen darktable-Preset, sodass alle Fotos eines Events den gleichen Look haben.

### Anwendungsfall

- Alle RAW-Fotos einer Rallye mit einheitlichem Stil entwickeln
- Deinen Signature-Look auf alle Event-Fotos anwenden
- Stapel-Konvertierung von RAW zu hochwertigem JPEG

### Konfiguration

Passe den Script-Header an:

```bash
# Standard darktable-Preset/Stil
DEFAULT_PRESET="Adventure"

# Ausgabe-Qualität
JPEG_QUALITY=92

# Unterordner-Name für Ausgabe
OUTPUT_SUBFOLDER="developed"
```

### Darktable-Presets erstellen

1. Öffne ein repräsentatives Foto in darktable
2. Bearbeite es mit deinem gewünschten Look (Belichtung, Farben, Kontrast)
3. Gehe zum 'Stile'-Modul (linkes Panel im Dunkelkammer-Modus)
4. Klicke 'Stil erstellen' und benenne ihn (z.B. "Enduro Action")

### Grundlegende Verwendung

```bash
# Album mit Standard-Preset entwickeln
./examples/develop-album.sh "GS_Treffen_Highlights"

# Bestimmtes Preset verwenden
./examples/develop-album.sh "Alps_Tour" --preset "Vivid Landscape"

# Ordner mit benutzerdefinierter Ausgabe entwickeln
./examples/develop-album.sh ~/Pictures/PhotoLibrary/2026-07-10 --output ~/Desktop/Developed

# Verfügbare Presets auflisten
./examples/develop-album.sh --list-presets
```

### Ausgabe-Struktur

Entwickelte JPEGs werden in einem Unterordner abgelegt:

```
Albums/GS_Treffen_Highlights/
├── IMG_001.cr3                    # Original RAW (Symlink)
├── IMG_002.cr3
├── IMG_003.cr3
└── developed/                     # Vom Script erstellt
    ├── IMG_001.jpg                # Entwickeltes JPEG
    ├── IMG_002.jpg
    └── IMG_003.jpg
```

### Workflow: Entwicklung → Export

Kombiniere mit `album-export.sh` für kompletten Workflow:

```bash
# 1. Mit einheitlichem Stil entwickeln
./examples/develop-album.sh "Rally_Photos" --preset "Enduro Action"

# 2. Entwickelte Fotos mit Lizenzierung exportieren
./examples/album-export.sh "Rally_Photos/developed" --output ~/Desktop/Share
```

---

## Album-Export Workflow

Das Script `examples/album-export.sh` exportiert ein Album oder Ordner mit korrekten Lizenz-Metadaten und optionalem Wasserzeichen. Ideal zum Teilen von Fotos mit klaren Nutzungsrechten.

### Anwendungsfall

- Fotos von einem Event mit Teilnehmern teilen
- Fotos mit korrekter Lizenzierung veröffentlichen (CC BY-NC-SA 4.0)
- Wasserzeichen für Namensnennung hinzufügen
- Kontaktinformationen in Metadaten setzen

### Konfiguration

Passe den Script-Header an:

```bash
# Ersteller-Information
CREATOR_NAME="Jan Doberstein"
CREATOR_EMAIL="foto@pixelpiste.de"

# Lizenzierung
LICENSE="CC BY-NC-SA 4.0"
COPYRIGHT_STATUS="protected"
USAGE_TERMS="Privatnutzung frei mit Namensnennung. Kommerzielle Nutzung nur nach Rücksprache."

# Wasserzeichen
WATERMARK_TEXT="pixelPiste"
WATERMARK_COLOR="white"
WATERMARK_OPACITY="0.6"

# Export-Einstellungen
EXPORT_QUALITY=85
```

### Gesetzte Metadaten

Das Script setzt diese Metadaten-Felder:

| Feld | Wert |
|------|------|
| Lizenz | CC BY-NC-SA 4.0 |
| Copyright | (c) 2026 Jan Doberstein. Alle Rechte vorbehalten. |
| Copyright Status | protected |
| Nutzungsbedingungen | Privatnutzung frei mit Namensnennung... |
| Ersteller | Jan Doberstein |
| Kontakt-E-Mail | foto@pixelpiste.de |

### Grundlegende Verwendung

```bash
# Album mit Wasserzeichen exportieren
./examples/album-export.sh "GS_Treffen_Highlights" --output ~/Desktop/Share

# Ordner direkt exportieren
./examples/album-export.sh ~/Pictures/PhotoLibrary/2026-07-10 --output ~/Desktop/Export

# Höhere Qualität für Druck, ohne Wasserzeichen
./examples/album-export.sh "Alps_Tour" --output ~/Desktop/Print --quality 95 --no-watermark

# Vorschau ohne Änderungen
./examples/album-export.sh "Rally_Photos" --output ~/Desktop/Test --dry-run
```

### Workflow-Schritte

1. **Vorbereiten** - Bilder kopieren (RAW entwickeln falls nötig)
2. **Metadaten** - Lizenz- und Copyright-Informationen setzen
3. **Exportieren** - Wasserzeichen hinzufügen und zu JPEG komprimieren

### Wasserzeichen

Das Wasserzeichen ist:
- Klein und unauffällig (ca. 1% der Bildbreite)
- Weiß mit dezenten Schatten für Sichtbarkeit
- Positioniert in der rechten unteren Ecke
- Kann mit `--no-watermark` deaktiviert werden

### Typische Verwendung nach Event

```bash
# 1. Album mit besten Fotos erstellen
pg-album create "GS_Treffen_Best"
pg-album add "GS_Treffen_Best" ~/Pictures/PhotoLibrary/2026-07-10/*.cr3

# 2. Zum Teilen exportieren
./examples/album-export.sh "GS_Treffen_Best" --output ~/Desktop/FuerTeilnehmer
```

---

## Adventure Camp Workflow

Das Script `examples/adventure-camp-workflow.sh` führt Import (Event "Adventure Camp", Ort "Stadtoldendorf", mit `--split-by-type`: RAW in `raw/`, JPG in `jpg/` pro Datum) und anschließend RAW-Entwicklung mit RawTherapee und einem Kodak-Preset aus. Ideal für ein zweitägiges Wochenend-Event.

### Verwendung

```bash
./examples/adventure-camp-workflow.sh /Volumes/CARD [--output DIR] [--preset PATH] [--dry-run]
./examples/adventure-camp-workflow.sh --skip-import ~/Pictures/PhotoLibrary/2026-02-22 --output ~/Desktop/Developed
```

Ein Kodak-PP3 kann in `templates/rawtherapee-kodak-portra.pp3` mitgeliefert werden; sonst `RAWTHERAPEE_PRESET` in .env setzen oder `--preset` angeben. PP3 aus der Community nutzen oder in RawTherapee anlegen (RawPedia Film Simulation = HaldCLUT in der GUI; CLI braucht eine .pp3-Datei). Kodak-Portra-PP3s von [TheSquirrelMafia/RawTherapee-PP3-Settings](https://github.com/TheSquirrelMafia/RawTherapee-PP3-Settings) laden (z. B. *TSM - Film Simulations / Color Films*). Das Projekt liefert kein Preset mit (kein permissiv lizenziertes PP3 gefunden); siehe [RawTherapee-Preset-Recherche](preset-research.de.md). [Workflow: Wochenend-Event mit RawTherapee](workflow.de.md#wochenend-event-mit-rawtherapee-adventure-camp).

---

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

### Bestätigung vor Verarbeitung

Das Script zeigt einen detaillierten Plan bevor die Verarbeitung startet:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    ENDURO EVENT WORKFLOW - PLAN                      ║
╚══════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────┐
│  SOURCE ANALYSIS                                                     │
├──────────────────────────────────────────────────────────────────────┤
│  Path: /Volumes/EOS_DIGITAL                                          │
│  Files found:                                                        │
│    RAW files (CR2/CR3/NEF/ARW/etc.): 247                            │
│    JPG files:                        0                               │
│    Total photos:                     247                             │
│  Total size: 8.2 GB                                                  │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  METADATA TO BE APPLIED                                             │
├──────────────────────────────────────────────────────────────────────┤
│  Event:     2026-01-24 Endurotraining                               │
│  Location:  Stadtoldendorf                                          │
│  GPS:       51.875222,9.648111 (if missing on photos)               │
│  Author:    Jan Doberstein                                          │
│  Artist:    pixelpiste                                              │
│  Copyright: Unlicense - Public Domain                               │
└──────────────────────────────────────────────────────────────────────┘

...

╔══════════════════════════════════════════════════════════════════════╗
║  Type YES to start processing, or anything else to abort            ║
╚══════════════════════════════════════════════════════════════════════╝

Confirm: YES
```

Nur die Eingabe von `YES` (exakt, Groß-/Kleinschreibung beachten) startet die Verarbeitung. Jede andere Eingabe bricht ab.

Nutze `-y` oder `--yes` um die Bestätigung für automatisierte Workflows zu überspringen:

```bash
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --yes
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
| `-y, --yes` | Bestätigung überspringen, sofort starten |

### Beispiele

```bash
# Bereits importierte Fotos verarbeiten
./examples/enduro-workflow.sh --skip-import ~/Pictures/PhotoLibrary/2026-01-24

# Bestimmtes darktable-Preset für Entwicklung verwenden
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --darktable-preset "Enduro Action"

# Benutzerdefinierter Event-Name
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --event "GS Trophy Training 2026"

# Bestätigung überspringen (für automatisierte Scripts)
./examples/enduro-workflow.sh /Volumes/EOS_DIGITAL --yes
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
