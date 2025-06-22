# 🖱️ MouseControl_v2

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**Control your computer's mouse remotely from your phone with a beautiful, modern interface.**

MouseControl_v2 is a sleek PyQt6 application that turns your smartphone into a wireless mouse, keyboard, and trackpad. Simply start the server, connect your phone to the web interface, and control your computer remotely over WiFi.

## ✨ Features

### 🎮 Modern GUI Application
- **Dark theme** with glassmorphism design
- **System tray integration** - runs in background
- **Real-time logging** of all connections and actions
- **Built-in troubleshooting** guide and help system
- **One-click server** start/stop with status indicators

### 📱 Mobile-Optimized Interface
- **Touch-responsive trackpad** for smooth cursor control
- **Multi-touch gestures**:
  - Single tap for left click
  - Two-finger scroll (vertical)
  - Pinch to zoom (Ctrl + scroll)
- **Click buttons** for left/right click and scroll up/down
- **Full virtual keyboard** with:
  - QWERTY layout
  - Number row
  - Special keys (Tab, Esc, Enter, Backspace, etc.)
  - Keyboard shortcuts (Copy, Paste, Undo, Redo, Select All)
  - Arrow keys and navigation
- **Gesture indicators** showing current action
- **Auto-scrolling** when keyboard is displayed
- **Cross-platform** - works on any device with a web browser
- **No app installation** required on phone

### 🛡️ Enterprise Ready
- **Standalone executable** - no Python required for end users
- **Comprehensive help system** built into the GUI
- **Automatic IP detection** and connection guidance
- **Firewall configuration** assistance
- **Professional logging** with timestamps and clear formatting
- **Error handling** for network and input device issues

## 🚀 Quick Start

### For End Users (Windows Executable)
1. Download `MouseController.exe` from [Releases](../../releases)
2. Run the executable
3. Click "🚀 Start Server"
4. Open the displayed URL on your phone's browser
5. Control your mouse and keyboard remotely!

### For Developers
```bash
# Clone the repository
git clone https://github.com/YourUsername/MouseControl_v2.git
cd MouseControl_v2

# Install dependencies
pip install PyQt6 pynput

# Run the application
python mouse_server.py
```

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- Windows, macOS, or Linux
- WiFi network (both devices on same network)

### Install Dependencies
```bash
pip install PyQt6 pynput
```

### Optional: Build Executable (Windows)
```bash
pip install pyinstaller

# Build with icon and optimizations
pyinstaller --onefile --windowed --name="MouseController" --icon="mouse.ico" mouse_server.py
```

Your executable will be created in the `dist/` folder.

## 🎯 Use Cases

- **Presentations** - Control slides from anywhere in the room
- **Media Centers** - Navigate your HTPC from the couch
- **Accessibility** - Alternative input method for users with mobility challenges
- **Remote Work** - Control a computer from across the room
- **Gaming** - Use phone as a wireless mouse for casual gaming
- **Teaching** - Control computer while moving around classroom

## 🖥️ Interface Guide

### Desktop Application
1. **Control Tab**: Start/stop server, view connection info
2. **Logs Tab**: Monitor all connections and actions in real-time
3. **Help Tab**: Comprehensive troubleshooting and setup guides

### Mobile Web Interface
1. **Trackpad Area**: 
   - Move finger to control cursor
   - Tap for left click
   - Two fingers for scrolling
   - Pinch for zoom
2. **Control Buttons**: Quick access to clicks and scrolls
3. **Virtual Keyboard**: Full keyboard with special keys and shortcuts
4. **Status Bar**: Connection status and current time

## 🔧 Configuration

### Network Setup
1. Ensure both devices are on the same WiFi network
2. Set Windows network profile to "Private" (see Help tab)
3. Configure firewall if needed (automated guidance provided)

### Firewall Configuration
The application provides step-by-step firewall setup instructions, or use this quick command:
```cmd
netsh advfirewall firewall add rule name="Mouse Controller" dir=in action=allow protocol=TCP localport=3000
```

