"""
Input validáció utility függvények
"""
import re
from pathlib import Path
from typing import Optional, Tuple
from src.utils.logger import get_logger

logger = get_logger()


def validate_hotkey(hotkey: str) -> Tuple[bool, Optional[str]]:
    """
    Hotkey string validálása

    Args:
        hotkey: Hotkey string (pl. "F8", "ctrl+shift+space")

    Returns:
        (valid, error_message) tuple
    """
    if not hotkey or not isinstance(hotkey, str):
        return False, "Hotkey nem lehet üres"

    # Engedélyezett modifierek és billentyűk
    valid_modifiers = {'ctrl', 'alt', 'shift', 'win', 'cmd'}
    valid_keys = {
        # F gombok
        *[f'f{i}' for i in range(1, 13)],
        # Számok
        *[str(i) for i in range(10)],
        # Betűk
        *'abcdefghijklmnopqrstuvwxyz',
        # Speciális
        'space', 'enter', 'tab', 'backspace', 'delete', 'insert',
        'home', 'end', 'pageup', 'pagedown',
        'up', 'down', 'left', 'right',
        'esc', 'escape'
    }

    # Szétválasztás
    parts = [p.strip().lower() for p in hotkey.split('+')]

    if len(parts) == 0:
        return False, "Hotkey nem lehet üres"

    # Utolsó rész a fő billentyű
    main_key = parts[-1]
    modifiers = parts[:-1]

    # Modifierek ellenőrzése
    for mod in modifiers:
        if mod not in valid_modifiers:
            return False, f"Érvénytelen modifier: {mod}"

    # Fő billentyű ellenőrzése
    if main_key not in valid_keys:
        return False, f"Érvénytelen billentyű: {main_key}"

    return True, None


def validate_file_path(path: str, must_exist: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Fájl elérési út validálása

    Args:
        path: Fájl path
        must_exist: True ha a fájlnak léteznie kell

    Returns:
        (valid, error_message) tuple
    """
    if not path or not isinstance(path, str):
        return False, "Path nem lehet üres"

    try:
        p = Path(path)

        if must_exist and not p.exists():
            return False, f"Fájl nem található: {path}"

        # Parent mappa létezik-e (ha fájlt akarunk írni)
        if not must_exist and not p.parent.exists():
            return False, f"Szülő mappa nem található: {p.parent}"

        return True, None

    except Exception as e:
        return False, f"Érvénytelen path: {e}"


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    URL validálása

    Args:
        url: URL string

    Returns:
        (valid, error_message) tuple
    """
    if not url or not isinstance(url, str):
        return False, "URL nem lehet üres"

    # Egyszerű URL regex
    url_pattern = re.compile(
        r'^https?://'  # http:// vagy https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # opcionális port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not url_pattern.match(url):
        return False, "Érvénytelen URL formátum"

    return True, None


def validate_language_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Nyelvi kód validálása (ISO 639-1)

    Args:
        code: Nyelvi kód (pl. "hu", "en")

    Returns:
        (valid, error_message) tuple
    """
    if not code or not isinstance(code, str):
        return False, "Nyelvi kód nem lehet üres"

    # Támogatott nyelvek (Whisper)
    supported_languages = {
        'auto', 'en', 'zh', 'de', 'es', 'ru', 'ko', 'fr', 'ja', 'pt', 'tr',
        'pl', 'ca', 'nl', 'ar', 'sv', 'it', 'id', 'hi', 'fi', 'vi', 'he',
        'uk', 'el', 'ms', 'cs', 'ro', 'da', 'hu', 'ta', 'no', 'th', 'ur',
        'hr', 'bg', 'lt', 'la', 'mi', 'ml', 'cy', 'sk', 'te', 'fa', 'lv',
        'bn', 'sr', 'az', 'sl', 'kn', 'et', 'mk', 'br', 'eu', 'is', 'hy',
        'ne', 'mn', 'bs', 'kk', 'sq', 'sw', 'gl', 'mr', 'pa', 'si', 'km',
        'sn', 'yo', 'so', 'af', 'oc', 'ka', 'be', 'tg', 'sd', 'gu', 'am',
        'yi', 'lo', 'uz', 'fo', 'ht', 'ps', 'tk', 'nn', 'mt', 'sa', 'lb',
        'my', 'bo', 'tl', 'mg', 'as', 'tt', 'haw', 'ln', 'ha', 'ba', 'jw',
        'su'
    }

    if code.lower() not in supported_languages:
        return False, f"Nem támogatott nyelvi kód: {code}"

    return True, None


def validate_audio_settings(
    sample_rate: int,
    channels: int,
    chunk_size: int
) -> Tuple[bool, Optional[str]]:
    """
    Audio beállítások validálása

    Args:
        sample_rate: Mintavételi frekvencia (Hz)
        channels: Csatornák száma
        chunk_size: Buffer méret

    Returns:
        (valid, error_message) tuple
    """
    # Sample rate
    valid_sample_rates = [8000, 16000, 22050, 44100, 48000]
    if sample_rate not in valid_sample_rates:
        return False, f"Érvénytelen sample rate: {sample_rate} (engedélyezett: {valid_sample_rates})"

    # Channels
    if channels not in [1, 2]:
        return False, f"Érvénytelen csatorna szám: {channels} (1 vagy 2)"

    # Chunk size
    if chunk_size < 128 or chunk_size > 8192:
        return False, f"Érvénytelen chunk size: {chunk_size} (128-8192 között)"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Fájlnév tisztítása (érvénytelen karakterek eltávolítása)

    Args:
        filename: Original fájlnév

    Returns:
        Sanitized fájlnév
    """
    # Érvénytelen karakterek cseréje
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Whitespace normalizálás
    filename = ' '.join(filename.split())

    # Max hossz
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + ('.' + ext if ext else '')

    return filename
