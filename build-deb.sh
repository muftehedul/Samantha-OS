#!/bin/bash
# Build Samantha OS .deb package - Simple Web UI
# Single command launches everything

set -e

APP_NAME="samantha-os"
VERSION="2.0.0"
ARCH="amd64"
BUILD_DIR="build/${APP_NAME}_${VERSION}_${ARCH}"

echo "=========================================="
echo "  Samantha OS v${VERSION} - Web UI"
echo "=========================================="

# Uninstall previous version
pkexec apt-get remove -y samantha-os 2>/dev/null || true
pkexec dpkg --remove samantha-os 2>/dev/null || true

# Clean previous build
rm -rf build
mkdir -p "$BUILD_DIR"

# Create directory structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/opt/samantha-os/src/samantha/gui"
mkdir -p "$BUILD_DIR/opt/samantha-os/web"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$BUILD_DIR/usr/bin"

# Copy source files
cp src/samantha/*.py "$BUILD_DIR/opt/samantha-os/src/samantha/" 2>/dev/null || true
cp src/samantha/gui/*.py "$BUILD_DIR/opt/samantha-os/src/samantha/gui/" 2>/dev/null || true
cp src/samantha_app.py "$BUILD_DIR/opt/samantha-os/src/" 2>/dev/null || true
cp kilo_proxy.py "$BUILD_DIR/opt/samantha-os/"

# Copy web files
cp web/index.html "$BUILD_DIR/opt/samantha-os/web/"
cp web/manifest.json "$BUILD_DIR/opt/samantha-os/web/" 2>/dev/null || true
cp web/sw.js "$BUILD_DIR/opt/samantha-os/web/" 2>/dev/null || true
cp web/*.svg "$BUILD_DIR/opt/samantha-os/web/" 2>/dev/null || true
cp web_server.py "$BUILD_DIR/opt/samantha-os/"

# Create __init__.py
touch "$BUILD_DIR/opt/samantha-os/src/samantha/__init__.py"

# Create main launcher
cat > "$BUILD_DIR/usr/bin/sm" << 'LAUNCHER'
#!/bin/bash
cd /opt/samantha-os

echo "=========================================="
echo "  Samantha OS - Starting..."
echo "=========================================="

# Kill existing
pkill -f kilo_proxy.py 2>/dev/null
pkill -f web_server.py 2>/dev/null
sleep 1

# Start Kilo Proxy
echo "[1/2] Starting backend..."
python3 kilo_proxy.py > /tmp/kilo_proxy.log 2>&1 &
sleep 3

# Start Web Server
echo "[2/2] Starting web server..."
python3 web_server.py 2>&1 &
WEB_PID=$!

sleep 2

echo ""
echo "=========================================="
echo "  Samantha OS is running!"
echo "  Web UI: http://127.0.0.1:5000"
echo "=========================================="
echo ""
echo "🎤 Click mic button to speak"
echo "🔊 Voice responses enabled"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Open browser
xdg-open http://127.0.0.1:5000 2>/dev/null &

wait $WEB_PID
LAUNCHER
chmod +x "$BUILD_DIR/usr/bin/sm"

# Create CLI launcher
cat > "$BUILD_DIR/usr/bin/sm-cli" << 'EOF'
#!/bin/bash
cd /opt/samantha-os
exec python3 src/samantha_app.py --cli "$@"
EOF
chmod +x "$BUILD_DIR/usr/bin/sm-cli"

# Create icon
cat > "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/samantha-os.svg" << 'EOF'
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FF6B6B"/>
      <stop offset="100%" style="stop-color:#FFB4A2"/>
    </linearGradient>
  </defs>
  <circle cx="256" cy="256" r="240" fill="url(#grad)"/>
  <circle cx="256" cy="256" r="150" fill="#FFE5E5"/>
  <circle cx="256" cy="256" r="70" fill="#FF6B6B"/>
</svg>
EOF

# Create desktop entry
cat > "$BUILD_DIR/usr/share/applications/samantha-os.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Samantha
Comment=AI Voice Assistant
Exec=/usr/bin/sm
Icon=samantha-os
Terminal=true
Categories=Utility;
Keywords=ai;voice;samantha;
EOF

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: samantha-os
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.8), python3-flask, python3-requests, curl
Maintainer: Samantha OS <samantha@example.com>
Description: AI Voice Assistant with FREE Browser Speech
 Samantha OS - AI companion inspired by "Her" (2013).
 .
 Run 'samantha-os' to start. Opens web UI in browser.
 Uses FREE browser speech recognition (Chrome/Edge).
EOF

# Create postinst
cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
gtk-update-icon-cache -f /usr/share/icons/hicolor/ 2>/dev/null || true
echo ""
echo "✓ Samantha OS installed!"
echo "  Run: sm"
echo "  Web: http://127.0.0.1:5000"
EOF
chmod +x "$BUILD_DIR/DEBIAN/postinst"

# Create prerm
cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
pkill -f web_server.py 2>/dev/null || true
pkill -f kilo_proxy.py 2>/dev/null || true
EOF
chmod +x "$BUILD_DIR/DEBIAN/prerm"

# Build
echo "Building..."
dpkg-deb --build --root-owner-group "$BUILD_DIR" 2>/dev/null || dpkg-deb --build "$BUILD_DIR"

# Install
echo ""
echo "Installing..."
pkexec dpkg -i "build/${APP_NAME}_${VERSION}_${ARCH}.deb"

echo ""
echo "✓ Done! Run: sm"
