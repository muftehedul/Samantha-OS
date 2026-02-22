#!/bin/bash
# Samantha OS - Single Command Launcher
# Starts backend + opens web UI in browser

cd /opt/samantha-os

echo "=========================================="
echo "  Samantha OS v2.0.0"
echo "  FREE Browser Speech Recognition"
echo "=========================================="
echo ""

# Kill existing processes
pkill -f kilo_proxy.py 2>/dev/null
pkill -f web_server.py 2>/dev/null
sleep 1

# Start Kilo Proxy
echo "[1/2] Starting Kilo proxy..."
python3 kilo_proxy.py > /tmp/kilo_proxy.log 2>&1 &
PROXY_PID=$!

# Wait for proxy
for i in {1..15}; do
    if curl -s http://127.0.0.1:8765/v1/models > /dev/null 2>&1; then
        echo "     ✓ Proxy ready"
        break
    fi
    sleep 1
done

# Start Web Server
echo "[2/2] Starting web server..."
python3 web_server.py > /tmp/samantha_web.log 2>&1 &
WEB_PID=$!

sleep 2

# Open in browser
echo ""
echo "=========================================="
echo "  Samantha OS is running!"
echo "=========================================="
echo ""
echo "  Web UI: http://127.0.0.1:5000"
echo ""
echo "  🎤 Click mic to speak (Chrome/Edge)"
echo "  🔊 Voice responses enabled"
echo ""
echo "  Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000 2>/dev/null &
fi

# Wait for processes
wait $WEB_PID $PROXY_PID
