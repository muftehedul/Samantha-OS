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

### Prerequisites

Before installing, ensure you have:
- Ubuntu 20.04+ or Debian 11+
- 2GB RAM minimum (4GB recommended)
- 500MB free disk space
- Working microphone and speakers
- Internet connection (for initial setup and LLM)

### Method 1: Quick Install (Recommended)

#### Step 1: Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pyqt5 espeak-ng mpg123 \
    pulseaudio-utils alsa-utils portaudio19-dev
```

#### Step 2: Install Python Dependencies
```bash
pip3 install --break-system-packages faster-whisper sounddevice vosk \
    edge-tts pygame scipy numpy flask
```

**Note**: The `--break-system-packages` flag is needed on Ubuntu 23.04+ due to PEP 668. Alternatively, use a virtual environment.

#### Step 3: Download and Install Package
```bash
# Download the .deb package
wget https://github.com/muftehedul/Samantha-OS/releases/download/v1.0.0/samantha-os_1.0.0_amd64.deb

# Install
sudo dpkg -i samantha-os_1.0.0_amd64.deb

# Fix any missing dependencies
sudo apt-get install -f
```

#### Step 4: Launch
```bash
# From terminal
samantha-os

# Or search "Samantha OS" in your application menu
```

### Method 2: Install from Source

#### Step 1: Clone Repository
```bash
git clone https://github.com/muftehedul/Samantha-OS.git
cd Samantha-OS
```

#### Step 2: Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pyqt5 espeak-ng mpg123 \
    pulseaudio-utils alsa-utils portaudio19-dev
```

#### Step 3: Install Python Dependencies
```bash
pip3 install --break-system-packages faster-whisper sounddevice vosk \
    edge-tts pygame scipy numpy flask
```

#### Step 4: Build and Install
```bash
# Build .deb package
./build-deb.sh

# Install
sudo dpkg -i samantha-os_1.0.0_amd64.deb
```

#### Step 5: Launch
```bash
samantha-os
```

### Verify Installation

After installation, verify all components are working:

```bash
# Check Python packages
pip3 list | grep -E "faster-whisper|edge-tts|sounddevice|vosk"

# Test Edge TTS
edge-tts --voice en-US-JennyNeural --text "Hello test" --write-media /tmp/test.mp3
mpg123 /tmp/test.mp3

# Test audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

### First Run

On first launch, Samantha will:
1. Start Kilo proxy server (for LLM integration)
2. Load Whisper model (~150MB, downloaded automatically)
3. Load Vosk model (already included)
4. Initialize voice engine
5. Open GUI interface

This may take 30-60 seconds on first run.

## Usage

### Voice Mode
1. Click the 🎤 microphone button
2. Speak naturally when you see "🎤 Speak now..."
3. App automatically stops after 1.2 seconds of silence
4. Samantha responds with natural voice

### Text Mode
1. Type your message in the input field
2. Click → or press Enter to send
3. Samantha responds with voice and text

### Tips
- Speak clearly at normal volume
- Wait for "⏳ Processing..." before speaking again
- Use text mode if microphone issues occur
- Responses are concise (max 500 tokens)

## Troubleshooting

### Audio Issues
```bash
# Check audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone
arecord -d 3 test.wav && aplay test.wav

# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again
```

### Edge TTS Not Working
```bash
# Verify edge-tts is installed
pip3 list | grep edge-tts

# Test Edge TTS
edge-tts --voice en-US-JennyNeural --text "Hello test" --write-media /tmp/test.mp3
mpg123 /tmp/test.mp3

# Reinstall if needed
pip3 install --break-system-packages --force-reinstall edge-tts
```

### Missing Dependencies
```bash
# Fix package dependencies
sudo apt-get install -f

# Reinstall Python packages
pip3 install --break-system-packages faster-whisper sounddevice vosk edge-tts pygame scipy numpy flask
```

### App Won't Start
```bash
# Run from terminal to see errors
cd /opt/samantha-os
python3 src/samantha_app.py

# Check if Kilo proxy is running
ps aux | grep kilo_proxy

# Kill and restart
pkill -f samantha
samantha-os
```

### Microphone Not Detected
```bash
# List audio devices
arecord -l

# Test with specific device
python3 -c "import sounddevice as sd; sd.default.device = 0; print('Device 0 works')"
```

## Uninstall

```bash
sudo dpkg -r samantha-os
```

## Requirements

### System Packages
- `python3` (>= 3.8)
- `python3-pyqt5`
- `python3-pip`
- `espeak-ng`
- `mpg123`
- `pulseaudio-utils`
- `alsa-utils`
- `portaudio19-dev`

### Python Packages
- `faster-whisper` - Speech recognition
- `sounddevice` - Audio capture
- `vosk` - Offline STT
- `edge-tts` - Natural TTS
- `pygame` - Audio playback
- `scipy` - Signal processing
- `numpy` - Array operations
- `flask` - Kilo proxy

## Build DEB Package

```bash
# Build
./build-deb.sh

# Create control file (see debian/DEBIAN/control)
# Create launcher script (see debian/usr/bin/samantha)
# Create desktop entry (see debian/usr/share/applications/samantha.desktop)

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
- python3-pyaudio
- portaudio19-dev
- espeak-ng

## Technical Details

### Voice System
- **STT**: Faster-Whisper (accurate offline speech recognition)
- **TTS**: Edge TTS with Jenny Neural voice (natural, human-like)
- **Audio Detection**: Auto-stop after 1.2s silence
- **Audio Player**: mpg123 for Edge TTS playback

### LLM Integration
- **Model**: kilo/openrouter/free (via Kilo CLI)
- **Personality**: Samantha from "Her" (2013)
- **Response Length**: 500 tokens (concise responses)
- **Clean Output**: Removes markdown formatting

### UI Features
- Circular gradient voice button (Her movie style)
- Real-time audio visualization
- Auto-stop silence detection
- Warm color palette (coral #FF6B6B, peach #FFB4A2, seashell #FFF5EE)

## Cost

| Component | Provider | Cost |
|-----------|----------|------|
| Voice STT | Faster-Whisper (Offline) | FREE |
| Voice TTS | Edge TTS | FREE |
| LLM | Kilo OpenRouter | FREE |
| **Total** | | **$0/month** |

## Project Structure

```
Samantha-OS/
├── src/
│   ├── samantha/
│   │   ├── __init__.py
│   │   ├── core.py              # Main orchestrator & LLM integration
│   │   ├── voice.py             # Voice engine (Whisper + Edge TTS)
│   │   ├── personality.py       # Samantha's personality traits
│   │   ├── skills.py            # System commands & utilities
│   │   ├── workflow.py          # Task management
│   │   └── gui/
│   │       └── main_window.py   # PyQt5 GUI interface
│   └── samantha_app.py          # Entry point
├── models/
│   └── vosk-model-small-en-us-0.15/  # Vosk model (backup STT)
├── debian/
│   ├── DEBIAN/
│   │   └── control              # Package metadata
│   ├── opt/samantha-os/         # Application files
│   └── usr/
│       ├── bin/samantha-os      # Launcher script
│       └── share/applications/  # Desktop entry
├── kilo_proxy.py                # OpenAI-compatible proxy for Kilo
├── build-deb.sh                 # Build script
├── samantha-os_1.0.0_amd64.deb  # Installable package
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