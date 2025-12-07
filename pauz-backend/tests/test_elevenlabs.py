#!/usr/bin/env python3
"""
Test script for ElevenLabs API with voice recording
This script will:
1. Record audio from your microphone
2. Send it to ElevenLabs API
3. Show if the API key is working correctly
"""

import os
import sys
import json
import requests
import pyaudio
import wave
from io import BytesIO

# Configuration
ELEVENLABS_API_KEY = "YOUR_API_KEY_HERE"  # You'll need to replace this
ELEVENLABS_VOICE_ID = "rachel"  # Default voice, can be changed

def record_audio(duration=5, sample_rate=44100, channels=1, chunk=1024):
    """Record audio from microphone"""
    print(f"\n🎤 Recording for {duration} seconds...")
    print("Speak clearly into your microphone...")
    
    audio = pyaudio.PyAudio()
    
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk
    )
    
    frames = []
    
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        
        # Show progress
        progress = int((i / (sample_rate / chunk * duration)) * 20)
        sys.stdout.write(f"\r[{'█' * progress}{'-' * (20 - progress)}]")
        sys.stdout.flush()
    
    print("\n✅ Recording complete!")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    return frames, sample_rate, channels, audio.get_sample_size(pyaudio.paInt16)

def save_audio_to_buffer(frames, sample_rate, channels, sample_width):
    """Save audio frames to a buffer in WAV format"""
    buffer = BytesIO()
    
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    
    buffer.seek(0)
    return buffer

def test_elevenlabs_speech_to_speech(api_key, audio_buffer):
    """Test ElevenLabs API with speech-to-speech conversion"""
    print("\n🔄 Testing ElevenLabs API...")
    
    url = f"https://api.elevenlabs.io/v1/speech-to-speech/{ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key
    }
    
    # Read audio data from buffer
    audio_data = audio_buffer.read()
    
    files = {
        'audio': ('audio.wav', audio_data, 'audio/wav')
    }
    
    data = {
        'model_id': 'eleven_multilingual_v2',
        'voice_settings': json.dumps({
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        })
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API key is working! Speech-to-speech conversion successful.")
            
            # Save the response audio
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)
            print("💾 Response audio saved as 'test_output.mp3'")
            
            return True
        else:
            print("❌ API call failed:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return False

def test_elevenlabs_get_voices(api_key):
    """Test API key by fetching available voices"""
    print("\n🔍 Testing API key by fetching available voices...")
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ API key is valid! Found {len(voices.get('voices', []))} voices available.")
            
            # Show first few voices
            for i, voice in enumerate(voices.get('voices', [])[:5]):
                print(f"  {i+1}. {voice.get('name', 'Unknown')} ({voice.get('voice_id', 'Unknown')})")
            
            return True
        else:
            print("❌ API key validation failed:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return False

def main():
    print("🎵 ElevenLabs API Test Tool")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.getenv('ELEVENLABS_API_KEY') or ELEVENLABS_API_KEY
    
    if api_key == "YOUR_API_KEY_HERE":
        print("❌ Please set your ElevenLabs API key:")
        print("   Option 1: Set ELEVENLABS_API_KEY environment variable")
        print("   Option 2: Edit this script and replace YOUR_API_KEY_HERE")
        return
    
    # First test with a simple API call
    print("\n📋 Step 1: Testing API key with voice list...")
    if not test_elevenlabs_get_voices(api_key):
        print("\n❌ API key is invalid or has issues. Please check your key.")
        return
    
    # Ask user if they want to proceed with voice recording
    print("\n📋 Step 2: Voice recording test")
    choice = input("Do you want to record your voice for a full test? (y/n): ").lower().strip()
    
    if choice == 'y':
        try:
            # Record audio
            frames, sample_rate, channels, sample_width = record_audio(duration=5)
            
            # Save to buffer
            audio_buffer = save_audio_to_buffer(frames, sample_rate, channels, sample_width)
            
            # Test with ElevenLabs
            success = test_elevenlabs_speech_to_speech(api_key, audio_buffer)
            
            if success:
                print("\n🎉 All tests passed! Your ElevenLabs API key is working correctly.")
            else:
                print("\n⚠️  API key works for basic calls but failed on speech-to-speech.")
                print("   This might be a model limitation or quota issue.")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Test cancelled by user.")
        except Exception as e:
            print(f"\n❌ Error during recording: {str(e)}")
            print("   Make sure you have a microphone connected and pyaudio installed.")
    else:
        print("\n✅ Basic API key validation completed. Your key is working!")

if __name__ == "__main__":
    main()