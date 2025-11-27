#!/usr/bin/env python3
"""
Voice Dictation for Linux using whisper.cpp
Voice-to-text dictation triggered via GNOME keyboard shortcut
"""

import pyaudio
import wave
from pynput.keyboard import Controller
import time
import sys
import json
import os
import subprocess
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional

try:
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio
    HAS_GSETTINGS = True
except (ImportError, ValueError):
    HAS_GSETTINGS = False
    print("⚠️  GSettings not available, using config.json")


class VoiceDictation:
    """Main class for voice dictation functionality using whisper.cpp."""
    
    def __init__(self, config_path: Optional[str] = None, use_gsettings: bool = True):
        """
        Initialize the voice dictation system.
        
        Args:
            config_path: Path to configuration file (optional, fallback if no GSettings)
            use_gsettings: Use GSettings if available (default: True)
        """
        self.use_gsettings = use_gsettings and HAS_GSETTINGS
        
        if self.use_gsettings:
            try:
                self.settings = Gio.Settings.new('org.gnome.voicedictation')
                self.config = self._load_from_gsettings()
                print("✅ Using GSettings for configuration")
            except Exception as e:
                print(f"⚠️  GSettings error: {e}, using config.json")
                self.use_gsettings = False
                self.config = self._load_config(config_path)
        else:
            self.config = self._load_config(config_path)
        
        self.keyboard_controller = Controller()
        self.is_recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.pyaudio_instance = None
        # Adaptive silence threshold: will be calculated from initial noise floor
        self.silence_threshold = self.config.get('silence_threshold', 500)
        self.silence_duration = self.config.get('silence_duration', 2.0)
        self.last_sound_time = None
        self.noise_floor = None  # Will be measured during recording
        
        # Validate whisper.cpp installation
        self._check_whisper_installation()
        
        print("🎤 Voice Dictation for Linux (whisper.cpp)")
        print(f"Hotkey: {self.config['hotkey']}")
        print(f"Model: {self.config['model']}")
        print(f"Language: {self.config['language']}")
        print("Ready to dictate!")
    
    def _load_from_gsettings(self) -> dict:
        """Load configuration from GSettings."""
        return {
            "hotkey": self.settings.get_string('hotkey').replace('<', '').replace('>', '+').lower(),
            "language": self.settings.get_string('language'),
            "model": self.settings.get_string('model'),
            "whisper_cpp_path": os.path.expanduser(self.settings.get_string('whisper-cpp-path')),
            "model_path": os.path.expanduser(self.settings.get_string('model-path')),
            "silence_threshold": self.settings.get_int('silence-threshold'),
            "silence_duration": self.settings.get_double('silence-duration'),
            "sample_rate": self.settings.get_int('sample-rate'),
            "channels": 1,
            "enabled": self.settings.get_boolean('enabled'),
            "show_notifications": self.settings.get_boolean('show-notifications'),
        }
        print(f"Sprache: {self.config['language']}")
        print("Bereit zum Diktieren!")
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "hotkey": "ctrl+shift+space",
            "language": "de",
            "model": "base",
            "whisper_cpp_path": os.path.expanduser("~/.local/bin/whisper-cli"),
            "model_path": os.path.expanduser("~/.local/share/whisper/whisper.cpp/models"),
            "silence_threshold": 500,
            "silence_duration": 2.0,
            "sample_rate": 16000,
            "channels": 1,
            "input_device": "auto"  # "auto" | "pulse" | device name substring
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ Fehler beim Laden der Config: {e}")
        
        return default_config
    
    def _check_whisper_installation(self) -> None:
        """Check if whisper.cpp is installed and accessible."""
        whisper_path = self.config['whisper_cpp_path']
        
        # Check common locations
        possible_paths = [
            whisper_path,
            os.path.expanduser('~/.local/bin/whisper-cli'),
            '/usr/bin/whisper-cli',
            '/usr/local/bin/whisper-cli',
            '/usr/bin/whisper-cpp',
            '/usr/local/bin/whisper-cpp'
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.config['whisper_cpp_path'] = path
                return
        
        print("❌ whisper.cpp not found!")
        print("Please install whisper.cpp:")
        print("  Run: /usr/share/voice-dictation/bin/install-whisper.sh")
        sys.exit(1)
    
    def _download_model(self, model_name: str, model_dir: Path) -> bool:
        """Download whisper model if not present."""
        try:
            print(f"📥 Downloading model: {model_name}")
            print(f"   This may take a few minutes depending on model size...")
            
            # Ensure model directory exists
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Use whisper.cpp download script if available
            whisper_cpp_dir = Path.home() / '.local/share/whisper/whisper.cpp'
            download_script = whisper_cpp_dir / 'models/download-ggml-model.sh'
            
            if download_script.exists():
                # Use official download script
                result = subprocess.run(
                    ['bash', str(download_script), model_name],
                    cwd=str(whisper_cpp_dir / 'models'),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Move model to correct location if needed
                    source_model = whisper_cpp_dir / f'models/ggml-{model_name}.bin'
                    target_model = model_dir / f'ggml-{model_name}.bin'
                    
                    if source_model.exists() and source_model != target_model:
                        import shutil
                        shutil.copy2(str(source_model), str(target_model))
                    
                    print(f"✅ Model downloaded: {target_model}")
                    return True
                else:
                    print(f"❌ Download failed: {result.stderr}")
                    return False
            else:
                # Fallback: direct download from HuggingFace
                url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{model_name}.bin"
                target = model_dir / f"ggml-{model_name}.bin"
                
                result = subprocess.run(
                    ['wget', '-O', str(target), url],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"✅ Model downloaded: {target}")
                    return True
                else:
                    print(f"❌ Download failed: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
    
    def _get_model_path(self) -> str:
        """Get the path to the whisper model file."""
        model_dir = Path(self.config['model_path'])
        model_name = self.config['model']
        model_file = model_dir / f"ggml-{model_name}.bin"
        
        if not model_file.exists():
            print(f"⚠️  Model not found: {model_file}")
            print(f"🔄 Attempting to download model...")
            
            if self._download_model(model_name, model_dir):
                return str(model_file)
            else:
                print(f"\n❌ Failed to download model automatically.")
                print(f"Please download manually:")
                print(f"  mkdir -p {model_dir}")
                print(f"  cd {model_dir}")
                print(f"  wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{model_name}.bin")
                sys.exit(1)
        
        return str(model_file)
    
    def _calculate_rms(self, audio_data: bytes) -> float:
        """Calculate RMS (Root Mean Square) of audio data."""
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        return np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
    
    def _type_text(self, text: str) -> None:
        """
        Type the recognized text at the current cursor position.
        
        Args:
            text: Text to type
        """
        if not text or text.strip() == "":
            return
        
        # Clean up the text
        text = text.strip()
        
        # Small delay to ensure the application is ready
        time.sleep(0.1)
        
        # Type the text
        self.keyboard_controller.type(text)
        print(f"✅ Inserted: {text}")
    
    def _record_audio(self) -> None:
        """Record audio from microphone until stopped or silence detected."""
        print("📡 Initializing PyAudio...")
        self.pyaudio_instance = pyaudio.PyAudio()
        
        try:
            # List available input devices for debugging
            print("\n📋 Available input devices:")
            try:
                device_count = self.pyaudio_instance.get_device_count()
                for i in range(device_count):
                    try:
                        dev = self.pyaudio_instance.get_device_info_by_index(i)
                        max_input = int(dev.get('maxInputChannels', 0))
                        if max_input > 0:
                            print(f"   [{i}] {dev.get('name', 'Unknown')} (inputs: {max_input})")
                    except Exception:
                        continue
            except Exception as e:
                print(f"   ⚠️  Could not list devices: {e}")
            print()
            
            # Try to pick best input device
            # Priority: pipewire/pulse (with resampling) > hardware mic > built-in > default
            device_index = None
            desired = (self.config.get('input_device') or 'auto').lower()
            
            # Priority ranking for auto mode
            # Prefer pipewire/pulse because they handle resampling automatically
            pipewire_device = None
            pulse_device = None
            hardware_mic = None  # Direct hardware like ALC285, HDA
            builtin_device = None
            default_device = None

            try:
                device_count = self.pyaudio_instance.get_device_count()
            except Exception:
                device_count = 0

            for i in range(device_count):
                try:
                    dev = self.pyaudio_instance.get_device_info_by_index(i)
                    name = dev.get('name', '').lower()
                    max_input = int(dev.get('maxInputChannels', 0))
                    if max_input < 1:
                        continue
                    
                    # Explicit device selection (by substring or index)
                    if desired != 'auto':
                        # Check if desired is a device index
                        try:
                            if int(desired) == i:
                                device_index = i
                                print(f"🔌 Matched requested device index {desired}: [{i}] {dev.get('name')}")
                                break
                        except ValueError:
                            pass
                        
                        # Otherwise match by name substring
                        if desired in name:
                            device_index = i
                            print(f"🔌 Matched requested device '{desired}': [{i}] {dev.get('name')}")
                            break
                        continue
                    
                    # Auto mode: collect candidates by priority
                    if 'pipewire' in name and pipewire_device is None:
                        pipewire_device = i
                    elif 'pulse' in name and pulse_device is None:
                        pulse_device = i
                    # Hardware devices (ALSA hw:X,Y) - direct mic access
                    elif ('alc' in name or 'hda' in name or 'analog' in name) and 'hw:' in name and hardware_mic is None:
                        hardware_mic = i
                    elif 'built-in' in name and builtin_device is None:
                        builtin_device = i
                    elif 'default' in name and default_device is None:
                        default_device = i
                        
                except Exception:
                    continue

            # Auto mode: select best available (prefer sound servers for resampling support)
            if desired == 'auto':
                if pipewire_device is not None:
                    device_index = pipewire_device
                    dev_info = self.pyaudio_instance.get_device_info_by_index(device_index)
                    print(f"🔌 Selected pipewire: [{device_index}] {dev_info.get('name')}")
                elif pulse_device is not None:
                    device_index = pulse_device
                    dev_info = self.pyaudio_instance.get_device_info_by_index(device_index)
                    print(f"🔌 Selected pulse: [{device_index}] {dev_info.get('name')}")
                elif builtin_device is not None:
                    device_index = builtin_device
                    dev_info = self.pyaudio_instance.get_device_info_by_index(device_index)
                    print(f"🔌 Selected built-in: [{device_index}] {dev_info.get('name')}")
                elif hardware_mic is not None:
                    device_index = hardware_mic
                    dev_info = self.pyaudio_instance.get_device_info_by_index(device_index)
                    print(f"🔌 Selected hardware mic: [{device_index}] {dev_info.get('name')}")
                elif default_device is not None:
                    device_index = default_device
                    dev_info = self.pyaudio_instance.get_device_info_by_index(device_index)
                    print(f"🔌 Selected default: [{device_index}] {dev_info.get('name')}")
                else:
                    print("🔌 Using system default input device")
            elif device_index is None:
                print(f"⚠️  Requested device '{desired}' not found, using system default")

            print(f"🔌 Opening audio stream (rate={self.config['sample_rate']}, channels={self.config['channels']})...")
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=self.config['channels'],
                rate=self.config['sample_rate'],
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            print("🎤 Recording... (speak now)")
            start_time = time.time()
            self.last_sound_time = start_time
            grace_period = 1.0  # seconds before we consider silence (increased)
            min_recording_time = 1.5  # minimum recording duration in seconds
            max_recording_time = 30.0  # maximum recording duration in seconds
            has_detected_sound = False  # track if we've detected any sound above threshold
            
            # Measure noise floor in first 0.5 seconds (skip first few to avoid initialization spike)
            noise_samples = []
            calibration_time = 0.8
            skip_initial = 0.2  # Skip first 0.2s to avoid initialization spikes
            
            while self.is_recording:
                try:
                    data = self.audio_stream.read(1024, exception_on_overflow=False)
                    self.audio_frames.append(data)
                    
                    # Check for silence
                    rms = self._calculate_rms(data)
                    current_time = time.time()
                    elapsed = current_time - start_time
                    
                    # Calibrate noise floor between 0.2s and 0.8s (skip initialization spike)
                    if elapsed >= skip_initial and elapsed < calibration_time:
                        noise_samples.append(rms)
                        continue
                    
                    # After calibration, set adaptive threshold
                    if self.noise_floor is None and len(noise_samples) > 0:
                        # Use median instead of mean to ignore outliers
                        self.noise_floor = np.median(noise_samples)
                        # Set threshold to 3x noise floor, capped between 8000-15000
                        adaptive_threshold = self.noise_floor * 3.0
                        adaptive_threshold = max(8000, min(adaptive_threshold, 15000))
                        print(f"🔊 Noise floor: {self.noise_floor:.0f}, Threshold: {adaptive_threshold:.0f}")
                        self.silence_threshold = adaptive_threshold
                    
                    # Debug: occasional RMS log
                    if int(elapsed * 4) % 4 == 0:  # log every 0.25s
                        is_sound = "🗣️" if rms > self.silence_threshold else "🤫"
                        print(f"{is_sound} RMS={rms:.0f} | {elapsed:.1f}s")
                    
                    # Maximum recording time safety
                    if elapsed > max_recording_time:
                        print(f"⏸️  Maximum recording time ({max_recording_time}s) reached - stopping...")
                        self.is_recording = False
                        break
                    
                    # During grace period, don't stop on silence
                    if elapsed < grace_period:
                        if rms > self.silence_threshold:
                            has_detected_sound = True
                        self.last_sound_time = current_time
                        continue
                    
                    # Don't stop before minimum recording time
                    if elapsed < min_recording_time:
                        if rms > self.silence_threshold:
                            has_detected_sound = True
                            self.last_sound_time = current_time
                        continue

                    # Normal silence detection after grace + minimum time
                    if rms > self.silence_threshold:
                        has_detected_sound = True
                        self.last_sound_time = current_time
                    elif has_detected_sound and (current_time - self.last_sound_time > self.silence_duration):
                        print(f"⏸️  Silence detected after {elapsed:.1f}s - stopping recording...")
                        self.is_recording = False
                        break
                        
                except Exception as e:
                    print(f"⚠️  Recording error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error opening microphone: {e}")
            self.is_recording = False
        finally:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
    
    def _transcribe_with_whisper(self, audio_file: str) -> Optional[str]:
        """
        Transcribe audio file using whisper.cpp.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            whisper_path = self.config['whisper_cpp_path']
            model_file = self._get_model_path()
            language = self.config.get('language', 'de')
            threads = max(1, os.cpu_count() or 1)

            # Build command (use whisper-cli)
            cmd = [
                whisper_path,
                '-m', model_file,
                '-f', audio_file,
                '--language', language,
                '--threads', str(threads),
                '--no-timestamps'
            ]
            print(f"🛠️  Running: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print("❌ whisper.cpp error")
                if result.stderr:
                    print(result.stderr)
                else:
                    print(result.stdout)
                return None

            output = result.stdout.strip()
            if not output:
                print("ℹ️  whisper.cpp returned no output")
                return None

            # Parse lines, ignoring logging prefixes
            lines = [l.strip() for l in output.splitlines() if l.strip()]
            text = ' '.join(lines)
            print(f"🧾 whisper.cpp raw output: {text}")
            return text if text else None
        except subprocess.TimeoutExpired:
            print("❌ whisper.cpp timeout")
            return None
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None

    def _save_and_transcribe(self) -> None:
        """Save recorded audio frames, transcribe, and type the result."""
        if not self.audio_frames:
            print("⚠️  No audio captured. Try setting input_device to 'pulse' or lowering silence_threshold.")
            return
        
        print(f"📊 Captured {len(self.audio_frames)} audio frames")
        
        # Calculate total duration
        bytes_per_frame = 2 * self.config['channels']  # 16-bit = 2 bytes
        samples_per_frame = 1024
        total_samples = len(self.audio_frames) * samples_per_frame
        duration = total_samples / self.config['sample_rate']
        print(f"⏱️  Audio duration: {duration:.2f} seconds")
        
        # Save debug wav of last recording
        try:
            debug_wav = "/tmp/voice-dictation-last.wav"
            with wave.open(debug_wav, 'wb') as wf:
                wf.setnchannels(self.config['channels'])
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.config['sample_rate'])
                wf.writeframes(b''.join(self.audio_frames))
            print(f"🧪 Saved last recording to {debug_wav}")
        except Exception as e:
            print(f"⚠️  Could not save debug wav: {e}")

        # Filter out whisper hallucinations
        print("🔄 Transcribing with whisper.cpp...")

        # Save audio to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name
            
            # Convert to WAV format
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(self.config['channels'])
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.config['sample_rate'])
                wf.writeframes(b''.join(self.audio_frames))

        # Transcribe
        text = self._transcribe_with_whisper(temp_path)

        # Clean up
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

        # Filter out common whisper hallucinations for short/silent audio
        if text:
            text_lower = text.lower()
            hallucinations = ['[musik]', '[music]', '(musik)', '(music)', 
                            'untertitel', 'subtitle', 'www.', 'amara.org']
            is_hallucination = any(h in text_lower for h in hallucinations)
            
            if is_hallucination:
                print(f"⚠️  Detected hallucination/noise pattern: '{text}' - ignoring")
                print("💡 Tip: Speak longer sentences for better recognition")
                return
            
            self._type_text(text)
        else:
            print("ℹ️  No text recognized")
    
    def run(self) -> None:
        """Run a single dictation session - record, transcribe, and type."""
        print("\n🎤 Voice Dictation started")
        print("🔴 Recording... (speak now, auto-stops after 2 seconds of silence)")
        
        # Start recording
        self.is_recording = True
        self.audio_frames = []
        
        # Record audio until silence or stop
        self._record_audio()

        # Save, transcribe and type the recorded audio
        self._save_and_transcribe()
        
        print("👋 Dictation session complete\n")


def main():
    """Main entry point."""
    # Check for config file
    config_file = "config.json"
    if not os.path.exists(config_file):
        config_file = None
    
    # Create and run dictation system
    dictation = VoiceDictation(config_path=config_file)
    dictation.run()


if __name__ == "__main__":
    main()
