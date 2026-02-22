# Samantha OS

An AI Assistant inspired by the movie **"Her" (2013)** - A warm, emotionally intelligent AI companion with a beautiful web interface.

![Samantha OS](https://img.shields.io/badge/version-2.0.0-coral)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Linux-orange)

## ✨ Features

- 🎤 **FREE Browser Speech Recognition** - No Vosk/Whisper needed, uses browser's native Web Speech API
- 🔊 **Natural Voice** - Edge TTS with JennyNeural voice (warm, human-like)
- 💭 **Emotional Intelligence** - Empathetic, thoughtful responses
- 🎨 **Beautiful Web UI** - Siri-style wave animation, Her-movie inspired design
- 🔄 **Auto-Listen Mode** - Continuous conversation flow
- 💰 **100% Free** - No API keys required for speech features
- 🌐 **PWA Support** - Installable as desktop app

## 🚀 Quick Install

### Method 1: Install from .deb package (Recommended)

```bash
# Download and install
wget https://github.com/muftehedul/Samantha-OS/releases/download/v2.0.0/samantha-os_2.0.0_amd64.deb
sudo dpkg -i samantha-os_2.0.0_amd64.deb

# Run
sm
```

### Method 2: Install from Source

```bash
# Clone repository
git clone https://github.com/muftehedul/Samantha-OS.git
cd Samantha-OS

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-flask curl
pip3 install --break-system-packages flask requests edge-tts

# Build and install
./build-deb.sh

# Run
sm
```

## 📋 Requirements

### System Packages
- `python3` (>= 3.8)
- `python3-pip`
- `python3-flask`
- `curl`

### Python Packages
- `flask` - Web server
- `requests` - HTTP client
- `edge-tts` - Natural TTS (JennyNeural voice)

### For Best Speech Recognition
- **Chrome** or **Edge** browser (for Web Speech API)

## 🎮 Usage

### Launch
```bash
sm
```

This will:
1. Start the Kilo proxy (LLM backend)
2. Start the Flask web server
3. Open your browser at http://127.0.0.1:5000
4. Speak the welcome message
5. Auto-start listening

### Voice Conversation
1. Click the 🎤 mic button OR just speak (auto-listen enabled)
2. Speak naturally
3. Samantha responds with voice
4. Auto-listens again for continuous conversation

### Text Mode
1. Type your message in the input field
2. Click → or press Enter
3. Samantha responds with voice and text

## 🎨 UI Features

- **Siri-style Wave Animation** - Real-time audio visualization
- **Glassmorphism Design** - Modern, elegant interface
- **Her Movie Color Palette** - Warm coral (#FF6B6B) and peach tones
- **Responsive Layout** - Works on desktop and mobile
- **PWA Ready** - Install as desktop app

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `sm` | Launch web UI (default) |
| `sm-cli` | CLI mode |

## 📁 Project Structure

```
Samantha-OS/
├── web/
│   ├── index.html      # Web UI with Siri-style animation
│   ├── manifest.json   # PWA manifest
│   └── sw.js           # Service worker
├── src/
│   └── samantha/
│       ├── core.py     # Main orchestrator
│       ├── voice.py    # Voice engine (Edge TTS)
│       └── personality.py
├── web_server.py       # Flask web server
├── kilo_proxy.py       # LLM proxy
└── build-deb.sh        # Build script
```

## 🌐 Web Interface

Open http://127.0.0.1:5000 in your browser:
- **Chrome/Edge** - Best for speech recognition
- **Firefox** - Works with text mode
- **Mobile** - Responsive design

## 🔊 Voice Features

### Speech-to-Text (STT)
- **Browser Web Speech API** - FREE, no offline models needed
- Real-time transcription display
- Automatic silence detection

### Text-to-Speech (TTS)
- **Edge TTS JennyNeural** - Natural, warm female voice
- Same voice as desktop version
- Auto-speak responses

## ⚙️ Configuration

Config file: `~/.config/samantha/config.json`

```json
{
  "llm": {
    "provider": "kilo",
    "model": "kilo/z-ai/glm-5:free"
  },
  "voice": {
    "tts_provider": "edge-tts"
  },
  "personality": {
    "name": "Samantha",
    "style": "warm"
  }
}
```

## 🐛 Troubleshooting

### Speech Recognition Not Working
- Use **Chrome** or **Edge** browser
- Allow microphone access when prompted
- Check browser settings for microphone permissions

### No Audio / TTS Not Working
```bash
# Test Edge TTS
edge-tts --voice en-US-JennyNeural --text "Hello" --write-media /tmp/test.mp3
mpg123 /tmp/test.mp3

# Install mpg123 if needed
sudo apt install mpg123
```

### Server Not Starting
```bash
# Check if already running
pkill -f web_server
pkill -f kilo_proxy

# Run manually
cd /opt/samantha-os
python3 web_server.py
```

### Port 5000 Already in Use
```bash
# Kill process using port 5000
sudo lsof -i :5000
sudo kill -9 <PID>

# Or change port in web_server.py
```

## 💰 Cost

| Component | Provider | Cost |
|-----------|----------|------|
| Voice STT | Browser Web Speech API | **FREE** |
| Voice TTS | Edge TTS | **FREE** |
| LLM | Kilo (GLM-5 free) | **FREE** |
| **Total** | | **$0/month** |

## 🆕 What's New in v2.0.0

- ✅ **Web Interface** - Beautiful browser-based UI
- ✅ **FREE Browser STT** - No Vosk/Whisper needed
- ✅ **Siri-style Animation** - Real-time wave visualization
- ✅ **Auto-Listen Mode** - Continuous conversation flow
- ✅ **Simple Command** - Just type `sm` to run
- ✅ **PWA Support** - Installable web app
- ✅ **Edge TTS Voice** - Same JennyNeural voice from desktop

## 🔄 Upgrade from v1.0.0

```bash
# Remove old version
sudo apt remove samantha-os

# Install new version
sudo dpkg -i samantha-os_2.0.0_amd64.deb

# Run with new command
sm
```

## 🗑️ Uninstall

```bash
sudo dpkg -r samantha-os
```

## 📝 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- Film "Her" (2013) by Spike Jonze
- Browser Web Speech API
- Edge TTS (Microsoft)
- Kilo AI (GLM-5 free tier)

---

*"The past is just a story we tell ourselves."* - Samantha, Her (2013)
