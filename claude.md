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
   - Ubuntu-Repositories (primär)
   - Brother-Website (automatischer Download)
   - Open-Source-Alternativen (brlaser, etc.)
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
- [ ] Detaillierter Implementierungsplan
- [ ] GitHub-Repository einrichten
- [ ] Prototyp (USB+Netzwerk, Drucker+Scanner)
- [ ] Treiberlogik
- [ ] CUPS/SANE-Integration
- [ ] GUI-Entwicklung (GTK)
- [ ] CLI-Interface
- [ ] PolicyKit-Integration
- [ ] Backup/Restore-Funktion
- [ ] Tests & CI/CD
- [ ] Dokumentation
  - [ ] Benutzer-Handbuch
  - [ ] Entwickler-Dokumentation
  - [ ] Troubleshooting-Guide

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
