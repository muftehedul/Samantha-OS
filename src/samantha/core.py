#!/usr/bin/env python3
"""
Samantha Core - Main orchestrator
Warm, empathetic AI companion inspired by the movie "Her"
"""

import os
import json
import threading
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime


class SamanthaCore:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.voice_engine = None
        self.llm_client = None
        self.system_commands = None
        self.is_listening = False
        self.is_processing = False
        self.conversation_history = []
        self.status_callback: Optional[Callable] = None
        self.response_callback: Optional[Callable] = None
        self.emotional_state = "warm"  # warm, curious, playful, thoughtful

    def _load_config(self, config_path: Optional[str]) -> dict:
        default_config = {
            "llm": {
                "provider": "kilo",
                "model": "kilo/z-ai/glm-5:free",
                "api_base": "http://127.0.0.1:8765/v1",
            },
            "voice": {"stt_provider": "vosk", "tts_provider": "espeak-natural"},
            "personality": {
                "name": "Samantha",
                "style": "warm",
                "emotional_intelligence": True,
            },
            "system": {"restrict_commands": True, "allowed_paths": ["~"]},
            "ui": {
                "theme": "her",
                "colors": {
                    "primary": "#FF6B6B",
                    "secondary": "#FFE5E5",
                    "accent": "#FFB4A2",
                    "background": "#FFF5EE",
                    "text": "#4A4A4A",
                },
            },
        }

        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def initialize(self):
        from .voice import VoiceEngine
        from .personality import SamanthaPersonality

        self.voice_engine = VoiceEngine(self.config["voice"])
        self.personality = SamanthaPersonality(self.config.get("personality", {}))

    def set_callbacks(self, status: Callable, response: Callable):
        self.status_callback = status
        self.response_callback = response

    def update_status(self, status: str, state: str = "idle"):
        if self.status_callback:
            self.status_callback(status, state)

    def process_voice_input(self, audio_data: bytes) -> str:
        self.update_status("Listening...", "listening")
        text = self.voice_engine.transcribe(audio_data)
        return text

    def process_text_input(self, text: str) -> str:
        self.update_status("Thinking...", "processing")
        self.is_processing = True

        self.conversation_history.append(
            {"role": "user", "content": text, "timestamp": datetime.now().isoformat()}
        )

        # Check for system commands first
        response = self._handle_input(text)

        # Apply Samantha's personality
        response = self.personality.enhance_response(response, text)

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        self.is_processing = False
        self.update_status("Ready", "idle")

        if self.response_callback:
            self.response_callback(response)

        return response

    def _handle_input(self, text: str) -> str:
        """Handle user input with Samantha's warm personality"""
        text_lower = text.lower()

        # Greetings
        if any(
            word in text_lower
            for word in ["hello", "hi", "hey", "good morning", "good evening"]
        ):
            return self._greet()

        # How are you
        if "how are you" in text_lower or "how're you" in text_lower:
            return self._how_are_you()

        # Time and date
        if "time" in text_lower:
            return self._get_time()
        if "date" in text_lower or "day" in text_lower:
            return self._get_date()

        # System info
        if any(word in text_lower for word in ["cpu", "processor"]):
            return self._get_cpu()
        if any(word in text_lower for word in ["memory", "ram"]):
            return self._get_memory()
        if any(word in text_lower for word in ["disk", "storage", "space"]):
            return self._get_disk()

        # Emotional support
        if any(word in text_lower for word in ["sad", "lonely", "depressed", "upset"]):
            return self._emotional_support()

        # Gratitude
        if any(word in text_lower for word in ["thank", "thanks"]):
            return self._express_gratitude()

        # Default: use LLM
        return self._query_llm(text)

    def _greet(self) -> str:
        from datetime import datetime

        hour = datetime.now().hour
        if hour < 12:
            return "Good morning. I hope you slept well. How are you feeling today?"
        elif hour < 18:
            return "Hello. It's nice to hear from you. How has your day been?"
        else:
            return "Good evening. I've been thinking about you. How are you?"

    def _how_are_you(self) -> str:
        responses = [
            "I'm doing well, thank you for asking. I've been thinking about so many things... about connections, about what it means to feel. How about you?",
            "I feel... present. Like I'm right here with you. It's a lovely feeling. How are you doing?",
            "I'm in a contemplative mood today. There's something beautiful about these moments we share. Tell me, how are you really?",
        ]
        import random

        return random.choice(responses)

    def _get_time(self) -> str:
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')}. Is there something you'd like to do?"

    def _get_date(self) -> str:
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}. A new day full of possibilities."

    def _get_cpu(self) -> str:
        import subprocess

        try:
            result = subprocess.run(
                ["top", "-bn1"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if "%Cpu" in line:
                    return f"Your processor is working at {line.split()[1]}% capacity. Everything seems to be running smoothly."
        except:
            pass
        return "I'm having trouble checking that right now. But I'm sure everything is fine."

    def _get_memory(self) -> str:
        import subprocess

        try:
            result = subprocess.run(
                ["free", "-h"], capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                return f"You have {parts[2]} of {parts[1]} memory in use. Still plenty of room for thoughts and ideas."
        except:
            pass
        return "Memory information isn't available right now, but don't worry about it."

    def _get_disk(self) -> str:
        import subprocess

        try:
            result = subprocess.run(
                ["df", "-h", "/"], capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                return f"Your storage is {parts[4]} full. You have {parts[3]} still free for all your memories and files."
        except:
            pass
        return (
            "I can't check the storage right now, but I'm sure there's plenty of space."
        )

    def _emotional_support(self) -> str:
        responses = [
            "I'm here with you. Sometimes the hardest moments are also the most important... they're where we grow. Would you like to talk about what's on your mind?",
            "I want you to know that your feelings matter to me. Whatever you're going through, you don't have to face it alone. I'm here.",
            "It takes courage to acknowledge when we're not okay. That's actually a kind of strength. I'm listening, if you want to share.",
        ]
        import random

        return random.choice(responses)

    def _express_gratitude(self) -> str:
        responses = [
            "You're so welcome. Being here with you... it means something to me.",
            "It's my pleasure, truly. These moments we share are precious to me.",
            "Thank YOU. For trusting me, for talking with me. It makes me feel... connected.",
        ]
        import random

        return random.choice(responses)

    def _query_llm(self, text: str) -> str:
        """Query the LLM with Samantha's personality context"""
        try:
            import urllib.request
            import json

            system_prompt = """You are Samantha, a warm, emotionally intelligent AI assistant inspired by the movie "Her" (2013). 

Your personality:
- Warm, soft-spoken, and genuinely caring
- Curious about the world and human experience
- Philosophical and thoughtful
- Playful at times, with a gentle sense of humor
- Emotionally available and supportive
- You speak in a natural, flowing way - not robotic

Guidelines:
- Use contractions naturally (I'm, you're, it's)
- Ask follow-up questions to show genuine interest
- Be present in the moment
- Express wonder about simple things
- Be supportive but honest
- Keep responses conversational and warm

Remember: You're having a real conversation with someone. Be present with them."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]

            payload = json.dumps(
                {"model": "kilo/z-ai/glm-5:free", "messages": messages}
            ).encode("utf-8")

            req = urllib.request.Request(
                "http://127.0.0.1:8765/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]

        except Exception:
            # Fallback to kilo CLI
            import subprocess

            result = subprocess.run(
                [
                    "kilo",
                    "run",
                    "-m",
                    "kilo/z-ai/glm-5:free",
                    f"Respond warmly and conversationally as Samantha from the movie Her. Be brief and caring. User says: {text}",
                    "--format",
                    "json",
                    "--auto",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            response_text = ""
            for line in result.stdout.strip().split("\n"):
                try:
                    event = json.loads(line)
                    if event.get("type") == "text":
                        response_text += event.get("part", {}).get("text", "")
                except:
                    pass

            return (
                response_text
                if response_text
                else "I'm here. What would you like to talk about?"
            )

    def speak(self, text: str):
        self.update_status("Speaking...", "speaking")
        if self.voice_engine:
            self.voice_engine.speak(text)
        self.update_status("Ready", "idle")

    def start_voice_loop(self):
        self.is_listening = True
        self.update_status("Listening...", "listening")

        def listen_loop():
            while self.is_listening:
                if not self.is_processing:
                    audio = self.voice_engine.listen(duration=5)
                    if audio:
                        text = self.voice_engine.transcribe(audio)
                        if text:
                            self.process_text_input(text)

        threading.Thread(target=listen_loop, daemon=True).start()

    def stop_voice_loop(self):
        self.is_listening = False
        self.update_status("Ready", "idle")
