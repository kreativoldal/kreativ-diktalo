"""
Audio rögzítő modul sounddevice használatával
"""
import sounddevice as sd
import numpy as np
import wave
from pathlib import Path
from typing import Optional, Callable
from threading import Thread, Event
import tempfile
from src.utils.logger import get_logger

logger = get_logger()


class AudioRecorder:
    """Mikrofonról audio rögzítés kezelése"""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        vad_enabled: bool = True,
        silence_threshold: float = 0.01,
        silence_duration: float = 1.5
    ):
        """
        Args:
            sample_rate: Mintavételi frekvencia (Hz)
            channels: Csatornák száma (1=mono, 2=stereo)
            chunk_size: Buffer méret
            vad_enabled: Voice Activity Detection be/ki
            silence_threshold: Csend küszöb (amplitúdó)
            silence_duration: Mennyi csend után álljon le (másodperc)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.vad_enabled = vad_enabled
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

        self.is_recording = False
        self.audio_data = []
        self.stream: Optional[sd.InputStream] = None
        self.stop_event = Event()
        self.recording_thread: Optional[Thread] = None

        # Callbacks
        self.on_recording_started: Optional[Callable] = None
        self.on_recording_stopped: Optional[Callable] = None
        self.on_audio_chunk: Optional[Callable[[np.ndarray], None]] = None

        # VAD állapot
        self.silence_chunks = 0
        self.has_speech = False

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        Sounddevice callback - minden audio chunk-nál meghívódik

        Args:
            indata: Audio adatok NumPy array-ben
            frames: Frame-ek száma
            time_info: Időzítés info
            status: Stream státusz
        """
        if status:
            logger.warning(f"Audio stream státusz: {status}")

        # Audio másolása (ne referenciát tároljunk)
        chunk = indata.copy()
        self.audio_data.append(chunk)

        # Callback hívás (pl. vizualizációhoz)
        if self.on_audio_chunk:
            self.on_audio_chunk(chunk)

        # VAD - Voice Activity Detection
        if self.vad_enabled:
            self._process_vad(chunk)

    def _process_vad(self, chunk: np.ndarray):
        """
        Voice Activity Detection - csend detektálás

        Args:
            chunk: Audio chunk
        """
        # RMS (Root Mean Square) számítás - hangerő mérés
        rms = np.sqrt(np.mean(chunk**2))

        if rms < self.silence_threshold:
            # Csend
            self.silence_chunks += 1

            # Ha már volt beszéd és elég hosszú a csend -> stop
            if self.has_speech:
                silence_time = self.silence_chunks * self.chunk_size / self.sample_rate
                if silence_time >= self.silence_duration:
                    logger.info("VAD: Csend detektálva, rögzítés leállítása")
                    self.stop_event.set()
        else:
            # Beszéd detektálva
            self.silence_chunks = 0
            self.has_speech = True

    def start_recording(self) -> bool:
        """
        Audio rögzítés indítása

        Returns:
            True ha sikerült elindítani
        """
        if self.is_recording:
            # Ellenőrzés: a stream ténylegesen él-e még?
            if self.stream and self.stream.active:
                logger.warning("Rögzítés már fut")
                return False
            else:
                # Stream megszakadt (pl. sleep/wake után) - állapot reset
                logger.warning("Audio stream megszakadt - állapot visszaállítása és újrapróbálás")
                self.is_recording = False
                self.stream = None

        try:
            # Reset állapot
            self.audio_data = []
            self.stop_event.clear()
            self.silence_chunks = 0
            self.has_speech = False

            # Stream létrehozása
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._audio_callback,
                blocksize=self.chunk_size
            )

            self.stream.start()
            self.is_recording = True

            logger.info("Audio rögzítés elindult")

            if self.on_recording_started:
                self.on_recording_started()

            return True

        except Exception as e:
            logger.error(f"Hiba az audio rögzítés indításakor: {e}")
            # PortAudio újrainicializálás kísérlet (sleep/wake után szükséges lehet)
            try:
                logger.info("PortAudio újrainicializálása...")
                sd._terminate()
                sd._initialize()
            except Exception as reinit_e:
                logger.error(f"PortAudio reinit hiba: {reinit_e}")
            return False

    def stop_recording(self) -> bool:
        """
        Audio rögzítés leállítása

        Returns:
            True ha sikerült leállítani
        """
        if not self.is_recording:
            logger.warning("Nincs aktív rögzítés")
            return False

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            self.is_recording = False
            logger.info(f"Audio rögzítés leállt. Rögzített chunk-ok: {len(self.audio_data)}")

            if self.on_recording_stopped:
                self.on_recording_stopped()

            return True

        except Exception as e:
            logger.error(f"Hiba az audio rögzítés leállításakor: {e}")
            return False

    def get_recorded_audio(self, normalize: bool = True) -> Optional[np.ndarray]:
        """
        Rögzített audio lekérése NumPy array-ként

        Args:
            normalize: Ha True, automatikus gain alkalmazása (erősítés)

        Returns:
            NumPy array vagy None ha nincs adat
        """
        if not self.audio_data:
            logger.warning("Nincs rögzített audio adat")
            return None

        # Összes chunk összefűzése
        audio_array = np.concatenate(self.audio_data, axis=0)
        logger.info(f"Audio méret: {len(audio_array)} sample, {len(audio_array)/self.sample_rate:.2f} másodperc")

        if normalize:
            # Automatic Gain Control (AGC) - erősítsük fel a halk felvételeket
            max_amp = np.abs(audio_array).max()
            logger.info(f"Audio max amplitúdó: {max_amp:.4f}")

            if max_amp > 0.001:  # Ha van valami jel
                # Normalizálás 0.9-re (kis headroom marad)
                target_peak = 0.9
                gain = target_peak / max_amp
                audio_array = audio_array * gain
                logger.info(f"Auto-gain alkalmazva: {gain:.2f}x erősítés")
            else:
                logger.warning("Audio túlhalk (max < 0.001), nincs használható jel")

        return audio_array

    def save_to_file(self, filepath: Optional[str] = None) -> Optional[str]:
        """
        Rögzített audio mentése WAV fájlba

        Args:
            filepath: Cél fájl path (None = temp file)

        Returns:
            Mentett fájl path vagy None hiba esetén
        """
        audio = self.get_recorded_audio()
        if audio is None:
            return None

        try:
            # Temp file ha nincs megadva path
            if filepath is None:
                temp_dir = Path(tempfile.gettempdir()) / "kreativ-diktalo"
                temp_dir.mkdir(exist_ok=True)
                filepath = str(temp_dir / f"recording_{np.random.randint(10000)}.wav")

            filepath = str(filepath)

            # WAV fájl írás
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)

                # Float32 -> Int16 konverzió
                audio_int16 = (audio * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())

            logger.info(f"Audio mentve: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Hiba az audio mentésekor: {e}")
            return None

    def record_with_duration(self, duration: float) -> Optional[np.ndarray]:
        """
        Megadott ideig rögzít

        Args:
            duration: Rögzítés hossza másodpercben

        Returns:
            Rögzített audio vagy None
        """
        try:
            logger.info(f"Rögzítés indítása {duration} másodpercre")

            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()  # Várunk a rögzítés végére

            logger.info("Rögzítés befejeződött")
            return audio

        except Exception as e:
            logger.error(f"Hiba a rögzítés során: {e}")
            return None

    @staticmethod
    def list_devices() -> list:
        """
        Elérhető audio eszközök listázása

        Returns:
            Eszközök listája
        """
        try:
            devices = sd.query_devices()
            logger.info(f"Elérhető audio eszközök: {len(devices)}")
            return devices
        except Exception as e:
            logger.error(f"Hiba az eszközök lekérésekor: {e}")
            return []

    @staticmethod
    def get_default_device() -> Optional[dict]:
        """
        Alapértelmezett input eszköz lekérése

        Returns:
            Eszköz info vagy None
        """
        try:
            device = sd.query_devices(kind='input')
            logger.info(f"Alapértelmezett input: {device['name']}")
            return device
        except Exception as e:
            logger.error(f"Hiba az alapértelmezett eszköz lekérésekor: {e}")
            return None

    def cleanup(self):
        """Erőforrások felszabadítása"""
        if self.is_recording:
            self.stop_recording()
        logger.debug("AudioRecorder cleanup")
