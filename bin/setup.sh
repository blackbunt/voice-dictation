#!/bin/bash
# Setup script for Voice Dictation

echo "📦 Voice Dictation Installation"
echo "==================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Dieses Skript ist nur für Linux"
    exit 1
fi

# Install system dependencies
echo "📦 Installing System-Abhängigkeiten..."
if command -v pacman &> /dev/null; then
    sudo pacman -S --needed --noconfirm python python-pip python-pyaudio portaudio tk
elif command -v yay &> /dev/null; then
    yay -S --needed --noconfirm python python-pip python-pyaudio portaudio tk
elif command -v paru &> /dev/null; then
    paru -S --needed --noconfirm python python-pip python-pyaudio portaudio tk
else
    echo "⚠️ Kein Arch-basierter Package Manager gefunden."
    echo "Bitte manuell installieren:"
    echo "   sudo pacman -S python python-pip python-pyaudio portaudio tk"
    exit 1
fi

# Install Python dependencies
echo ""
echo "🐍 Installing Python-Packagee..."
pip install --user -r requirements.txt

# Create config if not exists
if [ ! -f "config.json" ]; then
    echo ""
    echo "⚙️ Erstelle Standard-Configuration..."
    cp config.json.example config.json
fi

# Setup autostart (optional)
echo ""
read -p "❓ Autostart einrichten? (j/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[JjYy]$ ]]; then
    mkdir -p ~/.config/autostart
    
    # Update desktop file with correct path
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    sed "s|/home/bernie/Repo/text2speech-local|$SCRIPT_DIR|g" voice-dictation.desktop > ~/.config/autostart/voice-dictation.desktop
    chmod +x ~/.config/autostart/voice-dictation.desktop
    
    echo "✅ Autostart eingerichtet!"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Start with: python dictate.py"
echo "⌨️  Standard Hotkey: Ctrl+Shift+Space"
echo ""
echo "💡 Tipp: Passe config.json an für eigene Einstellungen"
