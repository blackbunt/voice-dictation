#!/usr/bin/env python3
"""
Voice Dictation Settings GUI for GNOME
Configure voice dictation settings through GNOME Settings
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import os
import sys


class VoiceDictationSettings(Adw.PreferencesWindow):
    """Main settings window for Voice Dictation."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.settings = Gio.Settings.new('org.gnome.voicedictation')
        self.set_title('Voice Dictation Settings')
        self.set_default_size(600, 700)
        
        # Create pages
        self._create_general_page()
        self._create_audio_page()
        self._create_advanced_page()
    
    def _create_general_page(self):
        """Create general settings page."""
        page = Adw.PreferencesPage()
        page.set_title('General')
        page.set_icon_name('preferences-system-symbolic')
        
        # Service Group
        service_group = Adw.PreferencesGroup()
        service_group.set_title('Service')
        service_group.set_description('Voice Dictation Service Settings')
        
        # Enable/Disable
        enabled_row = Adw.SwitchRow()
        enabled_row.set_title('Enable Voice Dictation')
        enabled_row.set_subtitle('Enable or disable dictation function')
        self.settings.bind('enabled', enabled_row, 'active', Gio.SettingsBindFlags.DEFAULT)
        service_group.add(enabled_row)
        
        # Autostart
        autostart_row = Adw.SwitchRow()
        autostart_row.set_title('Start automatically')
        autostart_row.set_subtitle('Start automatically on login')
        self.settings.bind('autostart', autostart_row, 'active', Gio.SettingsBindFlags.DEFAULT)
        autostart_row.connect('notify::active', self._on_autostart_changed)
        service_group.add(autostart_row)
        
        # Notifications
        notif_row = Adw.SwitchRow()
        notif_row.set_title('Show notifications')
        notif_row.set_subtitle('Status notifications during recording')
        self.settings.bind('show-notifications', notif_row, 'active', Gio.SettingsBindFlags.DEFAULT)
        service_group.add(notif_row)
        
        page.add(service_group)
        
        # Hotkey Group
        hotkey_group = Adw.PreferencesGroup()
        hotkey_group.set_title('Hotkey')
        hotkey_group.set_description('Keyboard shortcut to start/stop')
        
        # Hotkey Entry
        hotkey_row = Adw.EntryRow()
        hotkey_row.set_title('Activation Hotkey')
        hotkey_row.set_text(self.settings.get_string('hotkey'))
        hotkey_row.connect('changed', self._on_hotkey_changed)
        hotkey_group.add(hotkey_row)
        
        page.add(hotkey_group)
        
        # Language Group
        lang_group = Adw.PreferencesGroup()
        lang_group.set_title('Sprache')
        lang_group.set_description('Recognition language for dictation')
        
        # Language ComboRow
        lang_row = Adw.ComboRow()
        lang_row.set_title('Sprache')
        lang_row.set_subtitle('Language for speech recognition')
        
        lang_model = Gtk.StringList()
        languages = [
            ('Deutsch', 'de'),
            ('English', 'en'),
            ('Español', 'es'),
            ('Français', 'fr'),
            ('Italiano', 'it'),
            ('Nederlands', 'nl'),
            ('Polski', 'pl'),
            ('Português', 'pt'),
            ('Русский', 'ru'),
        ]
        
        current_lang = self.settings.get_string('language')
        selected_index = 0
        
        for i, (name, code) in enumerate(languages):
            lang_model.append(name)
            if code == current_lang:
                selected_index = i
        
        lang_row.set_model(lang_model)
        lang_row.set_selected(selected_index)
        lang_row.connect('notify::selected', self._on_language_changed, languages)
        lang_group.add(lang_row)
        
        page.add(lang_group)
        
        # Model Group
        model_group = Adw.PreferencesGroup()
        model_group.set_title('Whisper Model')
        model_group.set_description('Larger models = better quality, slower')
        
        # Model ComboRow
        model_row = Adw.ComboRow()
        model_row.set_title('Modell')
        model_row.set_subtitle('Whisper model for recognition')
        
        model_model = Gtk.StringList()
        models = [
            ('Tiny (75 MB, fastest)', 'tiny'),
            ('Base (142 MB, recommended)', 'base'),
            ('Small (466 MB, gut)', 'small'),
            ('Medium (1.5 GB, sehr gut)', 'medium'),
            ('Large (2.9 GB, best quality)', 'large'),
        ]
        
        current_model = self.settings.get_string('model')
        selected_index = 1  # default to base
        
        for i, (name, code) in enumerate(models):
            model_model.append(name)
            if code == current_model:
                selected_index = i
        
        model_row.set_model(model_model)
        model_row.set_selected(selected_index)
        model_row.connect('notify::selected', self._on_model_changed, models)
        model_group.add(model_row)
        
        page.add(model_group)
        
        self.add(page)
    
    def _create_audio_page(self):
        """Create audio settings page."""
        page = Adw.PreferencesPage()
        page.set_title('Audio')
        page.set_icon_name('audio-input-microphone-symbolic')
        
        # Silence Detection Group
        silence_group = Adw.PreferencesGroup()
        silence_group.set_title('Silence Detection')
        silence_group.set_description('Configure auto-stop on silence')
        
        # Silence Threshold
        threshold_row = Adw.SpinRow.new_with_range(100, 2000, 50)
        threshold_row.set_title('Silence Threshold')
        threshold_row.set_subtitle('RMS value below which silence is detected')
        self.settings.bind('silence-threshold', threshold_row, 'value', Gio.SettingsBindFlags.DEFAULT)
        silence_group.add(threshold_row)
        
        # Silence Duration
        duration_row = Adw.SpinRow.new_with_range(0.5, 5.0, 0.5)
        duration_row.set_title('Silence Duration')
        duration_row.set_subtitle('Seconds of silence until auto-stop')
        duration_row.set_digits(1)
        self.settings.bind('silence-duration', duration_row, 'value', Gio.SettingsBindFlags.DEFAULT)
        silence_group.add(duration_row)
        
        page.add(silence_group)
        
        # Sample Rate Group
        sample_group = Adw.PreferencesGroup()
        sample_group.set_title('Audio Quality')
        
        # Sample Rate
        sample_row = Adw.ComboRow()
        sample_row.set_title('Sample-Rate')
        sample_row.set_subtitle('Audio sample rate (Whisper requires 16000 Hz)')
        
        sample_model = Gtk.StringList()
        sample_rates = [
            ('16 kHz (Whisper Standard)', 16000),
            ('44.1 kHz (CD Qualität)', 44100),
            ('48 kHz (Studio Qualität)', 48000),
        ]
        
        current_rate = self.settings.get_int('sample-rate')
        selected_index = 0
        
        for i, (name, rate) in enumerate(sample_rates):
            sample_model.append(name)
            if rate == current_rate:
                selected_index = i
        
        sample_row.set_model(sample_model)
        sample_row.set_selected(selected_index)
        sample_row.connect('notify::selected', self._on_sample_rate_changed, sample_rates)
        sample_group.add(sample_row)
        
        page.add(sample_group)
        
        self.add(page)
    
    def _create_advanced_page(self):
        """Create advanced settings page."""
        page = Adw.PreferencesPage()
        page.set_title('Advanced')
        page.set_icon_name('preferences-other-symbolic')
        
        # Paths Group
        paths_group = Adw.PreferencesGroup()
        paths_group.set_title('Paths')
        paths_group.set_description('Whisper.cpp installation and models')
        
        # Whisper.cpp Path
        whisper_row = Adw.EntryRow()
        whisper_row.set_title('whisper-cpp Pfad')
        whisper_row.set_text(self.settings.get_string('whisper-cpp-path'))
        whisper_row.connect('changed', self._on_whisper_path_changed)
        paths_group.add(whisper_row)
        
        # Model Path
        model_path_row = Adw.EntryRow()
        model_path_row.set_title('Model Directory')
        model_path_row.set_text(self.settings.get_string('model-path'))
        model_path_row.connect('changed', self._on_model_path_changed)
        paths_group.add(model_path_row)
        
        page.add(paths_group)
        
        # Info Group
        info_group = Adw.PreferencesGroup()
        info_group.set_title('Information')
        
        # Version
        version_row = Adw.ActionRow()
        version_row.set_title('Voice Dictation')
        version_row.set_subtitle('Version 1.0.0')
        info_group.add(version_row)
        
        # About
        about_row = Adw.ActionRow()
        about_row.set_title('About')
        about_row.set_subtitle('iOS-like dictation function for Linux with whisper.cpp')
        info_group.add(about_row)
        
        page.add(info_group)
        
        self.add(page)
    
    # Callback methods
    def _on_hotkey_changed(self, entry):
        """Handle hotkey change."""
        text = entry.get_text()
        if text:
            self.settings.set_string('hotkey', text)
    
    def _on_language_changed(self, combo, _pspec, languages):
        """Handle language change."""
        selected = combo.get_selected()
        if selected != Gtk.INVALID_LIST_POSITION:
            _, lang_code = languages[selected]
            self.settings.set_string('language', lang_code)
    
    def _on_model_changed(self, combo, _pspec, models):
        """Handle model change."""
        selected = combo.get_selected()
        if selected != Gtk.INVALID_LIST_POSITION:
            _, model_code = models[selected]
            self.settings.set_string('model', model_code)
    
    def _on_sample_rate_changed(self, combo, _pspec, rates):
        """Handle sample rate change."""
        selected = combo.get_selected()
        if selected != Gtk.INVALID_LIST_POSITION:
            _, rate = rates[selected]
            self.settings.set_int('sample-rate', rate)
    
    def _on_whisper_path_changed(self, entry):
        """Handle whisper path change."""
        text = entry.get_text()
        if text:
            self.settings.set_string('whisper-cpp-path', text)
    
    def _on_model_path_changed(self, entry):
        """Handle model path change."""
        text = entry.get_text()
        if text:
            self.settings.set_string('model-path', text)
    
    def _on_autostart_changed(self, switch, _pspec):
        """Handle autostart toggle."""
        autostart_dir = os.path.expanduser('~/.config/autostart')
        desktop_file = os.path.join(autostart_dir, 'voice-dictation.desktop')
        
        if switch.get_active():
            # Enable autostart
            os.makedirs(autostart_dir, exist_ok=True)
            # Copy desktop file
            source = '/usr/share/applications/voice-dictation.desktop'
            if os.path.exists(source):
                import shutil
                shutil.copy(source, desktop_file)
        else:
            # Disable autostart
            if os.path.exists(desktop_file):
                os.remove(desktop_file)


class VoiceDictationApp(Adw.Application):
    """Main application class."""
    
    def __init__(self):
        super().__init__(application_id='org.gnome.VoiceDictationSettings',
                        flags=Gio.ApplicationFlags.FLAGS_NONE)
    
    def do_activate(self):
        """Activate the application."""
        win = VoiceDictationSettings(application=self)
        win.present()


def main():
    """Main entry point."""
    app = VoiceDictationApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    main()
