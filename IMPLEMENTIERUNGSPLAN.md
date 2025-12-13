# Tipels - Detaillierter Implementierungsplan

## Phase 1: Projekt-Setup (Woche 1)

### 1.1 GitHub-Repository einrichten
- [ ] Repository auf GitHub erstellen: `github.com/[username]/Tipels`
- [ ] Lizenz: GPLv3
- [ ] README.md mit Projektbeschreibung
- [ ] .gitignore für Python
- [ ] Branch-Struktur: `main`, `develop`
- [ ] Issue-Templates erstellen
- [ ] Pull-Request-Template

### 1.2 Projekt-Grundstruktur
```
tipels/
├── .github/
│   ├── workflows/           # GitHub Actions
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── src/tipels/
│   ├── __init__.py
│   ├── __main__.py         # Entry Point
│   ├── core/               # Kern-Logik
│   │   ├── __init__.py
│   │   ├── config.py       # Konfigurationsverwaltung
│   │   ├── logger.py       # Logging-System
│   │   └── detector.py     # Hardware-Erkennung
│   ├── drivers/            # Treiber-Module
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract Base Class
│   │   └── brother/
│   │       ├── __init__.py
│   │       ├── printer.py
│   │       └── scanner.py
│   ├── gui/                # GUI
│   │   ├── __init__.py
│   │   ├── gtk/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py
│   │   │   └── widgets/
│   │   └── qt/             # Für später
│   ├── cli/                # CLI-Interface
│   │   ├── __init__.py
│   │   └── commands.py
│   ├── daemon/             # D-Bus Service (PolicyKit)
│   │   ├── __init__.py
│   │   └── service.py
│   └── utils/              # Hilfsfunktionen
│       ├── __init__.py
│       ├── cups_helper.py
│       ├── sane_helper.py
│       ├── network.py
│       └── backup.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── user-manual/
│   │   ├── de/
│   │   └── en/
│   ├── developer/
│   └── troubleshooting/
├── data/
│   ├── org.tipels.policy   # PolicyKit-Regeln
│   ├── tipels.desktop      # Desktop-Entry
│   ├── icons/
│   └── locale/             # i18n-Übersetzungen
│       ├── de/
│       └── en/
├── packaging/
│   ├── debian/             # .deb
│   ├── snap/
│   ├── appimage/
│   └── flatpak/
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
├── README.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

### 1.3 Entwicklungsumgebung
- [ ] Python 3.10+ Virtual Environment
- [ ] Dependencies installieren:
  - `PyGObject` (GTK)
  - `click` oder `argparse` (CLI)
  - `dbus-python` (D-Bus/PolicyKit)
  - `pytest` (Testing)
  - `black` (Code-Formatierung)
  - `pylint` (Linting)
  - `mypy` (Type-Checking)

---

## Phase 2: Kern-Logik (Woche 2-3)

### 2.1 Logging-System
**Datei:** `src/tipels/core/logger.py`

```python
import logging
from pathlib import Path

class TipelsLogger:
    """Zentrales Logging-System"""

    - Einfache Logs: INFO, WARNING, ERROR
    - Debug-Logs: DEBUG (optional aktivierbar)
    - Log-Dateien: ~/.local/share/tipels/logs/tipels.log
    - Log-Rotation (z.B. 5 Dateien à 10MB)
    - Crash-Report-Generator
```

**Tasks:**
- [ ] Logger-Klasse implementieren
- [ ] Log-Rotation konfigurieren
- [ ] Crash-Report-Generator (GitHub-Issue-Template)
- [ ] Unit-Tests

### 2.2 Konfigurationsverwaltung
**Datei:** `src/tipels/core/config.py`

```python
class TipelsConfig:
    """Verwaltung von Konfigurationsdateien"""

    - System: /etc/tipels/tipels.conf
    - User: ~/.config/tipels/tipels.conf
    - Format: JSON oder YAML
    - Default-Werte
    - Migrations-Logik für Updates
```

**Tasks:**
- [ ] Config-Klasse implementieren
- [ ] Default-Konfiguration erstellen
- [ ] Config-Validierung
- [ ] Unit-Tests

### 2.3 Hardware-Erkennung
**Datei:** `src/tipels/core/detector.py`

```python
class HardwareDetector:
    """Erkennung von Druckern und Scannern"""

    - USB-Erkennung: lsusb, udev
    - Netzwerk-Erkennung: avahi-browse, nmap
    - CUPS-Status: lpstat, lpinfo
    - SANE-Status: scanimage -L
    - Geräte-Informationen extrahieren (Hersteller, Modell, VID/PID)
