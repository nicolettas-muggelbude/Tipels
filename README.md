# Tipels

<p align="center">
  <img src="data/icons/tipels-logo.svg" alt="Tipels Logo" width="256"/>
</p>

<p align="center">
  <strong>Einfache Einrichtung von Druckern und Scannern unter Linux</strong>
</p>

<p align="center">
  <em>🐾 Kleine Schritte zum perfekt eingerichteten Drucker 🐾</em>
</p>

<p align="center">
  <a href="https://github.com/nicolettas-muggelbude/Tipels/actions"><img src="https://img.shields.io/github/actions/workflow/status/nicolettas-muggelbude/Tipels/tests.yml?branch=main" alt="Build Status"/></a>
  <a href="https://github.com/nicolettas-muggelbude/Tipels/releases"><img src="https://img.shields.io/github/v/release/nicolettas-muggelbude/Tipels?include_prereleases" alt="Release"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-blue.svg" alt="License"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python Version"/></a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#verwendung">Verwendung</a> •
  <a href="#dokumentation">Dokumentation</a> •
  <a href="#contributing">Mitmachen</a>
</p>

---

## 🐦 Über Tipels

**Tipels** (von *"tipeln"* = kleine Schritte machen) ist eine benutzerfreundliche Linux-Applikation, die das Einrichten von Druckern und Scannern vereinfacht.

Wie Vogelfußspuren auf einem Blatt Papier führt dich Tipels Schritt für Schritt zur perfekt eingerichteten Hardware - **ohne komplexe Terminal-Befehle, ohne Treibersuche, ohne Kopfschmerzen**.

### 💡 Warum Tipels?

- **🔌 Plug & Play**: Hardware anschließen, Tipels starten, fertig!
- **⚡ Automatische Treiberinstallation**: Kein manuelles Herunterladen mehr
- **🌐 Netzwerk & USB**: Unterstützt beide Verbindungsarten
- **💾 Backup & Restore**: Konfiguration sichern und wiederherstellen
- **🔓 Open Source**: Vollständig transparent und frei verfügbar (GPLv3)
- **🇩🇪 🇬🇧 Mehrsprachig**: Deutsch und Englisch

### 🖨️ Unterstützte Hersteller

**v1.0 (In Entwicklung):**
- ✅ **Brother** (alle Modelle)
  - Testgerät: Brother MFC-L2700DN

**v2.0+ (Geplant):**
- 🔜 HP
- 🔜 Epson
- 🔜 Canon

---

## ✨ Features

### 🖨️ Drucker-Setup
- ✅ **Automatische Erkennung** von USB- und Netzwerk-Druckern
- ✅ **OpenPrinting-First Strategie**: Foomatic-DB mit ~10.000+ Druckern
- ✅ **Intelligente Treiberauswahl**: OpenPrinting → Hersteller-Website → Fallback
- ✅ **Multi-Hersteller-Support**: Brother, HP, Canon, Epson (via Foomatic)
- ✅ **Treiber-Cache**: Schneller Zugriff auf bereits erkannte Drucker
- ✅ **CUPS-Integration**: Drucker registrieren, Status abfragen, verwalten
- ✅ **Testdruck-Funktion**: CUPS-Testseite oder eigene Datei drucken

### 🖼️ Scanner-Setup
- ✅ **Automatische Scanner-Erkennung**
- ✅ **SANE/brscan4-Integration** (Brother)
- ✅ **USB + Netzwerk-Support** via brsaneconfig4
- ✅ **Automatisches Hinzufügen zu Benutzergruppen** (`lp`, `scanner`, `saned`)
- ✅ **Test-Scan-Funktion** via scanimage
- ✅ **Scanner-Status-Prüfung** (Systemvoraussetzungen)

### 💾 Backup & Restore
- ✅ Konfiguration sichern (Drucker, Scanner, Treiber)
- ✅ Wiederherstellung auf gleichem oder neuem System
- ✅ Automatische Treiber-Nachinstallation
- ✅ JSON-Format (`.tipels-backup`)

