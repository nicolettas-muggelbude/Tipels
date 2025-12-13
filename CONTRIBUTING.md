# Contributing zu Tipels

Vielen Dank für dein Interesse, zu Tipels beizutragen! 🎉

## Code of Conduct

Sei freundlich, respektvoll und konstruktiv. Wir wollen eine einladende Community für alle schaffen.

## Wie kann ich beitragen?

### Bug-Reports

Bugs werden als [GitHub Issues](https://github.com/[username]/Tipels/issues) getrackt.

**Guter Bug-Report:**
- **Titel**: Kurz und beschreibend
- **Beschreibung**: Was ist passiert? Was wurde erwartet?
- **Schritte zum Reproduzieren**: 1, 2, 3...
- **System-Info**: OS, Tipels-Version, Python-Version
- **Logs**: Falls vorhanden, Log-Ausgabe anhängen

### Feature-Requests

Feature-Requests sind willkommen! Bitte erkläre:
- **Warum** das Feature nützlich wäre
- **Wie** es funktionieren sollte
- **Wer** davon profitieren würde

### Pull Requests

1. **Fork** das Repository
2. **Erstelle** einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. **Committe** deine Änderungen (`git commit -m 'Add amazing feature'`)
4. **Pushe** zum Branch (`git push origin feature/amazing-feature`)
5. **Öffne** einen Pull Request

**Pull Request Guidelines:**
- Schreibe aussagekräftige Commit-Messages
- Füge Tests hinzu für neue Features
- Aktualisiere die Dokumentation
- Stelle sicher, dass alle Tests bestehen
- Folge dem Code-Style (Black, Pylint)

## Entwicklungsumgebung einrichten

```bash
# Repository klonen
git clone https://github.com/[username]/Tipels.git
cd Tipels

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Development-Dependencies installieren
pip install -r requirements-dev.txt

# Tipels im Development-Modus installieren
pip install -e .
```

## Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=src/tipels --cov-report=html

# Nur Unit-Tests
pytest tests/unit/

# Nur Integration-Tests
pytest tests/integration/
```

## Code-Style

Wir verwenden:
- **Black** für Code-Formatierung
- **isort** für Import-Sortierung
- **Pylint** für Linting
- **mypy** für Type-Checking

```bash
# Code formatieren
black src/ tests/
isort src/ tests/

# Linting
pylint src/

# Type-Checking
mypy src/
```

## Commit-Messages

Folge dem [Conventional Commits](https://www.conventionalcommits.org/) Format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bug-Fix
- `docs`: Dokumentation
- `style`: Code-Style (Formatierung, etc.)
- `refactor`: Code-Refactoring
- `test`: Tests hinzufügen/ändern
- `chore`: Build-Prozess, Dependencies, etc.

**Beispiele:**
```
feat(brother): Add MFC-L2700DN support
fix(gui): Fix crash on network scan
docs(readme): Update installation instructions
```

## Neue Hersteller hinzufügen

Um Unterstützung für einen neuen Hersteller hinzuzufügen:

1. Erstelle `src/tipels/drivers/<manufacturer>/`
2. Implementiere `DriverBase` aus `src/tipels/drivers/base.py`
3. Füge Tests in `tests/unit/test_<manufacturer>.py` hinzu
4. Aktualisiere die Dokumentation

Siehe [Developer-Dokumentation](docs/developer/adding-manufacturers.md) für Details.

## Fragen?

- **Diskussionen**: [GitHub Discussions](https://github.com/[username]/Tipels/discussions)
- **Issues**: [GitHub Issues](https://github.com/[username]/Tipels/issues)

Danke für deine Unterstützung! 🚀
