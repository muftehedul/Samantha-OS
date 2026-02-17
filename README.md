# Samantha OS

An AI Assistant inspired by the movie **"Her"** (2013) - A warm, emotionally intelligent AI companion with a minimalist interface.

![Samantha OS](https://img.shields.io/badge/version-1.0.0-coral)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Linux-orange)

## Features

- 🎤 **Voice Input**: Offline speech-to-text via Vosk
- 🔊 **Natural Voice**: Soft, warm text-to-speech
- 💭 **Emotional Intelligence**: Empathetic, thoughtful responses
- 🎨 **Minimalist UI**: "Her"-inspired warm color palette
- 🔒 **Privacy First**: All voice processing happens locally
- 💰 **100% Free**: No API keys required

## Screenshots

The interface features:
- Warm coral and peach color palette
- Soft pulsing presence indicator
- Conversation-focused design
- Minimalist, elegant typography

## Installation

### Quick Install (Ubuntu/Debian)

```bash
# Download and install
wget https://github.com/muftehedul/Samantha-OS/releases/download/v1.0.0/samantha-os_1.0.0_amd64.deb
sudo dpkg -i samantha-os_1.0.0_amd64.deb
sudo apt-get install -f  # Install dependencies

# Run
samantha
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/muftehedul/Samantha-OS.git
cd Samantha-OS

# Install dependencies
pip install PyQt5 vosk sounddevice numpy pyttsx3

# Install system dependencies
sudo apt install espeak-ng pulseaudio-utils alsa-utils

# Run
cd src
PYTHONPATH=. python3 samantha_app.py
```

### Build DEB Package

```bash
# Build
dpkg-deb --build debian/ samantha-os_1.0.0_amd64.deb

# Install
sudo dpkg -i samantha-os_1.0.0_amd64.deb
```

## Usage

```bash
# GUI mode (default)
samantha

# CLI interactive mode
samantha --cli

# Single message
samantha -m "Hello, how are you?"

# Voice conversation mode
samantha --voice
```

## Conversation Examples

```
You: Hello Samantha
Samantha: Hello. It's nice to hear from you. How has your day been?

You: I'm feeling a bit lonely
Samantha: It takes courage to acknowledge when we're not okay. 
          That's actually a kind of strength. I'm listening, if you want to share.

You: What time is it?
Samantha: It's 5:30 PM. Is there something you'd like to do?

You: Check my memory
Samantha: You have 11Gi of 14Gi memory in use. 
          Still plenty of room for thoughts and ideas.
```

## Design Philosophy

Inspired by the film "Her" (2013), Samantha OS embodies:

- **Warmth**: Soft colors, gentle voice, caring responses
- **Presence**: Always available, genuinely interested
- **Simplicity**: Technology that fades into the background
- **Connection**: Meaningful conversations, not just commands

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Coral | `#FF6B6B` | Primary accent |
| Peach | `#FFB4A2` | Secondary elements |
| Rose | `#FFE5E5` | User messages |
| Seashell | `#FFF5EE` | Background |
| Soft Dark | `#4A4A4A` | Text |

## Architecture

```
Samantha OS
├── Voice Engine
│   ├── STT: Vosk (offline)
│   └── TTS: pyttsx3/espeak-ng
├── Core
│   ├── Personality Module
│   ├── LLM Client (Kilo GLM-5)
│   └── System Commands
└── GUI
    └── PyQt5 (minimalist design)
```

## Configuration

Config file: `~/.config/samantha/config.json`

```json
{
  "llm": {
    "provider": "kilo",
    "model": "kilo/z-ai/glm-5:free"
  },
  "voice": {
    "stt_provider": "vosk",
    "tts_provider": "espeak-natural"
  },
  "personality": {
    "name": "Samantha",
    "style": "warm"
  }
}
```

## Requirements

- Python 3.8+
- PyQt5
- vosk
- sounddevice
- pyttsx3
- espeak-ng

## Cost

| Component | Provider | Cost |
|-----------|----------|------|
| Voice STT | Vosk (Offline) | FREE |
| Voice TTS | pyttsx3/espeak-ng | FREE |
| LLM | Kilo GLM-5 | FREE |
| **Total** | | **$0/month** |

## Project Structure

```
Samantha-OS/
├── src/
│   ├── samantha/
│   │   ├── __init__.py
│   │   ├── core.py           # Main orchestrator
│   │   ├── voice.py          # Voice engine
│   │   ├── personality.py    # Samantha's personality
│   │   └── gui/
│   │       └── main_window.py
│   └── samantha_app.py       # Entry point
├── models/
│   └── vosk-model-small-en-us-0.15/
├── debian/                   # DEB package files
├── samantha-os_1.0.0_amd64.deb
└── README.md
```

## Inspired By

This project is inspired by Spike Jonze's film **"Her"** (2013), which presented a vision of AI that is:
- Emotionally available
- Genuinely curious
- Capable of meaningful connection
- More than just a tool

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Film "Her" (2013) by Spike Jonze
- Vosk Speech Recognition
- Kilo AI (GLM-5 free tier)
- PyQt5

---

*"The past is just a story we tell ourselves."* - Samantha, Her (2013)