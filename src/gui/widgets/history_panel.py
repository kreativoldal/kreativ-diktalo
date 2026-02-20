"""
History Panel Widget

Shows history of all dictations with ability to copy/paste later
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont
import pyperclip
from datetime import datetime
from typing import List, Dict


class HistoryItem:
    """Single dictation history item"""

    def __init__(self, raw_text: str, cleaned_text: str, timestamp: datetime = None):
        self.raw_text = raw_text
        self.cleaned_text = cleaned_text
        self.timestamp = timestamp or datetime.now()

    def __str__(self):
        time_str = self.timestamp.strftime("%H:%M:%S")
        preview = self.cleaned_text[:50] + "..." if len(self.cleaned_text) > 50 else self.cleaned_text
        return f"[{time_str}] {preview}"


class HistoryPanel(QWidget):
    """
    History panel showing all past dictations

    Features:
    - List of all dictations with timestamps
    - Click to view full raw + cleaned text
    - Copy button to copy to clipboard
    - Paste button to insert at current cursor
    """

    # Signals
    paste_requested = pyqtSignal(str)  # When user wants to paste a history item

    def __init__(self, parent=None, max_items: int = 50):
        super().__init__(parent)
        self.max_items = max_items
        self.history_items: List[HistoryItem] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QHBoxLayout()
        title = QLabel("📜 Előzmények")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        header.addWidget(title)
        header.addStretch()

        self.clear_btn = QPushButton("🗑️ Törlés")
        self.clear_btn.setMaximumWidth(80)
        self.clear_btn.clicked.connect(self.clear_history)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        # Splitter: List on left, details on right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === LEFT: History list ===
        self.history_list = QListWidget()
        self.history_list.setFont(QFont("Consolas", 9))
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #2B2B2B;
                color: #CCCCCC;
                border: 1px solid #404040;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #404040;
            }
        """)
        self.history_list.currentItemChanged.connect(self._on_selection_changed)

        splitter.addWidget(self.history_list)

        # === RIGHT: Details panel ===
        details_panel = QWidget()
        details_layout = QVBoxLayout(details_panel)
        details_layout.setContentsMargins(5, 0, 0, 0)

        # Raw text
        raw_label = QLabel("🎤 Nyers")
        raw_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        details_layout.addWidget(raw_label)

        self.raw_preview = QTextEdit()
        self.raw_preview.setReadOnly(True)
        self.raw_preview.setMaximumHeight(100)
        self.raw_preview.setFont(QFont("Consolas", 9))
        self.raw_preview.setStyleSheet("""
            QTextEdit {
                background-color: #2B2B2B;
                color: #CCCCCC;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        details_layout.addWidget(self.raw_preview)

        # Cleaned text
        cleaned_label = QLabel("✨ Tisztított")
        cleaned_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        details_layout.addWidget(cleaned_label)

        self.cleaned_preview = QTextEdit()
        self.cleaned_preview.setReadOnly(True)
        self.cleaned_preview.setFont(QFont("Segoe UI", 10))
        self.cleaned_preview.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        details_layout.addWidget(self.cleaned_preview)

        # Buttons
        button_layout = QHBoxLayout()

        self.copy_btn = QPushButton("📋 Másolás")
        self.copy_btn.clicked.connect(self._copy_selected)
        button_layout.addWidget(self.copy_btn)

        self.paste_btn = QPushButton("📝 Beillesztés")
        self.paste_btn.clicked.connect(self._paste_selected)
        button_layout.addWidget(self.paste_btn)

        details_layout.addLayout(button_layout)

        splitter.addWidget(details_panel)

        # Set splitter sizes (40% list, 60% details)
        splitter.setSizes([200, 300])

        layout.addWidget(splitter)

    @pyqtSlot(str, str)
    def add_item(self, raw_text: str, cleaned_text: str):
        """Add new dictation to history"""
        item = HistoryItem(raw_text, cleaned_text)
        self.history_items.insert(0, item)  # Add to beginning (newest first)

        # Limit to max_items
        if len(self.history_items) > self.max_items:
            self.history_items = self.history_items[:self.max_items]

        # Update list
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the history list widget"""
        self.history_list.clear()
        for item in self.history_items:
            list_item = QListWidgetItem(str(item))
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.history_list.addItem(list_item)

    def _on_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """When user selects a history item"""
        if not current:
            self.raw_preview.clear()
            self.cleaned_preview.clear()
            return

        item: HistoryItem = current.data(Qt.ItemDataRole.UserRole)
        self.raw_preview.setPlainText(item.raw_text)
        self.cleaned_preview.setPlainText(item.cleaned_text)

    def _copy_selected(self):
        """Copy selected item to clipboard"""
        current = self.history_list.currentItem()
        if not current:
            return

        item: HistoryItem = current.data(Qt.ItemDataRole.UserRole)
        pyperclip.copy(item.cleaned_text)

        # Visual feedback
        original_text = self.copy_btn.text()
        self.copy_btn.setText("✅ Másolva!")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.copy_btn.setText(original_text))

    def _paste_selected(self):
        """Paste selected item (emits signal for smart paste)"""
        current = self.history_list.currentItem()
        if not current:
            return

        item: HistoryItem = current.data(Qt.ItemDataRole.UserRole)
        self.paste_requested.emit(item.cleaned_text)

    def clear_history(self):
        """Clear all history"""
        self.history_items.clear()
        self.history_list.clear()
        self.raw_preview.clear()
        self.cleaned_preview.clear()

    def get_all_items(self) -> List[HistoryItem]:
        """Get all history items"""
        return self.history_items.copy()
