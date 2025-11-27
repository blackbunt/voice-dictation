#!/bin/bash
# Post-install script for Voice Dictation

echo "📦 Voice Dictation Installation"
echo "================================"
echo ""

# Compile GSettings schema
echo "🔧 Kompiliere GSettings Schema..."
glib-compile-schemas /usr/share/glib-2.0/schemas/

echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "📝 Nächste Schritte:"
echo ""
echo "1️⃣  Installiere whisper.cpp:"
echo "   Führe aus: install-whisper.sh"
echo ""
echo "2️⃣  Konfiguriere Voice Dictation:"
echo "   - Öffne GNOME Einstellungen"
echo "   - Suche nach 'Voice Dictation'"
echo "   - Oder terminal: voice-dictation-settings"
echo ""
echo "3️⃣  Starte Voice Dictation:"
echo "   voice-dictation"
echo ""
echo "⌨️  Standard Hotkey: Ctrl+Shift+Space"
echo ""
