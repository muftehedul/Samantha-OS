#!/usr/bin/env python3
"""
Samantha Voice Engine - Soft, warm, natural voice
Inspired by Scarlett Johansson's portrayal in "Her" (2013)
"""

import os
import subprocess
import tempfile
import wave
from typing import Optional


class VoiceEngine:
    def __init__(self, config: dict):
        self.config = config
        self.stt_provider = config.get("stt_provider", "vosk")
        self.tts_provider = config.get("tts_provider", "espeak-natural")
        self.sample_rate = 16000
        self.channels = 1

        self.vosk_model = None
        self.vosk_recognizer = None
        self._init_vosk()

    def _init_vosk(self):
        if self.stt_provider == "vosk":
            try:
                from vosk import Model, KaldiRecognizer

                model_paths = [
                    "/opt/samantha/models/vosk-model-small-en-us-0.15",
                    os.path.expanduser(
                        "~/.samantha/models/vosk-model-small-en-us-0.15"
                    ),
                    "/opt/jarvis/models/vosk-model-small-en-us-0.15",
                ]

                model_path = None
                for path in model_paths:
                    if os.path.exists(path):
                        model_path = path
                        break

                if model_path:
                    self.vosk_model = Model(model_path)
                    self.vosk_recognizer = KaldiRecognizer(
                        self.vosk_model, self.sample_rate
                    )
                    print(f"[Samantha] Voice ready")
                else:
                    self._download_vosk_model()

            except ImportError:
                print("[Samantha] Install vosk: pip install vosk")

    def _download_vosk_model(self):
        import urllib.request
        import zipfile

        model_dir = os.path.expanduser("~/.samantha/models")
        os.makedirs(model_dir, exist_ok=True)

        model_url = (
            "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        )
        zip_path = os.path.join(model_dir, "vosk-model.zip")

        try:
            print("[Samantha] Downloading voice model...")
            urllib.request.urlretrieve(model_url, zip_path)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(model_dir)
            os.unlink(zip_path)

            from vosk import Model, KaldiRecognizer

            model_path = os.path.join(model_dir, "vosk-model-small-en-us-0.15")
            self.vosk_model = Model(model_path)
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
            print("[Samantha] Voice model ready")
        except Exception as e:
            print(f"[Samantha] Voice model error: {e}")

    def transcribe(self, audio_data: bytes) -> str:
        if self.stt_provider == "vosk" and self.vosk_recognizer:
            try:
                import json

                self.vosk_recognizer.AcceptWaveform(audio_data)
                result = json.loads(self.vosk_recognizer.FinalResult())
                return result.get("text", "")
            except Exception as e:
                print(f"[Samantha] Transcription error: {e}")
        return ""

    def speak(self, text: str):
        """Speak with Samantha's soft, warm voice"""
        if not text or not text.strip():
            return

        text = text.strip()

        # Try pyttsx3 first (better female voice)
        if self._speak_pyttsx3_female(text):
            return

        # Fallback to espeak with soft settings
        self._speak_espeak_soft(text)

    def _speak_pyttsx3_female(self, text: str) -> bool:
        """Speak with pyttsx3 female voice"""
        try:
            import pyttsx3

            engine = pyttsx3.init()

            # Slower, softer rate
            engine.setProperty("rate", 140)
            engine.setProperty("volume", 0.85)

            # Find female voice
            voices = engine.getProperty("voices")
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()

                # Look for female English voices
                if (
                    "female" in voice_name
                    or "woman" in voice_name
                    or "zira" in voice_id
                    or "samantha" in voice_name
                    or "karen" in voice_name
                    or "victoria" in voice_name
                ):
                    engine.setProperty("voice", voice.id)
                    break
                elif "english" in voice_name and "female" not in voice_name:
                    # Use any English voice as fallback
                    engine.setProperty("voice", voice.id)

            engine.say(text)
            engine.runAndWait()
            return True

        except Exception as e:
            print(f"[Samantha] Voice error: {e}")
            return False

    def _speak_espeak_soft(self, text: str):
        """Soft, warm espeak voice"""
        try:
            # Use Storm variant with slower, softer settings
            subprocess.run(
                [
                    "espeak-ng",
                    "-v",
                    "!v/Storm",  # Storm voice (warmer)
                    "-s",
                    "130",  # Slower = softer feel
                    "-p",
                    "55",  # Slightly higher pitch
                    "-a",
                    "120",  # Softer volume
                    "-k",
                    "10",  # Gentle emphasis
                    text,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
        except Exception:
            # Absolute fallback
            print(f"[Samantha] {text}")

    def listen(self, duration: float = 5.0) -> Optional[bytes]:
        """Listen for voice input"""
        try:
            import sounddevice as sd

            print(f"[Samantha] Listening... ({duration}s)")

            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
            )
            sd.wait()

            return recording.tobytes()

        except ImportError:
            # Fallback to arecord
            try:
                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    temp_path = f.name

                subprocess.run(
                    [
                        "arecord",
                        "-f",
                        "cd",
                        "-t",
                        "wav",
                        "-d",
                        str(int(duration)),
                        "-r",
                        str(self.sample_rate),
                        temp_path,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=duration + 5,
                )

                with open(temp_path, "rb") as f:
                    # Skip WAV header
                    f.read(44)
                    audio_data = f.read()

                os.unlink(temp_path)
                return audio_data

            except Exception as e:
                print(f"[Samantha] Listen error: {e}")
                return None
        except Exception as e:
            print(f"[Samantha] Listen error: {e}")
            return None

    def listen_continuous(self, callback):
        """Continuous listening mode"""
        try:
            import sounddevice as sd
            import json

            if not self.vosk_recognizer:
                return

            def audio_callback(indata, frames, time, status):
                audio_bytes = indata.tobytes()
                if self.vosk_recognizer.AcceptWaveform(audio_bytes):
                    result = json.loads(self.vosk_recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        callback(text)

            print("[Samantha] Continuous listening... (Ctrl+C to stop)")
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=audio_callback,
            ):
                import time

                while True:
                    time.sleep(0.1)

        except ImportError:
            print("[Samantha] Install sounddevice: pip install sounddevice")
        except KeyboardInterrupt:
            print("\n[Samantha] Stopped listening")
        except Exception as e:
            print(f"[Samantha] Listen error: {e}")
