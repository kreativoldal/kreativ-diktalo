"""
Globális hotkey figyelő modul pynput használatával
"""
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from typing import Callable, Optional, Set, Union
from threading import Thread
from src.utils.logger import get_logger

logger = get_logger()


class HotkeyListener:
    """Globális hotkey figyelő és kezelő"""

    def __init__(self):
        """HotkeyListener inicializálás"""
        self.listener: Optional[keyboard.Listener] = None
        self.is_listening = False

        # Hotkey-k és callback-jeik
        self.hotkeys: dict[str, dict] = {}

        # Aktuálisan lenyomott billentyűk
        self.current_keys: Set[Union[Key, KeyCode]] = set()

    def _normalize_key(self, key: Union[Key, KeyCode, str]) -> str:
        """
        Billentyű normalizálása stringgé

        Args:
            key: Billentyű objektum vagy string

        Returns:
            Normalizált key string
        """
        if isinstance(key, str):
            return key.lower()

        if isinstance(key, KeyCode):
            # Normál karakter billentyű (a, b, c, ...)
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            # VK code alapú
            return f'vk_{key.vk}'

        if isinstance(key, Key):
            # Speciális billentyűk (ctrl, alt, shift, ...)
            return key.name.lower()

        return str(key).lower()

    def _parse_hotkey_string(self, hotkey_str: str) -> Set[str]:
        """
        Hotkey string feldolgozása (pl. "ctrl+shift+a")

        Args:
            hotkey_str: Hotkey string

        Returns:
            Set of key stringek
        """
        parts = [p.strip().lower() for p in hotkey_str.split('+')]
        normalized = set()

        for part in parts:
            # Alias-ok kezelése
            if part in ['control', 'ctrl']:
                normalized.add('ctrl')
            elif part in ['cmd', 'win', 'windows']:
                normalized.add('cmd')
            elif part == 'space':
                normalized.add('space')
            elif part.startswith('f') and part[1:].isdigit():
                # F gombok (f1, f2, ...)
                normalized.add(part)
            else:
                normalized.add(part)

        return normalized

    def register_hotkey(
        self,
        hotkey: str,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None
    ):
        """
        Hotkey regisztrálása callback-ekkel

        Args:
            hotkey: Hotkey string (pl. "F8", "ctrl+shift+space")
            on_press: Callback lenyomáskor
            on_release: Callback felengedéskor
        """
        normalized_keys = self._parse_hotkey_string(hotkey)

        self.hotkeys[hotkey] = {
            'keys': normalized_keys,
            'on_press': on_press,
            'on_release': on_release,
            'is_pressed': False
        }

        logger.info(f"Hotkey regisztrálva: {hotkey} -> {normalized_keys}")

    def unregister_hotkey(self, hotkey: str):
        """
        Hotkey eltávolítása

        Args:
            hotkey: Hotkey string
        """
        if hotkey in self.hotkeys:
            del self.hotkeys[hotkey]
            logger.info(f"Hotkey törölve: {hotkey}")

    def _check_hotkey_match(self) -> Optional[str]:
        """
        Ellenőrzi, hogy az aktuális billentyű kombináció megfelel-e valamelyik hotkeynak

        Returns:
            Egyező hotkey string vagy None
        """
        current_normalized = {self._normalize_key(k) for k in self.current_keys}

        for hotkey_str, hotkey_info in self.hotkeys.items():
            required_keys = hotkey_info['keys']

            # Exact match kell
            if current_normalized == required_keys:
                return hotkey_str

        return None

    def _on_press(self, key: Union[Key, KeyCode]):
        """
        Billentyű lenyomás esemény

        Args:
            key: Lenyomott billentyű
        """
        try:
            self.current_keys.add(key)

            # Hotkey ellenőrzés
            matched_hotkey = self._check_hotkey_match()

            if matched_hotkey:
                hotkey_info = self.hotkeys[matched_hotkey]

                # Csak egyszer hívjuk meg (ne ismételje amíg nyomva van)
                if not hotkey_info['is_pressed']:
                    hotkey_info['is_pressed'] = True

                    logger.debug(f"Hotkey lenyomva: {matched_hotkey}")

                    if hotkey_info['on_press']:
                        try:
                            hotkey_info['on_press']()
                        except Exception as e:
                            logger.error(f"Hiba a hotkey callback-ben: {e}")

        except Exception as e:
            logger.error(f"Hiba a billentyű lenyomás kezelésében: {e}")

    def _on_release(self, key: Union[Key, KeyCode]):
        """
        Billentyű felengedés esemény

        Args:
            key: Felengedett billentyű
        """
        try:
            # Ellenőrizzük előbb a hotkey-t MIELŐTT eltávolítanánk a billentyűt
            matched_hotkey = self._check_hotkey_match()

            if matched_hotkey:
                hotkey_info = self.hotkeys[matched_hotkey]

                if hotkey_info['is_pressed']:
                    hotkey_info['is_pressed'] = False

                    logger.debug(f"Hotkey felengedve: {matched_hotkey}")

                    if hotkey_info['on_release']:
                        try:
                            hotkey_info['on_release']()
                        except Exception as e:
                            logger.error(f"Hiba a hotkey callback-ben: {e}")

            # Billentyű eltávolítása a set-ből
            if key in self.current_keys:
                self.current_keys.remove(key)

        except Exception as e:
            logger.error(f"Hiba a billentyű felengedés kezelésében: {e}")

    def start(self):
        """Hotkey listener indítása"""
        if self.is_listening:
            logger.warning("Listener már fut")
            return

        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )

            self.listener.start()
            self.is_listening = True

            logger.info("Hotkey listener elindult")

        except Exception as e:
            logger.error(f"Hiba a listener indításakor: {e}")

    def stop(self):
        """Hotkey listener leállítása"""
        if not self.is_listening:
            logger.warning("Listener nincs elindítva")
            return

        try:
            if self.listener:
                self.listener.stop()
                self.listener = None

            self.is_listening = False
            self.current_keys.clear()

            logger.info("Hotkey listener leállt")

        except Exception as e:
            logger.error(f"Hiba a listener leállításakor: {e}")

    def wait(self):
        """
        Várakozás a listener befejeződéséig (blocking)
        """
        if self.listener:
            self.listener.join()

    def cleanup(self):
        """Erőforrások felszabadítása"""
        self.stop()
        logger.debug("HotkeyListener cleanup")


# Egyszerű teszt funkció
def _test_hotkey_listener():
    """Teszt futtatás"""
    import time

    def on_f8_press():
        print("F8 lenyomva!")

    def on_f8_release():
        print("F8 felengedve!")

    def on_ctrl_space_press():
        print("Ctrl+Space lenyomva!")

    listener = HotkeyListener()
    listener.register_hotkey("f8", on_press=on_f8_press, on_release=on_f8_release)
    listener.register_hotkey("ctrl+space", on_press=on_ctrl_space_press)

    listener.start()
    print("Hotkey listener fut... (F8 vagy Ctrl+Space)")
    print("Nyomj Ctrl+C-t a kilépéshez")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nLeállítás...")
        listener.stop()


if __name__ == "__main__":
    _test_hotkey_listener()
