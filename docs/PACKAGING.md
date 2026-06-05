Packaging WidgetWall as a macOS .app

Goal
- Produce a macOS .app bundle (standalone application) suitable for local distribution.

Why this extra step
- py2app + PyQt6 + modern Python versions sometimes have compatibility issues.
- In this project we saw py2app fail on Python 3.14. A reliable path is to build with Python 3.11.

What this doc provides
- A reproducible set of steps to build an .app locally using Python 3.11
- A helper shell script `scripts/build_mac_app.sh` that automates the steps (requires macOS, Xcode command line tools)

Prerequisites
- macOS machine (this repo targets macOS only)
- Xcode Command Line Tools installed (xcode-select --install)
- Homebrew (recommended) if you plan to install pyenv
- A Python 3.11 installation (recommended via pyenv)

Recommended approach (pyenv)
1. Install pyenv (if not present):
   brew update
   brew install pyenv

2. Install Python 3.11.x and create a venv:

```bash
# pick a 3.11.x version, for example 3.11.16
pyenv install 3.11.16
pyenv virtualenv 3.11.16 widgetwall-build-3.11
pyenv activate widgetwall-build-3.11
```

3. From the project root, create and activate a venv (if you prefer builtin venv):

```bash
python -m venv .venv-build
source .venv-build/bin/activate
```

4. Install build requirements:

```bash
pip install --upgrade pip setuptools wheel
pip install py2app==0.28
# Install PyQt6 pinned to a stable compatible version
pip install PyQt6==6.6.2
# Install other runtime deps
pip install -r requirements.txt
```

5. Ensure `setup.py` at project root is present and configured (the project has one already). You may need to adjust `OPTIONS`->`includes`/`packages` if your py2app warnings indicate missing modules.

6. Run the build (from project root):

```bash
python setup.py py2app -q
```

7. If the build succeeds, your `.app` will be in `dist/WidgetWall.app`.

Troubleshooting
- If py2app errors reference `importlib.resources._files` or similar internal changes, confirm you're on Python 3.11 or 3.10. py2app compatibility for Python 3.14 is not guaranteed.
- For PyQt6 resource data, py2app sometimes needs explicit includes for Qt plugins (platforms, imageformats). If the app crashes on launch due to missing Qt platform plugins, add a `packages` or `resources` stanza in `setup.py` and copy the plugin folders into the `resources` list.
- Consider using a macOS CI runner (GitHub Actions `macos-latest`) to run the same build steps in a reproducible environment.

Automation script
- See `scripts/build_mac_app.sh` in the repo root to automate venv creation and build steps. Edit the script if you use pyenv or system Python.

Notes
- This repository's `setup.py` is already present and configured for py2app. The prior packaging attempt failed when run under Python 3.14; building with Python 3.11 is the recommended fix.
- If you want, I can attempt the build inside this workspace if you allow creating a Python 3.11 environment here (I will run commands and report results). Otherwise, follow the steps above locally.

Contact me which option you prefer: (A) I attempt the build here now (I'll create a 3.11 venv and run py2app), or (B) you run the included script locally and report results. If you pick (A), allow me to proceed and I'll start the build attempt.
