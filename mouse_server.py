#!/usr/bin/env python3
"""
Simple Mouse Controller Server
Allows you to control your computer's mouse from your phone via web browser.
"""

import socket
import json
import http.server
import socketserver
from pynput.mouse import Button
from pynput import mouse
import sys


class MouseControlHandler(http.server.BaseHTTPRequestHandler):
    # Create a single mouse controller instance
    mouse_controller = mouse.Controller()

    def do_GET(self):
        """Serve the HTML interface"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Serve the HTML interface
            html_content = self.get_html_interface()
            self.wfile.write(html_content.encode('utf-8'))
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
                # Scale the movement for better control
                self.move_mouse(dx * 2, dy * 2)

            elif action == 'click':
                button = command.get('button', 'left')
                self.click(button)

            elif action == 'scroll':
                direction = command.get('direction', 'up')
                self.scroll(direction)

            response = json.dumps({'status': 'ok'})
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            print(f"Error handling command: {e}")
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
        current_x, current_y = self.mouse_controller.position
        new_x = current_x + dx
        new_y = current_y + dy
        self.mouse_controller.position = (new_x, new_y)

    def click(self, button='left'):
        """Perform mouse click"""
        if button == 'left':
            self.mouse_controller.click(Button.left)
        elif button == 'right':
            self.mouse_controller.click(Button.right)
        elif button == 'middle':
            self.mouse_controller.click(Button.middle)

    def scroll(self, direction):
        """Scroll mouse wheel"""
        if direction == 'up':
            self.mouse_controller.scroll(0, 1)
        elif direction == 'down':
            self.mouse_controller.scroll(0, -1)

    def log_message(self, format, *args):
        """Override to reduce console spam"""
        pass

    def get_html_interface(self):
        """Return the HTML interface"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mouse Controller</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
            user-select: none;
        }

        .container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 10px;
        }

        .status {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: center;
            color: white;
            font-weight: bold;
        }

        .status.connected {
            background: rgba(76, 175, 80, 0.3);
        }

        .trackpad {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .trackpad::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 2px;
            height: 2px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            transform: translate(-50%, -50%);
        }

        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin-bottom: 10px;
        }

        .control-btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: none;
            border-radius: 10px;
            padding: 15px;
            color: white;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .control-btn:active {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0.95);
        }

        .scroll-controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .instructions {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 10px;
            color: white;
            font-size: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="status" class="status connected">Mouse Controller Ready</div>

        <div class="trackpad" id="trackpad">
            <div>Trackpad<br><small>Move your finger here</small></div>
        </div>

        <div class="controls">
            <button class="control-btn" onclick="sendClick('left')">Left Click</button>
            <button class="control-btn" onclick="sendClick('right')">Right Click</button>
            <button class="control-btn" onclick="sendClick('middle')">Middle Click</button>
        </div>

        <div class="scroll-controls">
            <button class="control-btn" onclick="sendScroll('up')">Scroll Up</button>
            <button class="control-btn" onclick="sendScroll('down')">Scroll Down</button>
        </div>

        <div class="instructions">
            Move your finger on the trackpad to control the mouse cursor
        </div>
    </div>

    <script>
        let lastTouchX = 0;
        let lastTouchY = 0;

        function sendCommand(command) {
            fetch(window.location.origin, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(command)
            }).catch(error => {
                console.error('Error:', error);
            });
        }

        function sendClick(button) {
            sendCommand({
                action: 'click',
                button: button
            });
        }

        function sendScroll(direction) {
            sendCommand({
                action: 'scroll',
                direction: direction
            });
        }

        // Touch/mouse events for trackpad
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

            sendCommand({
                action: 'move',
                dx: deltaX,
                dy: deltaY
            });

            lastTouchX = touch.clientX;
            lastTouchY = touch.clientY;
        });

        // Mouse events for desktop testing
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

            sendCommand({
                action: 'move',
                dx: deltaX,
                dy: deltaY
            });

            lastTouchX = e.clientX;
            lastTouchY = e.clientY;
        }

        // Prevent scrolling and zooming on mobile
        document.addEventListener('touchmove', function(e) {
            e.preventDefault();
        }, { passive: false });

        document.addEventListener('gesturestart', function(e) {
            e.preventDefault();
        });
    </script>
</body>
</html>'''


def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine our local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            # Fallback method
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "127.0.0.1"


def main():
    HOST = '0.0.0.0'  # Listen on all interfaces
    PORT = 3000

    try:
        # Create the server
        with socketserver.TCPServer((HOST, PORT), MouseControlHandler) as httpd:
            print("=" * 60)
            print("🖱️  MOUSE CONTROLLER SERVER STARTED")
            print("=" * 60)

            # Get and display connection information
            local_ip = get_local_ip()

            print(f"\n📱 CONNECT YOUR PHONE TO:")
            print(f"   http://{local_ip}:{PORT}")
            print(f"\n💻 TEST ON THIS COMPUTER:")
            print(f"   http://localhost:{PORT}")

            print(f"\n📋 INSTRUCTIONS:")
            print(f"   1. Make sure your phone and computer are on the same WiFi")
            print(f"   2. Open the URL above in your phone's web browser")
            print(f"   3. Use the trackpad area to move the mouse")
            print(f"   4. Use the buttons to click and scroll")

            print(f"\n🔧 TROUBLESHOOTING:")
            print(f"   If you can't connect:")
            print(f"   - Check your firewall settings")
            print(f"   - Make sure both devices are on the same WiFi network")
            print(f"   - Try the localhost URL on this computer first")

            print(f"\n⏹️  Press Ctrl+C to stop the server")
            print("=" * 60)

            # Start serving
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print("Try closing other applications or use a different port.")
        else:
            print(f"\n❌ Error starting server: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    # Check if pynput is installed
    try:
        import pynput
    except ImportError:
        print("❌ Error: pynput library not found!")
        print("Please install it with: pip install pynput")
        sys.exit(1)

    main()