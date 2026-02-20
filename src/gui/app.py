"""
Qt Application Wrapper

QApplication wrapper globális beállításokkal és exception handling-gel
"""
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.utils.logger import get_logger

logger = get_logger()


class KreativDiktaloGUI(QApplication):
    """
    Main GUI Application

    Wraps QApplication és kezeli a globális beállításokat és kivételeket
    """

    def __init__(self, argv: list):
        super().__init__(argv)

        # Application metadata
        self.setApplicationName("Kreatív Diktáló")
        self.setOrganizationName("Kreatív Diktáló")
        self.setApplicationVersion("1.0.0")

        # Note: High DPI support is enabled by default in PyQt6

        # Global exception handler
        sys.excepthook = self._exception_handler

        logger.info("GUI Application initialized")

    def _exception_handler(self, exc_type, exc_value, exc_tb):
        """
        Global exception handler

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_tb: Exception traceback
        """
        import traceback

        # Log exception
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.error(f"Unhandled exception:\n{error_msg}")

        # Show error dialog
        QMessageBox.critical(
            None,
            "Kritikus hiba",
            f"Nem kezelt kivétel történt:\n\n{str(exc_value)}\n\n"
            f"Típus: {exc_type.__name__}\n\n"
            f"További részletek a naplófájlban."
        )

        # Exit
        sys.exit(1)