```

**Tasks:**
- [ ] USB-Erkennung implementieren
- [ ] Netzwerk-Erkennung (Avahi)
- [ ] CUPS-Abfrage
- [ ] SANE-Abfrage
- [ ] Geräte-Datenklassen (Device, Printer, Scanner)
- [ ] Unit-Tests (mit Mock-Daten)
- [ ] Integration-Tests

---

## Phase 3: Brother-Treiber-Modul (Woche 4-5)

### 3.1 Treiber-Basis-Klasse
**Datei:** `src/tipels/drivers/base.py`

```python
from abc import ABC, abstractmethod

class DriverBase(ABC):
    """Abstract Base Class für Treiber-Module"""

    @abstractmethod
    def detect_model(self, device): ...

    @abstractmethod
    def get_driver_info(self, model): ...

    @abstractmethod
    def download_driver(self, driver_info): ...

    @abstractmethod
    def install_driver(self, driver_path): ...

    @abstractmethod
    def configure_device(self, device, driver): ...

    @abstractmethod
    def test_device(self, device): ...
```

### 3.2 Brother-Drucker-Modul
**Datei:** `src/tipels/drivers/brother/printer.py`

**Funktionen:**
- [ ] Brother-Modell erkennen (VID/PID-Datenbank)
- [ ] Treiber-Quellen prüfen:
  1. Ubuntu-Repository (`apt search brother-*-lpr`)
  2. Brother-Website (automatischer Download)
  3. Open-Source (brlaser)
- [ ] Treiber herunterladen
- [ ] Treiber installieren (dpkg -i oder apt install)
- [ ] CUPS-Konfiguration:
  - `lpadmin -p <name> -E -v <uri> -m <ppd>`
  - PPD-Datei finden/installieren
- [ ] Testdruck durchführen
- [ ] Toner-Status auslesen (falls möglich)

**Brother-Treiber-Datenbank:**
```python
BROTHER_PRINTERS = {
    "MFC-L2700DN": {
        "lpr_package": "brother-mfc-l2700dn-lpr",
        "cups_package": "brother-mfc-l2700dn-cups-wrapper",
        "download_url": "https://support.brother.com/...",
        "ppd_file": "brother-mfc-l2700dn.ppd",
        "opensource_driver": "brlaser",  # Alternative
    },
    # ... weitere Modelle
}
```

### 3.3 Brother-Scanner-Modul
**Datei:** `src/tipels/drivers/brother/scanner.py`

**Funktionen:**
- [ ] Scanner erkennen
- [ ] SANE-Treiber installieren:
  - `brscan4` (Brother Scanner Driver)
  - Konfiguration mit `brsaneconfig4`
- [ ] Scanner registrieren:
  - USB: `brsaneconfig4 -a name=Brother model=MFC-L2700DN nodename=<dev>`
  - Netzwerk: `brsaneconfig4 -a name=Brother model=MFC-L2700DN ip=192.168.1.100`
- [ ] Benutzer zu Gruppen hinzufügen:
  - `usermod -aG lp,scanner,saned $USER`
- [ ] Test-Scan durchführen
- [ ] Scanner-Status prüfen

---

## Phase 4: CUPS & SANE Integration (Woche 5-6)

### 4.1 CUPS-Helper
**Datei:** `src/tipels/utils/cups_helper.py`

```python
class CupsHelper:
    - list_printers()          # Alle installierten Drucker
    - add_printer(name, uri, ppd)
    - remove_printer(name)
    - test_print(printer_name)
    - get_printer_status(name)
    - get_ppd_file(model)
```

### 4.2 SANE-Helper
**Datei:** `src/tipels/utils/sane_helper.py`

```python
class SaneHelper:
    - list_scanners()
    - add_scanner(name, model, connection)
    - remove_scanner(name)
    - test_scan(scanner_name)
    - get_scanner_status(name)
```

### 4.3 Netzwerk-Helper
**Datei:** `src/tipels/utils/network.py`

```python
class NetworkHelper:
    - scan_network()           # Avahi/mDNS-Suche
    - find_devices_by_ip(ip_range)
    - check_firewall_rules()
    - suggest_firewall_rules()
