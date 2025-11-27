# Voice Dictation for Linux

Eine einfache Diktierfunktion für Linux, vergleichbar mit der iOS Spracheingabe.

## Features

- 🎤 **Hotkey-Aktivierung**: Drücke einen Hotkey und diktiere sofort
- ⚡ **Echtzeit-Transkription**: Gesprochener Text wird direkt eingefügt
- 🔌 **Systemweit**: Funktioniert in jeder Anwendung
- 🌐 **Offline-fähig**: Nutzt lokale Spracherkennung (optional auch Online)
- 🇩🇪 **Mehrsprachig**: Unterstützt Deutsch, Englisch und weitere Sprachen

## Installation

### Voraussetzungen

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev python3-tk

# Fedora
sudo dnf install python3-pyaudio portaudio-devel python3-tkinter

# Arch
sudo pacman -S python-pyaudio portaudio tk
```

### Python-Pakete installieren

```bash
pip install -r requirements.txt
```

## Verwendung

### Einfacher Start

```bash
python dictate.py
```

Das Programm läuft im Hintergrund. Standard-Hotkey: **Ctrl+Shift+Space**

### Diktat starten

1. Drücke den Hotkey (Ctrl+Shift+Space)
2. Sprich deinen Text
3. Pause oder drücke erneut den Hotkey zum Beenden
4. Der Text wird automatisch an der Cursor-Position eingefügt

### Konfiguration

Erstelle eine `config.json` für eigene Einstellungen:

```json
{
  "hotkey": "<ctrl>+<shift>+space",
  "language": "de-DE",
  "engine": "google"
}
```

**Unterstützte Sprachen:**
- `de-DE` - Deutsch
- `en-US` - Englisch (US)
- `en-GB` - Englisch (UK)

## Autostart einrichten

```bash
# Desktop-Entry erstellen
cp voice-dictation.desktop ~/.config/autostart/
```

## Troubleshooting

### Mikrofon wird nicht erkannt
```bash
# Mikrofon testen
arecord -l
# Standard-Mikrofon setzen
pavucontrol
```

### Keine Audio-Eingabe
```bash
# PyAudio neu installieren
pip uninstall pyaudio
pip install pyaudio
```

## Technische Details

- **Spracherkennung**: Google Speech Recognition API (online) oder CMU Sphinx (offline)
- **Texteingabe**: pynput für Keyboard-Simulation
- **Hotkey-Detection**: keyboard-Modul für globale Hotkeys

## Lizenz

MIT License
