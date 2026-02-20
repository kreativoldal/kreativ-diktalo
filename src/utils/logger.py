"""
Logging konfiguráció és setup
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class Logger:
    """Központi logging manager"""

    _instance: Optional['Logger'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger("KreativDiktalo")
            self._initialized = True

    def setup(
        self,
        level: str = "INFO",
        log_file: Optional[str] = None,
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5
    ):
        """
        Logging beállítása

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            log_file: Log fájl elérési útja
            max_bytes: Maximális fájlméret rotate előtt
            backup_count: Backup fájlok száma
        """
        # Log level beállítás
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(log_level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (ha meg van adva)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.info("Logging inicializálva")

    def get_logger(self) -> logging.Logger:
        """Logger instance lekérése"""
        return self.logger


# Global logger instance
_logger_instance = Logger()


def get_logger() -> logging.Logger:
    """
    Global logger lekérése

    Returns:
        logging.Logger: Logger instance
    """
    return _logger_instance.get_logger()


def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,
    backup_count: int = 5
):
    """
    Global logger beállítása

    Args:
        level: Log level
        log_file: Log fájl path
        max_bytes: Max file size
        backup_count: Backup count
    """
    _logger_instance.setup(level, log_file, max_bytes, backup_count)
