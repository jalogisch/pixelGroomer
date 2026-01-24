# Web Workflow Planner

*[English Version](web-planner.en.md)*

Eine Flask-basierte Web-Oberfläche für PixelGroomer mit visuellem Workflow-Planer und Album-Verwaltung.

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Browser                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Jinja2 Templates + HTMX                                    │    │
│  │  - Workflow Planner Seite                                   │    │
│  │  - Album Manager Seite                                      │    │
│  │  - Theme Umschalter (EUI / Solarized, Light / Dark)        │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP / HTMX
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Flask Backend                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │    Routes    │  │   Services   │  │   Modules    │              │
│  │  /workflow   │──│  Workflow    │──│  import.py   │              │
│  │  /album      │  │  Album       │  │  exif.py     │              │
│  │  /api        │  │  Library     │  │  develop.py  │              │
│  └──────────────┘  └──────────────┘  │  export.py   │              │
│                                       │  verify.py   │              │
│                                       └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ subprocess
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Bestehende CLI Scripts                            │
│  pg-import  pg-exif  pg-develop  pg-album  pg-verify                │
└─────────────────────────────────────────────────────────────────────┘
```

## Technologie-Entscheidung: KISS-Prinzip

Wir haben uns für **Flask + Jinja2 + HTMX** anstelle moderner SPA-Frameworks entschieden:

### Warum nicht React/Vue/Angular?

| Aspekt | SPA Framework | Flask + HTMX |
|--------|---------------|--------------|
| Build-Prozess | npm, webpack, Bundler | Keiner |
| Sprachen | Python + JavaScript/TypeScript | Python + HTML/CSS |
| Debugging | Browser DevTools + Backend Logs | Nur Server Logs |
| State Management | Komplex (Redux, Vuex, etc.) | Server-seitige Session |
| API Versionierung | Erforderlich | Nicht nötig |
| Lernkurve | Hoch | Niedrig |
| Abhängigkeiten | 100+ npm Pakete | 3 Python Pakete |

### Warum HTMX?

HTMX bietet moderne Interaktivität (AJAX Updates, WebSocket Support) ohne:
- JavaScript zu schreiben
- Client-seitigen State zu verwalten
- Eine REST API zu bauen

Beispiel: Foto bewerten

```html
<!-- Traditioneller Ansatz: JS schreiben, State verwalten, API aufrufen -->
<button onclick="ratePhoto(42, 5)">★★★★★</button>

<!-- HTMX Ansatz: Verhalten in HTML deklarieren -->
<button hx-post="/api/photos/42/rate" 
        hx-vals='{"rating": 5}'
        hx-swap="outerHTML">
  ★★★★★
</button>
```

### Warum CSS Custom Properties für Theming?

Themes können ohne JavaScript gewechselt werden:

```css
/* themes/eui-light.css */
:root {
  --color-primary: #006BB4;
  --color-background: #FFFFFF;
}

/* themes/solarized-dark.css */
:root {
  --color-primary: #268bd2;
  --color-background: #002b36;
}
```

Theme-Wechsel bedeutet nur, eine andere CSS-Datei zu laden.

## Modul-System

Workflow-Module sind Plugins, definiert durch zwei Dateien:

### 1. Modul-Konfiguration (`module.yaml`)

Deklariert UI und Parameter des Moduls:

```yaml
id: import
name: Fotos importieren
description: Fotos von SD-Karte oder Ordner importieren
icon: upload
order: 1

parameters:
  - id: source
    type: path
    label: Quellverzeichnis
    required: true
    
  - id: event
    type: text
    label: Event-Name
    placeholder: "2026-01-24 Endurotraining"
    
  - id: author
    type: text
    label: Autor
    default: "{{DEFAULT_AUTHOR}}"

outputs:
  - id: imported_files
    type: file_list
  - id: target_directory
    type: path
```

### 2. Modul-Logik (`module.py`)

Implementiert das Verhalten des Moduls:

```python
from modules.base import WorkflowModule

