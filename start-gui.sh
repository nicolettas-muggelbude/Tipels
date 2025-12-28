#!/bin/bash
# Tipels GUI Starter

cd "$(dirname "$0")"
PYTHONPATH=src python3 -m tipels.gui.gtk.main "$@"
