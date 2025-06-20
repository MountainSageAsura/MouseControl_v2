#!/usr/bin/env python3
"""
Mouse Controller GUI - Modern PyQt6 Application
Control your computer's mouse from your phone with a beautiful GUI interface
"""

import sys
import socket
import json
import http.server
import socketserver
import threading
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QFrame, QGridLayout,
    QSystemTrayIcon, QMenu, QMessageBox, QSplitter, QGroupBox, QScrollArea
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QAction

try:
    from pynput.mouse import Button
    from pynput import mouse

    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class MouseControlHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for mouse control commands"""
    mouse_controller = None
    log_callback = None

    @classmethod
    def set_mouse_controller(cls, controller):
        cls.mouse_controller = controller

    @classmethod
    def set_log_callback(cls, callback):
        cls.log_callback = callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def do_GET(self):
        """Serve the HTML interface"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            html_content = self.get_html_interface()
            self.wfile.write(html_content.encode('utf-8'))
            self.log(f"Served interface to {self.client_address[0]}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle mouse control commands"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command = json.loads(post_data.decode('utf-8'))

            action = command.get('action')

            if action == 'move':
                dx = command.get('dx', 0)
                dy = command.get('dy', 0)
                self.move_mouse(dx * 2, dy * 2)
            elif action == 'click':
                button = command.get('button', 'left')
                self.click(button)
                self.log(f"Click: {button} from {self.client_address[0]}")
            elif action == 'scroll':
                direction = command.get('direction', 'up')
                self.scroll(direction)
                self.log(f"Scroll: {direction} from {self.client_address[0]}")

            response = json.dumps({'status': 'ok'})
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            self.log(f"Error handling command: {e}")
            response = json.dumps({'status': 'error', 'message': str(e)})
            self.wfile.write(response.encode('utf-8'))

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def move_mouse(self, dx, dy):
        """Move mouse relative to current position"""
        if self.mouse_controller:
            current_x, current_y = self.mouse_controller.position
            new_x = current_x + dx
            new_y = current_y + dy
            self.mouse_controller.position = (new_x, new_y)

    def click(self, button='left'):
        """Perform mouse click"""
        if self.mouse_controller:
            if button == 'left':
                self.mouse_controller.click(Button.left)
            elif button == 'right':
                self.mouse_controller.click(Button.right)
            elif button == 'middle':
                self.mouse_controller.click(Button.middle)

    def scroll(self, direction):
        """Scroll mouse wheel"""
        if self.mouse_controller:
            if direction == 'up':
                self.mouse_controller.scroll(0, 1)
            elif direction == 'down':
                self.mouse_controller.scroll(0, -1)

    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass

    def get_html_interface(self):
        """Return the mobile-optimized HTML interface"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🖱️ Mouse Controller</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh; overflow: hidden; user-select: none;
        }
        .container { height: 100vh; display: flex; flex-direction: column; padding: 15px; }
        .header {
            background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(20px);
            border-radius: 15px; padding: 15px; margin-bottom: 15px;
            text-align: center; color: white;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { opacity: 0.8; font-size: 14px; }
        .trackpad {
            flex: 1; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px);
            border-radius: 20px; margin-bottom: 15px; display: flex;
            align-items: center; justify-content: center; color: white;
            font-size: 18px; text-align: center; position: relative;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }
        .trackpad::before {
            content: ''; position: absolute; top: 50%; left: 50%;
            width: 4px; height: 4px; background: rgba(255, 255, 255, 0.6);
            border-radius: 50%; transform: translate(-50%, -50%);
        }
        .controls {
            display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 12px;
        }
        .control-btn {
            background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(20px);
            border: none; border-radius: 12px; padding: 18px; color: white;
            font-size: 14px; font-weight: 600; cursor: pointer;
            transition: all 0.2s ease; border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .control-btn:active {
            background: rgba(255, 255, 255, 0.3); transform: scale(0.96);
        }
        .scroll-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖱️ Mouse Controller</h1>
            <p>Control your computer's mouse remotely</p>
        </div>

        <div class="trackpad" id="trackpad">
            <div>📱 Trackpad<br><small>Move your finger here</small></div>
        </div>

        <div class="controls">
            <button class="control-btn" onclick="sendClick('left')">👆 Left Click</button>
            <button class="control-btn" onclick="sendClick('right')">👆 Right Click</button>
            <button class="control-btn" onclick="sendClick('middle')">👆 Middle Click</button>
        </div>

        <div class="scroll-controls">
            <button class="control-btn" onclick="sendScroll('up')">⬆️ Scroll Up</button>
            <button class="control-btn" onclick="sendScroll('down')">⬇️ Scroll Down</button>
        </div>
    </div>

    <script>
        let lastTouchX = 0, lastTouchY = 0;
        function sendCommand(command) {
            fetch(window.location.origin, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(command)
            }).catch(error => console.error('Error:', error));
        }
        function sendClick(button) { sendCommand({ action: 'click', button: button }); }
        function sendScroll(direction) { sendCommand({ action: 'scroll', direction: direction }); }

        const trackpad = document.getElementById('trackpad');
        trackpad.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const touch = e.touches[0];
            lastTouchX = touch.clientX;
            lastTouchY = touch.clientY;
        });
        trackpad.addEventListener('touchmove', function(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const deltaX = touch.clientX - lastTouchX;
            const deltaY = touch.clientY - lastTouchY;
            sendCommand({ action: 'move', dx: deltaX, dy: deltaY });
            lastTouchX = touch.clientX;
            lastTouchY = touch.clientY;
        });
        trackpad.addEventListener('mousedown', function(e) {
            e.preventDefault();
            lastTouchX = e.clientX;
            lastTouchY = e.clientY;
            trackpad.addEventListener('mousemove', handleMouseMove);
        });
        trackpad.addEventListener('mouseup', function(e) {
            trackpad.removeEventListener('mousemove', handleMouseMove);
        });
        function handleMouseMove(e) {
            e.preventDefault();
            const deltaX = e.clientX - lastTouchX;
            const deltaY = e.clientY - lastTouchY;
            sendCommand({ action: 'move', dx: deltaX, dy: deltaY });
            lastTouchX = e.clientX;
            lastTouchY = e.clientY;
        }
        document.addEventListener('touchmove', function(e) { e.preventDefault(); }, { passive: false });
        document.addEventListener('gesturestart', function(e) { e.preventDefault(); });
    </script>
</body>
</html>'''


class ServerThread(QThread):
    """Thread to run the HTTP server"""
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, str)  # status, ip

    def __init__(self, port=3000):
        super().__init__()
        self.port = port
        self.httpd = None
        self.running = False

        if PYNPUT_AVAILABLE:
            MouseControlHandler.set_mouse_controller(mouse.Controller())
        MouseControlHandler.set_log_callback(self.emit_log)

    def emit_log(self, message):
        self.log_signal.emit(message)

    def get_local_ip(self):
        """Get the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def run(self):
        """Start the HTTP server"""
        try:
            self.httpd = socketserver.TCPServer(("0.0.0.0", self.port), MouseControlHandler)
            self.running = True

            local_ip = self.get_local_ip()
            self.emit_log(f"🚀 Server started on port {self.port}")
            self.emit_log(f"📱 Phone URL: http://{local_ip}:{self.port}")
            self.emit_log(f"💻 Local URL: http://localhost:{self.port}")
            self.status_signal.emit("running", local_ip)

            self.httpd.serve_forever()
        except Exception as e:
            self.emit_log(f"❌ Server error: {e}")
            self.status_signal.emit("error", "")
        finally:
            self.running = False
            self.status_signal.emit("stopped", "")

    def stop(self):
        """Stop the HTTP server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        self.running = False
        self.emit_log("🛑 Server stopped")


def create_icon(color, size=64):
    """Create a simple colored icon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, size - 8, size - 8)
    painter.end()

    return QIcon(pixmap)


