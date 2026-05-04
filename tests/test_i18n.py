def test_get_locale_defaults_to_pt_br(app):
    with app.test_request_context('/'):
        from app.i18n import get_locale
        assert get_locale() == 'pt-BR'


def test_get_locale_from_query_param(app):
    with app.test_request_context('/?lang=en'):
        from app.i18n import get_locale
        assert get_locale() == 'en'


def test_get_locale_from_cookie(app):
    with app.test_request_context('/', headers={'Cookie': 'lang=en'}):
        from app.i18n import get_locale
        assert get_locale() == 'en'


def test_get_locale_invalid_query_falls_back(app, monkeypatch):
    monkeypatch.setenv('DEFAULT_LANGUAGE', 'invalid')
    with app.test_request_context('/?lang=invalid'):
        from app.i18n import get_locale
        assert get_locale() == 'pt-BR'


def test_get_locale_invalid_default_falls_back(app, monkeypatch):
    monkeypatch.setenv('DEFAULT_LANGUAGE', 'invalid')
    with app.test_request_context('/'):
        from app.i18n import get_locale
        assert get_locale() == 'pt-BR'


def test_get_t_returns_dict_for_active_locale(app):
    with app.test_request_context('/?lang=en'):
        from app.i18n import get_t
        t = get_t()
        assert t['btn_create'] == 'Create secure link'


def test_translations_have_matching_keys():
    from app.i18n import TRANSLATIONS
    pt_keys = set(TRANSLATIONS['pt-BR'].keys())
    en_keys = set(TRANSLATIONS['en'].keys())
    assert pt_keys == en_keys, f"Key mismatch: {pt_keys.symmetric_difference(en_keys)}"
