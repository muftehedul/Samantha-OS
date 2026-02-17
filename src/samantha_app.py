#!/usr/bin/env python3
"""
Samantha OS - AI Assistant inspired by "Her" (2013)
Usage:
    samantha         - Launch GUI
    samantha --cli   - CLI mode
    samantha -m "msg" - Single message
"""

import sys
import os
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Samantha OS - AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-m", "--message", type=str, help="Send a single message")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--voice", action="store_true", help="Voice input mode")
    parser.add_argument("--version", action="version", version="Samantha OS 1.0.0")

    args = parser.parse_args()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from samantha.core import SamanthaCore

    config_path = os.path.expanduser("~/.config/samantha/config.json")

    if args.message:
        return cli_single_message(args.message, config_path)
    elif args.cli:
        return cli_interactive(config_path)
    elif args.voice:
        return voice_mode(config_path)
    else:
        return gui_mode(config_path)


def gui_mode(config_path: str):
    """Launch GUI mode"""
    try:
        from PyQt5.QtWidgets import QApplication
        from samantha.gui.main_window import SamanthaWindow
        from samantha.core import SamanthaCore
        import threading

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        samantha = SamanthaCore(config_path)
        samantha.initialize()

        window = SamanthaWindow()

        def on_response(text):
            window.add_message(text, is_user=False)
            threading.Thread(target=samantha.speak, args=(text,), daemon=True).start()

        def on_status(status, state):
            window.set_state(state, status)

        samantha.set_callbacks(on_status, on_response)

        def send_message():
            text = window.input_field.toPlainText().strip()
            if text:
                window.add_message(text, is_user=True)
                window.input_field.clear()
                threading.Thread(
                    target=samantha.process_text_input, args=(text,), daemon=True
                ).start()

        def toggle_voice(checked):
            if checked:
                window.set_state("listening", "Listening...")
                window.voice_btn.setText("🎤 Listening...")

                # Start voice recording
                def listen_and_process():
                    audio = samantha.voice_engine.listen(duration=5)
                    if audio:
                        text = samantha.voice_engine.transcribe(audio)
                        if text:
                            window.add_message(text, is_user=True)
                            samantha.process_text_input(text)
                    window.voice_btn.setChecked(False)
                    window.voice_btn.setText("🎤  Hold to speak")
                    window.set_state("idle", "Online")

                threading.Thread(target=listen_and_process, daemon=True).start()

        window.send_btn.clicked.connect(send_message)
        window.voice_btn.clicked.connect(toggle_voice)

        return app.exec_()

    except ImportError as e:
        print(f"GUI not available: {e}")
        print("Install: pip install PyQt5")
        return cli_interactive(config_path)


def cli_single_message(message: str, config_path: str):
    """Send a single message"""
    from samantha.core import SamanthaCore

    samantha = SamanthaCore(config_path)
    samantha.initialize()

    print(f"\nYou: {message}")
    response = samantha.process_text_input(message)
    print(f"\nSamantha: {response}")

    return 0


def cli_interactive(config_path: str):
    """Interactive CLI mode"""
    from samantha.core import SamanthaCore

    samantha = SamanthaCore(config_path)
    samantha.initialize()

    print("\n" + "=" * 50)
    print("   Samantha OS - AI Assistant")
    print("   Inspired by the film 'Her' (2013)")
    print("=" * 50)
    print("\nType 'quit' to exit, 'voice' for voice input\n")

    # Greet the user
    greeting = samantha._greet()
    print(f"Samantha: {greeting}\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print(f"\nSamantha: {samantha.personality.get_farewell()}")
                break

            if user_input.lower() == "voice":
                print("\n[Samantha is listening...]")
                audio = samantha.voice_engine.listen(duration=5)
                if audio:
                    text = samantha.voice_engine.transcribe(audio)
                    if text:
                        print(f"You: {text}")
                        user_input = text
                    else:
                        print(
                            "Samantha: I couldn't quite hear that. Could you try again?"
                        )
                        continue
                else:
                    print("Samantha: Voice input isn't available right now.")
                    continue

            response = samantha.process_text_input(user_input)
            print(f"\nSamantha: {response}\n")

        except KeyboardInterrupt:
            print(f"\n\nSamantha: {samantha.personality.get_farewell()}")
            break
        except EOFError:
            break

    return 0


def voice_mode(config_path: str):
    """Continuous voice conversation mode"""
    from samantha.core import SamanthaCore

    samantha = SamanthaCore(config_path)
    samantha.initialize()

    print("\n" + "=" * 50)
    print("   Samantha Voice Mode")
    print("=" * 50)

    # Greet
    greeting = samantha._greet()
    print(f"\nSamantha: {greeting}")
    samantha.speak(greeting)

    def handle_speech(text):
        print(f"\nYou: {text}")
        response = samantha.process_text_input(text)
        print(f"Samantha: {response}")
        samantha.speak(response)

    print("\n[Speak naturally. Press Ctrl+C to stop]\n")

    try:
        samantha.voice_engine.listen_continuous(handle_speech)
    except KeyboardInterrupt:
        print(f"\n\nSamantha: {samantha.personality.get_farewell()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