```

---

## Phase 5: Backup & Restore (Woche 6)

### 5.1 Backup-Modul
**Datei:** `src/tipels/utils/backup.py`

```python
class BackupManager:
    def create_backup(self, output_path):
        """
        Erstellt Backup im JSON-Format

        Struktur:
        {
          "version": "1.0",
          "created": "2025-12-13T10:30:00",
          "system": {...},
          "printers": [{...}],
          "scanners": [{...}],
          "drivers": [{...}]
        }
        """

    def restore_backup(self, backup_path):
        """
        Stellt Konfiguration wieder her
        - Treiber automatisch nachinstallieren
        - CUPS/SANE-Konfiguration wiederherstellen
        """
```

**Tasks:**
- [ ] JSON-Schema definieren
- [ ] Backup-Erstellung
- [ ] Restore-Logik
- [ ] Treiber-Nachinstallation
- [ ] Unit-Tests

---

## Phase 6: PolicyKit-Integration (Woche 7)

### 6.1 D-Bus-Service
**Datei:** `src/tipels/daemon/service.py`

```python
import dbus
import dbus.service

class TipelsDaemonService(dbus.service.Object):
    """D-Bus Service für privilegierte Operationen"""

    @dbus.service.method("org.tipels.Daemon",
                         in_signature='s', out_signature='b',
                         sender_keyword='sender')
    def InstallDriver(self, driver_path, sender=None):
        # PolicyKit-Check
        # dpkg -i driver_path
        pass

    # Weitere Methoden...
```

### 6.2 PolicyKit-Regeln
**Datei:** `data/org.tipels.policy`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <action id="org.tipels.install-driver">
    <description>Install printer/scanner driver</description>
    <message>Authentication is required to install a driver</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
  </action>
  <!-- Weitere Aktionen -->
</policyconfig>
```

**Tasks:**
- [ ] D-Bus Service implementieren
- [ ] PolicyKit-Regeln definieren
- [ ] Systemd-Service-Datei
- [ ] Installation-Skript für .deb

---

## Phase 7: GUI (GTK) (Woche 8-10)

### 7.1 Hauptfenster
**Datei:** `src/tipels/gui/gtk/main_window.py`

**Komponenten:**
- [ ] Headerbar mit App-Name und Logo
- [ ] Stack/Notebook für verschiedene Ansichten:
  1. **Setup-Assistent** (Hauptansicht)
  2. **Geräte-Verwaltung** (installierte Drucker/Scanner)
  3. **Backup/Restore**
  4. **Einstellungen**
  5. **Über/Hilfe**

### 7.2 Setup-Assistent
**Schritte:**
1. **Hardware-Scan**
   - Spinner während Scan
   - Fortschrittsbalken
   - Gefundene Geräte anzeigen (Liste)

2. **Geräte-Auswahl**
   - Automatisch erkanntes Gerät vorauswählen
   - Option: Manuell auswählen (Dropdown mit Modellen)
   - USB/Netzwerk-Auswahl
   - Bei Netzwerk: IP-Eingabe

3. **Treiber-Installation**
   - Treiberquelle anzeigen (Repo/Brother/OpenSource)
   - Fortschrittsbalken
   - Log-Ausgabe (optional erweitert)

4. **Konfiguration**
   - CUPS/SANE-Setup
   - Benutzer zu Gruppen hinzufügen
   - Firewall-Check (bei Netzwerk)

5. **Test**
   - Testdruck/Testscan
   - Status anzeigen (Toner, Papier)

6. **Fertig**
   - Erfolgsmeldung
   - Desktop-Benachrichtigung
   - Option: Weiteres Gerät einrichten

### 7.3 Widgets
- [ ] DeviceListWidget (gefundene Geräte)
- [ ] DriverSelectionWidget (Treiberauswahl)
- [ ] ProgressWidget (Fortschrittsanzeige)
- [ ] LogWidget (Log-Ausgabe)
- [ ] StatusWidget (Geräte-Status)

### 7.4 Geräte-Verwaltung
- [ ] Liste installierter Drucker/Scanner
- [ ] Status anzeigen (online, offline, Toner, etc.)
- [ ] Deinstallations-Button
- [ ] Test-Button (Testdruck/Testscan)

---

## Phase 8: CLI (Woche 10)

### 8.1 CLI-Commands
**Datei:** `src/tipels/cli/commands.py`

```python
import click

@click.group()
def cli():
    """Tipels - Drucker & Scanner Setup-Tool"""
    pass

@cli.command()
def scan():
    """Scanne nach Druckern und Scannern"""
    pass

@cli.command()
@click.option('--model', required=True)
@click.option('--connection', type=click.Choice(['usb', 'network']))
@click.option('--ip', help='IP-Adresse (nur bei Netzwerk)')
def install(model, connection, ip):
    """Installiere Drucker/Scanner"""
    pass

@cli.command()
@click.argument('device_name')
def remove(device_name):
    """Entferne Drucker/Scanner"""
    pass

@cli.command()
def list():
    """Liste installierte Geräte"""
    pass

@cli.command()
@click.argument('output_path')
def backup(output_path):
    """Erstelle Backup"""
    pass

@cli.command()
@click.argument('backup_path')
def restore(backup_path):
    """Stelle Backup wieder her"""
    pass
```

