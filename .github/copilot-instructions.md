# GitHub Copilot Instructions

## Project Overview
This is a Voice Dictation system for Linux that provides iOS-like voice input functionality. 
It captures speech via hotkey and converts it to text in real-time, inserting it at the cursor position in any application.

## Development Guidelines

### Code Style
- Use Python type hints for all function parameters and return values
- Follow PEP 8 naming conventions
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Project Structure
- Keep speech recognition and keyboard simulation code separated
- Separate concerns: audio input, speech recognition, keyboard control, and configuration
- Use clear variable names that describe the data they contain
- Main components: voice capture, text recognition, hotkey handling, text insertion

### Error Handling
- Handle microphone access errors gracefully (device not found, permission denied)
- Catch speech recognition timeouts and unknown value errors
- Handle network errors when using online speech recognition
- Validate configuration before starting the service

### Performance
- Minimize latency between speech end and text insertion
- Use threading to avoid blocking the main hotkey detection loop
- Cache recognizer configuration to avoid repeated initialization
- Optimize microphone adjustment for ambient noise

### Dependencies
- Prefer offline speech recognition for privacy when possible
- Support Whisper.cpp for local speech recognition
- Document all required system dependencies (PortAudio, PyAudio)
- Keep dependencies minimal and well-maintained

### Testing
- Test with various microphone devices and audio setups
- Verify text insertion works across different applications
- Test hotkey detection reliability
- Handle edge cases (no microphone, silence, background noise, multiple languages)
