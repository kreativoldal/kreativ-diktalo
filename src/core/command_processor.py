"""
Command Mode feldolgozó - szöveg átalakítás hangparancsokkal
"""
from typing import Optional, Dict
from src.core.speech_to_text import SpeechToText
from src.core.llm_cleaner import LLMCleaner
from src.core.keyboard_sim import KeyboardSimulator
from src.utils.logger import get_logger

logger = get_logger()


class CommandProcessor:
    """Command Mode kezelő - szöveg módosítás hangparancsokkal"""

    # Előre definiált parancs sablonok
    DEFAULT_COMMANDS = {
        'barátságos': 'Írd át a szöveget barátságosabb, melegebb hangnemben',
        'fordítsd angol': 'Fordítsd le a szöveget angolra',
        'fordítsd magyar': 'Fordítsd le a szöveget magyarra',
        'rövidítsd': 'Rövidítsd le a szöveget, tartsd meg a lényeget',
        'javítsd': 'Javítsd ki a helyesírási és nyelvtani hibákat',
        'lista': 'Alakítsd át a szöveget pontokba szedett listává',
        'hosszabbítsd': 'Bővítsd ki a szöveget részletesebben',
        'egyszerűsítsd': 'Egyszerűsítsd le a szöveget, használj egyszerűbb szavakat',
        'formális': 'Írd át formálisabb, hivatalosabb hangnemben',
        'email': 'Alakítsd át email formátumúvá címzéssel és aláírással'
    }

    def __init__(
        self,
        stt: SpeechToText,
        llm: LLMCleaner,
        keyboard: KeyboardSimulator
    ):
        """
        Args:
            stt: SpeechToText instance
            llm: LLMCleaner instance
            keyboard: KeyboardSimulator instance
        """
        self.stt = stt
        self.llm = llm
        self.keyboard = keyboard

        logger.info("CommandProcessor inicializálva")

    def process_audio_command(
        self,
        audio_path: str,
        selected_text: Optional[str] = None
    ) -> Optional[str]:
        """
        Audio parancs feldolgozása

        Args:
            audio_path: Audio fájl elérési útja (parancs)
            selected_text: Kijelölt szöveg (None = clipboard-ról veszi)

        Returns:
            Módosított szöveg vagy None
        """
        try:
            # 1. Parancs átírása
            logger.info("Parancs felismerése audio-ból...")
            command_result = self.stt.transcribe_file(audio_path)
            command = command_result['text'].strip().lower()

            logger.info(f"Felismert parancs: '{command}'")

            # 2. Kijelölt szöveg lekérése (ha nincs megadva)
            if selected_text is None:
                logger.info("Kijelölt szöveg lekérése...")
                selected_text = self.keyboard.get_selected_text()

                if not selected_text:
                    logger.error("Nincs kijelölt szöveg")
                    return None

            logger.info(f"Kijelölt szöveg: {len(selected_text)} karakter")

            # 3. Parancs feldolgozása LLM-mel
            logger.info("Szöveg módosítása LLM-mel...")
            modified_text = self._execute_command(selected_text, command)

            if not modified_text:
                logger.error("LLM nem adott vissza eredményt")
                return None

            logger.info(f"Módosított szöveg: {len(modified_text)} karakter")
            return modified_text

        except Exception as e:
            logger.error(f"Hiba a parancs feldolgozásakor: {e}")
            return None

    def process_text_command(
        self,
        command: str,
        selected_text: Optional[str] = None
    ) -> Optional[str]:
        """
        Text parancs feldolgozása (audio nélkül)

        Args:
            command: Parancs szövegként
            selected_text: Kijelölt szöveg

        Returns:
            Módosított szöveg vagy None
        """
        try:
            # Kijelölt szöveg lekérése ha nincs megadva
            if selected_text is None:
                selected_text = self.keyboard.get_selected_text()

                if not selected_text:
                    logger.error("Nincs kijelölt szöveg")
                    return None

            # Parancs végrehajtása
            modified_text = self._execute_command(selected_text, command)
            return modified_text

        except Exception as e:
            logger.error(f"Hiba a parancs feldolgozásakor: {e}")
            return None

    def _execute_command(self, text: str, command: str) -> Optional[str]:
        """
        Parancs végrehajtása LLM-mel

        Args:
            text: Eredeti szöveg
            command: Parancs

        Returns:
            Módosított szöveg vagy None
        """
        # Előre definiált parancs ellenőrzése
        matched_template = self._match_command_template(command)

        if matched_template:
            logger.info(f"Előre definiált parancs használata: {matched_template}")
            command_prompt = self.DEFAULT_COMMANDS[matched_template]
        else:
            logger.info("Egyedi parancs használata")
            command_prompt = command

        # LLM hívás
        modified_text = self.llm.process_command(text, command_prompt)

        return modified_text

    def _match_command_template(self, command: str) -> Optional[str]:
        """
        Parancs egyeztetése előre definiált sablonokkal

        Args:
            command: Felhasználói parancs

        Returns:
            Egyező sablon kulcs vagy None
        """
        command_lower = command.lower()

        # Egyszerű substring matching
        for key in self.DEFAULT_COMMANDS.keys():
            if key in command_lower:
                return key

        return None

    def execute_and_replace(
        self,
        audio_path: Optional[str] = None,
        command: Optional[str] = None
    ) -> bool:
        """
        Teljes Command Mode flow: parancs feldolgozás + szöveg csere

        Args:
            audio_path: Audio fájl (hangparancs) vagy None
            command: Text parancs vagy None

        Returns:
            True ha sikeres
        """
        try:
            # 1. Parancs feldolgozása
            if audio_path:
                modified_text = self.process_audio_command(audio_path)
            elif command:
                modified_text = self.process_text_command(command)
            else:
                logger.error("Sem audio sem text parancs nincs megadva")
                return False

            if not modified_text:
                return False

            # 2. Szöveg cseréje
            logger.info("Szöveg cseréje az aktív ablakban...")
            success = self.keyboard.replace_selected_text(modified_text)

            if success:
                logger.info("Command Mode sikeres!")
            else:
                logger.error("Szöveg csere sikertelen")

            return success

        except Exception as e:
            logger.error(f"Hiba a command végrehajtáskor: {e}")
            return False

    def get_available_commands(self) -> Dict[str, str]:
        """
        Elérhető parancsok listája

        Returns:
            Dictionary: parancs -> leírás
        """
        return self.DEFAULT_COMMANDS.copy()

    def add_custom_command(self, trigger: str, prompt: str):
        """
        Egyedi parancs hozzáadása

        Args:
            trigger: Parancs trigger szó
            prompt: LLM prompt sablon
        """
        self.DEFAULT_COMMANDS[trigger.lower()] = prompt
        logger.info(f"Egyedi parancs hozzáadva: {trigger}")

    def remove_custom_command(self, trigger: str):
        """
        Egyedi parancs eltávolítása

        Args:
            trigger: Parancs trigger szó
        """
        if trigger.lower() in self.DEFAULT_COMMANDS:
            del self.DEFAULT_COMMANDS[trigger.lower()]
            logger.info(f"Parancs törölve: {trigger}")