class ImportModule(WorkflowModule):
    def validate(self, params: dict) -> list[str]:
        errors = []
        if not params.get('source'):
            errors.append("Quellverzeichnis ist erforderlich")
        return errors
    
    def execute(self, params: dict, context: dict) -> dict:
        # Ruft pg-import Script auf
        result = self.run_script('pg-import', [
            params['source'],
            '--event', params.get('event', ''),
            '--author', params.get('author', ''),
        ])
        return {
            'imported_files': result.get('files', []),
            'target_directory': result.get('target'),
        }
```

### Neues Modul hinzufügen

1. Ordner `web/modules/meinmodul/` erstellen
2. `module.yaml` mit UI-Definition hinzufügen
3. `module.py` mit Logik hinzufügen
4. Modul erscheint automatisch in der UI

## Theming-System

### Verfügbare Themes

| Theme | Beschreibung |
|-------|--------------|
| EUI Light | Elastic UI inspiriert, heller Hintergrund |
| EUI Dark | Elastic UI inspiriert, dunkler Hintergrund |
| Solarized Light | Ethan Schoonovers Solarized, hell |
| Solarized Dark | Ethan Schoonovers Solarized, dunkel |

### CSS-Variablen

Alle Farben sind als CSS Custom Properties definiert:

```css
:root {
  /* Basisfarben */
  --color-primary: #006BB4;
  --color-secondary: #69707D;
  --color-success: #017D73;
  --color-warning: #F5A700;
  --color-danger: #BD271E;
  
  /* Hintergrund-Ebenen */
  --color-background: #FFFFFF;
  --color-background-light: #F5F7FA;
  --color-background-dark: #E9EDF3;
  
  /* Textfarben */
  --color-text: #343741;
  --color-text-subdued: #69707D;
  --color-text-inverse: #FFFFFF;
  
  /* Rahmenfarben */
  --color-border: #D3DAE6;
  --color-border-dark: #98A2B3;
  
  /* Komponenten-spezifisch */
  --color-tab-active: var(--color-primary);
  --color-rating-star: #F5A700;
}
```

### Theme-Wechsel

```html
<!-- Theme-Auswahl im Header -->
<select hx-post="/api/theme" hx-vals="js:{theme: this.value}">
  <option value="eui-light">EUI Light</option>
  <option value="eui-dark">EUI Dark</option>
  <option value="solarized-light">Solarized Light</option>
  <option value="solarized-dark">Solarized Dark</option>
</select>
```

## Seiten

### Workflow Planner (`/workflow`)

- Tab-Navigation für verfügbare Module
- Drag-and-Drop Schritt-Sortierung
- Parameter-Formulare automatisch aus YAML generiert
- Workflows als Vorlagen speichern
- Workflows mit Bestätigung ausführen

### Album Manager (`/album`)

- Foto-Bibliothek nach Ordnern durchsuchen
- Bildvorschau mit Tastatur-Navigation (Pfeiltasten)
- 5-Sterne Bewertungssystem
- Fotos zu Alben zuordnen
- Web-Exports konfigurieren und ausführen

## API-Endpunkte (HTMX)

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/workflow/steps` | GET | Workflow-Schritte auflisten |
| `/api/workflow/steps` | POST | Schritt zum Workflow hinzufügen |
| `/api/workflow/steps/<id>` | DELETE | Schritt entfernen |
| `/api/workflow/execute` | POST | Workflow ausführen |
| `/api/photos/<folder>` | GET | Fotos im Ordner auflisten |
| `/api/photos/<id>/rate` | POST | Foto-Bewertung setzen |
| `/api/photos/<id>/album` | POST | Zu Album hinzufügen/entfernen |
| `/api/albums` | GET/POST | Alben auflisten/erstellen |
| `/api/albums/<id>/export` | POST | Album exportieren |
| `/api/theme` | POST | Theme wechseln |

## Web-Interface starten

```bash
# Vom Projekt-Root
cd web
source ../.venv/bin/activate
flask run --debug

# Öffne http://localhost:5000
```

## Abhängigkeiten

```
flask>=3.0
pyyaml>=6.0
pillow>=10.0
```

HTMX ist als statische Datei eingebunden (kein npm erforderlich).
