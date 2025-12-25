# Tipels - Projekt-Dokumentation

## Projektübersicht
Tipels ist eine Linux-Applikation zur vereinfachten Einrichtung von Druckern und Scannern.

### Projektziele
- **Phase 1**: Unterstützung für Brother-Geräte (Testgerät: Brother MFC-L2700DN)
- **Spätere Phasen**: Erweiterung auf weitere Marken (HP, Epson, Canon)
- Automatische Hardware-Erkennung (Plug & Play)
- Manuelle Einrichtung als Fallback
- Integration in CUPS und SANE
- Open Source (GPLv3) auf GitHub
- Repository-Name: **Tipels**

### Ziel-Plattformen
- **Primär**: Debian, Ubuntu, Linux Mint
- **Später**: Weitere Linux-Distributionen
- **Desktop-Umgebungen**: GNOME, Cinnamon, XFCE (GTK-basiert)

### Technologie-Stack
- **Python**: Version 3.10+
- **GUI**: PyGObject (GTK 3/4) - Primär
- **GUI**: PyQt/PySide (Qt) - Sekundär
- **System-Integration**: CUPS (Drucker), SANE (Scanner)
- **CLI**: Kommandozeilen-Interface zusätzlich zur GUI
- **Sprachen**: Deutsch/Englisch (i18n)

### Kernfunktionen
1. **Hardware-Erkennung**
   - USB und Netzwerk-Geräte
   - Automatische Suche (Avahi/mDNS)
   - Manuelle IP-Eingabe für Poweruser

2. **Treiberinstallation**
   - **OpenPrinting-First Strategie**: Foomatic-DB (primär, ~10.000+ Drucker)
   - Ubuntu-Repositories (OpenPrinting-Treiber: brlaser, hplip, gutenprint)
   - Brother-Website (automatischer Download als Fallback)
   - Intelligentes Caching erkannter Drucker
   - Automatische Installation von Abhängigkeiten

3. **Multi-Geräte-Verwaltung**
   - Mehrere Drucker/Scanner installieren
   - Geräte deinstallieren (inkl. Treiber)
   - Backup/Wiederherstellung der Konfiguration

4. **Berechtigungsmanagement**
   - GUI: PolicyKit (granulare Berechtigungen)
   - CLI: Sudo (einfach für Poweruser)
   - Automatisches Hinzufügen zu Gruppen (lp, scanner, saned)

5. **Benachrichtigungen**
   - Desktop-Benachrichtigungen bei Erfolg/Fehler
   - Toner-Status nach Einrichtung
   - Firewall-Hinweise bei Netzwerk-Setup

6. **Fehlerbehandlung**
   - Einfache Logs (primär)
   - Crash-Report-Generator für GitHub-Issues
   - Anonymisierte Logs für Support

## Technische Entscheidungen

### Treiberarchitektur

#### OpenPrinting-First Strategie
Tipels nutzt eine dreistufige Treiberarchitektur:

1. **Foomatic-DB (Primär, alle Hersteller)**
   - Integration mit CUPS via `lpinfo -m`
   - Zugriff auf ~10.000+ Drucker-PPD-Dateien
   - Automatische Erkennung für Brother, HP, Canon, Epson, Xerox, Lexmark, etc.
   - Treiber-Priorität: brlaser (10) > hplip (9) > gutenprint (8) > postscript (7)
   - In-Memory + Persistenter Cache für schnellen Zugriff

2. **Tipels Printer Cache**
   - JSON-basierte Datenbank erkannter Drucker
   - Speicherort: `~/.local/share/tipels/printer_cache.json`
   - Speichert: OpenPrinting-Treiber, Official-Treiber, PPD-Namen, last_used
   - Case-insensitive Schlüssel (manufacturer:model)

3. **Herstellerspezifische Treiber (Fallback)**
   - Brother Official Drivers (.deb Download von Brother-Website)
   - Nur wenn Foomatic keinen Treiber findet ODER User explizit wünscht
   - Nützlich für spezielle Features (Fax, erweiterte Funktionen)
   - Modellspezifische Download-URLs in driver_db.py

