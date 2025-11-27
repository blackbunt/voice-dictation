#!/bin/bash
# Post-install script for Voice Dictation

echo "📦 Voice Dictation Installation"
echo "================================"
echo ""

# Compile GSettings schema
echo "🔧 Kompiliere GSettings Schema..."
glib-compile-schemas /usr/share/glib-2.0/schemas/

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Nächste Schritte:"
echo ""
echo "1️⃣  Installing whisper.cpp:"
echo "   Führe aus: install-whisper.sh"
echo ""
echo "📦 Voice Dictation Installation"
echo "   - Öffne GNOME Einstellungen"
echo "📦 Voice Dictation Installation"
echo "   - Oder terminal: voice-dictation-settings"
echo ""
echo "📦 Voice Dictation Installation"
echo "   voice-dictation"
echo ""
echo "⌨️  Standard Hotkey: Ctrl+Shift+Space"
echo ""