**Tasks:**
- [ ] CLI-Befehle implementieren
- [ ] Colored Output (z.B. mit `rich`)
- [ ] Progress-Bars für CLI
- [ ] Man-Page erstellen
- [ ] Bash-Completion

---

## Phase 9: Testing (Woche 11)

### 9.1 Unit-Tests
```
tests/unit/
├── test_config.py
├── test_logger.py
├── test_detector.py
├── test_brother_printer.py
├── test_brother_scanner.py
├── test_cups_helper.py
├── test_sane_helper.py
└── test_backup.py
```

**Ziel:** >80% Code-Coverage

### 9.2 Integration-Tests
```
tests/integration/
├── test_full_usb_setup.py
├── test_full_network_setup.py
├── test_backup_restore.py
└── test_multi_device.py
```

**Mit Mock-Hardware:**
- `unittest.mock` für System-Calls
- Fixtures für CUPS/SANE-Ausgaben

### 9.3 Manuelle Tests
**Mit echtem Gerät: Brother MFC-L2700DN**
- [ ] USB-Setup
- [ ] Netzwerk-Setup (WLAN/LAN)
- [ ] Testdruck
- [ ] Testscan
- [ ] Mehrere Geräte
- [ ] Deinstallation
- [ ] Backup/Restore
- [ ] Toner-Status

### 9.4 CI/CD (GitHub Actions)
```yaml
.github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=src/tipels tests/
      - run: black --check src/
      - run: pylint src/
```

---

## Phase 10: Packaging (Woche 12)

### 10.1 .deb-Paket
**Verzeichnis:** `packaging/debian/`

```
debian/
├── control          # Paket-Metadaten
├── rules            # Build-Anweisungen
├── changelog
├── copyright
├── install          # Dateien installieren
├── postinst         # Post-Install-Skript
├── prerm            # Pre-Remove-Skript
└── tipels.service   # Systemd-Service für Daemon
```

**Tasks:**
- [ ] Debian-Packaging-Struktur erstellen
- [ ] Dependencies definieren
- [ ] Post-Install-Skript:
  - PolicyKit-Regeln installieren
  - D-Bus-Service registrieren
  - Icon-Cache aktualisieren
- [ ] Pre-Remove-Skript:
  - Service stoppen
  - PolicyKit-Regeln entfernen
- [ ] Build-Skript: `dpkg-buildpackage`
- [ ] Test: `dpkg -i tipels_1.0.0_amd64.deb`

### 10.2 Snap
**Datei:** `packaging/snap/snapcraft.yaml`

```yaml
name: tipels
version: '1.0.0'
summary: Einfaches Setup für Drucker und Scanner
description: |
  Tipels vereinfacht die Installation von Druckern und Scannern
  auf Linux-Systemen. Aktuell mit Fokus auf Brother-Geräte.

grade: stable
confinement: classic  # Wegen privilegierten Operationen

apps:
  tipels:
    command: bin/tipels
    desktop: share/applications/tipels.desktop

parts:
  tipels:
    plugin: python
    source: .
    python-packages:
      - .
    stage-packages:
      - cups
      - sane
      - avahi-utils
```

**Tasks:**
- [ ] Snapcraft.yaml erstellen
- [ ] Build: `snapcraft`
- [ ] Test: `snap install tipels_1.0.0_amd64.snap --dangerous`
- [ ] Snap Store registrieren

### 10.3 AppImage & Flatpak
- [ ] Für spätere Phasen zurückgestellt

---

## Phase 11: Dokumentation (Woche 13)

### 11.1 Benutzer-Handbuch
**Verzeichnis:** `docs/user-manual/`

**Deutsch (`de/`):**
- [ ] Installation
- [ ] Erste Schritte
- [ ] USB-Drucker einrichten
- [ ] Netzwerk-Drucker einrichten
- [ ] Scanner einrichten
- [ ] Backup erstellen
- [ ] Backup wiederherstellen
- [ ] FAQ

**Englisch (`en/`):**
- [ ] Übersetzungen

### 11.2 Entwickler-Dokumentation
**Verzeichnis:** `docs/developer/`

