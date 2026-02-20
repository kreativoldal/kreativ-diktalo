"""
LLM-alapú szövegtisztító modul Ollama használatával
"""
import ollama
import re
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger()


class LLMCleaner:
    """Ollama LLM-mel történő szövegtisztítás"""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.1:8b",
        timeout: int = 30,
        temperature: float = 0.3
    ):
        """
        Args:
            host: Ollama szerver URL
            model: Használandó modell
            timeout: Timeout másodpercben
            temperature: LLM temperature (0.0-1.0)
        """
        self.host = host
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.ollama_available = False
        self.client = ollama.Client(host=self.host)

        self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Ollama szerver elérhetőség ellenőrzése"""
        try:
            # Modellek lekérése (teszt) - self.client újrafelhasználás
            models = self.client.list()

            self.ollama_available = True
            logger.info(f"Ollama szerver elérhető: {self.host}")

            # Modellek listája - különböző API verziók kezelése
            if hasattr(models, 'models'):
                model_list = models.models
            elif isinstance(models, dict):
                model_list = models.get('models', [])
            else:
                model_list = []

            model_names = []

            for m in model_list:
                # Extract model name from different formats
                if hasattr(m, 'model'):
                    name = m.model
                elif hasattr(m, 'name'):
                    name = m.name
                elif isinstance(m, dict):
                    name = m.get('model', m.get('name', str(m)))
                else:
                    name = str(m)
                model_names.append(name)

            logger.info(f"Elérhető modellek: {model_names}")

            # Ellenőrizzük hogy a kért modell elérhető-e
            if self.model not in model_names:
                logger.warning(f"A kért modell ({self.model}) nincs telepítve. Kérlek futtasd: ollama pull {self.model}")

        except Exception as e:
            self.ollama_available = False
            logger.warning(f"Ollama nem elérhető: {e}")
            logger.info("Fallback: Alapvető regex-alapú tisztítás lesz használva")

    def _build_cleaning_prompt(self, text: str) -> str:
        """
        Prompt generálása szövegtisztításhoz

        Args:
            text: Nyers szöveg

        Returns:
            Prompt string
        """
        prompt = f"""Javítsd ki ezt a szöveget. Távolítsd el a töltelékszavakat (hát, szóval, ööö), javítsd a helyesírást és írásjeleket. Válaszolj CSAK a javított szöveggel, semmi mással.

Szöveg: {text}

Javított:"""

        return prompt

    def _build_command_prompt(self, text: str, command: str) -> str:
        """
        Prompt generálása command mode-hoz

        Args:
            text: Eredeti szöveg
            command: Felhasználói parancs

        Returns:
            Prompt string
        """
        prompt = f"""Te egy szövegszerkesztő asszisztens vagy. A feladatod, hogy módosítsd a megadott szöveget a felhasználó parancsa szerint.

PARANCS: {command}

EREDETI SZÖVEG:
{text}

