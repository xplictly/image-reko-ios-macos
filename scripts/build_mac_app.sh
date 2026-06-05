#!/usr/bin/env bash
# Helper script to build WidgetWall as a macOS .app
# Usage: chmod +x scripts/build_mac_app.sh && ./scripts/build_mac_app.sh

set -euo pipefail

# Adjust PYTHON_CMD to your Python 3.11 executable if different
PYTHON_CMD=${PYTHON_CMD:-python3}
VENV_DIR=".venv-py311-build"

echo "Using Python: $(${PYTHON_CMD} --version 2>&1)"

# Create venv
if [ ! -d "$VENV_DIR" ]; then
  ${PYTHON_CMD} -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip setuptools wheel
# pin py2app to a known working release for Python 3.11
pip install py2app==0.28
# Use a currently available PyQt6 release — avoid a pinned version that may not exist on all Pythons
pip install PyQt6==6.10.2
# install runtime deps if you have requirements.txt
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Run py2app
python setup.py py2app -q

echo "Build finished. Check dist/WidgetWall.app"
