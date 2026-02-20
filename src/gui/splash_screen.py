"""
Splash Screen

Inicializációs splash screen Whisper modell betöltés közben
"""
from PyQt6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont


class SplashScreen(QSplashScreen):
    """
    Splash screen az alkalmazás indításakor

    Megjeleníti az alkalmazás logót/nevét és egy progress bart
    a Whisper modell betöltésének követéséhez.
    """

    def __init__(self):
        # Create a custom pixmap instead of loading from file
        pixmap = self._create_splash_pixmap()
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        # Message label
        self.message_label = None
        self.progress_bar = None
        self._setup_widgets()

        # Show
        self.show()

    def _create_splash_pixmap(self) -> QPixmap:
        """
        Create a custom splash screen pixmap

        Returns:
            QPixmap with gradient background and title
        """
        width, height = 500, 300
        pixmap = QPixmap(width, height)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        from PyQt6.QtGui import QLinearGradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0.0, QColor("#1E3A5F"))
        gradient.setColorAt(1.0, QColor("#0F1E2E"))
        painter.fillRect(0, 0, width, height, gradient)

        # Title text
        painter.setPen(QColor("#FFFFFF"))
        title_font = QFont("Arial", 32, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Kreatív Diktáló")

        # Subtitle
        subtitle_font = QFont("Arial", 12)
        painter.setFont(subtitle_font)
        painter.setPen(QColor("#AAAAAA"))
        subtitle_rect = pixmap.rect().adjusted(0, 80, 0, 0)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                        "Intelligens magyar diktáló alkalmazás")

        painter.end()
        return pixmap

    def _setup_widgets(self):
        """Setup overlay widgets on splash screen"""
        # Progress bar at bottom
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 5px;
                background-color: #2B2B2B;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #00AA00;
                border-radius: 3px;
            }
        """)

        # Message label
        self.message_label = QLabel("Inicializálás...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                background: transparent;
            }
        """)

        # Layout (using showMessage is simpler, but we want custom widgets)
        # We'll position them manually
        self.progress_bar.setGeometry(50, 220, 400, 25)
        self.progress_bar.setParent(self)

        self.message_label.setGeometry(50, 250, 400, 30)
        self.message_label.setParent(self)

    @pyqtSlot(int, str)
    def update_progress(self, percentage: int, message: str):
        """
        Update splash screen progress

        Args:
            percentage: Progress percentage (0-100)
            message: Status message
        """
        self.progress_bar.setValue(percentage)
        self.message_label.setText(message)
        self.repaint()  # Force immediate repaint

    def finish_loading(self, main_window):
        """
        Close splash screen and show main window

        Args:
            main_window: MainWindow instance
        """
        self.finish(main_window)