### 🎨 Benutzerfreundlich
- ✅ **GTK-GUI** für Desktop-Umgebungen (GNOME, Cinnamon, XFCE)
- ✅ **CLI** für Poweruser und Skripte
- ✅ Deutsch und Englisch (i18n)
- ✅ Desktop-Benachrichtigungen
- ✅ Hilfreiche Fehlermeldungen mit Crash-Report-Generator

### 🔒 Sicherheit
- ✅ **PolicyKit-Integration** für sichere Berechtigungen (GUI)
- ✅ Granulare Rechte-Vergabe (nur benötigte Aktionen)
- ✅ Kein unnötiger Root-Zugriff

---

## 📦 Installation

### Voraussetzungen

- **OS**: Ubuntu 20.04+, Debian 11+, Linux Mint 20+
- **Python**: 3.10 oder höher
- **Desktop**: GTK-basierte Umgebung (GNOME, Cinnamon, XFCE, MATE)

### Ubuntu / Debian / Linux Mint

#### Via .deb-Paket (empfohlen - *noch nicht verfügbar*)
```bash
# Download der neuesten Version
wget https://github.com/nicolettas-muggelbude/Tipels/releases/download/v1.0.0/tipels_1.0.0_amd64.deb

# Installation
sudo dpkg -i tipels_1.0.0_amd64.deb
sudo apt-get install -f  # Falls Abhängigkeiten fehlen
```

#### Via Snap (*noch nicht verfügbar*)
```bash
sudo snap install tipels
```

### 🛠️ Aus dem Quellcode (Development)

```bash
# 1. Repository klonen
git clone https://github.com/nicolettas-muggelbude/Tipels.git
cd Tipels

# 2. System-Dependencies installieren
./install-system-deps.sh

# 3. Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# 4. Python-Dependencies installieren
make install-dev

# 5. Tipels starten
tipels --version
```

**Hinweis**: PyGObject und dbus-python werden über System-Pakete installiert, nicht über pip!

---

## 🚀 Verwendung

### GUI-Modus

```bash
# Tipels starten
tipels
```

Oder über das Anwendungsmenü: **System → Einstellungen → Tipels**

### CLI-Modus

```bash
# Hardware scannen
tipels scan

# Drucker installieren (automatisch)
sudo tipels install --model "MFC-L2700DN" --connection usb

# Netzwerk-Scanner installieren
sudo tipels install --model "MFC-L2700DN" --connection network --ip 192.168.1.100

# Installierte Geräte auflisten
tipels list

# Gerät entfernen
sudo tipels remove "Brother_MFC_L2700DN"

# Backup erstellen
tipels backup ~/tipels-backup.tipels-backup

# Backup wiederherstellen
sudo tipels restore ~/tipels-backup.tipels-backup
```

---

## 📚 Dokumentation

- 📖 **[Benutzer-Handbuch (Deutsch)](docs/user-manual/de/README.md)**
- 📖 **[User Manual (English)](docs/user-manual/en/README.md)**
- 🔧 **[Entwickler-Dokumentation](docs/developer/README.md)**
- ❓ **[Troubleshooting](docs/troubleshooting/README.md)**
- 📝 **[Changelog](CHANGELOG.md)**
- 📋 **[Implementierungsplan](IMPLEMENTIERUNGSPLAN.md)**

---

## 🤝 Contributing

Beiträge sind herzlich willkommen! Siehe **[CONTRIBUTING.md](CONTRIBUTING.md)** für Details.

### Wie kann ich helfen?

