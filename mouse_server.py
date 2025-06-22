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
                # Scale the movement for better control
                self.move_mouse(dx * 2, dy * 2)
            elif action == 'click':
                button = command.get('button', 'left')
                self.click(button)
                self.log(f"Click: {button} from {self.client_address[0]}")
            elif action == 'scroll':
                direction = command.get('direction', 'up')
                amount = command.get('amount', 1)
                self.scroll(direction, amount)
                self.log(f"Scroll: {direction} (x{amount}) from {self.client_address[0]}")
            elif action == 'key':
                key_type = command.get('key_type', 'char')
                key_value = command.get('key_value', '')
                self.send_key(key_type, key_value)
                self.log(f"Key: {key_type}={key_value} from {self.client_address[0]}")
            elif action == 'zoom':
                direction = command.get('direction', 'in')
                self.zoom(direction)
                self.log(f"Zoom: {direction} from {self.client_address[0]}")

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
            try:
                current_x, current_y = self.mouse_controller.position
                new_x = current_x + dx
                new_y = current_y + dy
                self.mouse_controller.position = (new_x, new_y)
            except Exception as e:
                self.log(f"Mouse move error: {e}")

    def click(self, button='left'):
        """Perform mouse click"""
        if self.mouse_controller:
            try:
                if button == 'left':
                    self.mouse_controller.click(Button.left)
                elif button == 'right':
                    self.mouse_controller.click(Button.right)
                elif button == 'middle':
                    self.mouse_controller.click(Button.middle)
            except Exception as e:
                self.log(f"Mouse click error: {e}")

    def scroll(self, direction, amount=1):
        """Scroll mouse wheel"""
        if self.mouse_controller:
            try:
                scroll_amount = amount * (1 if direction == 'up' else -1)
                self.mouse_controller.scroll(0, scroll_amount)
            except Exception as e:
                self.log(f"Mouse scroll error: {e}")

    def send_key(self, key_type, key_value):
        """Send keyboard input"""
        try:
            from pynput.keyboard import Key, Controller as KeyboardController
            keyboard = KeyboardController()

            if key_type == 'char':
                # Regular character
                keyboard.type(key_value)
            elif key_type == 'special':
                # Special keys
                key_map = {
                    'enter': Key.enter,
                    'backspace': Key.backspace,
                    'space': Key.space,
                    'tab': Key.tab,
                    'escape': Key.esc,
                    'shift': Key.shift,
                    'ctrl': Key.ctrl,
                    'alt': Key.alt,
                    'up': Key.up,
                    'down': Key.down,
                    'left': Key.left,
                    'right': Key.right,
                    'home': Key.home,
                    'end': Key.end,
                    'page_up': Key.page_up,
                    'page_down': Key.page_down,
                    'delete': Key.delete,
                    'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
                    'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
                    'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
                }

                if key_value in key_map:
                    keyboard.press(key_map[key_value])
                    keyboard.release(key_map[key_value])
            elif key_type == 'combo':
                # Key combinations like Ctrl+C
                keys = key_value.split('+')
                key_objects = []

                for key in keys:
                    if key.lower() == 'ctrl':
                        key_objects.append(Key.ctrl)
                    elif key.lower() == 'shift':
                        key_objects.append(Key.shift)
                    elif key.lower() == 'alt':
                        key_objects.append(Key.alt)
                    else:
                        key_objects.append(key.lower())

                # Press all keys
                for key in key_objects:
                    keyboard.press(key)

                # Release all keys in reverse order
                for key in reversed(key_objects):
                    keyboard.release(key)

        except Exception as e:
            self.log(f"Keyboard error: {e}")

    def zoom(self, direction):
        """Simulate zoom using Ctrl + scroll wheel"""
        if self.mouse_controller:
            try:
                from pynput.keyboard import Key, Controller as KeyboardController
                keyboard = KeyboardController()

                keyboard.press(Key.ctrl)
                if direction == 'in':
                    self.mouse_controller.scroll(0, 3)  # More scroll for zoom
                else:  # zoom out
                    self.mouse_controller.scroll(0, -3)
                keyboard.release(Key.ctrl)
            except Exception as e:
                self.log(f"Zoom error: {e}")  # Log zoom errors for debugging

    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass

    def get_html_interface(self):
        """Return the mobile-optimized HTML interface"""
        return '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>🖱️ Mouse Controller</title>
        <style>
            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh; 
                overflow: hidden; 
                touch-action: none;
            }
            .container { 
                height: 100vh; 
                display: flex; 
                flex-direction: column; 
                padding: 10px; 
                overflow-y: auto;
            }
            .header {
                background: rgba(255, 255, 255, 0.1); 
                backdrop-filter: blur(15px);
                border-radius: 12px; 
                padding: 12px; 
                margin-bottom: 10px;
                text-align: center; 
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            .trackpad {
                flex: 1; 
                background: rgba(255, 255, 255, 0.08); 
                backdrop-filter: blur(20px);
                border-radius: 16px; 
                margin-bottom: 10px; 
                display: flex;
                align-items: center; 
                justify-content: center; 
                color: rgba(255, 255, 255, 0.7);
                font-size: 16px; 
                text-align: center; 
                position: relative;
                border: 1px solid rgba(255, 255, 255, 0.15);
                cursor: none;
                min-height: 200px;
            }
            .trackpad-hint {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                pointer-events: none;
                font-size: 14px;
                opacity: 0.6;
            }
            .status-bar {
                background: rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 12px;
                text-align: center;
                font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            }
            .gesture-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 12px;
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: 1000;
            }
            .gesture-indicator.show {
                opacity: 1;
            }
            .controls {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr 1fr;
                gap: 10px;
                margin-bottom: 10px;
            }
            .control-btn {
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(20px);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 15px 8px;
                color: white;
                font-size: 14px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
                text-align: center;
                user-select: none;
            }
            .control-btn:active, .control-btn:hover {
                background: rgba(255, 255, 255, 0.4);
                transform: scale(0.95);
                border-color: rgba(255, 255, 255, 0.5);
            }
            .keyboard-toggle {
                background: rgba(100, 200, 255, 0.3);
                backdrop-filter: blur(20px);
                border: 2px solid rgba(100, 200, 255, 0.5);
                border-radius: 10px;
                padding: 15px;
                color: white;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
                margin-bottom: 50px;
                text-align: center;
                width: 100%;
                user-select: none;
            }
            .keyboard-toggle.keyboard-open {
                margin-bottom: 10px;
            }
            .keyboard-toggle:active, .keyboard-toggle:hover {
                background: rgba(100, 200, 255, 0.5);
                transform: scale(0.98);
                border-color: rgba(100, 200, 255, 0.7);
            }
            .keyboard {
                background: rgba(86, 87, 96, 0.45);
                backdrop-filter: blur(20px);
                border-radius: 12px;
                padding: 5px;
                margin-bottom: 5px;
                margin-top: 5px;
                margin-left: -5px;
                margin-right: -5px;
                display: none;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
            .keyboard.show {
                display: block;
            }
            .keyboard-row {
                display: flex;
                gap: 6px;
                margin-bottom: 8px;
                justify-content: center;
            }
            .key {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.1s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                min-width: 32px;
                height: 40px;
                padding: 0 8px;
                user-select: none;
            }
            .key:active, .key:hover {
                background: rgba(255, 255, 255, 0.4);
                transform: scale(0.95);
                border-color: rgba(255, 255, 255, 0.5);
            }
            .key.wide {
                flex: 2;
            }
            .key.extra-wide {
                flex: 3;
            }
            .special-keys {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 8px;
                margin-top: 10px;
            }
            .special-key {
                background: rgba(100, 150, 255, 0.3);
                border: 2px solid rgba(100, 150, 255, 0.5);
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.1s ease;
                padding: 10px 6px;
                text-align: center;
                user-select: none;
            }
            .special-key:active, .special-key:hover {
                background: rgba(100, 150, 255, 0.6);
                transform: scale(0.95);
                border-color: rgba(100, 150, 255, 0.7);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                🖱️ Mouse Controller
            </div>

            <div class="trackpad" id="trackpad">
                <div class="trackpad-hint">
                    Move • Tap • 2-Finger Scroll • Pinch Zoom
                </div>
            </div>

            <div class="controls">
                <button class="control-btn" onclick="sendClick('left')">👆 Left</button>
                <button class="control-btn" onclick="sendClick('right')">👆 Right</button>
                <button class="control-btn" onclick="sendScroll('up')">⬆️ Up</button>
                <button class="control-btn" onclick="sendScroll('down')">⬇️ Down</button>
            </div>

            <button class="keyboard-toggle" onclick="toggleKeyboard()">⌨️ Keyboard</button>

            <div class="keyboard" id="keyboard">
                <!-- Number row -->
                <div class="keyboard-row">
                    <div class="key" data-key="char" data-value="1">1</div>
                    <div class="key" data-key="char" data-value="2">2</div>
                    <div class="key" data-key="char" data-value="3">3</div>
                    <div class="key" data-key="char" data-value="4">4</div>
                    <div class="key" data-key="char" data-value="5">5</div>
                    <div class="key" data-key="char" data-value="6">6</div>
                    <div class="key" data-key="char" data-value="7">7</div>
                    <div class="key" data-key="char" data-value="8">8</div>
                    <div class="key" data-key="char" data-value="9">9</div>
                    <div class="key" data-key="char" data-value="0">0</div>
                </div>

                <!-- Top row -->
                <div class="keyboard-row">
                    <div class="key" data-key="char" data-value="q">Q</div>
                    <div class="key" data-key="char" data-value="w">W</div>
                    <div class="key" data-key="char" data-value="e">E</div>
                    <div class="key" data-key="char" data-value="r">R</div>
                    <div class="key" data-key="char" data-value="t">T</div>
                    <div class="key" data-key="char" data-value="y">Y</div>
                    <div class="key" data-key="char" data-value="u">U</div>
                    <div class="key" data-key="char" data-value="i">I</div>
                    <div class="key" data-key="char" data-value="o">O</div>
                    <div class="key" data-key="char" data-value="p">P</div>
                </div>

                <!-- Middle row -->
                <div class="keyboard-row">
                    <div class="key" data-key="char" data-value="a">A</div>
                    <div class="key" data-key="char" data-value="s">S</div>
                    <div class="key" data-key="char" data-value="d">D</div>
                    <div class="key" data-key="char" data-value="f">F</div>
                    <div class="key" data-key="char" data-value="g">G</div>
                    <div class="key" data-key="char" data-value="h">H</div>
                    <div class="key" data-key="char" data-value="j">J</div>
                    <div class="key" data-key="char" data-value="k">K</div>
                    <div class="key" data-key="char" data-value="l">L</div>
                </div>

                <!-- Bottom row -->
                <div class="keyboard-row">
                    <div class="key" data-key="char" data-value="z">Z</div>
                    <div class="key" data-key="char" data-value="x">X</div>
                    <div class="key" data-key="char" data-value="c">C</div>
                    <div class="key" data-key="char" data-value="v">V</div>
                    <div class="key" data-key="char" data-value="b">B</div>
                    <div class="key" data-key="char" data-value="n">N</div>
                    <div class="key" data-key="char" data-value="m">M</div>
                    <div class="key" data-key="special" data-value="backspace">⌫</div>
                </div>

                <!-- Space and Enter row -->
                <div class="keyboard-row">
                    <div class="key wide" data-key="special" data-value="shift">⇧ Shift</div>
                    <div class="key extra-wide" data-key="special" data-value="space">Space</div>
                    <div class="key wide" data-key="special" data-value="enter">↵ Enter</div>
                </div>

                <!-- Special keys -->
                <div class="special-keys">
                    <div class="special-key" data-key="special" data-value="tab">Tab</div>
                    <div class="special-key" data-key="special" data-value="escape">Esc</div>
                    <div class="special-key" data-key="combo" data-value="ctrl+c">Copy</div>
                    <div class="special-key" data-key="combo" data-value="ctrl+v">Paste</div>
                    <div class="special-key" data-key="special" data-value="up">↑</div>
                    <div class="special-key" data-key="special" data-value="down">↓</div>
                    <div class="special-key" data-key="special" data-value="left">←</div>
                    <div class="special-key" data-key="special" data-value="right">→</div>
                    <div class="special-key" data-key="combo" data-value="ctrl+z">Undo</div>
                    <div class="special-key" data-key="combo" data-value="ctrl+y">Redo</div>
                    <div class="special-key" data-key="combo" data-value="ctrl+a">All</div>
                    <div class="special-key" data-key="special" data-value="delete">Del</div>
                </div>
            </div>

            <div class="status-bar" id="status">
                Ready • Left/Right Click • Scroll • Keyboard Available
            </div>
        </div>

        <div class="gesture-indicator" id="gestureIndicator"></div>

        <script>
            // Global variables
            let lastTouchX = 0, lastTouchY = 0;
            let lastTouchTime = 0;
            let gestureStartDistance = 0;
            let isScrolling = false;
            let lastZoomDistance = 0;
            let isZooming = false;
            let keyboardVisible = false;

            // Get DOM elements
            const gestureIndicator = document.getElementById('gestureIndicator');
            const status = document.getElementById('status');
            const keyboard = document.getElementById('keyboard');
            const trackpad = document.getElementById('trackpad');

            // Core functions
            function showGesture(text) {
                gestureIndicator.textContent = text;
                gestureIndicator.classList.add('show');
                setTimeout(() => gestureIndicator.classList.remove('show'), 1000);
            }

            function sendCommand(command) {
                fetch(window.location.origin, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(command)
                }).catch(error => console.error('Error:', error));
            }

            function sendClick(button) {
                sendCommand({ action: 'click', button: button });
                showGesture(button === 'left' ? '👆 Left Click' : '👆 Right Click');
            }

            function sendScroll(direction) {
                sendCommand({ action: 'scroll', direction: direction, amount: 3 });
                showGesture(direction === 'up' ? '⬆️ Scroll Up' : '⬇️ Scroll Down');
            }

            function sendKey(type, value) {
                sendCommand({ action: 'key', key_type: type, key_value: value });
                let displayValue = value;
                if (type === 'combo') {
                    displayValue = value.replace('ctrl+', 'Ctrl+');
                } else if (type === 'special') {
                    displayValue = value.charAt(0).toUpperCase() + value.slice(1);
                }
                showGesture(`⌨️ ${displayValue}`);
            }

            function toggleKeyboard() {
                keyboardVisible = !keyboardVisible;
                keyboard.classList.toggle('show', keyboardVisible);
                const toggleBtn = document.querySelector('.keyboard-toggle');
                toggleBtn.classList.toggle('keyboard-open', keyboardVisible);
                toggleBtn.textContent = keyboardVisible ? '❌ Hide Keyboard' : '⌨️ Show Keyboard';
                
                // Auto-scroll to keyboard when shown
                if (keyboardVisible) {
                    setTimeout(() => {
                        const container = document.querySelector('.container');
                        container.scrollTop = container.scrollHeight;
                        /*keyboard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });*/
                    }, 50);  // Small delay to ensure keyboard is rendered
                }
            }

            function getDistance(touch1, touch2) {
                const dx = touch1.clientX - touch2.clientX;
                const dy = touch1.clientY - touch2.clientY;
                return Math.sqrt(dx * dx + dy * dy);
            }

            // Set up keyboard event listeners
            document.querySelectorAll('.key, .special-key').forEach(key => {
                key.addEventListener('click', function(e) {
                    e.preventDefault();
                    const keyType = this.getAttribute('data-key');
                    const keyValue = this.getAttribute('data-value');
                    sendKey(keyType, keyValue);
                });
            });

            // Trackpad touch events
            trackpad.addEventListener('touchstart', function(e) {
                e.preventDefault();
                const touches = e.touches;
                lastTouchTime = Date.now();

                if (touches.length === 1) {
                    lastTouchX = touches[0].clientX;
                    lastTouchY = touches[0].clientY;
                    isScrolling = false;
                    isZooming = false;
                } else if (touches.length === 2) {
                    lastTouchX = (touches[0].clientX + touches[1].clientX) / 2;
                    lastTouchY = (touches[0].clientY + touches[1].clientY) / 2;
                    gestureStartDistance = getDistance(touches[0], touches[1]);
                    lastZoomDistance = gestureStartDistance;
                    isScrolling = true;
                    isZooming = false;
                }
            });

            trackpad.addEventListener('touchmove', function(e) {
                e.preventDefault();
                const touches = e.touches;

                if (touches.length === 1 && !isScrolling && !isZooming) {
                    const deltaX = touches[0].clientX - lastTouchX;
                    const deltaY = touches[0].clientY - lastTouchY;

                    if (Math.abs(deltaX) > 1 || Math.abs(deltaY) > 1) {
                        sendCommand({
                            action: 'move',
                            dx: deltaX,
                            dy: deltaY
                        });

                        lastTouchX = touches[0].clientX;
                        lastTouchY = touches[0].clientY;
                    }
                } else if (touches.length === 2) {
                    const centerX = (touches[0].clientX + touches[1].clientX) / 2;
                    const centerY = (touches[0].clientY + touches[1].clientY) / 2;
                    const currentDistance = getDistance(touches[0], touches[1]);

                    const zoomThreshold = 30;
                    const distanceDiff = currentDistance - lastZoomDistance;

                    if (Math.abs(distanceDiff) > zoomThreshold) {
                        isZooming = true;
                        if (distanceDiff > 0) {
                            sendCommand({ action: 'zoom', direction: 'in' });
                            showGesture('🔍+ Zoom In');
                        } else {
                            sendCommand({ action: 'zoom', direction: 'out' });
                            showGesture('🔍- Zoom Out');
                        }
                        lastZoomDistance = currentDistance;
                        lastTouchY = centerY;
                    } else if (!isZooming) {
                        const deltaY = centerY - lastTouchY;
                        if (Math.abs(deltaY) > 8) {
                            const direction = deltaY < 0 ? 'up' : 'down';
                            const amount = Math.ceil(Math.abs(deltaY) / 15);
                            sendCommand({
                                action: 'scroll',
                                direction: direction,
                                amount: amount
                            });
                            lastTouchY = centerY;
                            showGesture(direction === 'up' ? '⬆️ Scroll' : '⬇️ Scroll');
                        }
                    }
                }
            });

            trackpad.addEventListener('touchend', function(e) {
                e.preventDefault();
                const touchDuration = Date.now() - lastTouchTime;

                if (touchDuration < 200 && e.changedTouches.length === 1 && e.touches.length === 0) {
                    const wasMoving = Math.abs(e.changedTouches[0].clientX - lastTouchX) > 10 || 
                                     Math.abs(e.changedTouches[0].clientY - lastTouchY) > 10;

                    if (!wasMoving && !isScrolling && !isZooming) {
                        sendCommand({ action: 'click', button: 'left' });
                        showGesture('👆 Left Click');
                    }
                }

                if (e.touches.length === 0) {
                    isScrolling = false;
                    isZooming = false;
                }
            });

            // Prevent default behaviors
            trackpad.addEventListener('contextmenu', e => e.preventDefault());
            document.addEventListener('gesturestart', e => e.preventDefault());
            document.addEventListener('gesturechange', e => e.preventDefault());
            document.addEventListener('gestureend', e => e.preventDefault());

            // Update status periodically
            setInterval(() => {
                status.textContent = `Connected • ${new Date().toLocaleTimeString()} • ${keyboardVisible ? 'Keyboard Active' : 'Ready'}`;
            }, 5000);
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