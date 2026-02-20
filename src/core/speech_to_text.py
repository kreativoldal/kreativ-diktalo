"""
Speech-to-Text modul faster-whisper használatával (4-5x gyorsabb mint openai-whisper)
"""
from faster_whisper import WhisperModel
import numpy as np
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from src.utils.logger import get_logger

logger = get_logger()


class SpeechToText:
    """faster-whisper alapú beszédfelismerő - sokkal gyorsabb mint az eredeti"""

    # Elérhető modellek
    MODELS = ['tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en',
              'medium', 'medium.en', 'large-v1', 'large-v2', 'large-v3', 'turbo']

    # Model méretek (aproximált MB-ban)
    MODEL_SIZES = {
        'tiny': 75,
        'tiny.en': 75,
        'base': 150,
        'base.en': 150,
        'small': 500,
        'small.en': 500,
        'medium': 1500,
        'medium.en': 1500,
        'large-v1': 3000,
        'large-v2': 3000,
        'large-v3': 3000,
        'turbo': 1500
    }

    def __init__(
        self,
        model_name: str = "base",
        device: str = "cpu",
        language: str = "auto",
        compute_type: str = "int8"
    ):
        """
        Args:
            model_name: Whisper modell neve (tiny, base, small, medium, large-v3, turbo)
            device: "cuda" GPU-hoz, "cpu" CPU-hoz
            language: Nyelvi kód ("auto", "hu", "en", stb.) vagy None
            compute_type: Számítási típus
                - CPU: "int8" (gyors, ajánlott), "int8_float16", "float32"
                - GPU: "float16" (gyors), "int8_float16", "float32"
        """
        self.model_name = model_name
        self.device = device
        self.language = None if language == "auto" else language

        # CPU-n int8 az optimális (gyors és pontos)
        # GPU-n float16 az optimális
        if device == "cpu" and compute_type == "float16":
            logger.info("CPU-n float16 helyett int8 használata (gyorsabb)")
            compute_type = "int8"

        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None
        self._load_model()

    def _load_model(self):
        """faster-whisper modell betöltése"""
        try:
            logger.info(f"faster-whisper modell betöltése: {self.model_name} ({self.device}, {self.compute_type})")

            if self.model_name not in self.MODELS:
                logger.warning(f"Ismeretlen modell: {self.model_name}, 'base' használata")
                self.model_name = "base"

            # faster-whisper modell betöltés
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=None,  # Default cache directory
                local_files_only=False
            )

            logger.info(f"Modell sikeresen betöltve: {self.model_name} (~{self.MODEL_SIZES.get(self.model_name, '?')}MB)")
            logger.info("faster-whisper: 4-5x gyorsabb mint az eredeti Whisper!")

        except Exception as e:
            logger.error(f"Hiba a modell betöltésekor: {e}")
            raise

    def transcribe_file(
        self,
        audio_path: Union[str, Path],
        beam_size: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Audio fájl átírása szöveggé

        Args:
            audio_path: Audio fájl elérési útja
            beam_size: Beam search méret (1-10, magasabb = pontosabb de lassabb)
            **kwargs: További faster-whisper paraméterek

        Returns:
            Result dictionary:
            {
                'text': str,           # Teljes átírt szöveg
                'segments': list,      # Szegmensek timestamp-ekkel
                'language': str        # Detektált nyelv
            }
        """
        if self.model is None:
            raise RuntimeError("Modell nincs betöltve")

        try:
            audio_path = str(audio_path)
            logger.info(f"Audio átírás kezdése: {audio_path}")

            # faster-whisper transcribe (generator-t ad vissza!)
            segments_generator, info = self.model.transcribe(
                audio_path,
                language=self.language,
                beam_size=beam_size,
                **kwargs
            )

            # Szegmensek összegyűjtése
            segments = []
            full_text = []

            for segment in segments_generator:
                segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                })
                full_text.append(segment.text)

            text = ' '.join(full_text).strip()
            detected_lang = info.language

            logger.info(f"Átírás kész: {len(text)} karakter, nyelv: {detected_lang}")
            logger.debug(f"Szöveg: {text[:100]}...")

            return {
                'text': text,
                'segments': segments,
                'language': detected_lang,
                'language_probability': info.language_probability
            }

        except Exception as e:
            logger.error(f"Hiba az átírás során: {e}")
            raise

    def transcribe_array(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        beam_size: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        NumPy array átírása szöveggé

        Args:
            audio: Audio NumPy array (float32, -1.0 to 1.0)
            sample_rate: Mintavételi frekvencia
            beam_size: Beam search méret
            **kwargs: További faster-whisper paraméterek

        Returns:
            Result dictionary
        """
        if self.model is None:
            raise RuntimeError("Modell nincs betöltve")

        try:
            logger.info(f"Audio átírás NumPy array-ből: {len(audio)} samples, {sample_rate} Hz")
            logger.info(f"Audio stats: min={audio.min():.4f}, max={audio.max():.4f}, mean={np.abs(audio).mean():.4f}")

            # faster-whisper 16kHz-et vár
            if sample_rate != 16000:
                audio = self._resample_audio(audio, sample_rate, 16000)

            # Ensure float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Flatten if needed (remove channel dimension)
            if audio.ndim > 1:
                logger.info(f"Audio shape before flatten: {audio.shape}")
                audio = audio.flatten()
                logger.info(f"Audio shape after flatten: {audio.shape}")

            # faster-whisper transcribe NumPy array-ből
            segments_generator, info = self.model.transcribe(
                audio,
                language=self.language,
                beam_size=beam_size,
                **kwargs
            )

            # Szegmensek összegyűjtése
            segments = []
            full_text = []

            for segment in segments_generator:
                segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                })
                full_text.append(segment.text)

            text = ' '.join(full_text).strip()
            detected_lang = info.language

            logger.info(f"Átírás kész: {len(text)} karakter, nyelv: {detected_lang}")
            logger.debug(f"Szöveg: {text[:100]}...")

            return {
                'text': text,
                'segments': segments,
                'language': detected_lang,
                'language_probability': info.language_probability
            }

        except Exception as e:
            logger.error(f"Hiba az átírás során: {e}")
            raise

    def _resample_audio(
        self,
        audio: np.ndarray,
        orig_sr: int,
        target_sr: int
    ) -> np.ndarray:
        """
        Audio resample (sample rate konverzió)

        Args:
            audio: Audio array
            orig_sr: Eredeti sample rate
            target_sr: Cél sample rate

        Returns:
            Resampled audio
        """
        try:
            from scipy import signal

            # Resample arány
            num_samples = int(len(audio) * target_sr / orig_sr)

            # Scipy resample
            resampled = signal.resample(audio, num_samples)

            logger.debug(f"Resample: {orig_sr} Hz -> {target_sr} Hz")
            return resampled.astype(np.float32)

        except Exception as e:
            logger.error(f"Hiba a resample során: {e}")
            # Fallback: egyszerű interpoláció
            indices = np.linspace(0, len(audio) - 1, int(len(audio) * target_sr / orig_sr))
            return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

    def quick_transcribe(
        self,
        audio_path: Union[str, Path]
    ) -> str:
        """
        Egyszerű átírás - csak a szöveget adja vissza

        Args:
            audio_path: Audio fájl path

        Returns:
            Átírt szöveg
        """
        result = self.transcribe_file(audio_path)
        return result['text']

    def transcribe_with_timestamps(
        self,
        audio_path: Union[str, Path]
    ) -> List[Dict[str, Any]]:
        """
        Átírás timestamp-ekkel (szegmensenként)

        Args:
            audio_path: Audio fájl path

        Returns:
            Lista: [{'start': float, 'end': float, 'text': str}, ...]
        """
        result = self.transcribe_file(audio_path)
        return result['segments']

    def detect_language(self, audio_path: Union[str, Path]) -> str:
        """
        Nyelv detektálása audio fájlból

        Args:
            audio_path: Audio fájl path

        Returns:
            Nyelvi kód (pl. "hu", "en")
        """
        if self.model is None:
            raise RuntimeError("Modell nincs betöltve")

        try:
            audio_path = str(audio_path)
            logger.info(f"Nyelv detektálása: {audio_path}")

            # faster-whisper: csak átírunk 30 mp-et nyelv detektáláshoz
            segments_generator, info = self.model.transcribe(
                audio_path,
                beam_size=1,  # Gyors detektálás
                best_of=1,
                language=None  # Auto-detect
            )

            # Csak az info-ra van szükségünk
            detected_lang = info.language
            prob = info.language_probability

            logger.info(f"Detektált nyelv: {detected_lang} ({prob:.2%})")
            return detected_lang

        except Exception as e:
            logger.error(f"Hiba a nyelv detektáláskor: {e}")
            return "unknown"

    def get_model_info(self) -> dict:
        """
        Modell információk lekérése

        Returns:
            Info dictionary
        """
        return {
            'name': self.model_name,
            'device': self.device,
            'language': self.language or 'auto',
            'compute_type': self.compute_type,
            'size_mb': self.MODEL_SIZES.get(self.model_name, 0),
            'loaded': self.model is not None,
            'engine': 'faster-whisper (4-5x gyorsabb)'
        }

    def cleanup(self):
        """Model felszabadítása memóriából"""
        if self.model is not None:
            del self.model
            self.model = None
            logger.info("faster-whisper modell felszabadítva")


# Teszt funkció
def _test_stt():
    """Egyszerű teszt"""
    import sys

    if len(sys.argv) < 2:
        print("Használat: python speech_to_text.py <audio_fajl.wav>")
        return

    audio_file = sys.argv[1]

    print("faster-whisper STT teszt")
    print(f"Audio: {audio_file}")

    stt = SpeechToText(model_name="base", device="cpu", compute_type="int8")

    print("\nÁtírás...")
    result = stt.transcribe_file(audio_file)

    print(f"\nSzöveg: {result['text']}")
    print(f"Nyelv: {result.get('language', 'unknown')}")

    print("\nSzegmensek:")
    for seg in result.get('segments', []):
        print(f"  [{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")


if __name__ == "__main__":
    _test_stt()
