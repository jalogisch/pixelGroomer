# Beitragen zu PixelGroomer

*[English Version](CONTRIBUTING.md)*

Vielen Dank, dass du einen Beitrag zu PixelGroomer in Betracht ziehst!

## Erste Schritte

1. Forke das Repository
2. Klone deinen Fork lokal
3. Führe das Setup-Script aus:
   ```bash
   ./setup.sh
   ```
4. Erstelle einen Feature-Branch:
   ```bash
   git checkout -b feature/dein-feature-name
   ```

## Entwicklungsrichtlinien

### Sprachen

Dieses Projekt verwendet nur zwei Programmiersprachen:

- **Bash** - Für Scripts und Orchestrierung
- **Python** - Für komplexe Logik (EXIF, YAML, JSON)

Führe keine anderen Sprachen ein (Node.js, Ruby, Go, etc.).

### Bash-Anforderungen

- Scripts müssen mit Bash 3.2 kompatibel sein (macOS-Standard)
- Alle Scripts müssen die ShellCheck-Validierung bestehen
- Python muss immer in der virtuellen Umgebung des Projekts laufen

### Tests

Alle neuen Features und Bugfixes benötigen Tests:

```bash
make test          # Alle Tests ausführen
make test-fast     # Langsame Tests überspringen
```

Tests müssen bestehen, bevor ein Pull Request eingereicht wird.

### Dokumentation

Dieses Projekt pflegt zweisprachige Dokumentation (Englisch und Deutsch):

- Erstelle sowohl `*.en.md` als auch `*.de.md` Versionen
- Halte den Inhalt zwischen den Versionen synchron

### Commit-Nachrichten

Verwende aktionspräfixierte Commit-Nachrichten:

```
created: neues Feature hinzufügen
enhanced: bestehende Funktionalität verbessern
fixed: einen Bug korrigieren
refactored: Umstrukturierung ohne Verhaltensänderung
updated: Abhängigkeits- oder Konfigurationsänderungen
removed: Dateien oder Features löschen
```

## Pull-Request-Prozess

1. Stelle sicher, dass alle Tests bestehen (`make test`)
2. Aktualisiere die Dokumentation falls nötig (sowohl EN als auch DE)
3. Befolge das Commit-Nachrichtenformat
4. Reiche deinen Pull Request mit einer klaren Beschreibung ein

## Fragen?

Öffne ein Issue, wenn du Fragen hast oder Hilfe beim Einstieg brauchst.
