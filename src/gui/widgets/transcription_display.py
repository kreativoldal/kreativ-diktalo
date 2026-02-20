"""
Transcription Display Widget

Dual-panel megjelenítés a nyers és tisztított szövegnek
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
import pyperclip


class TranscriptionDisplay(QWidget):
    """
    Szöveg megjelenítő widget két panellel

    - Felső panel: Nyers STT szöveg (Whisper kimenet)
    - Alsó panel: Tisztított LLM szöveg

    Mindkét panelnek van másolás gomb.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """UI felépítése"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Splitter a két panel között (méretezhető)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # === Felső panel: Nyers szöveg ===
        raw_panel = QWidget()
        raw_layout = QVBoxLayout(raw_panel)
        raw_layout.setContentsMargins(5, 5, 5, 5)

        # Header
        raw_header = QHBoxLayout()
        raw_label = QLabel("🎤 Nyers szöveg (Whisper)")
        raw_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        raw_header.addWidget(raw_label)
        raw_header.addStretch()

        self.copy_raw_btn = QPushButton("📋 Másolás")
        self.copy_raw_btn.setMaximumWidth(100)
        self.copy_raw_btn.clicked.connect(self._copy_raw_text)
        raw_header.addWidget(self.copy_raw_btn)

        raw_layout.addLayout(raw_header)

        # TextEdit
        self.raw_text_edit = QTextEdit()
        self.raw_text_edit.setReadOnly(True)
        self.raw_text_edit.setPlaceholderText("A nyers felismerés itt jelenik meg...")
        self.raw_text_edit.setFont(QFont("Consolas", 10))
        self.raw_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2B2B2B;
                color: #CCCCCC;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        raw_layout.addWidget(self.raw_text_edit)

        splitter.addWidget(raw_panel)

        # === Alsó panel: Tisztított szöveg ===
        cleaned_panel = QWidget()
        cleaned_layout = QVBoxLayout(cleaned_panel)
        cleaned_layout.setContentsMargins(5, 5, 5, 5)

        # Header
        cleaned_header = QHBoxLayout()
        cleaned_label = QLabel("✨ Tisztított szöveg (LLM)")
        cleaned_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        cleaned_header.addWidget(cleaned_label)
        cleaned_header.addStretch()

        self.copy_cleaned_btn = QPushButton("📋 Másolás")
        self.copy_cleaned_btn.setMaximumWidth(100)
        self.copy_cleaned_btn.clicked.connect(self._copy_cleaned_text)
        cleaned_header.addWidget(self.copy_cleaned_btn)

        cleaned_layout.addLayout(cleaned_header)

        # TextEdit
        self.cleaned_text_edit = QTextEdit()
        self.cleaned_text_edit.setReadOnly(True)
        self.cleaned_text_edit.setPlaceholderText("A tisztított szöveg itt jelenik meg...")
        self.cleaned_text_edit.setFont(QFont("Segoe UI", 11))
        self.cleaned_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        cleaned_layout.addWidget(self.cleaned_text_edit)

        splitter.addWidget(cleaned_panel)

        # Splitter beállítás (50-50%)
        splitter.setSizes([300, 300])

        layout.addWidget(splitter)

        # === Clear All gomb ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.clear_btn = QPushButton("🗑️ Törlés")
        self.clear_btn.setMaximumWidth(100)
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

    @pyqtSlot(str)
    def set_raw_text(self, text: str):
        """
        Nyers szöveg beállítása

        Args:
            text: Nyers STT szöveg
        """
        from src.utils.logger import get_logger
        logger = get_logger()
        logger.info(f"=== TRANSCRIPTION DISPLAY === set_raw_text CALLED! Text: '{text}'")
        logger.info(f"Widget visible: {self.isVisible()}, enabled: {self.isEnabled()}")
        self.raw_text_edit.setPlainText(text)
        logger.info(f"Text set! Current content: '{self.raw_text_edit.toPlainText()}'")

        # Force update
        self.raw_text_edit.update()
        self.update()

    @pyqtSlot(str)
    def set_cleaned_text(self, text: str):
        """
        Tisztított szöveg beállítása

        Args:
            text: Tisztított LLM szöveg
        """
        from src.utils.logger import get_logger
        logger = get_logger()
        logger.info(f"=== TRANSCRIPTION DISPLAY === set_cleaned_text CALLED! Text: '{text}'")
        logger.info(f"Widget visible: {self.isVisible()}, enabled: {self.isEnabled()}")
        self.cleaned_text_edit.setPlainText(text)
        logger.info(f"Text set! Current content: '{self.cleaned_text_edit.toPlainText()}'")

        # Force update
        self.cleaned_text_edit.update()
        self.update()

    def _copy_raw_text(self):
        """Nyers szöveg másolása vágólapra"""
        text = self.raw_text_edit.toPlainText()
        if text:
            pyperclip.copy(text)
            self.copy_raw_btn.setText("✅ Másolva!")
            # Reset after 2 seconds
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.copy_raw_btn.setText("📋 Másolás"))

    def _copy_cleaned_text(self):
        """Tisztított szöveg másolása vágólapra"""
        text = self.cleaned_text_edit.toPlainText()
        if text:
            pyperclip.copy(text)
            self.copy_cleaned_btn.setText("✅ Másolva!")
            # Reset after 2 seconds
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.copy_cleaned_btn.setText("📋 Másolás"))

    def clear_all(self):
        """Mindkét panel törlése"""
        self.raw_text_edit.clear()
        self.cleaned_text_edit.clear()

    def get_raw_text(self) -> str:
        """Nyers szöveg lekérése"""
        return self.raw_text_edit.toPlainText()

    def get_cleaned_text(self) -> str:
        """Tisztított szöveg lekérése"""
        return self.cleaned_text_edit.toPlainText()
