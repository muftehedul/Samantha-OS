# Samantha OS - Installation Guide

## Quick Install (Ubuntu/Debian)

### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pyqt5 espeak-ng mpg123 \
    pulseaudio-utils alsa-utils portaudio19-dev
```

### 2. Install Python Dependencies
```bash
pip3 install --break-system-packages faster-whisper sounddevice vosk \
    edge-tts pygame scipy numpy flask
```

### 3. Download and Install Package
```bash
# Download the .deb package
wget https://github.com/muftehedul/Samantha-OS/releases/download/v1.0.0/samantha-os_1.0.0_amd64.deb

# Install
sudo dpkg -i samantha-os_1.0.0_amd64.deb

# Fix any missing dependencies
sudo apt-get install -f
```

### 4. Launch
```bash
# From terminal
samantha-os

# Or search "Samantha OS" in your application menu
```

## Build from Source

```bash
git clone https://github.com/muftehedul/Samantha-OS.git
cd Samantha-OS

# Install dependencies
sudo apt install -y python3 python3-pip python3-pyqt5 espeak-ng mpg123 \
    pulseaudio-utils alsa-utils portaudio19-dev

pip3 install --break-system-packages faster-whisper sounddevice vosk \
    edge-tts pygame scipy numpy flask

# Build .deb package
./build-deb.sh

# Install
sudo dpkg -i samantha-os_1.0.0_amd64.deb
```

## What Gets Installed

- **Application**: `/opt/samantha-os/`
- **Launcher**: `/usr/bin/samantha-os`
- **Desktop Entry**: `/usr/share/applications/samantha-os.desktop`
- **Icon**: `/usr/share/icons/hicolor/256x256/apps/samantha-os.svg`

## Dependencies

### System Packages (via apt)
- `python3` (>= 3.8) - Python runtime
- `python3-pyqt5` - GUI framework
- `python3-pip` - Package installer
- `espeak-ng` - Backup text-to-speech
- `mpg123` - Audio player for Edge TTS
- `pulseaudio-utils` - Audio system utilities
- `alsa-utils` - ALSA audio utilities
- `portaudio19-dev` - Audio I/O library

### Python Packages (via pip)
- `faster-whisper` - Accurate speech recognition
- `sounddevice` - Audio capture
- `vosk` - Offline speech-to-text
- `edge-tts` - Natural text-to-speech (Jenny Neural voice)
- `pygame` - Audio playback
- `scipy` - Audio signal processing
- `numpy` - Array operations
- `flask` - Kilo proxy server

## First Run

On first launch, Samantha will:
1. Download Whisper base model (~150MB)
2. Download Vosk model (~40MB)
3. Initialize voice engine
4. Start Kilo proxy for LLM

## Usage

### Voice Mode
1. Click the 🎤 microphone button
2. Speak naturally
3. App auto-stops after 1.2s of silence
4. Samantha responds with natural voice

### Text Mode
1. Type in the input field
2. Click → to send or press Enter
3. Samantha responds with voice

## Troubleshooting

### Audio Issues
```bash
# Check audio devices
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone
arecord -d 3 test.wav && aplay test.wav
```

### Missing Dependencies
```bash
sudo apt-get install -f
pip3 install --break-system-packages faster-whisper edge-tts sounddevice vosk
```

### Edge TTS Not Working
```bash
# Test Edge TTS
edge-tts --voice en-US-JennyNeural --text "Hello test" --write-media /tmp/test.mp3
mpg123 /tmp/test.mp3
```

### Permissions
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again
```

## Features

✅ Natural voice interaction with Siri-like animation
✅ Accurate speech recognition (Whisper)
✅ Natural text-to-speech (Edge TTS - Jenny Neural)
✅ Auto-stop after silence detection
✅ Caring, empathetic personality
✅ Free LLM integration (Kilo CLI)
✅ Beautiful, responsive UI
✅ 100% offline voice processing

## System Requirements

- Ubuntu 20.04+ or Debian 11+
- 2GB RAM minimum (4GB recommended)
- 500MB disk space
- Microphone and speakers
- Internet connection (for LLM only)

## Uninstall

```bash
sudo dpkg -r samantha-os
```

## Support

For issues, check:
- System logs: `journalctl -xe`
- Test mode: Run `samantha-os` from terminal to see output
- GitHub Issues: https://github.com/muftehedul/Samantha-OS/issues
