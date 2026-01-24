# Web Workflow Planner

*[Deutsche Version](web-planner.de.md)*

A Flask-based web interface for PixelGroomer that provides a visual workflow planner and album management.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Browser                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Jinja2 Templates + HTMX                                    │    │
│  │  - Workflow Planner Page                                    │    │
│  │  - Album Manager Page                                       │    │
│  │  - Theme Switcher (EUI / Solarized, Light / Dark)          │    │
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
│                    Existing CLI Scripts                              │
│  pg-import  pg-exif  pg-develop  pg-album  pg-verify                │
└─────────────────────────────────────────────────────────────────────┘
```

## Technology Decision: KISS Principle

We chose **Flask + Jinja2 + HTMX** over modern SPA frameworks for the following reasons:

### Why Not React/Vue/Angular?

| Aspect | SPA Framework | Flask + HTMX |
|--------|---------------|--------------|
| Build process | npm, webpack, bundler | None |
| Languages | Python + JavaScript/TypeScript | Python + HTML/CSS |
| Debugging | Browser DevTools + Backend logs | Server logs only |
| State management | Complex (Redux, Vuex, etc.) | Server-side session |
| API versioning | Required | Not needed |
| Learning curve | High | Low |
| Dependencies | 100+ npm packages | 3 Python packages |

### Why HTMX?

HTMX provides modern interactivity (AJAX updates, WebSocket support) without:
- Writing JavaScript
- Managing client-side state
- Building a REST API

Example: Rating a photo

```html
<!-- Traditional approach: Write JS, manage state, call API -->
<button onclick="ratePhoto(42, 5)">★★★★★</button>

<!-- HTMX approach: Declare behavior in HTML -->
<button hx-post="/api/photos/42/rate" 
        hx-vals='{"rating": 5}'
        hx-swap="outerHTML">
  ★★★★★
</button>
```

### Why CSS Custom Properties for Theming?

Themes can be switched without JavaScript:

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

Theme switching is just changing which CSS file is loaded.

## Module System

Workflow modules are plugins defined by two files:

### 1. Module Configuration (`module.yaml`)

Declares the module's UI and parameters:

```yaml
id: import
name: Import Photos
description: Import photos from SD card or folder
icon: upload
order: 1

parameters:
  - id: source
    type: path
    label: Source Directory
    required: true
    
  - id: event
    type: text
    label: Event Name
    placeholder: "2026-01-24 Endurotraining"
    
  - id: author
    type: text
    label: Author
    default: "{{DEFAULT_AUTHOR}}"

outputs:
  - id: imported_files
    type: file_list
  - id: target_directory
    type: path
```

### 2. Module Logic (`module.py`)

Implements the module's behavior:

```python
from modules.base import WorkflowModule

class ImportModule(WorkflowModule):
    def validate(self, params: dict) -> list[str]:
        errors = []
        if not params.get('source'):
            errors.append("Source directory is required")
        return errors
    
    def execute(self, params: dict, context: dict) -> dict:
        # Calls pg-import script
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

### Adding a New Module

1. Create folder `web/modules/mymodule/`
2. Add `module.yaml` with UI definition
3. Add `module.py` with logic
4. Module appears automatically in the UI

## Theming System

### Available Themes

| Theme | Description |
|-------|-------------|
| EUI Light | Elastic UI inspired, light background |
| EUI Dark | Elastic UI inspired, dark background |
| Solarized Light | Ethan Schoonover's Solarized, light |
| Solarized Dark | Ethan Schoonover's Solarized, dark |

### CSS Variables

All colors are defined as CSS custom properties:

```css
:root {
  /* Base colors */
  --color-primary: #006BB4;
  --color-secondary: #69707D;
  --color-success: #017D73;
  --color-warning: #F5A700;
  --color-danger: #BD271E;
  
  /* Background levels */
  --color-background: #FFFFFF;
  --color-background-light: #F5F7FA;
  --color-background-dark: #E9EDF3;
  
  /* Text colors */
  --color-text: #343741;
  --color-text-subdued: #69707D;
  --color-text-inverse: #FFFFFF;
  
  /* Border colors */
  --color-border: #D3DAE6;
  --color-border-dark: #98A2B3;
  
  /* Component-specific */
  --color-tab-active: var(--color-primary);
  --color-rating-star: #F5A700;
}
```

### Theme Switching

```html
<!-- Theme selector in header -->
<select hx-post="/api/theme" hx-vals="js:{theme: this.value}">
  <option value="eui-light">EUI Light</option>
  <option value="eui-dark">EUI Dark</option>
  <option value="solarized-light">Solarized Light</option>
  <option value="solarized-dark">Solarized Dark</option>
</select>
```

## Pages

### Workflow Planner (`/workflow`)

- Tab navigation for available modules
- Drag-and-drop step ordering
- Parameter forms auto-generated from YAML
- Save workflows as templates
- Execute workflows with confirmation

### Album Manager (`/album`)

- Browse photo library by folder
- Image preview with keyboard navigation (arrow keys)
- 5-star rating system
- Assign photos to albums
- Configure and execute web exports

## API Endpoints (HTMX)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/workflow/steps` | GET | List workflow steps |
| `/api/workflow/steps` | POST | Add step to workflow |
| `/api/workflow/steps/<id>` | DELETE | Remove step |
| `/api/workflow/execute` | POST | Execute workflow |
| `/api/photos/<folder>` | GET | List photos in folder |
| `/api/photos/<id>/rate` | POST | Set photo rating |
| `/api/photos/<id>/album` | POST | Add/remove from album |
| `/api/albums` | GET/POST | List/create albums |
| `/api/albums/<id>/export` | POST | Export album |
| `/api/theme` | POST | Change theme |

## Running the Web Interface

```bash
# From project root
cd web
source ../.venv/bin/activate
flask run --debug

# Open http://localhost:5000
```

## Dependencies

```
flask>=3.0
pyyaml>=6.0
pillow>=10.0
```

HTMX is included as a static file (no npm required).
