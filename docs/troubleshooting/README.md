# Tipels - Troubleshooting Guide

Lösungen für häufige Probleme mit Tipels.

## Allgemeine Probleme

### Tipels startet nicht

**Symptom**: Fehler beim Starten von Tipels

**Lösungen**:
1. Prüfe die Python-Version: `python3 --version` (mindestens 3.10)
2. Installiere GTK-Abhängigkeiten:
   ```bash
   sudo apt install python3-gi gir1.2-gtk-3.0
   ```
3. Prüfe die Logs: `~/.local/share/tipels/logs/tipels.log`

### Keine Geräte gefunden

**Symptom**: Hardware-Scan findet keine Drucker/Scanner

**Lösungen**:
1. **USB**: Prüfe ob Gerät angeschlossen ist: `lsusb`
2. **Netzwerk**: Prüfe Netzwerk-Verbindung: `ping <drucker-ip>`
3. Installiere Avahi: `sudo apt install avahi-daemon avahi-utils`
4. Starte Avahi neu: `sudo systemctl restart avahi-daemon`

## Drucker-Probleme

### Treiber-Installation schlägt fehl

**Symptom**: Fehler bei Treiber-Installation

**Lösungen**:
1. Prüfe Internet-Verbindung
2. Prüfe verfügbaren Speicherplatz: `df -h`
3. Aktualisiere Paketlisten: `sudo apt update`
4. Prüfe manuelle Installation:
   ```bash
   sudo apt install brother-lpr-drivers-common
   ```

### Testdruck funktioniert nicht

**Symptom**: Testdruck wird nicht gedruckt

**Lösungen**:
1. Prüfe CUPS-Status:
   ```bash
   systemctl status cups
   lpstat -t
   ```
2. Prüfe Druckerwarteschlange: `lpq`
3. Öffne CUPS-Webinterface: `http://localhost:631`
4. Teste direkt mit CUPS:
   ```bash
   lp -d <drucker-name> /usr/share/cups/data/testprint
   ```

### Netzwerk-Drucker nicht erreichbar

**Symptom**: Drucker im Netzwerk wird nicht gefunden/erreicht

**Lösungen**:
1. Prüfe Firewall-Regeln:
   ```bash
   sudo ufw status
   ```
2. Erlaube CUPS-Ports:
   ```bash
   sudo ufw allow 631/tcp
   sudo ufw allow 5353/udp  # mDNS
   ```
3. Prüfe IP-Adresse des Druckers (im Drucker-Menü)
4. Teste Verbindung: `ping <drucker-ip>`

## Scanner-Probleme

### Scanner nicht gefunden

**Symptom**: Scanner wird nicht erkannt

**Lösungen**:
1. Installiere SANE: `sudo apt install sane sane-utils`
2. Teste Scanner-Erkennung:
   ```bash
   scanimage -L
   ```
3. Prüfe Benutzergruppen:
   ```bash
   groups
   # Sollte enthalten: lp, scanner, saned
   ```
4. Füge Benutzer zu Gruppen hinzu:
   ```bash
   sudo usermod -aG lp,scanner,saned $USER
   # Abmelden und neu anmelden!
   ```

### Scan-Berechtigung verweigert

**Symptom**: "Permission denied" bei Scanner-Zugriff

**Lösungen**:
1. Prüfe Berechtigungen:
   ```bash
   ls -l /dev/bus/usb/
   ```
2. Erstelle udev-Regel für Brother-Scanner:
   ```bash
   sudo nano /etc/udev/rules.d/60-brother-scanner.rules
   ```
   Inhalt:
   ```
   ATTRS{idVendor}=="04f9", MODE="0666", GROUP="scanner"
   ```
3. Lade udev-Regeln neu:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

## PolicyKit-Probleme

### Authentifizierung schlägt fehl

**Symptom**: PolicyKit-Dialog erscheint nicht oder schlägt fehl

**Lösungen**:
1. Prüfe PolicyKit-Installation:
   ```bash
   systemctl status polkit
   ```
2. Prüfe Tipels-Policy:
   ```bash
   pkaction --verbose | grep tipels
   ```
3. Installiere PolicyKit-Regeln neu:
   ```bash
   sudo cp data/org.tipels.policy /usr/share/polkit-1/actions/
   ```

## Backup/Restore-Probleme

### Backup schlägt fehl

**Symptom**: Backup kann nicht erstellt werden

**Lösungen**:
1. Prüfe Schreibrechte im Zielverzeichnis
2. Prüfe verfügbaren Speicherplatz: `df -h`
3. Erstelle Backup-Verzeichnis manuell:
   ```bash
   mkdir -p ~/tipels-backups
   ```

### Restore schlägt fehl

**Symptom**: Backup kann nicht wiederhergestellt werden

**Lösungen**:
1. Prüfe Backup-Datei: `cat backup.tipels-backup | jq`
2. Prüfe Tipels-Version im Backup
3. Installiere fehlende Treiber manuell

## Log-Analyse

### Logs finden

```bash
# Benutzer-Logs
cat ~/.local/share/tipels/logs/tipels.log

# System-Logs
journalctl -u tipels

# CUPS-Logs
cat /var/log/cups/error_log
```

### Debug-Modus aktivieren

```bash
# In config.json
nano ~/.config/tipels/tipels.conf
# Setze: "debug_mode": true
```

## Weitere Hilfe

Wenn diese Lösungen nicht helfen:

1. **GitHub Issues**: [https://github.com/[username]/Tipels/issues](https://github.com/[username]/Tipels/issues)
2. **Diskussionen**: [https://github.com/[username]/Tipels/discussions](https://github.com/[username]/Tipels/discussions)
3. **Log-Datei anhängen**: `~/.local/share/tipels/logs/tipels.log`

---

**Tipp**: Aktiviere den Debug-Modus für detailliertere Logs!
