"""
ElevenLabs Voice Service for Text-to-Speech and Speech-to-Text
Handles converting text hints and messages to natural-sounding speech
"""

import os
import json
import uuid
import base64
import requests
from typing import Optional, Dict, Any
from io import BytesIO

class VoiceService:
    """Service for converting text to speech and speech to text using ElevenLabs API"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Default voice settings - can be customized
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Adam - warm, gentle voice perfect for journaling
        self.default_model_id = "eleven_multilingual_v2"
        
        # Single consistent friendly voice for ALL interactions
        self.voice_profiles = {
            "hints": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - extra soft and calming for hints
                "stability": 0.2,  # Very natural variation
                "similarity_boost": 0.2,  # Very gentle 
                "style": 0.8,  # Expressive but calming
                "use_speaker_boost": True
            },
            "welcome": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Same Bella voice for consistency
                "stability": 0.3,
                "similarity_boost": 0.3,
                "style": 0.7,
                "use_speaker_boost": True
            },
            "guide": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # SAME Bella voice for all interactions
                "stability": 0.3,
                "similarity_boost": 0.3,
                "style": 0.7,
                "use_speaker_boost": True
            }
        }
    
    def is_available(self) -> bool:
        """Check if ElevenLabs API is configured and available"""
        return self.api_key is not None and self.api_key.strip() != ""
    
    def text_to_speech(
        self, 
        text: str, 
        voice_profile: str = "hints",
        custom_voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert text to speech using ElevenLabs API
        
        Args:
            text: The text to convert to speech
            voice_profile: Predefined voice profile ("hints", "welcome", "guide")
            custom_voice_id: Override voice ID if needed
            
        Returns:
            Dict containing audio data and metadata
        """
        if not self.is_available():
            raise ValueError("ElevenLabs API key not configured")
        
        # Get voice settings
        settings = self.voice_profiles.get(voice_profile, self.voice_profiles["hints"])
        voice_id = custom_voice_id or settings["voice_id"]
        
        # Prepare API request
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": self.default_model_id,
            "voice_settings": {
                "stability": settings["stability"],
                "similarity_boost": settings["similarity_boost"],
                "style": settings["style"],
                "use_speaker_boost": settings["use_speaker_boost"]
            }
        }
        
        try:
            print(f"🎤 Converting text to speech: '{text[:50]}...'")
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                # Convert audio to base64 for easy transmission
                audio_base64 = base64.b64encode(response.content).decode()
                
                result = {
                    "success": True,
                    "audio_data": audio_base64,
                    "content_type": "audio/mpeg",
                    "text": text,
                    "voice_id": voice_id,
                    "voice_profile": voice_profile,
                    "duration_seconds": len(response.content) / 16000,  # Rough estimate
                    "file_size": len(response.content)
                }
                
                print(f"✅ Voice generation successful ({len(response.content)} bytes)")
                return result
                
            else:
                error_msg = f"ElevenLabs API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            error_msg = f"Voice service error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices from ElevenLabs"""
        if not self.is_available():
            return {"success": False, "error": "API key not configured"}
        
        try:
            url = f"{self.base_url}/voices"
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                voices_data = response.json()
                return {
                    "success": True,
                    "voices": voices_data.get("voices", []),
                    "total_count": len(voices_data.get("voices", []))
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch voices: {str(e)}"
            }
    
    def save_audio_to_file(self, audio_base64: str, filename: str) -> str:
        """Save base64 audio data to file (for testing/debugging)"""
        try:
            audio_bytes = base64.b64decode(audio_base64)
            
            # Create audio directory if it doesn't exist
            os.makedirs("audio_output", exist_ok=True)
            
            filepath = f"audio_output/{filename}"
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            
            print(f"💾 Audio saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save audio: {str(e)}")
            raise
    
    def speech_to_text(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Convert speech to text using ElevenLabs Speech-to-Text API
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            Dict containing transcribed text and metadata
        """
        if not self.is_available():
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            print(f"🎤 Converting speech to text...")
            
            # Prepare the request for speech-to-text
            url = f"{self.base_url}/speech-to-text"
            
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            # Prepare the audio file for upload
            files = {
                "file": ("audio.webm", audio_data, "audio/webm")
            }
            
            # Optional parameters for better transcription
            data = {
                "model_id": "scribe_v1",
                "language_code": "eng",  # English
                "include_timestamps": False
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                transcription = {
                    "success": True,
                    "text": result.get("text", "").strip(),
                    "language_code": result.get("language_code", "eng"),
                    "duration_seconds": result.get("duration_seconds", 0),
                    "confidence": result.get("confidence", 0)
                }
                
                print(f"✅ Transcription successful: '{transcription['text'][:50]}...'")
                return transcription
                
            else:
                error_msg = f"ElevenLabs STT error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            error_msg = f"Speech-to-text error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def voice_to_voice_conversation(self, audio_data: bytes, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete voice-to-voice conversation flow using PAUZ Voice Service:
        1. Transcribe user speech to text
        2. Generate contextual response with ongoing conversation memory
        3. Convert response to speech
        
        Args:
            audio_data: User's voice input as bytes
            user_context: Optional user context for personalized responses
            
        Returns:
            Dict containing audio response and metadata
        """
        try:
            # Step 1: Speech to text
            transcription_result = self.speech_to_text(audio_data)
            
            if not transcription_result["success"]:
                return {
                    "success": False,
                    "error": f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
                }
            
            user_text = transcription_result["text"]
            
            # Step 2: Generate response using PAUZ Voice Service with conversation memory
            try:
                from app.services.pauz_voice_service import pauz_voice_service
                response_text = pauz_voice_service.generate_response(
                    user_input=user_text,
                    user_id=str(user_context.get("user_id", "anonymous")) if user_context else "anonymous",
                    user_context=user_context
                )
            except Exception as e:
                print(f"❌ PAUZ Voice response failed, using fallback: {e}")
                # Fallback to basic response
                from app.routes.voice_assistant import get_guidance_response
                response_text = get_guidance_response(user_text, user_id=user_context.get("user_id") if user_context else None)
            
            # Step 3: Text to speech
            voice_result = self.text_to_speech(
                text=response_text,
                voice_profile="guide"
            )
            
            if not voice_result["success"]:
                return {
                    "success": False,
                    "error": f"Voice generation failed: {voice_result.get('error', 'Unknown error')}"
                }
            
            # Complete conversation result
            return {
                "success": True,
                "user_transcription": user_text,
                "assistant_response": response_text,
                "audio_data": voice_result["audio_data"],
                "content_type": voice_result["content_type"],
                "voice_profile": voice_result["voice_profile"],
                "metadata": {
                    "transcription_confidence": transcription_result.get("confidence", 0),
                    "conversation_type": "smart_memory_voice_to_voice",
                    "user_context": user_context,
                    "ai_model": "gemini-2.5-flash",
                    "memory_enabled": True
                }
            }
            
        except Exception as e:
            error_msg = f"Voice-to-voice conversation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }

# Global instance
voice_service = VoiceService()