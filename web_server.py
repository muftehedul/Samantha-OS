#!/usr/bin/env python3
"""
Samantha Web Server - Flask API bridge for web interface
Connects browser-based UI with Samantha Core
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import sys

app = Flask(__name__, static_folder="web")


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


samantha_core = None


def init_samantha():
    global samantha_core
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    from samantha.core import SamanthaCore

    config_path = os.path.expanduser("~/.config/samantha/config.json")
    samantha_core = SamanthaCore(config_path)
    samantha_core.initialize()
    print("[Samantha] Core initialized for web server")


@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        response = samantha_core.process_text_input(message)
        return jsonify({"response": response})

    except Exception as e:
        print(f"[Error] {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def history():
    try:
        return jsonify({"history": samantha_core.conversation_history[-20:]})
    except:
        return jsonify({"history": []})


@app.route("/speak", methods=["POST", "OPTIONS"])
def speak():
    if request.method == "OPTIONS":
        return jsonify({})
    try:
        data = request.get_json()
        text = data.get("text", "")

        if text and samantha_core.voice_engine:
            # Run TTS in background thread to avoid blocking
            import threading

            def run_tts():
                try:
                    samantha_core.voice_engine.speak(text)
                except Exception as e:
                    print(f"[TTS Error] {e}")

            thread = threading.Thread(target=run_tts, daemon=True)
            thread.start()
            return jsonify({"status": "speaking", "voice": "Edge TTS JennyNeural"})

        return jsonify({"status": "no text"})

    except Exception as e:
        print(f"[Speak Error] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("   Samantha Web Interface")
    print("   Free Browser Speech Recognition")
    print("=" * 50)

    init_samantha()

    print("\n🌐 Open http://127.0.0.1:5000 in Chrome or Edge")
    print("🎤 Click the mic button to speak (FREE - uses browser STT)")
    print("🔊 Responses will be spoken using browser TTS (FREE)")
    print("\nPress Ctrl+C to stop\n")

    app.run(host="127.0.0.1", port=5000, debug=False)
