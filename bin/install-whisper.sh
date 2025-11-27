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
echo "🔨 Building whisper.cpp..."
cd "$INSTALL_DIR/whisper.cpp"
make clean 2>/dev/null || true
make

# Install to local bin
echo ""
echo "📦 Installing whisper-cli to $BIN_DIR..."
cp build/bin/whisper-cli "$BIN_DIR/whisper-cli"
chmod +x "$BIN_DIR/whisper-cli"

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
        echo "📦 Voice Dictation Installation"
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
    echo "📥 Downloading ggml-$MODEL.bin..."
    bash "$INSTALL_DIR/whisper.cpp/models/download-ggml-model.sh" "$MODEL"
    echo "✅ Model downloaded: $MODEL_DIR/ggml-$MODEL.bin"
else
    echo "✓ Model already exists: $MODEL_DIR/ggml-$MODEL.bin"
fi

echo ""
echo "✅ whisper.cpp Installation complete!"
echo ""
echo "📝 Configure voice-dictation-settings or config.json:"
echo "   \"model\": \"$MODEL\""
echo "   \"whisper_cpp_path\": \"$BIN_DIR/whisper-cli\""
echo "   \"model_path\": \"$HOME/.local/share/whisper/whisper.cpp/models\""
echo ""
echo "🎙️  Start: voice-dictation"
echo "⌨️  Hotkey: Ctrl+Shift+Space"
