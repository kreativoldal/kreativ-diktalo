"""
AssemblyAI Speech-to-Text Integration

Online API-based transcription with excellent Hungarian support.
185 hours/month free tier.
"""
import requests
import time
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import soundfile as sf
from src.utils.logger import get_logger

logger = get_logger()


class AssemblyAISpeechToText:
    """
    AssemblyAI-based speech recognition

    Features:
    - Excellent Hungarian language support
    - Fast cloud-based processing
    - 185 hours/month free tier
    - Auto-punctuation and capitalization
    """

    def __init__(self, api_key: str, language: str = "hu"):
        """
        Initialize AssemblyAI client (using direct HTTP API)

        Args:
            api_key: AssemblyAI API key
            language: Language code (hu, en, etc.)
        """
        self.api_key = api_key
        self.language = language
        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {
            "authorization": api_key,
            "content-type": "application/json"
        }

        logger.info(f"AssemblyAI inicializálva (language: {language}, HTTP API)")

    def transcribe_file(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file using direct HTTP API

        Args:
            audio_path: Path to audio file

        Returns:
            dict with 'text' and metadata
        """
        logger.info(f"AssemblyAI transcription indítása: {audio_path}")

        try:
            # Step 1: Upload audio file
            with open(audio_path, 'rb') as f:
                upload_response = requests.post(
                    f"{self.base_url}/upload",
                    headers=self.headers,
                    data=f
                )
            upload_response.raise_for_status()
            audio_url = upload_response.json()['upload_url']
            logger.info(f"Audio feltöltve: {audio_url}")

            # Step 2: Request transcription
            transcript_request = {
                "audio_url": audio_url,
                "language_code": self.language,
                "speech_models": ["universal-2"],  # EXPLICIT MODEL!
                "punctuate": True,
                "format_text": True
            }

            transcript_response = requests.post(
                f"{self.base_url}/transcript",
                headers=self.headers,
                json=transcript_request
            )
            transcript_response.raise_for_status()
            transcript_id = transcript_response.json()['id']
            logger.info(f"Transcription ID: {transcript_id}")

            # Step 3: Poll for completion (adaptive polling)
            poll_count = 0
            while True:
                polling_response = requests.get(
                    f"{self.base_url}/transcript/{transcript_id}",
                    headers=self.headers
                )
                polling_response.raise_for_status()
                status_data = polling_response.json()

                if status_data['status'] == 'completed':
                    result = {
                        'text': status_data['text'],
                        'language': self.language,
                        'duration': status_data.get('audio_duration'),
                        'confidence': status_data.get('confidence')
                    }
                    logger.info(f"Transcription kész: {len(result['text'])} karakter (polls: {poll_count})")
                    return result
                elif status_data['status'] == 'error':
                    raise Exception(f"Transcription failed: {status_data.get('error')}")

                poll_count += 1
                # Adaptive polling: start fast, then slow down
                if poll_count < 3:
                    time.sleep(0.5)  # First 3 polls: 0.5s
                elif poll_count < 10:
                    time.sleep(1)    # Next 7 polls: 1s
                else:
                    time.sleep(2)    # After that: 2s

        except Exception as e:
            logger.error(f"AssemblyAI hiba: {str(e)}", exc_info=True)
            raise

    def transcribe_array(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Transcribe audio from numpy array

        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate in Hz

        Returns:
            dict with 'text' and metadata
        """
        logger.info(f"🎤 AssemblyAI transcription (array: {audio.shape}, sr: {sample_rate})")

        # Flatten if needed
        if audio.ndim > 1:
            logger.info(f"Audio shape before flatten: {audio.shape}")
            audio = audio.flatten()
            logger.info(f"Audio shape after flatten: {audio.shape}")

        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Write audio to temp file
            sf.write(tmp_path, audio, sample_rate)
            logger.info(f"📝 Temp audio fájl: {tmp_path}")

            # Transcribe
            result = self.transcribe_file(tmp_path)

            return result

        finally:
            # Clean up temp file
            try:
                Path(tmp_path).unlink()
                logger.debug(f"🗑️ Temp fájl törölve: {tmp_path}")
            except:
                pass

    def is_available(self) -> bool:
        """
        Check if API is available and key is valid

        Returns:
            True if API is accessible
        """
        try:
            # Simple check - try to get account info
            # AssemblyAI doesn't have a simple ping endpoint,
            # so we just assume it's available if API key is set
            return bool(self.api_key)
        except:
            return False
