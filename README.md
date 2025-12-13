# Tipels

<p align="center">
  <img src="data/icons/tipels-logo.svg" alt="Tipels Logo" width="200"/>
</p>

<p align="center">
  <strong>Einfache Einrichtung von Druckern und Scannern unter Linux</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#verwendung">Verwendung</a> •
  <a href="#dokumentation">Dokumentation</a> •
  <a href="#contributing">Mitmachen</a>
</p>

---

## Über Tipels

Tipels ist eine benutzerfreundliche Linux-Applikation, die das Einrichten von Druckern und Scannern vereinfacht. Schluss mit komplexen Terminal-Befehlen und Treibersuche - Tipels erledigt alles automatisch.

### Warum Tipels?

- **Plug & Play**: Hardware anschließen, Tipels starten, fertig!
- **Automatische Treiberinstallation**: Kein manuelles Herunterladen mehr
- **Netzwerk & USB**: Unterstützt beide Verbindungsarten
- **Backup & Restore**: Konfiguration sichern und wiederherstellen
- **Open Source**: Vollständig transparent und frei verfügbar

### Unterstützte Hersteller

**v1.0:**
- ✅ Brother (alle Modelle)

**Geplant (v2.0+):**
- 🔜 HP
- 🔜 Epson
- 🔜 Canon

---

## Features

### 🖨️ Drucker-Setup
- Automatische Erkennung von USB- und Netzwerk-Druckern
- Intelligente Treiberauswahl (Repository, Hersteller-Website, Open-Source)
- Automatische CUPS-Integration
- Testdruck nach Installation
- Toner-/Tintenstatus anzeigen

### 🖼️ Scanner-Setup
- Automatische Scanner-Erkennung
- SANE-Integration
- Automatisches Hinzufügen zu erforderlichen Benutzergruppen
- Testscan nach Installation

### 💾 Backup & Restore
- Konfiguration sichern (Drucker, Scanner, Treiber)
- Wiederherstellung auf gleichem oder neuem System
- Automatische Treiber-Nachinstallation

### 🎨 Benutzerfreundlich
- GTK-GUI für Desktop-Umgebungen (GNOME, Cinnamon, XFCE)
- CLI für Poweruser und Skripte
- Deutsch und Englisch
- Desktop-Benachrichtigungen
- Hilfreiche Fehlermeldungen

### 🔒 Sicherheit
- PolicyKit-Integration für sichere Berechtigungen (GUI)
- Granulare Rechte-Vergabe
- Kein unnötiger Root-Zugriff

---

## Installation

### Ubuntu / Debian / Linux Mint

#### Via .deb-Paket (empfohlen)
```bash
# Download der neuesten Version
wget https://github.com/[username]/Tipels/releases/download/v1.0.0/tipels_1.0.0_amd64.deb

# Installation
sudo dpkg -i tipels_1.0.0_amd64.deb
sudo apt-get install -f  # Falls Abhängigkeiten fehlen
```

#### Via Snap
```bash
sudo snap install tipels
```

### Aus dem Quellcode

```bash
# Repository klonen
git clone https://github.com/[username]/Tipels.git
cd Tipels

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Tipels installieren
pip install -e .

# Starten
tipels
```

---

## Verwendung

### GUI

```bash
# Tipels starten
tipels
```

Oder über das Anwendungsmenü: **System → Einstellungen → Tipels**

### CLI

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

## Dokumentation

- 📖 [Benutzer-Handbuch (Deutsch)](docs/user-manual/de/README.md)
- 📖 [User Manual (English)](docs/user-manual/en/README.md)
- 🔧 [Entwickler-Dokumentation](docs/developer/README.md)
- ❓ [Troubleshooting](docs/troubleshooting/README.md)
- 📝 [Changelog](CHANGELOG.md)

---

## Systemanforderungen

- **Betriebssystem**: Ubuntu 20.04+, Debian 11+, Linux Mint 20+
- **Python**: 3.10 oder höher
- **Desktop**: GTK-basierte Umgebung (GNOME, Cinnamon, XFCE, MATE)
- **Abhängigkeiten**: CUPS, SANE, Avahi (werden automatisch installiert)

---

## Contributing

Beiträge sind herzlich willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

### Wie kann ich helfen?

- 🐛 Bugs melden
- 💡 Feature-Ideen einreichen
- 📝 Dokumentation verbessern
- 🌍 Übersetzungen hinzufügen
- 💻 Code beitragen

### Entwicklung

```bash
# Repository klonen
git clone https://github.com/[username]/Tipels.git
cd Tipels

# Development-Dependencies installieren
pip install -r requirements-dev.txt

# Tests ausführen
pytest tests/

# Code-Formatierung
black src/ tests/

# Linting
pylint src/
```

---

## Lizenz

Tipels ist freie Software, lizenziert unter der **GNU General Public License v3.0**.

Siehe [LICENSE](LICENSE) für Details.

---

## Danksagungen

- **Brother** - für Linux-Treiber-Unterstützung
- **CUPS** - Common Unix Printing System
- **SANE** - Scanner Access Now Easy
- **PyGObject** - Python-GTK-Bindings
- Alle Contributors und Tester

---

## Support

- 🐛 **Bug-Reports**: [GitHub Issues](https://github.com/[username]/Tipels/issues)
- 💬 **Diskussionen**: [GitHub Discussions](https://github.com/[username]/Tipels/discussions)
- 📧 **E-Mail**: [support@tipels.org]

---

## Roadmap

### v1.0 (Aktuell)
- [x] Brother-Drucker & Scanner
- [x] USB & Netzwerk
- [x] GTK-GUI
- [x] CLI
- [x] Backup/Restore
- [x] .deb & Snap

### v1.1 (Geplant)
- [ ] Qt-GUI
- [ ] AppImage & Flatpak
- [ ] Weitere Distributionen (Fedora, Arch)

### v2.0 (Zukunft)
- [ ] HP-Geräte
- [ ] Epson-Geräte
- [ ] Canon-Geräte
- [ ] Drucker-Monitoring
- [ ] Firmware-Updates

---

<p align="center">
  Gemacht mit ❤️ für die Linux-Community
</p>
