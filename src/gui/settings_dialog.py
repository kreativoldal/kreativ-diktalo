"""
Settings Dialog

Comprehensive settings panel for customizing the app
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QPushButton, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence

from src.utils.config_manager import ConfigManager
from src.utils.logger import get_logger

logger = get_logger()


class HotkeyEdit(QLineEdit):
    """Custom widget for capturing hotkey combinations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Click and press key combination...")

    def keyPressEvent(self, event):
        """Capture key press and convert to hotkey string"""
        # Ignore modifier keys alone
        if event.key() in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return

        # Build key sequence
        modifiers = event.modifiers()
        key = event.key()

        # Convert to string
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")

        # Add the key
        key_text = QKeySequence(key).toString()
        if key_text:
            parts.append(key_text)

        hotkey = "+".join(parts) if parts else ""
        self.setText(hotkey)


class SettingsDialog(QDialog):
    """
    Settings dialog with multiple tabs

    Tabs:
    - General: Language, theme, startup
    - Hotkeys: Customize keyboard shortcuts
    - Speech: STT provider, model selection
    - Text: LLM settings, cleaning options
    """

    settings_changed = pyqtSignal()  # Emitted when settings are saved

    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._load_settings()

        # Connect theme combo to preview
        self.theme_combo.currentTextChanged.connect(self._preview_theme)

    def _setup_ui(self):
        """Setup UI"""
        self.setWindowTitle("Beállítások")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()

        # Apply initial theme (will be updated in _load_settings)
        current_theme = self.config.get('ui.theme', 'dark')
        self.tabs.setStyleSheet(self._get_stylesheet(current_theme))

        # Create tabs
        self.tabs.addTab(self._create_general_tab(), "Általános")
        self.tabs.addTab(self._create_hotkeys_tab(), "Billentyűk")
        self.tabs.addTab(self._create_speech_tab(), "Beszédfelismerés")
        self.tabs.addTab(self._create_text_tab(), "Szövegtisztítás")

        layout.addWidget(self.tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Mégse")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Mentés")
        self.save_btn.clicked.connect(self._save_settings)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _create_general_tab(self):
        """General settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sötét", "Világos"])
        layout.addRow("Téma:", self.theme_combo)

        # Language
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Magyar", "English"])
        layout.addRow("Nyelv:", self.lang_combo)

        # Window settings
        self.start_minimized_check = QCheckBox("Induláskor minimalizált")
        layout.addRow(self.start_minimized_check)

        self.minimize_to_tray_check = QCheckBox("Bezáráskor tray-be minimalizálás")
        layout.addRow(self.minimize_to_tray_check)

        layout.addRow(QLabel(""))  # Spacer
        return widget

    def _create_hotkeys_tab(self):
        """Hotkeys customization tab"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Dictation hotkey
        self.dictation_hotkey = HotkeyEdit()
        layout.addRow("Diktálás hotkey:", self.dictation_hotkey)

        # Command mode hotkey
        self.command_hotkey = HotkeyEdit()
        layout.addRow("Command mode hotkey:", self.command_hotkey)

        # Info label
        info = QLabel("Kattints a mezőbe és nyomd meg a kívánt billentyűkombinációt")
        info.setStyleSheet("color: gray; font-style: italic;")
        layout.addRow(info)

        layout.addRow(QLabel(""))  # Spacer
        return widget

    def _create_speech_tab(self):
        """Speech recognition settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # STT Provider
        self.stt_provider_combo = QComboBox()
        self.stt_provider_combo.addItems(["Groq (ajánlott)", "AssemblyAI", "Whisper (helyi)"])
        layout.addRow("STT Provider:", self.stt_provider_combo)

        # Language
        self.stt_lang_combo = QComboBox()
        self.stt_lang_combo.addItems(["Magyar (hu)", "English (en)", "Auto"])
        layout.addRow("Felismerési nyelv:", self.stt_lang_combo)

        layout.addRow(QLabel(""))  # Spacer
        return widget

    def _create_text_tab(self):
        """Text cleaning settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Enable text cleaning
        self.enable_cleaning_check = QCheckBox("Szövegtisztítás engedélyezése (LLM)")
        self.enable_cleaning_check.setToolTip(
            "Ha be van kapcsolva, az LLM kijavítja a töltelékszavakat, helyesírást és írásjeleket.\n"
            "Ha ki van kapcsolva, közvetlenül a nyers Whisper szöveget íródik be (gyorsabb)."
        )
        layout.addRow(self.enable_cleaning_check)

        # LLM temperature
        self.llm_temp_spin = QSpinBox()
        self.llm_temp_spin.setRange(0, 100)
        self.llm_temp_spin.setSuffix(" / 100")
        layout.addRow("LLM hőmérséklet:", self.llm_temp_spin)

        # Auto-paste
        self.auto_paste_check = QCheckBox("Automatikus beillesztés")
        layout.addRow(self.auto_paste_check)

        layout.addRow(QLabel(""))  # Spacer
        return widget

    def _load_settings(self):
        """Load settings from config"""
        # General
        theme = self.config.get('ui.theme', 'dark')
        self.theme_combo.setCurrentText("Sötét" if theme == "dark" else "Világos")

        lang = self.config.get('ui.language', 'hu')
        self.lang_combo.setCurrentText("Magyar" if lang == "hu" else "English")

        self.start_minimized_check.setChecked(self.config.get('ui.start_minimized', False))
        self.minimize_to_tray_check.setChecked(self.config.get('ui.minimize_to_tray', True))

        # Hotkeys
        self.dictation_hotkey.setText(self.config.get('hotkeys.dictation', 'F8'))
        self.command_hotkey.setText(self.config.get('hotkeys.command_mode', 'Ctrl+Shift+Space'))

        # Speech
        provider = self.config.get('stt.provider', 'groq')
        provider_map = {'groq': 0, 'assemblyai': 1, 'whisper': 2}
        self.stt_provider_combo.setCurrentIndex(provider_map.get(provider, 0))

        # Text
        self.enable_cleaning_check.setChecked(self.config.get('text_processing.enable_cleaning', True))

        temp = int(self.config.get('ollama.temperature', 0.3) * 100)
        self.llm_temp_spin.setValue(temp)

        self.auto_paste_check.setChecked(self.config.get('keyboard.paste_mode', True))

    def _save_settings(self):
        """Save settings to config"""
        # General
        theme = "dark" if self.theme_combo.currentText() == "Sötét" else "light"
        self.config.set('ui.theme', theme)

        lang = "hu" if self.lang_combo.currentText() == "Magyar" else "en"
        self.config.set('ui.language', lang)

        self.config.set('ui.start_minimized', self.start_minimized_check.isChecked())
        self.config.set('ui.minimize_to_tray', self.minimize_to_tray_check.isChecked())

        # Hotkeys
        self.config.set('hotkeys.dictation', self.dictation_hotkey.text())
        self.config.set('hotkeys.command_mode', self.command_hotkey.text())

        # Speech
        provider_map = {0: 'groq', 1: 'assemblyai', 2: 'whisper'}
        provider = provider_map[self.stt_provider_combo.currentIndex()]
        self.config.set('stt.provider', provider)

        # Text
        self.config.set('text_processing.enable_cleaning', self.enable_cleaning_check.isChecked())

        temp = self.llm_temp_spin.value() / 100.0
        self.config.set('ollama.temperature', temp)

        self.config.set('keyboard.paste_mode', self.auto_paste_check.isChecked())

        # Save to file
        self.config.save()

        logger.info("Settings saved")
        self.settings_changed.emit()
        self.accept()

    def _preview_theme(self, theme_text: str):
        """Preview theme when combo changes"""
        theme = "dark" if theme_text == "Sötét" else "light"
        self.tabs.setStyleSheet(self._get_stylesheet(theme))

    def _get_stylesheet(self, theme: str) -> str:
        """Get stylesheet for given theme"""
        if theme == "dark":
            return """
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2B2B2B;
                }
                QTabBar::tab {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid #555555;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #0078D4;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background-color: #505050;
                }
                QWidget {
                    background-color: #2B2B2B;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #3C3C3C;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    padding: 4px;
                    border-radius: 3px;
                }
                QCheckBox {
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #0078D4;
                    color: #FFFFFF;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #1084D8;
                }
                QPushButton:pressed {
                    background-color: #006CC1;
                }
            """
        else:  # light theme
            return """
                QTabWidget::pane {
                    border: 1px solid #CCCCCC;
                    background-color: #FFFFFF;
                }
                QTabBar::tab {
                    background-color: #F0F0F0;
                    color: #000000;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid #CCCCCC;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #0078D4;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background-color: #E0E0E0;
                }
                QWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    padding: 4px;
                    border-radius: 3px;
                }
                QCheckBox {
                    color: #000000;
                }
                QPushButton {
                    background-color: #0078D4;
                    color: #FFFFFF;
                    border: none;
                    padding: 6px 16px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #1084D8;
                }
                QPushButton:pressed {
                    background-color: #006CC1;
                }
            """
