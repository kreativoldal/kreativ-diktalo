"""
Kreatív Diktáló - Main Entry Point
"""
import sys
import signal
import platform
from pathlib import Path
from typing import Any

# Projekt gyökér hozzáadása a path-hoz
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.utils.config_manager import ConfigManager
from src.core.audio_recorder import AudioRecorder
# NOTE: SpeechToText imported lazily in __init__ to avoid c10.dll crash on import
from src.core.llm_cleaner import LLMCleaner
from src.core.keyboard_sim import KeyboardSimulator

# Platform-specifikus hotkey listener
if platform.system() == 'Windows':
    try:
        from src.core.hotkey_listener_windows import WindowsHotkeyListener as HotkeyListener
    except ImportError:
        from src.core.hotkey_listener import HotkeyListener
else:
    from src.core.hotkey_listener import HotkeyListener


class KreativDiktalo:
    """Fő alkalmazás osztály - CLI verzió (GUI nélkül)"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Args:
            config_path: Konfiguráció fájl elérési útja
        """
        self.config = ConfigManager(config_path)
        self.logger = get_logger()

        # Modulok
        self.audio_recorder: AudioRecorder = None
        self.hotkey_listener: HotkeyListener = None
        self.stt: Any = None
        self.llm: LLMCleaner = None
        self.keyboard: KeyboardSimulator = None

        # Állapot
        self.is_running = False
        self.temp_audio_file = None

        self._initialize_modules()

    def _initialize_modules(self):
        """Modulok inicializálása"""
        self.logger.info("=" * 60)
        self.logger.info("Kreatív Diktáló - Inicializálás")
        self.logger.info("=" * 60)

        # Audio Recorder
        self.logger.info("Audio Recorder betöltése...")
        self.audio_recorder = AudioRecorder(
            sample_rate=self.config.get('audio.sample_rate', 16000),
            channels=self.config.get('audio.channels', 1),
            vad_enabled=self.config.get('audio.vad_enabled', True),
            silence_threshold=self.config.get('audio.silence_threshold', 2.0)
        )
        self.audio_recorder.on_recording_started = self._on_recording_started
        self.audio_recorder.on_recording_stopped = self._on_recording_stopped

        # Speech-to-Text
        self.logger.info("Whisper modell betöltése (ez eltarthat...)...")
        self.stt = SpeechToText(
            model_name=self.config.get('whisper.model', 'large-v3'),
            device=self.config.get('whisper.device', 'cuda'),
            language=self.config.get('whisper.language', 'auto')
        )

        # LLM Cleaner
        self.logger.info("LLM Cleaner inicializálás...")
        self.llm = LLMCleaner(
            host=self.config.get('ollama.host', 'http://localhost:11434'),
            model=self.config.get('ollama.model', 'llama3.1:8b'),
            timeout=self.config.get('ollama.timeout', 30),
            temperature=self.config.get('ollama.temperature', 0.3)
        )

        # Keyboard Simulator
        self.logger.info("Keyboard Simulator inicializálás...")
        self.keyboard = KeyboardSimulator(
            typing_speed=self.config.get('keyboard.typing_speed', 0.01),
            paste_mode=self.config.get('keyboard.paste_mode', True),
            delay_before_type=self.config.get('keyboard.delay_before_type', 0.1)
        )

        # Hotkey Listener
        self.logger.info("Hotkey Listener beállítása...")
        self.hotkey_listener = HotkeyListener()
        dictation_hotkey = self.config.get('hotkeys.dictation', 'F8')
        self.hotkey_listener.register_hotkey(
            dictation_hotkey,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release
        )

        self.logger.info("Inicializálás befejezve!")
        self.logger.info(f"Diktálás hotkey: {dictation_hotkey}")
        self.logger.info(f"Whisper modell: {self.stt.model_name} ({self.stt.device})")
        self.logger.info(f"Ollama elérhető: {self.llm.is_available()}")

    def _on_hotkey_press(self):
        """Hotkey lenyomás - rögzítés indítás"""
        self.logger.info("🎤 Hotkey lenyomva - rögzítés indítása")
        self.audio_recorder.start_recording()

    def _on_hotkey_release(self):
        """Hotkey felengedés - rögzítés leállítás + feldolgozás"""
        self.logger.info("⏹️  Hotkey felengedve - rögzítés leállítása")
        self.audio_recorder.stop_recording()

        # Feldolgozás indítása
        self._process_recording()

    def _on_recording_started(self):
        """Callback: rögzítés elindult"""
        self.logger.info("✅ Rögzítés aktív...")

    def _on_recording_stopped(self):
        """Callback: rögzítés leállt"""
        self.logger.info("⏸️  Rögzítés leállt")

    def _process_recording(self):
        """Rögzített audio feldolgozása: STT → LLM → Keyboard"""
        try:
            self.logger.info("🔄 Feldolgozás indítása...")

            # 1. Audio mentése
            self.logger.info("  [1/4] Audio mentése...")
            self.temp_audio_file = self.audio_recorder.save_to_file()

            if not self.temp_audio_file:
                self.logger.error("❌ Audio mentés sikertelen")
                return

            # 2. Speech-to-Text
            self.logger.info("  [2/4] Beszédfelismerés (Whisper)...")
            stt_result = self.stt.transcribe_file(self.temp_audio_file)
            raw_text = stt_result['text'].strip()

            if not raw_text:
                self.logger.warning("⚠️  Nincs felismert szöveg")
                return

            self.logger.info(f"  ✅ Nyers szöveg: '{raw_text}'")

            # 3. LLM tisztítás (ha engedélyezve)
            enable_cleaning = self.config.get('text_processing.enable_cleaning', True)

            if enable_cleaning:
                self.logger.info("  [3/4] Szövegtisztítás (LLM)...")
                cleaned_text = self.llm.clean_text(raw_text)
                self.logger.info(f"  ✅ Tisztított szöveg: '{cleaned_text}'")
            else:
                self.logger.info("  [3/4] Szövegtisztítás kihagyva (beállítás szerint)")
                cleaned_text = raw_text

            # 4. Billentyűzet beírás
            self.logger.info("  [4/4] Szöveg beírása...")
            result = self.keyboard.type_text(cleaned_text)

            if result.get('success'):
                self.logger.info("✅ Diktálás sikeres!")
            else:
                self.logger.error("❌ Szöveg beírás sikertelen")

        except Exception as e:
            self.logger.error(f"❌ Hiba a feldolgozáskor: {e}", exc_info=True)

    def start(self):
        """Alkalmazás indítása"""
        if self.is_running:
            self.logger.warning("Alkalmazás már fut")
            return

        self.logger.info("\n" + "=" * 60)
        self.logger.info("Kreatív Diktáló elindítva!")
        self.logger.info("=" * 60)
        self.logger.info("Használat:")
        self.logger.info("  1. Nyomd le a hotkey-t (alapértelmezett: F8)")
        self.logger.info("  2. Beszélj a mikrofonba")
        self.logger.info("  3. Engedd fel a hotkey-t")
        self.logger.info("  4. Pár másodperc múlva beíródik a tisztított szöveg!")
        self.logger.info("")
        self.logger.info("Leállítás: Ctrl+C")
        self.logger.info("=" * 60 + "\n")

        self.is_running = True
        self.hotkey_listener.start()

        # Várakozás (blocking)
        try:
            self.hotkey_listener.wait()
        except KeyboardInterrupt:
            self.logger.info("\nCtrl+C észlelve, leállítás...")
            self.stop()

    def stop(self):
        """Alkalmazás leállítása"""
        if not self.is_running:
            return

        self.logger.info("Leállítás folyamatban...")

        self.hotkey_listener.stop()
        self.audio_recorder.cleanup()

        self.is_running = False
        self.logger.info("Kreatív Diktáló leállítva")

    def cleanup(self):
        """Erőforrások felszabadítása"""
        self.stop()

        if self.stt:
            self.stt.cleanup()


def signal_handler(sig, frame):
    """Signal handler a Ctrl+C-hez"""
    print("\n\nLeállítás...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Konfiguráció path
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config.yaml"

    # Logger setup
    log_file = project_root / "data" / "logs" / "app.log"
    setup_logger(level="INFO", log_file=str(log_file))

    logger = get_logger()

    try:
        # Signal handler
        signal.signal(signal.SIGINT, signal_handler)

        # Alkalmazás indítása
        app = KreativDiktalo(str(config_path))
        app.start()

    except Exception as e:
        logger.error(f"Kritikus hiba: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