MÓDOSÍTOTT SZÖVEG (csak a szöveget írd, semmi mást):"""

        return prompt

    def clean_text(self, text: str) -> str:
        """
        Szöveg tisztítása LLM-mel vagy fallback-kel

        Args:
            text: Nyers szöveg

        Returns:
            Tisztított szöveg
        """
        if not text or not text.strip():
            return text

        text = text.strip()
        logger.info(f"Szövegtisztítás indítása: {len(text)} karakter")

        # Ollama használat ha elérhető
        if self.ollama_available:
            try:
                cleaned = self._clean_with_ollama(text)
                logger.info("LLM tisztítás sikeres")
                return cleaned
            except Exception as e:
                logger.error(f"LLM tisztítás hiba: {e}, fallback használata")

        # Fallback: Regex-alapú tisztítás
        cleaned = self._basic_clean(text)
        logger.info("Regex alapú tisztítás használva")
        return cleaned

    def _clean_with_ollama(self, text: str) -> str:
        """
        Szöveg tisztítása Ollama LLM-mel

        Args:
            text: Nyers szöveg

        Returns:
            Tisztított szöveg
        """
        prompt = self._build_cleaning_prompt(text)

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                'temperature': self.temperature,
                'top_p': 0.9,
                'top_k': 40,
            }
        )

        cleaned_text = response['response'].strip()

        # Biztonság: ha túl rövid vagy üres, ne használjuk
        if len(cleaned_text) < len(text) * 0.3:
            logger.warning("LLM válasz túl rövid, fallback használata")
            return self._basic_clean(text)

        return cleaned_text

    def _basic_clean(self, text: str) -> str:
        """
        Alapvető regex-alapú szövegtisztítás (fallback)

        Args:
            text: Nyers szöveg

        Returns:
            Tisztított szöveg
        """
        cleaned = text

        # 1. Töltelékszavak eltávolítása
        filler_words = [
            r'\bhát\b', r'\bszóval\b', r'\búgy\b', r'\bna\b', r'\bnos\b',
            r'\bööö+\b', r'\bum+\b', r'\buh+\b', r'\behm+\b',
            r'\bte tudod\b', r'\bugye\b', r'\bhogy is mondjam\b'
        ]

        for pattern in filler_words:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # 2. Többszörös szóközök eltávolítása
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # 3. Szóköz írásjelek előtt/után
        cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned)  # Szóköz eltávolítása írásjelek előtt
        cleaned = re.sub(r'([.,!?;:])\s*', r'\1 ', cleaned)  # Szóköz írásjelek után

        # 4. Mondatkezdés nagybetűvel
        sentences = re.split(r'([.!?]\s+)', cleaned)
        cleaned = ''
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Mondat (nem delimiter)
                part = part[0].upper() + part[1:] if part else part
            cleaned += part

        # 5. Trim
        cleaned = cleaned.strip()

        # 6. Pont a végére ha nincs
        if cleaned and cleaned[-1] not in '.!?':
            cleaned += '.'

        return cleaned

    def process_command(self, text: str, command: str) -> str:
        """
        Szöveg módosítása parancs alapján (Command Mode)

        Args:
            text: Eredeti szöveg
            command: Felhasználói parancs

        Returns:
            Módosított szöveg
        """
        if not text or not command:
            return text

        logger.info(f"Command feldolgozás: '{command}'")

        if not self.ollama_available:
            logger.warning("Ollama nem elérhető, command mode nem működik")
            return text

        try:
            prompt = self._build_command_prompt(text, command)

            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                }
            )

            modified_text = response['response'].strip()

            logger.info("Command feldolgozás sikeres")
            return modified_text

        except Exception as e:
            logger.error(f"Hiba a command feldolgozáskor: {e}")
            return text

    def is_available(self) -> bool:
        """
        Ollama elérhetőség lekérése

        Returns:
            True ha Ollama elérhető
        """
        return self.ollama_available

    def get_status(self) -> dict:
        """
        Státusz információk lekérése

        Returns:
            Státusz dictionary
        """
        return {
            'ollama_available': self.ollama_available,
            'host': self.host,
            'model': self.model,
            'temperature': self.temperature
        }


# Teszt funkció
def _test_llm_cleaner():
    """Teszt futtatás"""

    test_texts = [
        "hát szóval úgy gondolom hogy ez egy teszt szöveg ööö igen",
        "holnap nem várj inkább pénteken találkozunk",
        "te tudod ez a dolog ami úgy van hogy nos hát igen",
    ]

    cleaner = LLMCleaner()

    print("LLM Cleaner teszt\n")
    print(f"Ollama elérhető: {cleaner.is_available()}\n")

    for i, text in enumerate(test_texts, 1):
        print(f"Teszt {i}:")
        print(f"  Eredeti: {text}")
        cleaned = cleaner.clean_text(text)
        print(f"  Tisztított: {cleaned}")
        print()

    # Command mode teszt
    if cleaner.is_available():
        print("Command Mode teszt:")
        original = "Ez egy hosszú és bonyolult mondat, amit szeretnék egyszerűsíteni."
        print(f"  Eredeti: {original}")
        result = cleaner.process_command(original, "rövidítsd le")
        print(f"  Rövidítve: {result}")


if __name__ == "__main__":
    _test_llm_cleaner()
