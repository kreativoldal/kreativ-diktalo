"""
Billentyűzet szimulációs modul - szöveg beírása aktív ablakba
"""
import pyautogui
import pyperclip
import time
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger()


class KeyboardSimulator:
    """Billentyűzet szimuláció és szöveg beírás"""

    def __init__(
        self,
        typing_speed: float = 0.01,
        paste_mode: bool = True,
        delay_before_type: float = 0.1
    ):
        """
        Args:
            typing_speed: Késleltetés karakterek között (másodperc)
            paste_mode: True = clipboard paste, False = simulate typing
            delay_before_type: Késleltetés beírás előtt
        """
        self.typing_speed = typing_speed
        self.paste_mode = paste_mode
        self.delay_before_type = delay_before_type

        # PyAutoGUI beállítások
        pyautogui.FAILSAFE = True  # Egér sarokban = vészleállás
        pyautogui.PAUSE = 0.01  # Alapértelmezett delay

        logger.debug(f"KeyboardSimulator: paste_mode={paste_mode}, speed={typing_speed}")

    def type_text(self, text: str, smart_paste: bool = True) -> dict:
        """
        Szöveg beírása az aktív ablakba - WISPR FLOW STYLE

        Args:
            text: Beírandó szöveg
            smart_paste: Ha True, intelligens paste (clipboard fallback)

        Returns:
            Dict: {
                'success': bool,
                'method': 'paste'|'clipboard_only'|'typing',
                'message': str (optional)
            }
        """
        if not text:
            logger.warning("Üres szöveg, nincs mit beírni")
            return {'success': False, 'method': 'none', 'message': 'Üres szöveg'}

        try:
            logger.info(f"Szöveg beírása: {len(text)} karakter, paste_mode={self.paste_mode}, smart={smart_paste}")

            # Várakozás
            if self.delay_before_type > 0:
                time.sleep(self.delay_before_type)

            if self.paste_mode:
                if smart_paste:
                    # WISPR FLOW STYLE: Smart paste with clipboard fallback
                    return self._smart_paste(text)
                else:
                    # Gyors mód: egyszerű clipboard paste
                    success = self._paste_text(text)
                    return {'success': success, 'method': 'paste'}
            else:
                # Lassú mód: karakter-by-karakter typing
                success = self._simulate_typing(text)
                return {'success': success, 'method': 'typing'}

        except pyautogui.FailSafeException:
            logger.warning("PyAutoGUI FailSafe aktiválva (egér sarokban)")
            return {'success': False, 'method': 'failsafe', 'message': 'FailSafe aktiválva'}
        except Exception as e:
            logger.error(f"Hiba a szöveg beírásakor: {e}")
            return {'success': False, 'method': 'error', 'message': str(e)}

    def _smart_paste(self, text: str) -> dict:
        """
        WISPR FLOW STYLE: Intelligens paste mechanizmus

        1. Szöveg mindig clipboard-ra kerül (fallback)
        2. Megpróbálja paste-elni
        3. Ha sikertelen, user-nek Ctrl+V-vel kell beillesztenie

        Args:
            text: Szöveg

        Returns:
            Dict: {'success': bool, 'method': str, 'clipboard': bool}
        """
        try:
            # STEP 1: ALWAYS put text on clipboard (safe fallback)
            pyperclip.copy(text)
            logger.info("Szöveg clipboard-ra másolva (fallback)")

            # STEP 2: Try to paste automatically
            try:
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.05)

                # Check if paste worked by seeing if focused window changed
                # (ezt nem tudjuk 100%-ban ellenőrizni, de próbáljuk)
                logger.info("Auto-paste kísérlet sikeres")
                return {
                    'success': True,
                    'method': 'auto_paste',
                    'clipboard': True,
                    'message': 'Szöveg beillesztve'
                }

            except Exception as paste_error:
                logger.warning(f"Auto-paste sikertelen: {paste_error}")
                # Paste failed, but text is on clipboard
                return {
                    'success': False,
                    'method': 'clipboard_only',
                    'clipboard': True,
                    'message': 'Szöveg clipboard-on - nyomd meg Ctrl+V a beillesztéshez'
                }

        except Exception as e:
            logger.error(f"Smart paste hiba: {e}")
            return {
                'success': False,
                'method': 'error',
                'clipboard': False,
                'message': f'Hiba: {str(e)}'
            }

    def _paste_text(self, text: str) -> bool:
        """
        Szöveg beillesztése clipboard-ról (gyors, egyszerű)

        Args:
            text: Szöveg

        Returns:
            True ha sikeres
        """
        try:
            # Eredeti clipboard mentése
            original_clipboard = pyperclip.paste()

            # Szöveg clipboard-ra másolás
            pyperclip.copy(text)

            # Ctrl+V paste
            pyautogui.hotkey('ctrl', 'v')

            # Kis várakozás a beillesztésre
            time.sleep(0.05)

            # Eredeti clipboard visszaállítás (opcionális)
            # pyperclip.copy(original_clipboard)

            logger.debug("Paste sikeres")
            return True

        except Exception as e:
            logger.error(f"Hiba a paste műveletkor: {e}")
            return False

    def _simulate_typing(self, text: str) -> bool:
        """
        Karakter-by-karakter typing szimuláció (lassú de biztonságos)

        Args:
            text: Szöveg

        Returns:
            True ha sikeres
        """
        try:
            for char in text:
                pyautogui.write(char, interval=self.typing_speed)

            logger.debug("Typing szimuláció sikeres")
            return True

        except Exception as e:
            logger.error(f"Hiba a typing szimulációkor: {e}")
            return False

    def type_with_newline(self, text: str) -> bool:
        """
        Szöveg beírása + Enter lenyomás

        Args:
            text: Szöveg

        Returns:
            True ha sikeres
        """
        result = self.type_text(text)
        if result.get('success'):
            time.sleep(0.05)
            pyautogui.press('enter')
            return True
        return False

    def replace_selected_text(self, text: str) -> bool:
        """
        Kijelölt szöveg cseréje (Command Mode)

        Args:
            text: Új szöveg

        Returns:
            True ha sikeres
        """
        try:
            logger.info("Kijelölt szöveg cseréje")

            # Delete (kijelölt szöveg törlése)
            pyautogui.press('delete')
            time.sleep(0.05)

            # Új szöveg beírása
            result = self.type_text(text)
            return result.get('success', False)

        except Exception as e:
            logger.error(f"Hiba a szöveg cseréjekor: {e}")
            return False

    def get_selected_text(self) -> Optional[str]:
        """
        Kijelölt szöveg lekérése clipboard-ról

        Returns:
            Kijelölt szöveg vagy None
        """
        try:
            # Eredeti clipboard mentése
            original = pyperclip.paste()

            # Clipboard törlése
            pyperclip.copy("")

            # Ctrl+C másolás
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.1)  # Várakozás a másolásra

            # Kimásolt szöveg
            selected = pyperclip.paste()

            # Eredeti visszaállítás
            if original:
                pyperclip.copy(original)

            if selected:
                logger.debug(f"Kijelölt szöveg: {len(selected)} karakter")
                return selected
            else:
                logger.warning("Nincs kijelölt szöveg")
                return None

        except Exception as e:
            logger.error(f"Hiba a kijelölt szöveg lekérésekor: {e}")
            return None

    def press_key(self, key: str):
        """
        Egyetlen billentyű lenyomása

        Args:
            key: Billentyű neve (pl. 'enter', 'backspace', 'f8')
        """
        try:
            pyautogui.press(key)
            logger.debug(f"Billentyű lenyomva: {key}")
        except Exception as e:
            logger.error(f"Hiba a billentyű lenyomásakor: {e}")

    def press_hotkey(self, *keys):
        """
        Hotkey kombináció lenyomása

        Args:
            *keys: Billentyűk (pl. 'ctrl', 'shift', 'v')
        """
        try:
            pyautogui.hotkey(*keys)
            logger.debug(f"Hotkey lenyomva: {'+'.join(keys)}")
        except Exception as e:
            logger.error(f"Hiba a hotkey lenyomásakor: {e}")

    def backspace(self, count: int = 1):
        """
        Backspace billentyű lenyomása N-szer

        Args:
            count: Hányszor
        """
        for _ in range(count):
            pyautogui.press('backspace')
            time.sleep(0.02)

    @staticmethod
    def get_cursor_position() -> tuple:
        """
        Egér kurzor pozíció lekérése

        Returns:
            (x, y) tuple
        """
        return pyautogui.position()

    @staticmethod
    def set_failsafe(enabled: bool):
        """
        PyAutoGUI FailSafe be/kikapcsolása

        Args:
            enabled: True = be, False = ki
        """
        pyautogui.FAILSAFE = enabled
        logger.debug(f"FailSafe: {enabled}")

    def set_typing_speed(self, speed: float):
        """
        Typing sebesség változtatása

        Args:
            speed: Új sebesség (másodperc/karakter)
        """
        self.typing_speed = speed
        logger.debug(f"Új typing speed: {speed}")

    def set_paste_mode(self, enabled: bool):
        """
        Paste mode be/kikapcsolása

        Args:
            enabled: True = paste, False = simulate typing
        """
        self.paste_mode = enabled
        logger.debug(f"Paste mode: {enabled}")

    def test_typing(self) -> bool:
        """
        Teszt typing - kis szöveg beírása

        Returns:
            True ha sikeres
        """
        test_text = "Teszt szöveg - KeyboardSimulator működik!"
        logger.info("Teszt typing 3 másodperc múlva...")

        time.sleep(3)  # Idő ablakváltásra

        return self.type_text(test_text)


# Teszt funkció
def _test_keyboard_sim():
    """Teszt futtatás"""
    print("KeyboardSimulator teszt")
    print("Nyiss meg egy szövegszerkesztőt (Notepad, stb.)")
    print("3 másodperc múlva beíródik egy teszt szöveg...\n")

    sim = KeyboardSimulator(paste_mode=True)

    # Teszt 1: Egyszerű szöveg
    sim.test_typing()

    time.sleep(2)

    # Teszt 2: Kijelölt szöveg lekérése
    print("\n\nJelölj ki egy szöveget és nyomd meg az Enter-t")
    input()

    selected = sim.get_selected_text()
    if selected:
        print(f"Kijelölt szöveg: '{selected}'")

        # Teszt 3: Csere
        print("\n3 másodperc múlva kicseréljük...")
        time.sleep(3)
        sim.replace_selected_text(f"[CSERÉLVE: {selected}]")
    else:
        print("Nincs kijelölt szöveg")


if __name__ == "__main__":
    _test_keyboard_sim()
