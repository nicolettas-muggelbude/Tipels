.PHONY: help install install-dev test lint format clean build

help:
	@echo "Tipels - Makefile Befehle:"
	@echo ""
	@echo "  make install      - Installiere Tipels"
	@echo "  make install-dev  - Installiere Development-Dependencies"
	@echo "  make test         - Führe Tests aus"
	@echo "  make lint         - Führe Linting aus"
	@echo "  make format       - Formatiere Code"
	@echo "  make clean        - Aufräumen"
	@echo "  make build        - Baue Pakete"

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ --cov=src/tipels --cov-report=html --cov-report=term

lint:
	pylint src/tipels
	mypy src/tipels --ignore-missing-imports

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

build:
	python -m build
