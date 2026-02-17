#!/bin/bash
# Build Samantha OS .deb package

set -e

APP_NAME="samantha-os"
VERSION="1.0.0"
ARCH="amd64"
BUILD_DIR="build/${APP_NAME}_${VERSION}_${ARCH}"

echo "Building Samantha OS .deb package..."

# Clean previous build
rm -rf build
mkdir -p "$BUILD_DIR"

# Create directory structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/opt/samantha-os"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$BUILD_DIR/usr/bin"

# Copy application files
cp -r src "$BUILD_DIR/opt/samantha-os/"
cp kilo_proxy.py "$BUILD_DIR/opt/samantha-os/"
cp -r models "$BUILD_DIR/opt/samantha-os/" 2>/dev/null || echo "Models not found, will download on first run"

# Create launcher script
cat > "$BUILD_DIR/usr/bin/samantha-os" << 'EOF'
#!/bin/bash
# Kill any existing proxy
pkill -f kilo_proxy.py 2>/dev/null || true
sleep 1

# Start kilo proxy
cd /opt/samantha-os
/usr/bin/python3 kilo_proxy.py > /tmp/kilo_proxy.log 2>&1 &
PROXY_PID=$!

echo "Starting kilo proxy (PID: $PROXY_PID)..."

# Wait for proxy to be ready
for i in {1..15}; do
    if curl -s http://127.0.0.1:8765/v1/models > /dev/null 2>&1; then
        echo "Proxy ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "Proxy failed to start. Check /tmp/kilo_proxy.log"
        cat /tmp/kilo_proxy.log
        exit 1
    fi
    sleep 1
done

cd /opt/samantha-os
exec /usr/bin/python3 src/samantha_app.py "$@"
EOF
chmod +x "$BUILD_DIR/usr/bin/samantha-os"

# Create GUI launcher wrapper
cat > "$BUILD_DIR/usr/bin/samantha-os-gui" << 'EOF'
#!/bin/bash
# GUI launcher - ensures proper environment
export DISPLAY="${DISPLAY:-:0}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"

# Log to file for debugging
exec /usr/bin/samantha-os 2>&1 | tee /tmp/samantha-os-gui.log
EOF
chmod +x "$BUILD_DIR/usr/bin/samantha-os-gui"

# Create desktop entry
cat > "$BUILD_DIR/usr/share/applications/samantha-os.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Samantha OS
Comment=AI Voice Assistant inspired by "Her"
Exec=/usr/bin/samantha-os-gui
Icon=samantha-os
Terminal=false
Categories=Utility;AudioVideo;
Keywords=ai;assistant;voice;samantha;
EOF

# Create icon (simple SVG)
cat > "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/samantha-os.svg" << 'EOF'
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <circle cx="128" cy="128" r="120" fill="#FF6B6B"/>
  <circle cx="128" cy="128" r="80" fill="#FFB4A2"/>
  <circle cx="128" cy="128" r="40" fill="#FFE5E5"/>
</svg>
EOF

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: samantha-os
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.8), python3-pyqt5, python3-numpy, python3-psutil, python3-pip
Maintainer: Samantha OS Team <samantha@example.com>
Description: AI Voice Assistant inspired by "Her"
 Samantha OS is a caring AI voice assistant with full system capabilities.
 Features:
  - Natural voice interaction
  - System monitoring and control
  - Task scheduling and reminders
  - Memory and learning
  - Beautiful Siri-like UI
EOF

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip3 install --break-system-packages faster-whisper sounddevice vosk pygame edge-tts flask scipy 2>/dev/null || true

echo "Samantha OS installed successfully!"
echo "Run 'samantha-os' to start"
exit 0
EOF
chmod +x "$BUILD_DIR/DEBIAN/postinst"

# Build the package
dpkg-deb --build "$BUILD_DIR"

# Move to current directory
mv "build/${APP_NAME}_${VERSION}_${ARCH}.deb" .

echo "✓ Package created: ${APP_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${APP_NAME}_${VERSION}_${ARCH}.deb"
echo "  sudo apt-get install -f  # Fix dependencies if needed"
echo ""
echo "To run:"
echo "  samantha-os"
