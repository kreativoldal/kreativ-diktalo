"""
Application State Machine for Kreatív Diktáló

Manages application state transitions and ensures valid state flow.
"""
from enum import Enum
from typing import Optional
from src.utils.logger import get_logger
from src.gui.signals import ApplicationSignals

logger = get_logger()


class AppState(Enum):
    """Alkalmazás állapotok"""
    INITIALIZING = "initializing"  # Whisper modell betöltése
    IDLE = "idle"                  # Kész, várja a hotkey-t
    RECORDING = "recording"        # Audio rögzítés folyamatban
    PROCESSING = "processing"      # STT + LLM feldolgozás
    TYPING = "typing"              # Billentyűzet szimuláció
    ERROR = "error"                # Hiba történt

    def __str__(self):
        return self.value

    @property
    def display_name(self) -> str:
        """Magyar megjelenítési név"""
        names = {
            AppState.INITIALIZING: "Inicializálás",
            AppState.IDLE: "Készen áll",
            AppState.RECORDING: "Rögzítés",
            AppState.PROCESSING: "Feldolgozás",
            AppState.TYPING: "Beírás",
            AppState.ERROR: "Hiba"
        }
        return names.get(self, self.value)

    @property
    def color(self) -> str:
        """Állapothoz tartozó szín (hex)"""
        colors = {
            AppState.INITIALIZING: "#808080",  # Gray
            AppState.IDLE: "#00FF00",          # Green
            AppState.RECORDING: "#FF0000",     # Red
            AppState.PROCESSING: "#0000FF",    # Blue
            AppState.TYPING: "#FFA500",        # Orange
            AppState.ERROR: "#FFFF00"          # Yellow
        }
        return colors.get(self, "#FFFFFF")


class InvalidTransitionError(Exception):
    """Kivétel érvénytelen állapotátmenet esetén"""
    pass


class StateMachine:
    """
    Alkalmazás állapotgép

    Kezeli az állapot átmeneteket és biztosítja hogy csak érvényes
    átmenetek történjenek. Minden állapotváltozás signal-t emit-el.
    """

    # Érvényes átmenetek (from_state -> [to_states])
    VALID_TRANSITIONS = {
        AppState.INITIALIZING: [AppState.IDLE, AppState.ERROR],
        AppState.IDLE: [AppState.RECORDING, AppState.ERROR],
        AppState.RECORDING: [AppState.PROCESSING, AppState.IDLE, AppState.ERROR],
        AppState.PROCESSING: [AppState.TYPING, AppState.IDLE, AppState.ERROR],
        AppState.TYPING: [AppState.IDLE, AppState.ERROR],
        AppState.ERROR: [AppState.IDLE, AppState.INITIALIZING]
    }

    def __init__(self, signals: ApplicationSignals):
        """
        Args:
            signals: ApplicationSignals instance signal emiteléshez
        """
        self.signals = signals
        self._current_state = AppState.INITIALIZING
        self._previous_state: Optional[AppState] = None

    @property
    def current_state(self) -> AppState:
        """Jelenlegi állapot"""
        return self._current_state

    @property
    def previous_state(self) -> Optional[AppState]:
        """Előző állapot"""
        return self._previous_state

    def can_transition_to(self, new_state: AppState) -> bool:
        """
        Ellenőrzi hogy lehetséges-e az átmenet

        Args:
            new_state: Cél állapot

        Returns:
            True ha érvényes az átmenet, különben False
        """
        valid_targets = self.VALID_TRANSITIONS.get(self._current_state, [])
        return new_state in valid_targets

    def transition_to(self, new_state: AppState, force: bool = False):
        """
        Átmenet új állapotba

        Args:
            new_state: Cél állapot
            force: Ha True, kihagyja a validációt (óvatosan használd!)

        Raises:
            InvalidTransitionError: Ha nem érvényes az átmenet és force=False
        """
        # Ugyanaz az állapot - nincs átmenet
        if new_state == self._current_state:
            logger.debug(f"Már ebben az állapotban vagyunk: {new_state}")
            return

        # Validáció (ha nincs force)
        if not force and not self.can_transition_to(new_state):
            error_msg = (
                f"Érvénytelen állapotátmenet: "
                f"{self._current_state.value} -> {new_state.value}"
            )
            logger.error(error_msg)
            raise InvalidTransitionError(error_msg)

        # Átmenet végrehajtása
        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state

        logger.info(
            f"Állapotátmenet: {old_state.value} -> {new_state.value}"
        )

        # Signal emitelés
        self.signals.state_changed.emit(old_state, new_state)

    def is_idle(self) -> bool:
        """Idle állapotban van-e"""
        return self._current_state == AppState.IDLE

    def is_recording(self) -> bool:
        """Rögzítés állapotban van-e"""
        return self._current_state == AppState.RECORDING

    def is_processing(self) -> bool:
        """Feldolgozás állapotban van-e"""
        return self._current_state == AppState.PROCESSING

    def is_error(self) -> bool:
        """Hiba állapotban van-e"""
        return self._current_state == AppState.ERROR

    def reset(self):
        """
        Visszaállítás IDLE állapotra

        Használd recovery után vagy újraindításkor
        """
        logger.info("State machine reset to IDLE")
        self.transition_to(AppState.IDLE, force=True)

    def __str__(self):
        return f"StateMachine(current={self._current_state.value})"

    def __repr__(self):
        return (
            f"StateMachine(current={self._current_state.value}, "
            f"previous={self._previous_state.value if self._previous_state else None})"
        )
