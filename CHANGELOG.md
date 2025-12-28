# Changelog

Alle wichtigen Änderungen an Tipels werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

### Hinzugefügt
- **CUPS-Helper**: Integration mit CUPS für Drucker-Verwaltung
  - Drucker hinzufügen/entfernen (USB, IPP, Socket, LPD)
  - Drucker-Status und -Auflistung
  - Testdruck-Funktion (CUPS-Testseite oder eigene Datei)
  - PPD-Datei-Suche via lpinfo
  - Vollständige Device-URI-Unterstützung
  - Optional sudo-Support für alle Admin-Operationen
- **SANE-Helper**: Herstellerunabhängige Scanner-Verwaltung
  - Scanner-Auflistung via scanimage -L
  - Parse: Device-Name, Hersteller, Modell, Backend, Typ
  - Test-Scan-Funktion (PNM, TIFF, PNG, JPEG)
  - Konfigurierbare Auflösung (Standard: 150 DPI)
  - Scanner-Fähigkeiten abfragen (Auflösungen, Modi, Quellen)
  - Scanner-Status-Prüfung (SANE, Scanner, Gruppen)
- **CLI-Interface**: Vollständig funktionsfähiges Kommandozeilen-Interface
  - `scan`: Hardware-Scan (USB + Netzwerk mit --usb, --network, --timeout)
  - `install`: Drucker/Scanner installieren (--model, --connection, --ip, --name, --type)
  - `remove`: Drucker/Scanner entfernen (--printer, --scanner mit Bestätigung)
  - `list`: Installierte Geräte auflisten (--printers, --scanners)
  - `status`: System-Status anzeigen (CUPS, SANE, Gruppen, Treiber)
  - `test-print`: Testdruck durchführen (--file für eigene Datei)
  - `test-scan`: Test-Scan durchführen (--device, --output, --format, --resolution)
  - `backup`: Backup erstellen (Platzhalter)
  - `restore`: Backup wiederherstellen (Platzhalter)
  - Farbcodierte Ausgabe (Grün ✓, Rot ✗, Gelb ⚠)
  - Detaillierte Fehlermeldungen und Logging
  - Exit-Codes für Skript-Integration
- **Tests**: 23 neue Unit-Tests hinzugefügt
  - 19 Tests für CUPS-Helper (87% Coverage)
  - 4 Tests für SANE-Helper (85% Coverage)
  - 197 Unit-Tests gesamt, 80% Coverage

### Geplant
- GTK-GUI
- PolicyKit-Integration
- Backup/Restore-Funktion (vollständige Implementierung)
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
