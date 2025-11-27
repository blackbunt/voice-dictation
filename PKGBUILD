# Maintainer: blackbunt
pkgname=voice-dictation
pkgver=1.0.0
pkgrel=1
pkgdesc="iOS-like voice dictation for Linux using whisper.cpp"
arch=('any')
url="https://github.com/blackbunt/voice-dictation"
license=('MIT')
depends=(
    'python'
    'python-pip'
    'python-pyaudio'
    'python-numpy'
    'python-gobject'
    'libadwaita'
    'portaudio'
    'tk'
)
makedepends=('python-setuptools' 'git' 'make' 'gcc' 'python-build' 'python-installer' 'python-wheel')
install=voice-dictation.install
source=()
sha256sums=()

package() {
    # Create installation directories
    install -dm755 "${pkgdir}/usr/share/${pkgname}"
    install -dm755 "${pkgdir}/usr/share/${pkgname}/bin"
    install -dm755 "${pkgdir}/usr/bin"
    install -dm755 "${pkgdir}/usr/share/applications"
    install -dm755 "${pkgdir}/usr/share/doc/${pkgname}"
    install -dm755 "${pkgdir}/usr/share/glib-2.0/schemas"
    
    # Install main script
    install -Dm755 "${startdir}/src/dictate.py" "${pkgdir}/usr/share/${pkgname}/dictate.py"
    
    # Install settings GUI
    install -Dm755 "${startdir}/src/voice-dictation-settings.py" "${pkgdir}/usr/share/${pkgname}/voice-dictation-settings.py"
    
    # Install helper scripts
    install -Dm755 "${startdir}/bin/install-whisper.sh" "${pkgdir}/usr/share/${pkgname}/bin/install-whisper.sh"
    install -Dm755 "${startdir}/bin/setup.sh" "${pkgdir}/usr/share/${pkgname}/bin/setup.sh"
    
    # Install GSettings schema
    install -Dm644 "${startdir}/data/org.gnome.voicedictation.gschema.xml" \
        "${pkgdir}/usr/share/glib-2.0/schemas/org.gnome.voicedictation.gschema.xml"
    
    # Install configuration example
    install -Dm644 "${startdir}/data/config.json.example" "${pkgdir}/usr/share/${pkgname}/config.json.example"
    
    # Install requirements.txt for reference
    install -Dm644 "${startdir}/docs/requirements.txt" "${pkgdir}/usr/share/doc/${pkgname}/requirements.txt"
    
    # Install README
    install -Dm644 "${startdir}/README.md" "${pkgdir}/usr/share/doc/${pkgname}/README.md"
    
    # Create wrapper script for dictation service
    cat > "${pkgdir}/usr/bin/voice-dictation" << 'EOF'
#!/bin/bash
# Voice Dictation wrapper script
exec python /usr/share/voice-dictation/dictate.py "$@"
EOF
    chmod 755 "${pkgdir}/usr/bin/voice-dictation"
    
    # Create wrapper script for settings GUI
    cat > "${pkgdir}/usr/bin/voice-dictation-settings" << 'EOF'
#!/bin/bash
# Voice Dictation Settings wrapper script
exec python /usr/share/voice-dictation/voice-dictation-settings.py "$@"
EOF
    chmod 755 "${pkgdir}/usr/bin/voice-dictation-settings"
    
    # Install desktop file for the service
    cat > "${pkgdir}/usr/share/applications/voice-dictation.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Voice Dictation
Comment=Systemweite Spracheingabe für Linux
Exec=voice-dictation
Icon=audio-input-microphone
Terminal=false
Categories=Utility;Accessibility;Audio;
StartupNotify=false
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF

    # Install desktop file for settings
    cat > "${pkgdir}/usr/share/applications/voice-dictation-settings.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Voice Dictation Einstellungen
Comment=Voice Dictation Einstellungen konfigurieren
Exec=voice-dictation-settings
Icon=preferences-desktop-keyboard-shortcuts
Terminal=false
Categories=Settings;GNOME;GTK;Audio;Accessibility;
Keywords=voice;speech;dictation;whisper;hotkey;
EOF
}
