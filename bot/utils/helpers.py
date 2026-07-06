"""Утилиты и вспомогательные функции"""
import re

# служебные пути Instagram — это не username
_RESERVED_PATHS = {
    "p", "reel", "reels", "stories", "tv", "explore",
    "accounts", "direct", "share", "about", "developer", "legal",
}


def is_instagram_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой на Instagram"""
    pattern = r"https?://(www\.)?(instagram\.com|instagr\.am)/(p|reel|reels|stories|tv)/[\w\-]+"
    return bool(re.match(pattern, text.strip()))


def extract_profile_username(text: str) -> str | None:
    """Достаёт username из ссылки на профиль Instagram.
    Формат: https://www.instagram.com/username (+ опциональные ?параметры).
    Возвращает None если это не профильная ссылка.
    """
    pattern = r"https?://(?:www\.)?(?:instagram\.com|instagr\.am)/([A-Za-z0-9._]+)/?(?:\?.*)?$"
    match = re.match(pattern, text.strip())
    if not match:
        return None

    username = match.group(1)
    if username.lower() in _RESERVED_PATHS:
        return None
    return username


def is_profile_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой на профиль Instagram"""
    return extract_profile_username(text) is not None


def clean_instagram_url(url: str) -> str:
    """Очищает URL от лишних параметров (utm, igsh и т.д.)"""
    # убираем query параметры
    clean = url.split("?")[0]
    # убираем trailing slash
    return clean.rstrip("/")
