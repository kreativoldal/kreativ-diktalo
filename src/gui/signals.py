"""
Qt Signal Definitions for Kreatív Diktáló GUI

Centralized signal hub for cross-component communication using Qt's signal/slot pattern.
"""
from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np


class ApplicationSignals(QObject):
    """
    Központi signal hub az összes GUI kommunikációhoz

    Ez az osztály tartalmazza az összes Qt signal-t, amely a GUI komponensek
    közötti kommunikációt biztosítja. A signal/slot pattern thread-safe módot
    biztosít az eseménykezelésre.
    """

    # === STATE SIGNALS ===
    state_changed = pyqtSignal(object, object)  # (old_state, new_state)

    # === RECORDING SIGNALS ===
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    audio_chunk_received = pyqtSignal(np.ndarray)  # Real-time audio chunks

    # === PROCESSING SIGNALS ===
    transcription_started = pyqtSignal()
    transcription_complete = pyqtSignal(str)  # raw_text
    cleaning_started = pyqtSignal()
    cleaning_complete = pyqtSignal(str)  # cleaned_text
    typing_started = pyqtSignal()
    typing_complete = pyqtSignal()
    processing_complete = pyqtSignal()

    # === PROGRESS SIGNALS ===
    stage_changed = pyqtSignal(str)  # "transcribing", "cleaning", "typing"
    progress_updated = pyqtSignal(int, str)  # (percentage, message)

    # === ERROR SIGNALS ===
    error_occurred = pyqtSignal(str, str)  # (title, message)
    warning_occurred = pyqtSignal(str)  # message

    # === CONFIGURATION SIGNALS ===
    config_changed = pyqtSignal(str)  # config_key (e.g., "ui.theme")

    # === STATUS SIGNALS ===
    status_message = pyqtSignal(str, int)  # (message, timeout_ms)

    def __init__(self):
        super().__init__()

    def emit_error(self, title: str, message: str):
        """
        Kényelmi metódus error signal emitelésére

        Args:
            title: Hiba címe
            message: Hiba üzenete
        """
        self.error_occurred.emit(title, message)

    def emit_warning(self, message: str):
        """
        Kényelmi metódus warning signal emitelésére

        Args:
            message: Figyelmeztetés üzenete
        """
        self.warning_occurred.emit(message)

    def emit_status(self, message: str, timeout: int = 3000):
        """
        Kényelmi metódus status üzenet emitelésére

        Args:
            message: Státusz üzenet
            timeout: Megjelenítési idő milliszekundumban
        """
        self.status_message.emit(message, timeout)

    def debug_signal_connections(self):
        """Debug: list all signal connections"""
        from src.utils.logger import get_logger
        logger = get_logger()
        logger.info(f"=== SIGNAL DEBUG ===")
        logger.info(f"transcription_complete receivers: {self.receivers(self.transcription_complete)}")
        logger.info(f"cleaning_complete receivers: {self.receivers(self.cleaning_complete)}")