#### Implementierte Module
- `tipels.core.foomatic`: FoomaticDetector, lpinfo-Parser, Treiber-Matching
- `tipels.core.printer_cache`: PrinterCache, JSON-Persistenz
- `tipels.drivers.brother.installer`: DriverInstaller mit Foomatic-Integration
- `tipels.drivers.brother.scanner`: BrotherScannerManager, SANE/brscan4-Integration
- `tipels.utils.cups_helper`: CupsHelper, CUPS-Drucker-Verwaltung
- `tipels.utils.sane_helper`: SaneHelper, SANE-Scanner-Verwaltung (allgemein)

#### Scanner-Integration (SANE)
Brother-Scanner werden über SANE (Scanner Access Now Easy) verwaltet:

1. **brscan4-Treiber**: Brother Scanner Driver für SANE
2. **Scanner-Registrierung**: Via `brsaneconfig4`
   - USB: `brsaneconfig4 -a name=Brother model=MFC-L2700DN nodename=/dev/usb/lp0`
   - Netzwerk: `brsaneconfig4 -a name=Brother model=MFC-L2700DN ip=192.168.1.100`
3. **Gruppenverwaltung**: Automatisches Hinzufügen zu scanner, saned, lp
4. **Test-Scan**: Via `scanimage` für Funktionstest
5. **Scanner-Status**: Systemprüfung (brscan4, SANE, Gruppen)

**SANE-Helper (Allgemein):**
Der allgemeine SANE-Helper (`tipels.utils.sane_helper`) bietet herstellerunabhängige Scanner-Funktionen:

1. **SaneHelper**: Wrapper für SANE-Kommandos (subprocess-basiert)
2. **Scanner-Auflistung**: Via `scanimage -L`
   - Liste: Alle verfügbaren SANE-Scanner
   - Parse: Device-Name, Hersteller, Modell, Backend, Typ
3. **Test-Scan**: Via `scanimage`
   - Formate: PNM, TIFF, PNG, JPEG
   - Auflösung: Konfigurierbar (Standard: 150 DPI)
   - Auto-Device oder spezifischer Scanner
4. **Scanner-Fähigkeiten**: Via `scanimage --help -d <device>`
   - Auflösungen, Modi (Color/Gray/Lineart), Quellen (Flatbed/ADF)
5. **Scanner-Status**: Systemprüfung (SANE, Scanner, Gruppen)

#### CUPS-Integration (Drucker)
Drucker werden über CUPS (Common UNIX Printing System) verwaltet:

1. **CupsHelper**: Wrapper für CUPS-Kommandos (subprocess-basiert)
2. **Drucker-Verwaltung**: Via `lpadmin`
   - Hinzufügen: `lpadmin -p name -E -v uri -m ppd -L location -D description`
   - Entfernen: `lpadmin -x name`
3. **Drucker-Abfragen**: Via `lpstat`, `lpoptions`
   - Liste: `lpstat -p` (alle Drucker)
   - Status: `lpstat -p name -l` (detaillierter Status)
   - URI: `lpstat -v name` (Device-URI)
   - Jobs: `lpstat -o name` (aktive Druckaufträge)
4. **PPD-Suche**: Via `lpinfo -m` (verfügbare PPD-Dateien)
5. **Testdruck**: Via `lp -d printer testfile`
6. **Unterstützte Verbindungen**: USB, IPP, Socket, LPD

### Architektur
- **Modularer Aufbau**: Plugin-System für Hersteller
- **Projektstruktur**:
  ```
  tipels/
  ├── src/tipels/
  │   ├── core/          # Kern-Logik
  │   ├── drivers/       # Treiber-Module (brother, hp, ...)
  │   ├── gui/           # GUI (gtk, qt)
  │   ├── cli/           # CLI-Interface
  │   ├── daemon/        # D-Bus Service (PolicyKit)
  │   └── utils/         # Hilfsfunktionen
  ├── tests/             # Unit- & Integrationstests
  ├── docs/              # Dokumentation
  ├── data/              # PolicyKit-Regeln, i18n
  └── packaging/         # .deb, snap, appimage, flatpak
  ```

