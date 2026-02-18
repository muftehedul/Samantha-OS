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
            # Use signal for thread-safe GUI update
            window.signals.message_add.emit(text, False)
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
                        # Response is already added via callback
                        # Speak response for text input mode
                        samantha.speak(response)
                    except Exception as e:
                        print(f"[ERROR] Processing failed: {e}")
                        import traceback
                        traceback.print_exc()
                
                threading.Thread(target=process_in_thread, daemon=True).start()

        continuous_mode = {"active": False}

        def toggle_voice(checked):
            if checked:
                continuous_mode["active"] = True
                window.voice_label.setText("Tap to stop")
                start_continuous_conversation()
            else:
                continuous_mode["active"] = False
                window.signals.state_change.emit("idle", "Online")
                window.voice_label.setText("Hold to speak")
                window.transcription_label.hide()

        def start_continuous_conversation():
            def conversation_loop():
                while continuous_mode["active"] and window.voice_btn.isChecked():
                    listen_and_process()
                    if not continuous_mode["active"]:
                        break
            
            threading.Thread(target=conversation_loop, daemon=True).start()

        def listen_and_process():
            if not continuous_mode["active"]:
                return
            
            import sounddevice as sd
            import numpy as np
            import wave
            import tempfile
            import os
            import time
            import json
            from vosk import KaldiRecognizer
            
            try:
                # Safety check for audio device
                try:
                    sd.query_devices()
                except Exception as e:
                    print(f"[Samantha] Audio device error: {e}")
                    window.signals.message.emit("samantha", "I'm having trouble with the microphone. Let's use text instead.")
                    continuous_mode["active"] = False
                    window.voice_btn.setChecked(False)
                    return
                # Use 48kHz native rate for best quality
                sample_rate = 48000
                target_rate = 16000  # Whisper expects 16kHz
                
                # Skip Vosk real-time (causes crashes) - only use Whisper at end
                recognizer = None
                
                all_audio = []
                start_time = time.time()
                last_speech_time = None
                speech_detected = False
                silence_threshold = 0.001  # Lower threshold for faster detection
                
                # Show UI immediately
                window.signals.state_change.emit("listening", "Listening...")
                window.signals.transcription_update.emit("🎤 Speak now...")
                window.transcription_label.show()
                
                # Smaller chunks for responsive visualization
                chunk_size = 1024
                
                def audio_callback(indata, frames, time_info, status):
                    try:
                        nonlocal all_audio, speech_detected, last_speech_time, silence_threshold
                        
                        if not continuous_mode["active"]:
                            raise sd.CallbackStop()
                        
                        if status:
                            print(f"[Samantha] Audio status: {status}")
                        
                        # Handle stereo/mono
                        audio_array = indata[:, 0] if indata.ndim > 1 else indata.flatten()
                        all_audio.append(audio_array.copy())
                        
                        # Calculate RMS with proper scaling
                        rms = np.sqrt(np.mean(audio_array**2))
                        
                        # Faster adaptive threshold
                        if len(all_audio) < 5:  # First 5 chunks only
                            silence_threshold = max(silence_threshold, rms * 1.2)
                        
                        # More sensitive noise gate
                        if rms < silence_threshold * 0.8:
                            vis_level = 0.0
                        else:
                            clean_rms = max(0, rms - silence_threshold * 0.5)
                            vis_level = min(1.0, clean_rms * 80)
                        
                        window.pulse_widget.set_audio_level(vis_level)
                        
                        # Update volume indicator
                        if speech_detected:
                            window.update_volume_indicator(vis_level)
                        
                        # Faster speech detection with silence tracking
                        if rms > silence_threshold * 1.1:  # More sensitive
                            if not speech_detected:
                                speech_detected = True
                            last_speech_time = time.time()  # Update only when speaking
                        # If below threshold and we've detected speech, don't update last_speech_time
                        # This allows the silence timer to work
                        
                        # Real-time transcription with Vosk
                        if recognizer and speech_detected:
                            try:
                                # Downsample 48kHz -> 16kHz (every 3rd sample)
                                downsampled = audio_array[::3]
                                audio_int16 = (downsampled * 32767).astype(np.int16).tobytes()
                                
                                if recognizer.AcceptWaveform(audio_int16):
                                    result = json.loads(recognizer.Result())
                                    if result.get("text"):
                                        window.signals.transcription_update.emit(f'🎤 "{result["text"]}"')
                                else:
                                    partial = json.loads(recognizer.PartialResult())
                                    if partial.get("partial"):
                                        window.signals.transcription_update.emit(f'🎤 "{partial["partial"]}"')
                            except Exception as vosk_err:
                                print(f"[Samantha] Vosk error: {vosk_err}")
                                # Continue without crashing
                    except Exception as e:
                        print(f"[Samantha] Audio callback error: {e}")
                        # Don't crash, just continue
                
                # Start recording
                with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32',
                                  callback=audio_callback, device=None, blocksize=chunk_size):
                    
                    while (time.time() - start_time) < 30:
                        if not continuous_mode["active"]:
                            break
                        
                        # Auto-stop after 1.2 seconds of silence
                        if speech_detected and last_speech_time:
                            if (time.time() - last_speech_time) > 1.2:
                                window.signals.transcription_update.emit("⏳ Processing...")
                                break
                        
                        time.sleep(0.02)
                
                # Reset visualization
                window.pulse_widget.set_audio_level(0)
                window.volume_indicator.hide()
                
                if not speech_detected:
                    window.signals.transcription_update.emit("❌ No speech detected")
                    time.sleep(1)
                    return
                
                # === PROFESSIONAL AUDIO PROCESSING ===
                
                # 1. Combine audio
                audio_data = np.concatenate(all_audio)
                
                # 2. Gentle high-pass filter (remove only very low frequencies)
                from scipy import signal as sp_signal
                sos = sp_signal.butter(3, 60, 'hp', fs=sample_rate, output='sos')
                audio_data = sp_signal.sosfilt(sos, audio_data)
                
                # 3. Simple trimming - less aggressive
                win_size = 480
                hop_size = 240
                rms_values = []
                for i in range(0, len(audio_data) - win_size, hop_size):
                    win = audio_data[i:i+win_size]
                    rms_values.append(np.sqrt(np.mean(win**2)))
                
                rms_values = np.array(rms_values)
                
                # Less aggressive trimming
                if len(rms_values) > 0:
                    noise_floor = np.percentile(rms_values, 5)
                    speech_threshold = noise_floor * 2.5
                    
                    speech_mask = rms_values > speech_threshold
                    
                    if np.any(speech_mask):
                        first_speech = np.argmax(speech_mask) * hop_size
                        last_speech = (len(speech_mask) - np.argmax(speech_mask[::-1]) - 1) * hop_size
                        
                        # Generous padding
                        start_idx = max(0, first_speech - 4800)
                        end_idx = min(len(audio_data), last_speech + 9600)
                        audio_data = audio_data[start_idx:end_idx]
                
                # 4. Normalize to 0.85
                max_val = np.abs(audio_data).max()
                if max_val > 0:
                    audio_data = audio_data / max_val * 0.85
                
                # 5. Resample to 16kHz
                from scipy.signal import resample_poly
                audio_16k = resample_poly(audio_data, target_rate, sample_rate)
                
                # 6. Convert to int16
                audio_16k = np.clip(audio_16k * 32767, -32768, 32767).astype(np.int16)
                
                # 7. Save to WAV
                temp_wav = tempfile.mktemp(suffix='.wav')
                with wave.open(temp_wav, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(target_rate)
                    wf.writeframes(audio_16k.tobytes())
                
                # 8. Transcribe with balanced Whisper settings
                text = ""
                if samantha.voice_engine.whisper_model:
                    segments, info = samantha.voice_engine.whisper_model.transcribe(
                        temp_wav,
                        language='en',
                        beam_size=5,
                        best_of=5,
                        temperature=0.0,
                        compression_ratio_threshold=2.4,
                        log_prob_threshold=-1.0,
                        no_speech_threshold=0.5,
                        condition_on_previous_text=False,
                        vad_filter=True,
                        vad_parameters=dict(
                            threshold=0.5,
                            min_speech_duration_ms=250,
                            min_silence_duration_ms=500,
                            speech_pad_ms=400
                        )
                    )
                    text = ''.join([seg.text for seg in segments]).strip()
                
                os.unlink(temp_wav)
                
                if text:
                    window.signals.transcription_update.emit(f'✓ "{text}"')
                    window.signals.message_add.emit(text, True)
                    
                    # Check test accuracy if in test mode
                    if window.test_mode_active:
                        window.check_test_accuracy(text)
                        time.sleep(2)
                        return  # Don't process response in test mode
                    
                    window.signals.state_change.emit("thinking", "Thinking...")
                    response = samantha.process_text_input(text)
                    window.signals.message_add.emit(response, False)
                    
                    window.signals.state_change.emit("speaking", "Speaking...")
                    samantha.speak(response)
                    time.sleep(0.5)
                else:
                    window.signals.transcription_update.emit("❌ Could not understand")
                    time.sleep(1)
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                window.signals.transcription_update.emit(f"Error: {str(e)}")
                time.sleep(2)

        window.send_btn.clicked.connect(send_message)
        window.input_field.send_callback = send_message  # Connect Enter key
        window.voice_btn.clicked.connect(toggle_voice)
        
        # Disable test mode for normal use
        # window.next_test_btn.clicked.connect(window.show_next_test)
        # window.start_test_mode()
        
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
