# Sicherheitsrichtlinie

*[English Version](SECURITY.md)*

## Unterstützte Versionen

| Version | Unterstützt       |
| ------- | ----------------- |
| latest  | :white_check_mark: |

## Sicherheitslücke melden

Wenn du eine Sicherheitslücke in PixelGroomer entdeckst, melde sie bitte
über eine private Security Advisory auf GitHub:

1. Öffne den **Security**-Tab des Repositorys
2. Klicke auf **Report a vulnerability**
3. Beschreibe das Problem ausführlich

Wir werden uns schnellstmöglich melden und mit dir an einer Lösung arbeiten.

## Sicherheitshinweise

PixelGroomer verarbeitet lokale Dateien und:

- verbindet sich nicht mit externen Servern (außer zur Paketinstallation)
- speichert oder überträgt keine personenbezogenen Daten
- benötigt keine erweiterten Rechte

Beim Einsatz des Tools solltest du dennoch:

- bei `.import.yaml` aus nicht vertrauenswürdigen Quellen vorsichtig sein
- Skripte prüfen, bevor du sie mit sensiblen Fotosammlungen ausführst
- Abhängigkeiten aktuell halten (`pip install -U -r requirements.txt`)