### Custom Port
To change the default port (3000), edit line in `mouse_server.py`:
```python
def __init__(self, port=3000):  # Change to desired port
```

## 🛠️ Technical Details

### Architecture
- **Frontend**: PyQt6 with dark theme and modern styling
- **Backend**: Python HTTP server with threading
- **Mobile Interface**: Responsive HTML5 with touch events
- **Mouse/Keyboard Control**: pynput library for cross-platform input simulation

### Mobile Interface Features
- **Responsive Design**: Adapts to any screen size
- **Touch Optimized**: All interactions designed for touch
- **Visual Feedback**: Gesture indicators and button animations
- **Smooth Scrolling**: Automatic scroll to keyboard when shown
- **No External Dependencies**: Pure HTML/CSS/JavaScript

### Performance
- **Latency**: <50ms on typical home networks
- **Mouse Movement**: 2x scaling for better control
- **Scroll Sensitivity**: Adjustable amount per gesture
- **Zoom Control**: Ctrl + scroll wheel simulation

## 🔍 Troubleshooting

The application includes a comprehensive help system. Common solutions:

### Can't Connect from Phone
1. Check both devices are on same WiFi (not guest network)
2. Disable Windows Firewall temporarily to test
3. Ensure server shows "Running" status
4. Try http://localhost:3000 on computer first

### Keyboard Not Showing
- Click "⌨️ Keyboard" button
- Keyboard will auto-scroll into view
- Use "❌ Hide Keyboard" to close

### Mouse Movement Issues
- Ensure pynput is installed: `pip install pynput`
- Check Windows security settings
- Try running as administrator

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Areas
- Add authentication/password protection
- Implement HTTPS support
- Add custom themes
- Improve gesture recognition
- Add gamepad/joystick mode

## 📋 Roadmap

- [ ] **Authentication** - Optional password protection
- [ ] **HTTPS Support** - Encrypted connections
- [ ] **Custom Themes** - Light theme and color customization
- [ ] **Advanced Gestures** - Three-finger gestures, swipe actions
- [ ] **Multi-Monitor** - Support for multiple displays
- [ ] **Macro Recording** - Record and playback mouse/keyboard actions
- [ ] **Mobile App** - Native iOS/Android applications
- [ ] **Bluetooth** - Direct Bluetooth connection option
- [ ] **Voice Commands** - Control via voice recognition

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt6** - For the excellent GUI framework
- **pynput** - For cross-platform input control
- **Open Source Community** - For inspiration and support

## 📞 Support

- **Documentation**: Check the built-in Help tab for comprehensive guides
- **Issues**: [GitHub Issues](../../issues) for bug reports and feature requests
- **Discussions**: [GitHub Discussions](../../discussions) for questions and community support

## ⚙️ Requirements

### Minimum System Requirements
- **OS**: Windows 7+, macOS 10.12+, or Linux with X11
- **Python**: 3.6 or higher (for running from source)
- **RAM**: 100MB free memory
- **Network**: WiFi or Ethernet connection

### Mobile Device Requirements
- **Browser**: Any modern browser (Chrome, Safari, Firefox)
- **OS**: iOS 10+, Android 5+, or any device with HTML5 support
- **Network**: Same network as computer

## 🎨 Customization

### Changing Colors
Edit the color scheme in `mouse_server.py`:
```python
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adjusting Touch Sensitivity
Modify movement scaling:
```python
self.move_mouse(dx * 2, dy * 2)  # Change multiplier
```

### Keyboard Layout
Add or modify keys in the HTML interface within `get_html_interface()` method.

## ⭐ Show Your Support

If this project helped you, please consider:
- Giving it a **star** ⭐
- **Sharing** it with others who might find it useful
- **Contributing** code, documentation, or bug reports
- **Sponsoring** development of new features

---

<div align="center">

**Made with ❤️ for the open source community**

[Report Bug](../../issues) · [Request Feature](../../issues) · [Join Discussion](../../discussions)

</div>