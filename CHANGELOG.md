# Changelog

Alle wichtigen Änderungen an Tipels werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Geplant
- CUPS-Integration (Drucker registrieren)
- SANE-Helper (Scanner-Utilities)
- Testdruck-Funktion
- GTK-GUI
- PolicyKit-Integration
- Backup/Restore-Funktion
- .deb & Snap Packaging

## [0.2.0] - 2025-12-14

### Hinzugefügt
- **Foomatic-Integration**: Automatische Treibersuche für ~10.000+ Drucker
  - `FoomaticDetector`: lpinfo-Parser, intelligentes Modell-Matching
  - Treiber-Priorität: brlaser > hplip > gutenprint > postscript
  - In-Memory-Cache für schnelle PPD-Abfragen
- **Printer-Cache**: JSON-basierte persistente Datenbank
  - Speicherort: `~/.local/share/tipels/printer_cache.json`
  - Case-insensitive Schlüssel, automatische Metadaten
- **DriverInstaller**: Erweiterte Treiber-Installation
  - OpenPrinting-First Strategie (Foomatic → Brother Official Fallback)
  - Repository-Installation via apt-get
  - Brother-Website-Download (.deb) mit automatischer Abhängigkeitsauflösung
  - Multi-Hersteller-Support (Brother, HP, Canon, Epson via Foomatic)
- **Brother-Scanner-Manager**: SANE/brscan4-Integration
  - Scanner-Registrierung (USB + Netzwerk) via brsaneconfig4
  - Automatische Benutzer-Gruppenverwaltung (scanner, saned, lp)
  - Test-Scan-Funktion via scanimage
  - Scanner-Status-Prüfung (Systemvoraussetzungen)
- **Tests**: 126 neue Unit-Tests hinzugefügt (155 gesamt, 76% Coverage)
  - 12 Tests für Foomatic (82% Coverage)
  - 15 Tests für PrinterCache (97% Coverage)
  - 21 Tests für Scanner-Manager (82% Coverage)

### Geändert
- `DriverInstaller.__init__()`: Neue Parameter `use_foomatic`, `cache_file`
- `install_driver_for_model()`: Neuer Parameter `manufacturer` (Standard: "Brother")
- Dokumentation aktualisiert (README.md, claude.md)

## [0.1.0] - 2025-12-13

### Hinzugefügt
- Initiales Projekt-Setup
- Basis-Struktur
- Logger-System (94% Coverage)
- Config-System (79% Coverage)
- Hardware-Detector (USB/Netzwerk, 83% Coverage)
- Device-Klassen (Printer, Scanner, MFP, 100% Coverage)
- Brother Treiber-Datenbank (driver_db.py, 100% Coverage)
- CLI-Grundgerüst
- 29 Unit-Tests (52% Coverage)
- CI/CD mit GitHub Actions
- Logo & Branding
- Umfassende Dokumentation
- Entwicklungsumgebung

---

**Legende:**
- `Hinzugefügt` - Neue Features
- `Geändert` - Änderungen an bestehenden Features
- `Veraltet` - Features die bald entfernt werden
- `Entfernt` - Entfernte Features
- `Behoben` - Bug-Fixes
- `Sicherheit` - Sicherheits-relevante Änderungen