### Backup-System
- **Phase 1**: JSON-Format (`.tipels-backup`)
  - CUPS-Konfiguration
  - SANE-Konfiguration
  - Tipels-Einstellungen
  - Installierte Treiber-Versionen
- **Phase 2**: TAR.GZ mit JSON-Manifest + Treiber-Bundles
- **Wiederherstellung**: Automatische Treiber-Nachinstallation

### Packaging & Distribution
- **Priorität 1**: .deb (Debian/Ubuntu/Mint)
- **Priorität 2**: Snap
- **Später**: AppImage, Flatpak

### CI/CD & Testing
- **GitHub Actions**: Automatische Tests & Builds
- **Testing-Strategie**:
  - Unit-Tests (Kern-Logik)
  - Integration-Tests (Mock-Hardware)
  - Manuelle Tests (echtes Gerät: MFC-L2700DN)
- **Versionierung**: Semantic Versioning (v1.0.0)
- **Branch-Strategie**:
  - `main` - Stable Releases
  - `develop` - Beta/Testing
  - Feature-Branches

### Konfiguration & Logging
- **System-Konfiguration**: `/etc/tipels/`
- **User-Konfiguration**: `~/.config/tipels/`
- **Logs**: `~/.local/share/tipels/logs/`
- **System-Logs**: `/var/log/tipels/` (optional)

### Update-Mechanismus
- **App-Updates**: Update-Prüfung mit Benachrichtigung
- **Treiber-Updates**: Für spätere Versionen

## Entwicklungsstand
- [x] Projektplanung erstellt
- [x] Anforderungen geklärt
- [x] Technische Entscheidungen getroffen
- [x] Detaillierter Implementierungsplan
- [x] GitHub-Repository-Struktur lokal
- [x] Logger-System (94% Coverage)
- [x] Config-System (79% Coverage)
- [x] Hardware-Erkennung (USB + Netzwerk)
- [x] Device-Klassen (Printer, Scanner, MFP)
- [x] Brother Treiber-Datenbank (OpenPrinting + Official)
- [x] **Foomatic-Integration** (lpinfo-Parser, Treiber-Matching)
- [x] **Printer Cache** (JSON-basiert, persistent)
- [x] **DriverInstaller** (Repository + Brother-Website-Download)
- [x] **OpenPrinting-First Strategie** (Foomatic → Brother Official Fallback)
- [x] **Brother Scanner-Manager** (SANE/brscan4-Integration)
- [x] **Scanner-Konfiguration** (USB + Netzwerk, brsaneconfig4)
- [x] **Benutzer-Gruppenverwaltung** (scanner, saned, lp)
- [x] **CUPS-Helper** (Drucker registrieren, Status, Testdruck)
- [x] **SANE-Helper** (Scanner-Utilities, Auflistung, Test-Scan, Fähigkeiten)
- [x] Unit-Tests (197 Tests, 78% Coverage)
- [x] CI/CD (GitHub Actions)
- [x] Logo & Branding
- [x] README.md aktualisiert
- [ ] GitHub-Repository online erstellen
- [ ] GUI-Entwicklung (GTK)
- [ ] CLI-Interface (funktionsfähig)
- [ ] PolicyKit-Integration
- [ ] Backup/Restore-Funktion
- [ ] Dokumentation erweitern
  - [x] Basis-Struktur
  - [ ] Benutzer-Handbuch (Details)
  - [ ] Entwickler-Dokumentation (Details)
  - [ ] Troubleshooting-Guide (Details)

## Funktionsumfang v1.0
- [x] Brother-Geräte (alle Modelle)
- [x] USB + Netzwerk-Verbindungen
- [x] Drucker + Scanner
- [x] Automatische Erkennung + Manuelle Auswahl
- [x] GTK-GUI + CLI
- [x] Backup/Restore
- [x] .deb + Snap Packaging
- [ ] Weitere Hersteller (v2.0+)

---
*Erstellt: 2025-12-12*