- [ ] Architektur-Übersicht
- [ ] Plugin-System (neue Hersteller hinzufügen)
- [ ] API-Referenz
- [ ] Contribution Guidelines
- [ ] Code-Style-Guide
- [ ] Testing-Guidelines

### 11.3 Troubleshooting-Guide
**Verzeichnis:** `docs/troubleshooting/`

- [ ] Häufige Probleme und Lösungen
- [ ] Log-Analyse
- [ ] Firewall-Konfiguration
- [ ] CUPS-Fehler
- [ ] SANE-Fehler
- [ ] Brother-spezifische Probleme

### 11.4 README.md
- [ ] Projekt-Beschreibung
- [ ] Screenshots/GIFs
- [ ] Installation (alle Methoden)
- [ ] Quick-Start
- [ ] Links zur Dokumentation
- [ ] Contribution-Hinweise
- [ ] Lizenz

---

## Phase 12: Release v1.0.0 (Woche 14)

### 12.1 Pre-Release-Checks
- [ ] Alle Tests bestehen (Unit + Integration)
- [ ] Manuelle Tests mit echtem Gerät erfolgreich
- [ ] Dokumentation vollständig
- [ ] .deb-Paket funktioniert
- [ ] Snap-Paket funktioniert
- [ ] Keine kritischen Bugs offen

### 12.2 Release erstellen
- [ ] `CHANGELOG.md` aktualisieren
- [ ] Version-Tag: `v1.0.0`
- [ ] GitHub Release erstellen
- [ ] Binaries hochladen (.deb, Snap)
- [ ] Release-Notes schreiben (DE/EN)

### 12.3 Veröffentlichung
- [ ] Snap Store: Publish
- [ ] Ankündigung: Reddit (r/linux, r/linuxquestions)
- [ ] Ankündigung: Linux-Foren (ubuntuusers.de, etc.)
- [ ] Social Media (optional)

---

## Zukünftige Phasen (v2.0+)

### Geplante Features:
- [ ] Weitere Hersteller (HP, Epson, Canon)
- [ ] Qt-GUI
- [ ] Drucker-Monitoring (Status, Toner, Warnungen)
- [ ] Firmware-Updates
- [ ] Treiber-Updates automatisch prüfen
- [ ] Backup: TAR.GZ-Format mit Treiber-Bundles
- [ ] Cross-System-Restore (Ubuntu 22.04 → 24.04)
- [ ] AppImage & Flatpak
- [ ] Weitere Distributionen (Fedora, Arch, openSUSE)
- [ ] Web-Interface (optional)

---

## Zeitplan-Übersicht

| Phase | Dauer | Beschreibung |
|-------|-------|--------------|
| 1 | Woche 1 | Projekt-Setup & Repository |
| 2 | Woche 2-3 | Kern-Logik (Logger, Config, Detector) |
| 3 | Woche 4-5 | Brother-Treiber-Module |
| 4 | Woche 5-6 | CUPS & SANE Integration |
| 5 | Woche 6 | Backup & Restore |
| 6 | Woche 7 | PolicyKit-Integration |
| 7 | Woche 8-10 | GTK-GUI |
| 8 | Woche 10 | CLI |
| 9 | Woche 11 | Testing |
| 10 | Woche 12 | Packaging (.deb, Snap) |
| 11 | Woche 13 | Dokumentation |
| 12 | Woche 14 | Release v1.0.0 |

**Gesamtdauer:** ~14 Wochen (3-4 Monate)

---

## Ressourcen & Links

### Brother-Treiber
- Brother Support: https://support.brother.com
- Brother Linux-Treiber: https://support.brother.com/g/b/downloadlist.aspx

### CUPS
- CUPS Dokumentation: https://www.cups.org/doc/
- lpadmin Manual: `man lpadmin`

### SANE
- SANE Dokumentation: http://www.sane-project.org/
- Brother SANE Backend: https://support.brother.com/g/s/id/linux/en/

### Python-Libraries
- PyGObject: https://pygobject.readthedocs.io/
- Click: https://click.palletsprojects.com/
- dbus-python: https://dbus.freedesktop.org/doc/dbus-python/

### Testing
- pytest: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/

### Packaging
- Debian Packaging: https://www.debian.org/doc/manuals/maint-guide/
- Snapcraft: https://snapcraft.io/docs
- AppImage: https://appimage.org/
- Flatpak: https://flatpak.org/

---

*Erstellt: 2025-12-13*
*Status: Planung abgeschlossen, bereit für Implementierung*
