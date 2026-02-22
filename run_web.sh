#!/bin/bash
# Samantha Web Interface - Free Browser Speech Recognition
# No Vosk, no Whisper, no paid APIs - uses browser's native Web Speech API

cd /home/mithul/my_files/agent/Samantha-OS

echo "=========================================="
echo "  Samantha Web - Free Speech Recognition"
echo "=========================================="
echo ""
echo "🎤 Using FREE browser Web Speech API"
echo "   - SpeechRecognition (Chrome/Edge)"
echo "   - SpeechSynthesis (All browsers)"
echo ""
echo "🌐 Opening in browser..."
echo ""

# Start server in background
python3 web_server.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Open in browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000
elif command -v google-chrome &> /dev/null; then
    google-chrome http://127.0.0.1:5000 &
elif command -v chromium &> /dev/null; then
    chromium http://127.0.0.1:5000 &
fi

# Wait for server
wait $SERVER_PID