class MouseControllerGUI(QMainWindow):
    """Main GUI application window"""

    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.server_running = False
        self.current_ip = ""

        self.init_ui()
        self.init_system_tray()

        # Check dependencies
        if not PYNPUT_AVAILABLE:
            self.log("⚠️ Warning: pynput not installed. Mouse control will not work.")
            self.log("Install with: pip install pynput")

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🖱️ Mouse Controller")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)

        # Set application icon
        self.setWindowIcon(create_icon("#667eea"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Main control tab
        self.create_main_tab()

        # Logs tab
        self.create_logs_tab()

        # Help tab
        self.create_help_tab()

        # Status bar
        self.statusBar().showMessage("Ready to start server")

    def create_main_tab(self):
        """Create the main control tab"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Header
        header = QGroupBox("🖱️ Mouse Controller Server")
        header_layout = QVBoxLayout(header)

        # Status display
        self.status_label = QLabel("Server Status: Stopped")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #e74c3c; padding: 10px;")
        header_layout.addWidget(self.status_label)

        self.ip_label = QLabel("IP Address: Not available")
        self.ip_label.setFont(QFont("Arial", 10))
        self.ip_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        header_layout.addWidget(self.ip_label)

        layout.addWidget(header)

        # Control buttons
        controls = QGroupBox("Controls")
        controls_layout = QHBoxLayout(controls)

        self.start_btn = QPushButton("🚀 Start Server")
        self.start_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.start_btn.clicked.connect(self.start_server)

        self.stop_btn = QPushButton("🛑 Stop Server")
        self.stop_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)

        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addStretch()

        layout.addWidget(controls)

        # Connection info
        info = QGroupBox("📱 Connection Information")
        info_layout = QVBoxLayout(info)

        self.connection_info = QLabel("""
<b>How to Connect:</b><br>
1. Make sure your phone and computer are on the same WiFi network<br>
2. Start the server using the button above<br>
3. Open the displayed URL in your phone's web browser<br>
4. Use the trackpad interface to control your mouse
        """)
        self.connection_info.setWordWrap(True)
        self.connection_info.setStyleSheet("padding: 15px; line-height: 1.4;")
        info_layout.addWidget(self.connection_info)

        layout.addWidget(info)
        layout.addStretch()

        self.tabs.addTab(main_widget, "🎮 Control")

    def create_logs_tab(self):
        """Create the logs tab"""
        logs_widget = QWidget()
        layout = QVBoxLayout(logs_widget)

        # Logs header
        header_layout = QHBoxLayout()
        logs_label = QLabel("📋 Server Logs")
        logs_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(logs_label)

        clear_btn = QPushButton("🗑️ Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        clear_btn.setMaximumWidth(120)
        header_layout.addWidget(clear_btn)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Logs text area
        self.logs_text = QTextEdit()
        self.logs_text.setFont(QFont("Consolas", 9))
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                padding: 10px;
            }
        """)
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)

        self.tabs.addTab(logs_widget, "📋 Logs")

    def create_help_tab(self):
        """Create the help tab"""
        help_widget = QWidget()
        layout = QVBoxLayout(help_widget)

        # Create scrollable area
        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        help_sections = [
            ("🚀 Quick Start", """
<b>1. Start the Server:</b> Click the "Start Server" button in the Control tab<br>
<b>2. Connect Your Phone:</b> Open the displayed URL in your phone's web browser<br>
<b>3. Control Mouse:</b> Use the trackpad area to move the cursor, tap buttons to click
            """),

            ("📱 Phone Setup", """
<b>Same WiFi Network:</b> Ensure both devices are connected to the same WiFi network<br>
<b>Disable Mobile Data:</b> Turn off mobile data to force WiFi usage<br>
<b>Try Different Browsers:</b> Chrome, Safari, Firefox all work<br>
<b>Bookmark the URL:</b> Save the connection URL for quick access
            """),

            ("🔧 Troubleshooting", """
<b>Can't Connect from Phone:</b><br>
• Check if both devices are on the same WiFi network (not guest network)<br>
• Disable Windows Firewall temporarily to test<br>
• Make sure the server is running (green status)<br>
• Try accessing http://localhost:3000 on this computer first<br><br>

<b>Windows Firewall Issues:</b><br>
• Press Win+R, type "firewall.cpl"<br>
• Click "Allow an app or feature through Windows Defender Firewall"<br>
• Add Python to the allowed apps list<br>
• Or temporarily disable Private network firewall<br><br>

<b>Network Profile Issues:</b><br>
• Go to Settings → Network & Internet → WiFi<br>
• Click your network name<br>
• Set Network profile to "Private"<br><br>

<b>Router Issues:</b><br>
• Some routers have "AP Isolation" or "Client Isolation" enabled<br>
• Log into your router and disable this feature<br>
• Make sure you're not on a guest network
            """),

            ("🛡️ Firewall Configuration", """
<b>Windows Defender Firewall:</b><br>
1. Press Win+R, type "wf.msc", press Enter<br>
2. Click "Inbound Rules" → "New Rule"<br>
3. Choose "Port" → "TCP" → "Specific local ports" → "3000"<br>
4. Choose "Allow the connection"<br>
5. Apply to all profiles (Domain, Private, Public)<br>
6. Name it "Mouse Controller"<br><br>

<b>Alternative - Allow Python:</b><br>
1. Press Win+R, type "firewall.cpl"<br>
2. Click "Allow an app or feature through Windows Defender Firewall"<br>
3. Click "Change Settings" → "Allow another app"<br>
4. Browse to python.exe (usually in AppData\\Local\\Programs\\Python)<br>
5. Check both "Private" and "Public" networks
            """),

            ("🌐 Network Diagnostics", """
<b>Check Your IP Address:</b><br>
• Open Command Prompt (cmd)<br>
• Type: ipconfig<br>
• Look for "Wireless LAN adapter Wi-Fi" section<br>
• Use the IPv4 Address shown<br><br>

<b>Test Server Locally:</b><br>
• Open http://localhost:3000 in your browser<br>
• If this doesn't work, the server has an issue<br>
• If it works, the problem is network/firewall related<br><br>

<b>Test from Another Computer:</b><br>
• Try connecting from another device on the same network<br>
• This helps isolate phone-specific issues
            """),

            ("📋 Requirements", """
<b>Software Requirements:</b><br>
• Python 3.6 or higher<br>
• PyQt6: pip install PyQt6<br>
• pynput: pip install pynput<br><br>

<b>Network Requirements:</b><br>
• WiFi network (both devices connected)<br>
• Windows network profile set to "Private"<br>
• Firewall configured to allow connections<br><br>

<b>Supported Devices:</b><br>
• Any device with a web browser<br>
• iOS Safari, Android Chrome, Desktop browsers<br>
• Works on tablets and phones
            """),

            ("⚙️ Advanced Settings", """
<b>Change Port:</b><br>
• Default port is 3000<br>
• If blocked, try 8080, 8000, or 5000<br>
• Edit the source code to change port<br><br>

<b>Security Notes:</b><br>
• Server allows anyone on your network to control your mouse<br>
• Only run on trusted networks<br>
• Stop the server when not in use<br><br>

<b>Performance Tips:</b><br>
• Close unnecessary applications for better responsiveness<br>
• Use 5GHz WiFi if available (faster than 2.4GHz)<br>
• Keep phone close to router for better signal
            """)
        ]

        for title, content in help_sections:
            group = QGroupBox(title)
            group_layout = QVBoxLayout(group)

            label = QLabel(content)
            label.setWordWrap(True)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setStyleSheet("padding: 10px; line-height: 1.4;")
            group_layout.addWidget(label)

            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        self.tabs.addTab(help_widget, "❓ Help")

    def init_system_tray(self):
        """Initialize system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(create_icon("#667eea", 32))

            tray_menu = QMenu()

            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            start_action = QAction("Start Server", self)
            start_action.triggered.connect(self.start_server)
            tray_menu.addAction(start_action)

            stop_action = QAction("Stop Server", self)
            stop_action.triggered.connect(self.stop_server)
            tray_menu.addAction(stop_action)

            tray_menu.addSeparator()

            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

            self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def start_server(self):
        """Start the mouse control server"""
        if not PYNPUT_AVAILABLE:
            QMessageBox.warning(self, "Missing Dependency",
                                "pynput library is not installed.\n\n"
                                "Please install it with: pip install pynput")
            return

        if self.server_thread and self.server_thread.isRunning():
            return

        self.server_thread = ServerThread(port=3000)
        self.server_thread.log_signal.connect(self.log)
        self.server_thread.status_signal.connect(self.update_server_status)
        self.server_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.server_running = True

    def stop_server(self):
        """Stop the mouse control server"""
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop()
            self.server_thread.wait()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.server_running = False

        self.status_label.setText("Server Status: Stopped")
        self.status_label.setStyleSheet("color: #e74c3c; padding: 10px;")
        self.ip_label.setText("IP Address: Not available")
        self.statusBar().showMessage("Server stopped")

    def update_server_status(self, status, ip):
        """Update server status display"""
        if status == "running":
            self.status_label.setText("Server Status: Running ✅")
            self.status_label.setStyleSheet("color: #27ae60; padding: 10px;")
            self.ip_label.setText(f"📱 Phone URL: http://{ip}:3000")
            self.statusBar().showMessage(f"Server running on {ip}:3000")
            self.current_ip = ip
        elif status == "error":
            self.status_label.setText("Server Status: Error ❌")
            self.status_label.setStyleSheet("color: #e74c3c; padding: 10px;")
            self.ip_label.setText("IP Address: Error occurred")
            self.statusBar().showMessage("Server error occurred")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        elif status == "stopped":
            self.status_label.setText("Server Status: Stopped")
            self.status_label.setStyleSheet("color: #e74c3c; padding: 10px;")
            self.ip_label.setText("IP Address: Not available")
            self.statusBar().showMessage("Server stopped")

    def log(self, message):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.logs_text.append(formatted_message)

        # Auto-scroll to bottom
        cursor = self.logs_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)

    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.clear()
        self.log("📋 Logs cleared")

    def closeEvent(self, event):
        """Handle window close event"""
        if self.server_running:
            reply = QMessageBox.question(
                self, 'Close Application',
                'Server is still running. Do you want to stop it and quit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.stop_server()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def quit_application(self):
        """Quit the application completely"""
        if self.server_running:
            self.stop_server()
        QApplication.quit()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray

    # Set application properties
    app.setApplicationName("Mouse Controller")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Mouse Controller")

    # Apply modern style
    app.setStyle('Fusion')

    # Dark theme palette
    from PyQt6.QtGui import QPalette
    from PyQt6.QtCore import Qt

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    # Create and show main window
    window = MouseControllerGUI()
    window.show()

    # Show welcome message
    window.log("🖱️ Mouse Controller GUI started")
    window.log("💡 Click 'Start Server' to begin")

    if not PYNPUT_AVAILABLE:
        QMessageBox.information(
            window, "Setup Required",
            "Welcome to Mouse Controller!\n\n"
            "To use this application, you need to install the pynput library:\n\n"
            "pip install pynput\n\n"
            "After installation, restart the application."
        )

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())