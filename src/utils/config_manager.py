"""
Konfiguráció kezelő modul
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger()


class ConfigManager:
    """YAML konfiguráció kezelő"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Args:
            config_path: Konfig fájl elérési útja
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Konfiguráció betöltése fájlból"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config fájl nem található: {self.config_path}")
                self._create_default_config()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}

            logger.info(f"Konfiguráció betöltve: {self.config_path}")

        except Exception as e:
            logger.error(f"Hiba a config betöltésekor: {e}")
            self.config = {}

    def _create_default_config(self):
        """Alapértelmezett konfiguráció létrehozása"""
        self.config = {
            'hotkeys': {
                'dictation': 'F8',
                'command_mode': 'ctrl+shift+space'
            },
            'whisper': {
                'model': 'large-v3',
                'language': 'auto',
                'device': 'cuda'
            },
            'ollama': {
                'host': 'http://localhost:11434',
                'model': 'llama3.1:8b',
                'timeout': 30
            },
            'keyboard': {
                'typing_speed': 0.01,
                'paste_mode': True,
                'delay_before_type': 0.1
            },
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'vad_enabled': True,
                'silence_threshold': 0.01
            },
            'ui': {
                'theme': 'dark',
                'language': 'hu',
                'show_preview': True,
                'minimize_to_tray': True
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'data/logs/app.log'
            }
        }
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Konfiguráció érték lekérése

        Args:
            key: Kulcs (pont szeparált, pl. 'whisper.model')
            default: Alapértelmezett érték

        Returns:
            Konfig érték vagy default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Konfiguráció érték beállítása

        Args:
            key: Kulcs (pont szeparált)
            value: Új érték
        """
        keys = key.split('.')
        config = self.config

        # Navigálás a nested dict-ben
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Utolsó kulcs beállítása
        config[keys[-1]] = value
        logger.debug(f"Config beállítva: {key} = {value}")

    def save(self):
        """Konfiguráció mentése fájlba"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Konfiguráció mentve: {self.config_path}")

        except Exception as e:
            logger.error(f"Hiba a config mentésekor: {e}")

    def reload(self):
        """Konfiguráció újratöltése"""
        self._load_config()

    def get_all(self) -> Dict[str, Any]:
        """Teljes konfiguráció dictionary lekérése"""
        return self.config.copy()
