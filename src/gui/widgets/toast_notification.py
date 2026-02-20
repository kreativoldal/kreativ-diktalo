"""
Toast Notification Widget - WISPR FLOW STYLE

Lightweight, non-blocking notifications that appear in corner of screen
"""
from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont
from typing import Literal


class ToastNotification(QLabel):
    """
    Toast notification - small popup message that auto-dismisses

    Appears in bottom-right corner, fades in/out automatically
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._is_showing = False

    def _setup_ui(self):
        """Setup UI styling"""
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Styling
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(40, 40, 40, 230);
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
            }
        """)

        self.setFont(QFont("Segoe UI", 11))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Opacity effect for fade in/out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

    def show_message(
        self,
        message: str,
        duration: int = 3000,
        toast_type: Literal['info', 'success', 'warning', 'error'] = 'info'
    ):
        """
        Show toast notification

        Args:
            message: Message text
            duration: Display duration in milliseconds
            toast_type: Type of toast (affects color)
        """
        if self._is_showing:
            # If already showing, just update text
            self.setText(message)
            return

        self._is_showing = True
        self.setText(message)

        # Set color based on type
        colors = {
            'info': 'rgba(40, 40, 40, 230)',
            'success': 'rgba(40, 120, 40, 230)',
            'warning': 'rgba(200, 120, 40, 230)',
            'error': 'rgba(180, 40, 40, 230)'
        }
        bg_color = colors.get(toast_type, colors['info'])

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
            }}
        """)

        # Position in bottom-right corner
        self.adjustSize()
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() - self.width() - 20,
            screen.height() - self.height() - 80
        )

        # Show window
        self.show()

        # Fade in animation
        self.fade_in()

        # Auto-dismiss after duration
        QTimer.singleShot(duration, self.fade_out)

    def fade_in(self):
        """Fade in animation"""
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

    def fade_out(self):
        """Fade out animation"""
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.finished.connect(self._on_fade_out_complete)
        self.animation.start()

    def _on_fade_out_complete(self):
        """Called when fade out animation completes"""
        self.hide()
        self._is_showing = False


class ToastManager:
    """
    Manages multiple toast notifications

    Ensures only one toast is shown at a time, queues if needed
    """

    def __init__(self):
        self.toast = ToastNotification()
        self.queue = []
        self.is_busy = False

    def show(self, message: str, duration: int = 3000, toast_type: str = 'info'):
        """Show toast notification (queues if busy)"""
        if self.is_busy:
            self.queue.append((message, duration, toast_type))
        else:
            self._show_now(message, duration, toast_type)

    def _show_now(self, message: str, duration: int, toast_type: str):
        """Show toast immediately"""
        self.is_busy = True
        self.toast.show_message(message, duration, toast_type)

        # Schedule next from queue
        QTimer.singleShot(duration + 300, self._show_next)

    def _show_next(self):
        """Show next toast from queue"""
        self.is_busy = False
        if self.queue:
            message, duration, toast_type = self.queue.pop(0)
            self._show_now(message, duration, toast_type)
