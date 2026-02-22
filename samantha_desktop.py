#!/usr/bin/env python3
"""
Samantha OS - All-in-One Desktop App Launcher
Starts backend server and opens webview window
"""

import os
import sys
import subprocess
import time
import threading
import signal
import http.server
import socketserver
import webbrowser
from pathlib import Path

APP_DIR = Path(__file__).parent.absolute()
WEB_DIR = APP_DIR / "web"
PORT = 5000
PROXY_PORT = 8765

processes = []


def start_kilo_proxy():
    """Start the kilo proxy server"""
    proxy_path = APP_DIR / "kilo_proxy.py"
    if proxy_path.exists():
        proc = subprocess.Popen(
            [sys.executable, str(proxy_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(APP_DIR),
        )
        processes.append(proc)
        print("[Samantha] Starting Kilo proxy...")

        # Wait for proxy to be ready
        import urllib.request

        for i in range(15):
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{PROXY_PORT}/v1/models", timeout=1
                )
                print("[Samantha] Kilo proxy ready")
                return True
            except:
                time.sleep(1)
        print("[Samantha] Warning: Kilo proxy not responding")
    return False


def start_flask_server():
    """Start Flask server in background"""
    from flask import Flask, request, jsonify, send_from_directory

    app = Flask(__name__, static_folder=str(WEB_DIR))

    @app.after_request
    def add_cors_headers(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response

    @app.route("/")
    def index():
        return send_from_directory(str(WEB_DIR), "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(str(WEB_DIR), filename)

    @app.route("/chat", methods=["POST", "OPTIONS"])
    def chat():
        if request.method == "OPTIONS":
            return jsonify({})
        try:
            data = request.get_json()
            message = data.get("message", "")
            if not message:
                return jsonify({"error": "No message"}), 400

            response = samantha_core.process_text_input(message)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/history", methods=["GET"])
    def history():
        try:
            return jsonify({"history": samantha_core.conversation_history[-20:]})
        except:
            return jsonify({"history": []})

    # Initialize Samantha Core
    global samantha_core
    sys.path.insert(0, str(APP_DIR / "src"))
    from samantha.core import SamanthaCore

    config_path = Path.home() / ".config/samantha/config.json"
    samantha_core = SamanthaCore(str(config_path))
    samantha_core.initialize()

    print(f"[Samantha] Server running at http://127.0.0.1:{PORT}")

    from werkzeug.serving import make_server

    server = make_server("127.0.0.1", PORT, app, threaded=True)
    server.serve_forever()


def open_webview():
    """Open webview window using available backend"""
    url = f"http://127.0.0.1:{PORT}"

    # Try to use pywebview for native window
    try:
        import webview

        print("[Samantha] Opening native window...")
        window = webview.create_window(
            "Samantha OS", url, width=800, height=900, resizable=True
        )
        webview.start()
        return
    except ImportError:
        pass
    except Exception as e:
        print(f"[Samantha] Webview error: {e}")

    # Fallback: open in browser
    print("[Samantha] Opening in browser (install pywebview for native window)")
    webbrowser.open(url)


def cleanup(signum=None, frame=None):
    """Cleanup all processes"""
    print("\n[Samantha] Shutting down...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            try:
                proc.kill()
            except:
                pass
    sys.exit(0)


def main():
    print("=" * 50)
    print("   Samantha OS v2.0.0 - PWA Desktop App")
    print("   Free Browser Speech Recognition")
    print("=" * 50)
    print()

    # Setup signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Start Kilo proxy
    start_kilo_proxy()

    # Start Flask server in thread
    server_thread = threading.Thread(target=start_flask_server, daemon=True)
    server_thread.start()

    # Wait for server
    time.sleep(2)

    # Open webview window
    open_webview()

    # Keep running
    try:
        while server_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
