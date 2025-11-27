# Voice Dictation for Linux

Eine einfache, iOS-ähnliche Diktierfunktion für Linux mit GNOME Integration, angetrieben von whisper.cpp.

## 🎯 Features

- 🎤 **Toggle-Hotkey**: Drücke Ctrl+Shift+Space zum Starten/Stoppen
- 🤫 **Auto-Stop bei Stille**: Automatisches Beenden nach 2 Sekunden Stille
- 🌐 **Komplett Offline**: Verwendet whisper.cpp - keine Cloud, keine Daten verlassen deinen PC
- 🔌 **Systemweit**: Funktioniert in jeder Anwendung
- ⚙️ **GNOME Integration**: Native Settings-App für einfache Konfiguration
- 🇩🇪 **Mehrsprachig**: Deutsch, English, Español, Français, und mehr
- 📦 **Arch Package**: Saubere Installation via PKGBUILD

## 📸 Verwendung

### Simpel wie unter iOS:

1. **Tastenkürzel drücken** → Aufnahme startet 🔴
2. **Sprechen** (Deutsch oder andere Sprache)
3. **Stille (2 Sek.)** → Aufnahme stoppt automatisch ⏹️
4. **Text erscheint** an der Cursor-Position ✨

**Alternativ:** Tastenkürzel erneut drücken zum manuellen Stoppen.

## 🚀 Installation (Arch Linux)

### Schnellinstallation

```bash
# 1. Repository klonen
git clone https://github.com/yourusername/voice-dictation.git
cd voice-dictation

# 2. Arch-Paket bauen und installieren
./bin/install-pkg.sh

# 3. whisper.cpp installieren
./bin/install-whisper.sh

# 4. Fertig! Starte Voice Dictation
voice-dictation
```

### Manuelle Installation

#### Schritt 1: System-Dependencies

```bash
sudo pacman -S --needed python python-pip python-pyaudio python-numpy \
                         python-gobject libadwaita portaudio tk base-devel git
```

#### Schritt 2: Python-Pakete

```bash
pip install --user -r docs/requirements.txt
```

#### Schritt 3: whisper.cpp kompilieren

```bash
# Automatisch
./bin/install-whisper.sh

# Oder manuell
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make
sudo cp main /usr/local/bin/whisper-cpp

# Modell herunterladen (z.B. base)
mkdir -p ~/.local/share/whisper/models
cd ~/.local/share/whisper/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

#### Schritt 4: GSettings Schema installieren

```bash
sudo cp data/org.gnome.voicedictation.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## ⚙️ Konfiguration

### GNOME Settings GUI (empfohlen)

```bash
voice-dictation-settings
```

Die Settings-App erscheint auch in deinen GNOME-Einstellungen unter "Anwendungen".

**Verfügbare Einstellungen:**

- 🎹 **Hotkey**: Tastenkombination ändern (Standard: Ctrl+Shift+Space)
- 🌍 **Sprache**: Deutsch, English, Español, Français, Italiano, Nederlands, Polski, Português, Русский
- 🧠 **Whisper-Modell**:
  - `tiny` (75 MB) - Schnellst, niedrigste Qualität
  - `base` (142 MB) - **Empfohlen** für Tests
  - `small` (466 MB) - Gut für Produktion
  - `medium` (1.5 GB) - Sehr gute Qualität
  - `large` (2.9 GB) - Beste Qualität, langsam
- 🤫 **Stille-Erkennung**: Schwellwert und Dauer anpassen
- 🔊 **Audio**: Sample-Rate konfigurieren
- 🚀 **Autostart**: Automatisch bei Anmeldung starten

### Manuelle Konfiguration (Optional)

Falls GSettings nicht verfügbar ist, nutzt das System `config.json`:

```bash
cp data/config.json.example ~/.config/voice-dictation/config.json
nano ~/.config/voice-dictation/config.json
```

## 📁 Projekt-Struktur

```
voice-dictation/
├── bin/                          # Installations-Skripte
│   ├── install-pkg.sh            # Arch-Paket bauen & installieren
│   ├── install-whisper.sh        # whisper.cpp Setup
│   ├── post-install.sh           # Post-Installation
│   └── setup.sh                  # Manuelles Setup
├── src/                          # Quellcode
│   ├── dictate.py                # Hauptprogramm
│   └── voice-dictation-settings.py  # Settings GUI
├── data/                         # Daten & Konfiguration
│   ├── org.gnome.voicedictation.gschema.xml  # GSettings Schema
│   ├── config.json.example       # Beispiel-Konfiguration
│   ├── voice-dictation.desktop   # Desktop-Entry (Service)
│   └── voice-dictation-settings.desktop  # Desktop-Entry (Settings)
├── docs/                         # Dokumentation
│   ├── README.md                 # Diese Datei
│   └── requirements.txt          # Python-Dependencies
├── .github/
│   └── copilot-instructions.md   # GitHub Copilot Richtlinien
├── PKGBUILD                      # Arch Linux Paket
├── .SRCINFO                      # AUR Metadaten
└── .gitignore
```

## 🔧 Technische Details

### Architektur

```
Hotkey (keyboard) → Audio-Aufnahme (pyaudio) → Stille-Erkennung (numpy)
                                                      ↓
                    Texteingabe (pynput) ← whisper.cpp (Transkription)
```

### Workflow

1. **Hotkey-Registrierung**: Global via `keyboard` Modul
2. **Audio-Capture**: 16kHz Mono via `pyaudio`
3. **RMS-Berechnung**: Echtzeit-Lautstärke-Analyse mit `numpy`
4. **Auto-Stop**: Nach 2 Sek. unter Schwellwert
5. **WAV-Export**: Temporäre Datei für whisper.cpp
6. **Transkription**: Offline via whisper.cpp
7. **Text-Injection**: Systemweite Keyboard-Simulation

### Whisper-Modelle

| Modell   | Größe  | Geschwindigkeit | Qualität | Empfehlung |
|----------|--------|-----------------|----------|------------|
| tiny     | 75 MB  | ⚡⚡⚡⚡⚡        | ⭐⭐      | Test       |
| base     | 142 MB | ⚡⚡⚡⚡          | ⭐⭐⭐    | **Start**  |
| small    | 466 MB | ⚡⚡⚡           | ⭐⭐⭐⭐  | Produktion |
| medium   | 1.5 GB | ⚡⚡             | ⭐⭐⭐⭐⭐ | High-End   |
| large    | 2.9 GB | ⚡              | ⭐⭐⭐⭐⭐ | Beste      |

## 🐛 Troubleshooting

### Mikrofon wird nicht erkannt

```bash
# Verfügbare Geräte anzeigen
arecord -l

# PulseAudio Mixer öffnen
pavucontrol
```

### whisper.cpp nicht gefunden

```bash
# Pfad überprüfen
which whisper-cpp

# In Settings GUI korrigieren oder:
gsettings set org.gnome.voicedictation whisper-cpp-path "/pfad/zu/whisper-cpp"
```

### Modell fehlt

```bash
# Herunterladen
cd ~/.local/share/whisper/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

### Keine Audio-Eingabe

```bash
# PyAudio neu installieren
pip uninstall pyaudio
pip install pyaudio
```

### GSettings Schema nicht gefunden

```bash
# Schema neu kompilieren
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/
```

## 🤝 Beitragen

Contributions sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Schnelle Whisper-Implementierung
- [OpenAI Whisper](https://github.com/openai/whisper) - Original Whisper-Modell
- GNOME Project - GTK & Libadwaita

## 💡 Inspiration

Dieses Projekt wurde inspiriert von der simplen und effektiven Spracheingabe unter iOS.
