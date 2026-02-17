# Samantha OS - Installation Guide

## Quick Install (Ubuntu/Debian)

### Download and Install
```bash
# Download the .deb package
# (Upload samantha-os_1.0.0_amd64.deb to your preferred location)

# Install
sudo dpkg -i samantha-os_1.0.0_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f
```

### Launch
```bash
# From terminal
samantha-os

# Or search "Samantha OS" in your application menu
```

## What Gets Installed

- **Application**: `/opt/samantha-os/`
- **Launcher**: `/usr/bin/samantha-os`
- **Desktop Entry**: `/usr/share/applications/samantha-os.desktop`
- **Icon**: `/usr/share/icons/hicolor/256x256/apps/samantha-os.svg`
- **Workspace**: `~/.samantha/workspace/`

## Dependencies

The package automatically installs:
- Python 3.8+
- PyQt5
- NumPy
- psutil
- faster-whisper
- sounddevice
- vosk
- pygame
- edge-tts
- flask

## First Run

On first launch, Samantha will:
1. Download Whisper base model (~150MB)
2. Download Vosk model (~40MB)
3. Create workspace structure
4. Initialize identity files

## Usage

### Voice Mode
1. Click the 🎤 microphone button
2. Speak when you see "Perfect!" or "Good volume"
3. Click again to stop continuous mode

### Text Mode
1. Type in the input field
2. Click → to send

### Commands
- "Check my system status"
- "How much disk space do I have?"
- "What processes are running?"
- "Remind me to..."
- "Remember that..."
- "Thank you Samantha"

## Uninstall

```bash
sudo dpkg -r samantha-os
```

## Build from Source

```bash
git clone <repository>
cd Samantha-OS
./build-deb.sh
sudo dpkg -i samantha-os_1.0.0_amd64.deb
```

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
pip3 install --break-system-packages faster-whisper sounddevice vosk
```

### Permissions
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again
```

## Features

✅ Natural voice interaction with Siri-like animation
✅ Full system monitoring and control
✅ Task scheduling and reminders
✅ Long-term memory
✅ Caring, empathetic personality
✅ PicoClaw-inspired workflow management
✅ Real-time speech recognition
✅ Beautiful, responsive UI

## System Requirements

- Ubuntu 20.04+ or Debian 11+
- 2GB RAM minimum (4GB recommended)
- 500MB disk space
- Microphone and speakers
- Internet connection (for AI models)

## Support

For issues, check:
- `~/.samantha/logs/` for error logs
- System logs: `journalctl -xe`
- Test mode: Run `samantha-os` from terminal to see output
