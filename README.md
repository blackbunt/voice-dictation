# Voice Dictation for Linux

A simple, iOS-like dictation feature for Linux with GNOME integration, powered by whisper.cpp.

## 🎯 Features

- 🎤 **Toggle Hotkey**: Press Ctrl+Shift+Space to start/stop recording
- 🤫 **Auto-Stop on Silence**: Automatically ends after 2 seconds of silence
- 🌐 **Completely Offline**: Uses whisper.cpp - no cloud, your data never leaves your PC
- 🔌 **System-wide**: Works in any application
- ⚙️ **GNOME Integration**: Native settings app for easy configuration
- � **Multi-language**: German, English, Spanish, French, and more
- 📦 **Arch Package**: Clean installation via PKGBUILD

## 📸 Usage

### Simple as on iOS:

1. **Press hotkey** → Recording starts 🔴
2. **Speak** (in German, English, or any supported language)
3. **Silence (2 sec)** → Recording stops automatically ⏹️
4. **Text appears** at cursor position ✨

**Alternative:** Press hotkey again to stop manually.

## 🚀 Installation (Arch Linux)

### Quick Installation

```bash
# 1. Clone repository
git clone https://github.com/blackbunt/voice-dictation.git
cd voice-dictation

# 2. Build and install package
./build.sh

# 3. Install whisper.cpp
./bin/install-whisper.sh

# 4. Done! Start Voice Dictation
voice-dictation
```

### Alternative: Using install-pkg.sh

```bash
# Automated build and install
./bin/install-pkg.sh
```

### Manual Build

```bash
# Build package
makepkg -sf

# Install package
sudo pacman -U voice-dictation-*.pkg.tar.zst
```

### Manual Installation

#### Step 1: System Dependencies

```bash
sudo pacman -S --needed python python-pip python-pyaudio python-numpy \
                         python-gobject libadwaita portaudio tk base-devel git
```

#### Step 2: Python Packages

```bash
pip install --user -r docs/requirements.txt
```

#### Step 3: Compile whisper.cpp

```bash
# Automatic
./bin/install-whisper.sh

# Or manual
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make
sudo cp main /usr/local/bin/whisper-cpp

# Download model (e.g. base)
mkdir -p ~/.local/share/whisper/models
cd ~/.local/share/whisper/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

#### Step 4: Install GSettings Schema

```bash
sudo cp data/org.gnome.voicedictation.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## ⚙️ Configuration

### GNOME Settings GUI (recommended)

```bash
voice-dictation-settings
```

The settings app also appears in your GNOME Settings under "Applications".

**Available Settings:**

- 🎹 **Hotkey**: Change keyboard shortcut (Default: Ctrl+Shift+Space)
- 🌍 **Language**: German, English, Spanish, French, Italian, Dutch, Polish, Portuguese, Russian
- 🧠 **Whisper Model**:
  - `tiny` (75 MB) - Fastest, lowest quality
  - `base` (142 MB) - **Recommended** for testing
  - `small` (466 MB) - Good for production
  - `medium` (1.5 GB) - Very good quality
  - `large` (2.9 GB) - Best quality, slow
- 🤫 **Silence Detection**: Adjust threshold and duration
- 🔊 **Audio**: Configure sample rate
- 🚀 **Autostart**: Start automatically on login

### Manual Configuration (Optional)

If GSettings is not available, the system uses `config.json`:

```bash
cp data/config.json.example ~/.config/voice-dictation/config.json
nano ~/.config/voice-dictation/config.json
```

## 📁 Project Structure

```
voice-dictation/
├── bin/                          # Installation scripts
│   ├── install-pkg.sh            # Automated build & install
│   ├── install-whisper.sh        # whisper.cpp setup
│   ├── post-install.sh           # Post-installation
│   └── setup.sh                  # Manual setup
├── src/                          # Source code
│   ├── dictate.py                # Main program
│   └── voice-dictation-settings.py  # Settings GUI
├── data/                         # Data & configuration
│   ├── org.gnome.voicedictation.gschema.xml  # GSettings schema
│   ├── config.json.example       # Example configuration
│   ├── voice-dictation.desktop   # Desktop entry (service)
│   └── voice-dictation-settings.desktop  # Desktop entry (settings)
├── docs/                         # Documentation
│   ├── README.md                 # This file
│   └── requirements.txt          # Python dependencies
├── .github/
│   └── copilot-instructions.md   # GitHub Copilot guidelines
├── build.sh                      # Quick build script
├── PKGBUILD                      # Arch Linux package
├── .SRCINFO                      # AUR metadata
└── .gitignore
```

## 🔧 Technical Details

### Architecture

```
Hotkey (keyboard) → Audio Recording (pyaudio) → Silence Detection (numpy)
                                                      ↓
                    Text Insertion (pynput) ← whisper.cpp (Transcription)
```

### Workflow

1. **Hotkey Registration**: Global via `keyboard` module
2. **Audio Capture**: 16kHz mono via `pyaudio`
3. **RMS Calculation**: Real-time volume analysis with `numpy`
4. **Auto-Stop**: After 2 sec below threshold
5. **WAV Export**: Temporary file for whisper.cpp
6. **Transcription**: Offline via whisper.cpp
7. **Text Injection**: System-wide keyboard simulation

### Whisper Models

| Model  | Size   | Speed     | Quality | Recommendation |
|--------|--------|-----------|---------|----------------|
| tiny   | 75 MB  | ⚡⚡⚡⚡⚡  | ⭐⭐    | Testing        |
| base   | 142 MB | ⚡⚡⚡⚡    | ⭐⭐⭐  | **Start here** |
| small  | 466 MB | ⚡⚡⚡     | ⭐⭐⭐⭐ | Production     |
| medium | 1.5 GB | ⚡⚡       | ⭐⭐⭐⭐⭐| High-End      |
| large  | 2.9 GB | ⚡        | ⭐⭐⭐⭐⭐| Best          |

## 🐛 Troubleshooting

### Microphone not detected

```bash
# Show available devices
arecord -l

# Open PulseAudio mixer
pavucontrol
```

### whisper.cpp not found

```bash
# Check path
which whisper-cpp

# Fix in settings GUI or:
gsettings set org.gnome.voicedictation whisper-cpp-path "/path/to/whisper-cpp"
```

### Model missing

```bash
# Download
cd ~/.local/share/whisper/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

### No audio input

```bash
# Reinstall PyAudio
pip uninstall pyaudio
pip install pyaudio
```

### GSettings schema not found

```bash
# Recompile schema
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Fast whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Original whisper model
- GNOME Project - GTK & Libadwaita

## 💡 Inspiration

This project was inspired by the simple and effective voice input on iOS.
