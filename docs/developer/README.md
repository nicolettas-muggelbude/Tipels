# Tipels - Developer Documentation

Documentation for developers contributing to Tipels.

## Architecture Overview

Tipels follows a modular architecture:

```
tipels/
├── core/          # Core functionality (config, logging, detection)
├── drivers/       # Driver modules (manufacturer-specific)
├── gui/           # Graphical user interfaces (GTK, Qt)
├── cli/           # Command-line interface
├── daemon/        # D-Bus service for PolicyKit
└── utils/         # Helper functions (CUPS, SANE, network)
```

## Key Concepts

### Driver Plugins

Each manufacturer has its own driver module that implements the `DriverBase` interface.

**Example**: `src/tipels/drivers/brother/`

### Hardware Detection

Hardware detection is handled by `HardwareDetector` in `core/detector.py`.

### CUPS & SANE Integration

- **CUPS**: Managed via `utils/cups_helper.py`
- **SANE**: Managed via `utils/sane_helper.py`

## Development Guides

1. [Adding a New Manufacturer](adding-manufacturers.md)
2. [Writing Tests](testing.md)
3. [GUI Development](gui-development.md)
4. [PolicyKit Integration](policykit.md)
5. [Packaging](packaging.md)

## API Reference

<!-- TODO: Auto-generate API docs with Sphinx -->

## Code Style

- **Formatting**: Black (100 chars line length)
- **Linting**: Pylint
- **Type Hints**: Encouraged, checked with mypy
- **Docstrings**: Google-style

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/tipels

# Only unit tests
pytest tests/unit/

# Only integration tests
pytest tests/integration/
```

## Building Documentation

```bash
cd docs/
sphinx-build -b html . _build/
```

## Resources

- [CUPS Documentation](https://www.cups.org/doc/)
- [SANE Documentation](http://www.sane-project.org/docs.html)
- [PyGObject Documentation](https://pygobject.readthedocs.io/)
- [PolicyKit Documentation](https://www.freedesktop.org/software/polkit/docs/latest/)

---

**TODO**: Expand developer documentation with detailed guides