- 🐛 **Bugs melden** - [GitHub Issues](https://github.com/nicolettas-muggelbude/Tipels/issues)
- 💡 **Feature-Ideen** einreichen
- 📝 **Dokumentation** verbessern
- 🌍 **Übersetzungen** hinzufügen
- 💻 **Code** beitragen
- 🧪 **Testen** mit verschiedenen Hardware

### Entwicklung

```bash
# Repository klonen
git clone https://github.com/nicolettas-muggelbude/Tipels.git
cd Tipels

# System-Dependencies & Development-Setup
./install-system-deps.sh
python3 -m venv venv
source venv/bin/activate
make install-dev

# Tests ausführen
make test

# Code-Formatierung
make format

# Linting
make lint
```

**Test-Status:**
- ✅ 174 Unit-Tests (alle bestehen)
- ✅ 78% Code-Coverage
- ✅ CI/CD mit GitHub Actions

---

## 🏗️ Entwicklungsstand

**Aktuelle Version**: v0.1.0 (Alpha - In Entwicklung)

### ✅ Implementiert (Phase 1-4.3)
- [x] Projekt-Struktur & Setup
- [x] Logger-System (94% Coverage)
- [x] Config-System (79% Coverage)
- [x] **Hardware-Detector** (USB/Netzwerk, 83% Coverage)
- [x] **Device-Klassen** (Printer, Scanner, MFP)
- [x] **Foomatic-Integration** (~10.000+ Drucker via OpenPrinting)
- [x] **Printer-Cache** (JSON-basiert, 97% Coverage)
- [x] **DriverInstaller** (Repository + Brother-Website, 67% Coverage)
- [x] **Brother-Scanner-Manager** (SANE/brscan4, 82% Coverage)
- [x] **OpenPrinting-First Strategie** (Automatische Multi-Hersteller-Unterstützung)
- [x] **CUPS-Helper** (Drucker registrieren, Status, Testdruck)
- [x] **SANE-Helper** (Scanner-Utilities, Auflistung, Test-Scan, Fähigkeiten, 92% Coverage)
- [x] **CLI-Interface** (funktionsfähig mit 9 Befehlen)
- [x] 197 Unit-Tests (80% Coverage)
- [x] CI/CD (GitHub Actions)
- [x] Logo & Branding
- [x] Umfassende Dokumentation

### 🚧 In Arbeit (Phase 5+)
- [ ] Backup/Restore-Funktion
- [ ] GTK-GUI
- [ ] PolicyKit-Integration
- [ ] Backup/Restore-Funktion

### 📅 Roadmap

**v1.0** (Erstes Release)
- Brother-Drucker & Scanner
- USB & Netzwerk
- GTK-GUI + CLI
- Backup/Restore
- .deb & Snap

**v1.1**
- Qt-GUI
- AppImage & Flatpak
- Weitere Distributionen (Fedora, Arch)

**v2.0**
- HP, Epson, Canon
- Drucker-Monitoring
- Firmware-Updates

Siehe **[IMPLEMENTIERUNGSPLAN.md](IMPLEMENTIERUNGSPLAN.md)** für Details.

---

## 📄 Lizenz

Tipels ist **freie Software**, lizenziert unter der **GNU General Public License v3.0**.

Siehe **[LICENSE](LICENSE)** für Details.

---

## 🙏 Danksagungen

- **Brother** - für Linux-Treiber-Unterstützung
- **CUPS** - Common Unix Printing System
- **SANE** - Scanner Access Now Easy
- **PyGObject** - Python-GTK-Bindings
- Alle zukünftigen Contributors und Tester

---

## 💬 Support

- 🐛 **Bug-Reports**: [GitHub Issues](https://github.com/nicolettas-muggelbude/Tipels/issues)
- 💬 **Diskussionen**: [GitHub Discussions](https://github.com/nicolettas-muggelbude/Tipels/discussions)
- 📖 **Dokumentation**: [docs/](docs/)

---

<p align="center">
  <img src="data/icons/tipels-icon.svg" alt="Tipels" width="64"/>
</p>

<p align="center">
  <strong>Gemacht mit ❤️ für die Linux-Community</strong><br>
  <em>🐾 Kleine Schritte. Große Wirkung. 🐾</em>
</p>
