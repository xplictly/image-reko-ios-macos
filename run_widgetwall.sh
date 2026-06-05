#!/bin/zsh
# WidgetWall Quick Launch Script

cd /Users/maanas/Project\ Files/widgetwall

# Clear any cached files
rm -rf __pycache__ 2>/dev/null
rm -rf app/__pycache__ 2>/dev/null
rm -rf app/*/__pycache__ 2>/dev/null

# Run the app with the correct Python
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 main.py

echo ""
echo "WidgetWall closed."

