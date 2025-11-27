#!/bin/bash
# Install whisper.cpp for Voice Dictation

set -e

echo "📦 whisper.cpp Installation"
echo "============================"
echo ""

INSTALL_DIR="$HOME/.local/share/whisper"
BIN_DIR="$HOME/.local/bin"
MODEL_DIR="$HOME/.local/share/whisper/models"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$MODEL_DIR"

# Clone whisper.cpp if not exists
if [ ! -d "$INSTALL_DIR/whisper.cpp" ]; then
    echo "📥 Klone whisper.cpp Repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git "$INSTALL_DIR/whisper.cpp"
else
    echo "✓ whisper.cpp bereits geklont"
fi

# Build whisper.cpp
echo ""
echo "🔨 Baue whisper.cpp..."
cd "$INSTALL_DIR/whisper.cpp"
make clean
make

# Install to local bin
echo ""
echo "📦 Installiere whisper-cpp nach $BIN_DIR..."
cp main "$BIN_DIR/whisper-cpp"
chmod +x "$BIN_DIR/whisper-cpp"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  Füge folgende Zeile zu deiner ~/.zshrc hinzu:"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    read -p "Soll ich das automatisch hinzufügen? (j/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[JjYy]$ ]]; then
        echo "" >> ~/.zshrc
        echo "# Voice Dictation - whisper.cpp" >> ~/.zshrc
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc
        echo "✅ PATH aktualisiert. Bitte öffne ein neues Terminal."
    fi
fi

# Download model
echo ""
echo "📥 Lade Whisper-Modelle herunter..."
echo ""
echo "Verfügbare Modelle:"
echo "  tiny   - 75 MB  (schnellst, geringste Qualität)"
echo "  base   - 142 MB (empfohlen für Tests)"
echo "  small  - 466 MB (gut für Produktion)"
echo "  medium - 1.5 GB (sehr gut)"
echo "  large  - 2.9 GB (beste Qualität, langsam)"
echo ""
read -p "Welches Modell möchtest du? [base]: " MODEL
MODEL=${MODEL:-base}

if [ ! -f "$MODEL_DIR/ggml-$MODEL.bin" ]; then
    echo "📥 Lade ggml-$MODEL.bin herunter..."
    wget -P "$MODEL_DIR" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$MODEL.bin"
    echo "✅ Modell heruntergeladen: $MODEL_DIR/ggml-$MODEL.bin"
else
    echo "✓ Modell bereits vorhanden: $MODEL_DIR/ggml-$MODEL.bin"
fi

echo ""
echo "✅ whisper.cpp Installation abgeschlossen!"
echo ""
echo "📝 Konfiguriere jetzt config.json:"
echo "   \"model\": \"$MODEL\""
echo "   \"whisper_cpp_path\": \"$BIN_DIR/whisper-cpp\""
echo "   \"model_path\": \"$MODEL_DIR\""
echo ""
echo "🚀 Starte Voice Dictation mit: python dictate.py"
