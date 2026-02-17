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
            # Don't speak here - let voice mode handle it separately
            # Text mode speaks via separate thread below

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
                        # Speak response for text input mode
                        samantha.speak(response)
                    except Exception as e:
                        print(f"[ERROR] Processing failed: {e}")
                        import traceback
                        traceback.print_exc()
                
                threading.Thread(target=process_in_thread, daemon=True).start()

        def toggle_voice(checked):
            if checked:
                window.signals.state_change.emit("listening", "Listening...")
                window.voice_label.setText("Listening...")
                window.transcription_label.setText("🎤 Speak...")
                window.transcription_label.show()

                def listen_and_process():
                    import sounddevice as sd
                    import numpy as np
                    import wave
                    import tempfile
                    import os
                    import time
                    import json
                    from vosk import KaldiRecognizer
                    
                    try:
                        sample_rate = 16000
                        
                        # Use Vosk for real-time transcription display
                        recognizer = None
                        if samantha.voice_engine.vosk_model:
                            recognizer = KaldiRecognizer(samantha.voice_engine.vosk_model, sample_rate)
                            recognizer.SetWords(True)
                        
                        all_audio = []
                        start_time = time.time()
                        last_speech_time = None
                        speech_detected = False
                        full_partial = ""
                        
                        window.signals.transcription_update.emit("🎤 Listening...")
                        
                        # Smoother audio capture with smaller chunks
                        chunk_size = 2000  # Smaller chunks for smoother display
                        
                        def audio_callback(indata, frames, time_info, status):
                            nonlocal all_audio, speech_detected, last_speech_time, full_partial
                            audio_array = indata.flatten()
                            all_audio.append(audio_array.copy())
                            
                            # Check audio level for speech detection (lower threshold)
                            level = np.abs(audio_array).mean()
                            if level > 200:  # Lower threshold for better detection
                                speech_detected = True
                                last_speech_time = time.time()
                            
                            # Real-time partial transcription
                            if recognizer:
                                data = bytes(indata)
                                if recognizer.AcceptWaveform(data):
                                    result = json.loads(recognizer.Result())
                                    if result.get("text"):
                                        full_partial = result["text"]
                                else:
                                    partial = json.loads(recognizer.PartialResult())
                                    if partial.get("partial"):
                                        display = full_partial + " " + partial["partial"] if full_partial else partial["partial"]
                                        full_partial = display
                        
                        # Record with callback
                        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16',
                                          callback=audio_callback, device=None,
                                          blocksize=chunk_size, latency='low'):
                            
                            last_update = time.time()
                            
                            while (time.time() - start_time) < 30:
                                if not window.voice_btn.isChecked():
                                    break
                                
                                # Show live transcription smoothly
                                if time.time() - last_update > 0.15:  # Update every 150ms
                                    if full_partial.strip():
                                        window.signals.transcription_update.emit(f'🎤 "{full_partial.strip()}"')
                                    elif speech_detected:
                                        window.signals.transcription_update.emit("🎤 Processing speech...")
                                    else:
                                        window.signals.transcription_update.emit("🎤 Listening...")
                                    last_update = time.time()
                                
                                # Stop after 3 seconds of silence
                                if speech_detected and last_speech_time:
                                    silence_duration = time.time() - last_speech_time
                                    if silence_duration > 3:
                                        window.signals.transcription_update.emit("⏳ Processing...")
                                        break
                                
                                time.sleep(0.03)  # Smoother polling
                        
                        if not speech_detected:
                            window.signals.transcription_update.emit("❌ No speech detected.")
                        else:
                            # Combine all audio
                            audio_data = np.concatenate(all_audio)
                            
                            # Trim silence from beginning and end
                            audio_abs = np.abs(audio_data)
                            threshold = 200
                            non_silent = np.where(audio_abs > threshold)[0]
                            if len(non_silent) > 0:
                                start_idx = max(0, non_silent[0] - 1600)  # Keep 0.1s before
                                end_idx = min(len(audio_data), non_silent[-1] + 1600)  # Keep 0.1s after
                                audio_data = audio_data[start_idx:end_idx]
                            
                            # Save to temp file
                            temp_wav = tempfile.mktemp(suffix='.wav')
                            with wave.open(temp_wav, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(sample_rate)
                                wf.writeframes(audio_data.tobytes())
                            
                            # Transcribe using Whisper
                            text = ""
                            if samantha.voice_engine.whisper_model:
                                segments, info = samantha.voice_engine.whisper_model.transcribe(
                                    temp_wav, 
                                    language='en',
                                    beam_size=5,  # Better accuracy
                                    vad_filter=True,  # Voice activity detection
                                    vad_parameters=dict(min_silence_duration_ms=500)
                                )
                                text = ''.join([segment.text for segment in segments]).strip()
                            
                            os.unlink(temp_wav)
                            
                            if text and len(text.strip()) > 0:
                                window.signals.transcription_update.emit(f'✓ "{text}"')
                                window.signals.message_add.emit(text, True)
                                
                                # Get response
                                window.signals.state_change.emit("thinking", "Thinking...")
                                response = samantha.process_text_input(text)
                                window.signals.message_add.emit(response, False)
                                
                                # Speak response and listen again
                                def speak_and_listen():
                                    samantha.speak(response)
                                    time.sleep(0.3)
                                    if window.voice_btn.isChecked():
                                        window.signals.state_change.emit("listening", "Listening...")
                                        window.signals.transcription_update.emit("🎤 Listening...")
                                
                                threading.Thread(target=speak_and_listen, daemon=True).start()
                            else:
                                window.signals.transcription_update.emit("❌ Could not understand.")
                                time.sleep(0.3)
                                if window.voice_btn.isChecked():
                                    window.signals.transcription_update.emit("🎤 Listening...")
                                
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        window.signals.transcription_update.emit(f"Error: {str(e)}")
                    
                    window.signals.voice_finished.emit()
                    window.signals.state_change.emit("idle", "Online")

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
