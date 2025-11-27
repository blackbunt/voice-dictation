#!/bin/bash
# Build and install the Arch package

set -e

echo "📦 Voice Dictation Installation"
echo "=========================================="
echo ""

# Check if we're on Arch
if ! command -v pacman &> /dev/null; then
    echo "❌ Dieses Skript ist nur für Arch Linux"
    exit 1
fi

# Install base-devel if needed
if ! pacman -Qq base-devel &> /dev/null; then
    echo "📦 Installing base-devel..."
    sudo pacman -S --needed base-devel
fi

# Build the package
echo "🔨 Building Package..."
makepkg -sf

# Find the built package
PKG_FILE=$(ls -t voice-dictation-*.pkg.tar.zst 2>/dev/null | head -n1)

if [ -z "$PKG_FILE" ]; then
    echo "❌ Package konnte nicht gebaut werden"
    exit 1
fi

echo ""
echo "✅ Package gebaut: $PKG_FILE"
echo ""

# Ask to install
read -p "❓ Package installieren? (j/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[JjYy]$ ]]; then
    sudo pacman -U "$PKG_FILE"
    
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "📝 Als nächstes:"
    echo "   1. Installing Python-Abhängigkeiten:"
    echo "      pip install --user speech_recognition pynput keyboard python-dotenv"
    echo ""
    echo "📦 Voice Dictation Installation"
    echo "      voice-dictation"
    echo ""
    echo "   3. Configuration anpassen:"
    echo "      nano ~/.config/voice-dictation/config.json"
    echo ""
    echo "   4. Autostart aktivieren:"
    echo "      cp /usr/share/applications/voice-dictation.desktop ~/.config/autostart/"
    echo ""
    echo "⌨️  Standard Hotkey: Ctrl+Shift+Space"
fi
