import json
import os
from pathlib import Path

from flask import request

_DIR = Path(__file__).parent / 'translations'
TRANSLATIONS = {
    locale: json.loads((_DIR / f'{locale}.json').read_text(encoding='utf-8'))
    for locale in ('pt-BR', 'en')
}

_VALID = frozenset(TRANSLATIONS)


def get_locale():
    lang = request.args.get('lang') or request.cookies.get('lang')
    if lang in _VALID:
        return lang
    default = os.environ.get('DEFAULT_LANGUAGE', 'pt-BR')
    return default if default in _VALID else 'pt-BR'


def get_t():
    return TRANSLATIONS[get_locale()]
