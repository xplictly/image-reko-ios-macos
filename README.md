# WidgetWall - Desktop Widgets for macOS

Premium desktop widgets for macOS 10.15 (Catalina) through macOS 15 (Sequoia/Tahoe) - completely **free**, no subscription required!

![WidgetWall Screenshot](screenshot.png)

## ✨ Features

### All Premium Features Included - Free!

- **13+ Customizable Widgets**
  - 🕐 **Clock** - Digital and analog clock with customizable styles
  - 📅 **Calendar** - Monthly view with date highlighting
  - 🌤️ **Weather** - Current conditions and 7-day forecast
  - 📝 **Notes** - Quick notes with rich text support
  - ✅ **To-Do** - Task management with priorities
  - 💻 **System Monitor** - CPU, RAM, and disk usage
  - 🔋 **Battery** - Detailed battery status and health
  - 🎵 **Music** - Music player controls
  - 🔢 **Calculator** - Scientific calculator
  - ⏱️ **Countdown** - Timer and countdown widget
  - 🖼️ **Photo Frame** - Slideshow from folder
  - 📌 **Pinterest** - Pinterest board integration
  - 💬 **Quotes** - Daily motivational quotes

### Advanced Features

- 🎨 **Multiple Themes** - Minimal Dark, Minimal Light, Midnight
- 👆 **Click-Through Mode** - Let clicks pass through widgets
- 📍 **Snap to Grid** - Precise widget positioning
- 🖥️ **Multi-Monitor Support** - Widgets on any screen
- 🔧 **Customizable Sizes** - Small, Medium, Large options
- 🎯 **Drag & Drop** - Easy widget repositioning
- ⚙️ **Global Settings** - Control all widgets at once
- 🔒 **Privacy First** - All data stored locally

## 📋 Requirements

- **macOS 10.15 (Catalina)** or later
- **macOS 15 (Sequoia/Tahoe)** fully supported
- Python 3.9+
- PyQt6

## 🚀 Installation

### Option 1: Run Directly (Recommended)

PyQt6 is pre-installed on macOS. Just run:

```bash
cd /Users/maanas/Project\ Files/widgetwall
python3 main.py
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/widgetwall.git
cd widgetwall

# Install PyQt6 using Homebrew (if not installed)
brew install pyqt6

# Or using pip3
pip3 install pyqt6

# Run the app
python3 main.py
```

### Option 3: Build as .app Bundle

```bash
# Install py2app
pip3 install py2app

# Build the app
python3 setup.py py2app

# The .app will be in dist/WidgetWall.app
```

## 📖 Usage

### Starting the App

1. Run `python main.py` from the widgetwall directory
2. Click the menu bar icon (📌) to access the menu
3. Select "Add Widget" to add widgets to your desktop

### Adding Widgets

1. Click the menu bar icon
2. Widget"
3. Navigate to "Add Select a widget type from the menu
4. The widget will appear on your desktop

### Customizing Widgets

**Right-click any widget** to access:
- Enable/Disable Click-Through Mode
- Widget Settings
- Size Options (Small/Medium/Large)
- Close Widget

### Global Settings

Access via menu bar icon:
- Change Theme
- Toggle Click-Through
- Snap to Grid Settings
- Show/Hide All Widgets

## 🎨 Themes

### Built-in Themes

1. **Minimal Dark** - Clean dark theme (default)
2. **Minimal Light** - Fresh light theme
3. **Midnight** - Deep blue-dark theme

### Custom Themes

Create custom themes by editing JSON files in `data/themes/custom/`.

## 🔧 Configuration

### Settings Location

All settings are stored in:
- `data/settings.json` - Main settings
- `data/themes/*.json` - Theme files
- `data/widget_positions.json` - Widget positions

### Command Line Options

```bash
python main.py --debug      # Enable debug mode
python main.py --reset      # Reset all settings
python main.py --theme dark # Force specific theme
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/intro) - GUI framework
- [WidgetWall](https://apps.apple.com/in/app/widgetwall/id1618466427) - Inspiration for this project
- [SF Symbols](https://developer.apple.com/sf-symbols/) - Beautiful Apple icons

## 📧 Support

For issues and feature requests, please open an issue on GitHub.

---

**Made with ❤️ for macOS users who want beautiful desktop widgets without subscription!**

