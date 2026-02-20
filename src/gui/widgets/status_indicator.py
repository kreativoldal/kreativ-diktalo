"""
Status Indicator Widget

Színes LED-szerű indikátor az alkalmazás állapotának megjelenítésére
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QBrush

from src.gui.state_machine import AppState


class StatusLED(QWidget):
    """
    LED indikátor widget - színes kör

    Minimális méret: 20x20 px
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = QColor("#808080")  # Default: szürke
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)

    def set_color(self, color: str):
        """
        LED szín beállítása

        Args:
            color: Hex színkód (pl. "#FF0000")
        """
        self.color = QColor(color)
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Qt paint event - rajzolja meg az LED-et"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Kör rajzolása
        brush = QBrush(self.color)
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 20, 20)


class StatusIndicator(QWidget):
    """
    Státusz indikátor widget: LED + szöveges label

    Megjeleníti az aktuális alkalmazás állapotot színnel és szöveggel
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_state = AppState.INITIALIZING
        self._setup_ui()

    def _setup_ui(self):
        """UI felépítése"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # LED indikátor
        self.led = StatusLED()
        layout.addWidget(self.led)

        # Szöveges label
        self.label = QLabel(AppState.INITIALIZING.display_name)
        self.label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.label)

        # Stretch a végén
        layout.addStretch()

        # Initial state
        self.update_state(AppState.INITIALIZING)

    @pyqtSlot(object, object)
    def on_state_changed(self, old_state: AppState, new_state: AppState):
        """
        Slot: state_changed signal kezelése

        Args:
            old_state: Előző állapot
            new_state: Új állapot
        """
        self.update_state(new_state)

    def update_state(self, state: AppState):
        """
        Állapot frissítése

        Args:
            state: Új állapot
        """
        self._current_state = state

        # LED szín frissítése
        self.led.set_color(state.color)

        # Label szöveg frissítése
        self.label.setText(state.display_name)

        # Label szín frissítése (olvashatóság)
        text_color = self._get_text_color(state)
        self.label.setStyleSheet(
            f"font-weight: bold; font-size: 14px; color: {text_color};"
        )

    def _get_text_color(self, state: AppState) -> str:
        """
        Szöveg szín meghatározása állapot alapján

        Args:
            state: Alkalmazás állapot

        Returns:
            Hex színkód
        """
        # Ha sötét témában vagyunk, világos szín kell
        # Egyszerűsített verzió - mindig ugyanaz
        colors = {
            AppState.INITIALIZING: "#808080",
            AppState.IDLE: "#00DD00",
            AppState.RECORDING: "#FF3333",
            AppState.PROCESSING: "#3333FF",
            AppState.TYPING: "#FF8800",
            AppState.ERROR: "#FFDD00"
        }
        return colors.get(state, "#FFFFFF")

    @property
    def current_state(self) -> AppState:
        """Jelenlegi állapot"""
        return self._current_state
