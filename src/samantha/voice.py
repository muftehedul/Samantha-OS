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
        self.stt_provider = config.get("stt_provider", "whisper")  # Default to whisper
        self.tts_provider = config.get("tts_provider", "spd-say")
        self.sample_rate = 16000
        self.channels = 1

        self.whisper_model = None
        self.vosk_model = None
        self.vosk_recognizer = None
        self._audio_device = None
        self._detect_audio_device()
        self._init_whisper()  # For accurate final transcription
        self._init_vosk()     # For real-time partial display

    def _detect_audio_device(self):
        """Detect the best audio input device"""
        try:
            import sounddevice as sd
            # Try to find a working device with input channels
            devices = sd.query_devices()
            # Prefer default device which handles channel conversion
            default_dev = sd.query_devices(kind='input')
            if default_dev and default_dev['max_input_channels'] > 0:
                print(f"[Samantha] Using default audio device: {default_dev['name']}")
                self._audio_device = None  # Use default
                return
            # Fallback: find pulse or alsa_input
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    if 'pulse' in dev['name'].lower() or 'alsa_input' in dev['name'].lower():
                        self._audio_device = i
                        print(f"[Samantha] Using audio device {i}: {dev['name']}")
                        return
            self._audio_device = None  # Use system default
        except Exception as e:
            print(f"[Samantha] Audio device detection: {e}")
            self._audio_device = None

    def _init_whisper(self):
        """Initialize Whisper model for speech recognition"""
        try:
            from faster_whisper import WhisperModel
            print("[Samantha] Loading Whisper model...")
            # Use tiny model for fast real-time transcription
            self.whisper_model = WhisperModel('tiny', device='cpu', compute_type='int8')
            print("[Samantha] Voice ready (Whisper)")
        except ImportError:
            print("[Samantha] faster-whisper not found, falling back to Vosk")
            self._init_vosk()
        except Exception as e:
            print(f"[Samantha] Whisper init error: {e}, falling back to Vosk")
            self._init_vosk()

    def _init_vosk(self):
        if self.stt_provider == "vosk":
            try:
                from vosk import Model, KaldiRecognizer

                model_paths = [
                    "/opt/samantha/models",
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
                    print(f"[Samantha] Vosk ready (for real-time display)")
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

    def transcribe_audio_file(self, audio_path: str) -> str:
        """Transcribe audio file using Whisper (more accurate)"""
        if self.whisper_model:
            try:
                segments, info = self.whisper_model.transcribe(audio_path, language='en')
                text = ''.join([segment.text for segment in segments])
                return text.strip()
            except Exception as e:
                print(f"[Samantha] Whisper transcription error: {e}")
        return ""

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
        """Speak with Samantha's soft, warm female voice using Edge TTS"""
        if not text or not text.strip():
            return

        text = text.strip()
        print(f"[Samantha] Speaking: {text[:50]}...")
        
        # Only use Edge TTS (most natural voice)
        self._speak_edge_tts(text)

    def _speak_spd_say(self, text: str):
        """Speak using speech-dispatcher spd-say with female voice"""
        try:
            subprocess.run(
                [
                    "spd-say",
                    "-t", "female1",      # Female voice type
                    "-r", "-10",          # Slightly slower rate
                    "-p", "30",           # Higher pitch for female
                    "-w",                 # Wait until done
                    text,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60,
            )
            print("[Samantha] Speech completed")
        except Exception as e:
            print(f"[Samantha] spd-say error: {e}")
            # Fallback to pyttsx3
            self._speak_pyttsx3_female(text)

    def _speak_edge_tts(self, text: str):
        """Speak using Edge TTS - natural sounding voice"""
        import tempfile
        import os
        
        temp_mp3 = tempfile.mktemp(suffix='.mp3')
        
        try:
            # Generate speech with JennyNeural (friendly female voice)
            subprocess.run(
                ["edge-tts", "--voice", "en-US-JennyNeural", "--text", text, "--write-media", temp_mp3],
                capture_output=True,
                timeout=30
            )
            
            # Play with pygame
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(temp_mp3)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
            
            print("[Samantha] Speech completed")
            
        except Exception as e:
            print(f"[Samantha] Edge TTS error: {e}")
        finally:
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)

    def _speak_pyttsx3_female(self, text: str) -> bool:
        """Speak with pyttsx3 female voice - warm and soft like Her movie"""
        try:
            import pyttsx3

            engine = pyttsx3.init()

            # Warm, conversational rate (like Samantha in Her)
            engine.setProperty("rate", 145)  # Natural speed
            engine.setProperty("volume", 1.0)

            # Find best female voice
            voices = engine.getProperty("voices")
            female_voice = None
            
            # Priority order for voice selection
            for voice in voices:
                voice_name = voice.name.lower() if voice.name else ""
                voice_id = voice.id.lower() if voice.id else ""

                # First choice: English America (most natural)
                if "english (america)" in voice_name or voice_id == "gmw/en-us":
                    female_voice = voice.id
                    print(f"[Samantha] Selected voice: {voice.name}")
                    break
                    
                # Second choice: Great Britain English
                if "english (great britain)" in voice_name or voice_id == "gmw/en":
                    if female_voice is None:
                        female_voice = voice.id
                        print(f"[Samantha] Selected voice: {voice.name}")

            if female_voice is None:
                # Fallback: find any English voice
                for voice in voices:
                    voice_name = voice.name.lower() if voice.name else ""
                    voice_id = voice.id.lower() if voice.id else ""
                    if "english" in voice_name:
                        female_voice = voice.id
                        print(f"[Samantha] Fallback voice: {voice.name}")
                        break

            if female_voice:
                engine.setProperty("voice", female_voice)
            else:
                print("[Samantha] No English voice found, using default")

            engine.say(text)
            engine.runAndWait()
            print("[Samantha] Speech completed")
            return True

        except Exception as e:
            print(f"[Samantha] Voice error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _speak_espeak_soft(self, text: str):
        """Soft, warm female espeak voice"""
        try:
            # Use female variant with warm settings
            subprocess.run(
                [
                    "espeak-ng",
                    "-v",
                    "en-us+f3",  # Female voice variant
                    "-s",
                    "160",  # Natural conversational speed
                    "-p",
                    "65",  # Higher pitch for female
                    "-a",
                    "150",  # Clear volume
                    text,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
        except Exception:
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
                device=self._audio_device,
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
                device=self._audio_device,
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
