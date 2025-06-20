# 🖱️ MouseControl_v2

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**Control your computer's mouse remotely from your phone with a beautiful, modern interface.**

MouseControl_v2 is a sleek PyQt6 application that turns your smartphone into a wireless mouse and trackpad. Simply start the server, connect your phone to the web interface, and control your computer remotely over WiFi.

![MouseControl Demo](https://via.placeholder.com/800x400/667eea/ffffff?text=MouseControl+v2+Demo)

## ✨ Features

### 🎮 Modern GUI Application
- **Dark theme** with glassmorphism design
- **System tray integration** - runs in background
- **Real-time logging** of all connections and actions
- **Built-in troubleshooting** guide and help system
- **One-click server** start/stop with status indicators

### 📱 Mobile-Optimized Interface
- **Touch-responsive trackpad** for smooth cursor control
- **Click buttons** for left, right, and middle mouse clicks
- **Scroll controls** for wheel scrolling
- **Cross-platform** - works on any device with a web browser
- **No app installation** required on phone

### 🛡️ Enterprise Ready
- **Standalone executable** - no Python required for end users
- **Comprehensive help system** built into the GUI
- **Automatic IP detection** and connection guidance
- **Firewall configuration** assistance
- **Professional logging** and error handling

## 🚀 Quick Start

### For End Users (Executable)
1. Download `MouseController.exe` from [Releases](../../releases)
2. Run the executable
3. Click "🚀 Start Server"
4. Open the displayed URL on your phone
5. Control your mouse remotely!

### For Developers
```bash
# Clone the repository
git clone https://github.com/YourUsername/MouseControl_v2.git
cd MouseControl_v2

# Install dependencies
pip install -r requirements.txt

# Run the application
python mouse_controller_gui.py
```

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- Windows, macOS, or Linux
- WiFi network (both devices on same network)

### Install Dependencies
```bash
pip install PyQt6 pynput pyinstaller
```

### Build Executable (Windows)
```bash
# Use the included build script
build_executable.bat

# Or manually
pyinstaller --onefile --windowed --name="MouseController" mouse_controller_gui.py
```

Your executable will be created in the `dist/` folder.

## 🖼️ Screenshots

<table>
<tr>
<td>
<img src="https://via.placeholder.com/400x300/2c3e50/ffffff?text=Main+Control+Panel" alt="Control Panel" width="400"/>
<br><em>Main Control Panel</em>
</td>
<td>
<img src="https://via.placeholder.com/400x300/667eea/ffffff?text=Mobile+Interface" alt="Mobile Interface" width="400"/>
<br><em>Mobile Web Interface</em>
</td>
</tr>
<tr>
<td>
<img src="https://via.placeholder.com/400x300/27ae60/ffffff?text=Real-time+Logs" alt="Logs" width="400"/>
<br><em>Real-time Connection Logs</em>
</td>
<td>
<img src="https://via.placeholder.com/400x300/e74c3c/ffffff?text=Help+System" alt="Help" width="400"/>
<br><em>Built-in Help & Troubleshooting</em>
</td>
</tr>
</table>

## 🎯 Use Cases

- **Presentations** - Control slides from anywhere in the room
- **Media Centers** - Navigate your HTPC from the couch
- **Accessibility** - Alternative input method for users with mobility challenges
- **Remote Work** - Control a computer from across the room
- **Gaming** - Use phone as a wireless mouse for gaming setups

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
Edit the port in `mouse_controller_gui.py`:
```python
self.server_thread = ServerThread(port=3000)  # Change to desired port
```

## 🛠️ Technical Details

### Architecture
- **Frontend**: PyQt6 with dark theme and modern styling
- **Backend**: Python HTTP server with threading
- **Mobile Interface**: Responsive HTML5 with touch events
- **Mouse Control**: pynput library for cross-platform input simulation

### Protocol
- **Communication**: HTTP REST API over WiFi
- **Commands**: JSON-formatted mouse actions (move, click, scroll)
- **Security**: Local network only, no external connections

### Performance
- **Latency**: <50ms on typical home networks
- **Compatibility**: Works with any device that has a web browser
- **Resource Usage**: Minimal CPU and memory footprint

## 🔍 Troubleshooting

The application includes a comprehensive help system with solutions for:

- **Connection Issues**: Network configuration and firewall setup
- **Performance Problems**: WiFi optimization and interference
- **Compatibility**: Device-specific browser quirks
- **Security**: Safe usage guidelines and best practices

For additional help, check the [Issues](../../issues) page or the built-in Help tab.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/YourUsername/MouseControl_v2.git
cd MouseControl_v2
pip install -r requirements.txt
python mouse_controller_gui.py
```

### Coding Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for new functions
- Test on multiple platforms when possible

## 📋 Roadmap

- [ ] **Authentication** - Optional password protection
- [ ] **Keyboard Support** - Virtual keyboard interface
- [ ] **Multi-Monitor** - Support for multiple displays
- [ ] **Gestures** - Advanced touch gestures (pinch, swipe)
- [ ] **Themes** - Light theme and custom color schemes
- [ ] **Encryption** - HTTPS support for enhanced security
- [ ] **Mobile App** - Native iOS/Android applications
- [ ] **Bluetooth** - Direct Bluetooth connection option

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt6** - For the excellent GUI framework
- **pynput** - For cross-platform input control
- **Contributors** - Thanks to everyone who has contributed to this project

## 📞 Support

- **Documentation**: Check the built-in Help tab for comprehensive guides
- **Issues**: [GitHub Issues](../../issues) for bug reports and feature requests
- **Discussions**: [GitHub Discussions](../../discussions) for questions and community support

## ⭐ Show Your Support

If this project helped you, please consider:
- Giving it a **star** ⭐
- **Sharing** it with others
- **Contributing** to make it even better

---

<div align="center">

**Made with ❤️ for the open source community**

[Report Bug](../../issues) · [Request Feature](../../issues) · [Join Discussion](../../discussions)

</div>