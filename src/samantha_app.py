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
                
                def process_in_thread():
                    try:
                        response = samantha.process_text_input(text)
                        print(f"[DEBUG] Got response: {response[:100]}...")
                    except Exception as e:
                        print(f"[ERROR] Processing failed: {e}")
                        import traceback
                        traceback.print_exc()
                
                threading.Thread(target=process_in_thread, daemon=True).start()

        def toggle_voice(checked):
            if checked:
                window.set_state("listening", "Listening...")
                window.voice_label.setText("Listening...")
                window.transcription_label.setText("")
                window.transcription_label.show()

                # Start voice recording with real-time transcription
                def listen_and_process():
                    import json
                    from vosk import KaldiRecognizer
                    
                    recognizer = KaldiRecognizer(samantha.voice_engine.vosk_model, 16000)
                    recognizer.SetWords(True)
                    
                    try:
                        import sounddevice as sd
                        import queue
                        
                        q = queue.Queue()
                        
                        def audio_callback(indata, frames, time, status):
                            q.put(bytes(indata))
                        
                        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                             channels=1, callback=audio_callback):
                            
                            full_text = ""
                            import time
                            start_time = time.time()
                            
                            while window.voice_btn.isChecked() and (time.time() - start_time) < 10:
                                try:
                                    data = q.get(timeout=0.1)
                                    if recognizer.AcceptWaveform(data):
                                        result = json.loads(recognizer.Result())
                                        if result.get("text"):
                                            full_text = result["text"]
                                            window.transcription_label.setText(full_text)
                                    else:
                                        partial = json.loads(recognizer.PartialResult())
                                        if partial.get("partial"):
                                            display_text = full_text + " " + partial["partial"] if full_text else partial["partial"]
                                            window.transcription_label.setText(display_text)
                                except queue.Empty:
                                    continue
                            
                            # Final result
                            final_result = json.loads(recognizer.FinalResult())
                            if final_result.get("text"):
                                full_text = final_result["text"]
                        
                        if full_text:
                            window.transcription_label.setText(f'"{full_text}"')
                            window.add_message(full_text, is_user=True)
                            samantha.process_text_input(full_text)
                        else:
                            window.transcription_label.setText("No speech detected")
                            
                    except Exception as e:
                        window.transcription_label.setText(f"Error: {str(e)}")
                    
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(2000, window.transcription_label.hide)
                    window.voice_btn.setChecked(False)
                    window.voice_label.setText("Hold to speak")
                    window.set_state("idle", "Online")

                threading.Thread(target=listen_and_process, daemon=True).start()

        window.send_btn.clicked.connect(send_message)
        window.voice_btn.clicked.connect(toggle_voice)
        
        window.show()

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
