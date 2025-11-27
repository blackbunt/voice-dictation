#!/usr/bin/env python3
"""
Test all available microphone devices
Tries to record 2 seconds from each device and shows which ones work
"""

import pyaudio
import wave
import tempfile
import os
import numpy as np

def test_device(p, device_index, device_name, sample_rate=16000):
    """Test if a device can record audio."""
    print(f"\n{'='*60}")
    print(f"Testing device [{device_index}]: {device_name}")
    print(f"{'='*60}")
    
    try:
        # Try to open stream
        print(f"  Opening stream at {sample_rate}Hz...")
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        print("  ✅ Stream opened successfully!")
        print("  Recording 2 seconds...")
        
        frames = []
        for i in range(0, int(sample_rate / 1024 * 2)):  # 2 seconds
            try:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                print(f"  ❌ Error reading: {e}")
                stream.stop_stream()
                stream.close()
                return False
        
        stream.stop_stream()
        stream.close()
        
        # Calculate RMS to check if we got actual audio
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
        
        print(f"  ✅ Recording successful!")
        print(f"  📊 Average RMS: {rms:.1f}")
        
        if rms < 10:
            print(f"  ⚠️  WARNING: Very low signal - might be wrong device or muted")
        
        # Save test file
        test_file = f"/tmp/mic-test-{device_index}.wav"
        with wave.open(test_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data)
        print(f"  💾 Saved test recording to: {test_file}")
        print(f"  🎧 Play it: aplay {test_file}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

def main():
    print("🎤 Microphone Device Tester")
    print("=" * 60)
    
    p = pyaudio.PyAudio()
    
    # List all input devices
    print("\n📋 Available input devices:\n")
    input_devices = []
    
    for i in range(p.get_device_count()):
        try:
            dev = p.get_device_info_by_index(i)
            max_input = int(dev.get('maxInputChannels', 0))
            if max_input > 0:
                name = dev.get('name', 'Unknown')
                input_devices.append((i, name, dev))
                print(f"  [{i}] {name} (inputs: {max_input})")
        except Exception:
            continue
    
    # Test each device
    print(f"\n\n🧪 Testing {len(input_devices)} devices...\n")
    working_devices = []
    
    for device_index, device_name, dev_info in input_devices:
        # Try multiple sample rates
        for rate in [16000, 44100, 48000]:
            print(f"\nTrying sample rate: {rate}Hz")
            if test_device(p, device_index, device_name, sample_rate=rate):
                working_devices.append((device_index, device_name, rate))
                print(f"  ✅ WORKS with {rate}Hz")
                break  # Found working rate, move to next device
            else:
                print(f"  ❌ Doesn't work with {rate}Hz")
    
    p.terminate()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if working_devices:
        print(f"\n✅ {len(working_devices)} working device(s) found:\n")
        for idx, name, rate in working_devices:
            print(f"  [{idx}] {name}")
            print(f"      Sample rate: {rate}Hz")
            print(f"      Test file: /tmp/mic-test-{idx}.wav")
            print()
        
        print("💡 Recommended for voice-dictation:")
        # Prefer pipewire/pulse
        for idx, name, rate in working_devices:
            if 'pipewire' in name.lower() or 'pulse' in name.lower():
                print(f"   Device [{idx}]: {name} (sample rate: {rate}Hz)")
                break
        else:
            # Otherwise first working device
            idx, name, rate = working_devices[0]
            print(f"   Device [{idx}]: {name} (sample rate: {rate}Hz)")
    else:
        print("\n❌ No working devices found!")
        print("\nTroubleshooting:")
        print("  - Check if microphone is plugged in")
        print("  - Check system audio settings")
        print("  - Run: pactl list sources")
        print("  - Check microphone permissions")

if __name__ == "__main__":
    main()
