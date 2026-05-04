import os

from flask import request

TRANSLATIONS = {
    'pt-BR': {
        'page_title_create': 'Criar secret — Vanishd',
        'page_title_view': 'Ver secret — Vanishd',
        'label_secret': 'Seu secret',
        'placeholder_secret': 'Cole aqui a senha, token, mensagem ou qualquer dado sensível...',
        'label_expires': 'Expira em',
        'opt_1h': '1 hora',
        'opt_24h': '24 horas',
        'opt_3d': '3 dias',
        'opt_7d': '7 dias',
        'label_mode': 'Modo',
        'mode_password_btn': 'Senha',
        'label_password': 'Senha',
        'placeholder_password_create': 'Senha que o destinatário vai digitar',
        'btn_create': 'Criar link seguro',
        'badge_link_created': 'Link criado',
        'btn_copy': 'Copiar link',
        'msg_one_time': 'Este link funciona uma única vez. Compartilhe apenas com o destinatário.',
        'history_title': 'Histórico',
        'btn_clear_history': 'Limpar tudo',
        'msg_decrypting': 'Decifrando...',
        'badge_one_time': 'Uso único',
        'msg_confirm': (
            'Este secret será <strong>destruído permanentemente</strong> ao ser revelado. '
            'Certifique-se de estar em um ambiente confiável antes de continuar.'
        ),
        'btn_reveal': 'Revelar secret',
        'msg_password_mode': 'Este secret foi protegido com senha. Digite a senha para decifrar.',
        'msg_password_warning': (
            '⚠️ O link será consumido ao tentar decifrar. '
            'Certifique-se de ter a senha correta.'
        ),
        'placeholder_password_view': 'Digite a senha...',
        'btn_decrypt': 'Decifrar',
        'badge_decrypted': 'Secret decifrado',
        'msg_consumed': 'Este link foi consumido e não funcionará novamente.',
        'badge_error': 'Erro',
        'btn_create_new': 'Criar novo secret',
        'err_too_large': 'Conteúdo muito grande. O tamanho máximo permitido foi excedido.',
        'err_not_found': 'Página não encontrada.',
        'err_server': 'Algo deu errado. Tente novamente mais tarde.',
        'js_enter_secret': 'Digite o secret.',
        'js_deriving': 'Derivando chave...',
        'js_encrypting': 'Cifrando...',
        'js_enter_password': 'Digite a senha.',
        'js_sending': 'Enviando...',
        'js_create_failed': 'Falha ao criar o secret.',
        'js_create_error': 'Erro ao criar o secret.',
        'js_copied': 'Copiado!',
        'js_copy': 'Copiar link',
        'js_not_found': 'Secret não encontrado ou já foi lido.',
        'js_not_found_expired': 'Secret não encontrado, expirado ou já foi lido.',
        'js_decrypt_failed': 'Falha ao decifrar o secret. O link pode estar corrompido.',
        'js_not_password_mode': 'Este secret não usa modo senha.',
        'js_wrong_password': 'Senha incorreta ou dados corrompidos.',
        'ttl_1h': '1 hora',
        'ttl_24h': '24 horas',
        'ttl_3d': '3 dias',
        'ttl_7d': '7 dias',
        'badge_active': 'Ativo',
        'badge_consumed': 'Consumido',
        'badge_expired': 'Expirado',
        'mode_password_label': 'Senha',
        'btn_copy_short': 'Copiar',
        'btn_copied_short': 'Copiado!',
        'btn_remove': 'Remover',
        'lang_label': 'EN',
        'lang_switch_target': 'en',
    },
    'en': {
        'page_title_create': 'Create secret — Vanishd',
        'page_title_view': 'View secret — Vanishd',
        'label_secret': 'Your secret',
        'placeholder_secret': 'Paste your password, token, message, or any sensitive data here...',
        'label_expires': 'Expires in',
        'opt_1h': '1 hour',
        'opt_24h': '24 hours',
        'opt_3d': '3 days',
        'opt_7d': '7 days',
        'label_mode': 'Mode',
        'mode_password_btn': 'Password',
        'label_password': 'Password',
        'placeholder_password_create': 'Password the recipient will type',
        'btn_create': 'Create secure link',
        'badge_link_created': 'Link created',
        'btn_copy': 'Copy link',
        'msg_one_time': 'This link works once. Share it only with the recipient.',
        'history_title': 'History',
        'btn_clear_history': 'Clear all',
        'msg_decrypting': 'Decrypting...',
        'badge_one_time': 'One-time',
        'msg_confirm': (
            'This secret will be <strong>permanently destroyed</strong> when revealed. '
            'Make sure you are in a trusted environment before continuing.'
        ),
        'btn_reveal': 'Reveal secret',
        'msg_password_mode': 'This secret is password-protected. Enter the password to decrypt.',
        'msg_password_warning': (
            '⚠️ The link will be consumed when decrypting. '
            'Make sure you have the correct password.'
        ),
        'placeholder_password_view': 'Enter password...',
        'btn_decrypt': 'Decrypt',
        'badge_decrypted': 'Secret decrypted',
        'msg_consumed': 'This link has been consumed and will not work again.',
        'badge_error': 'Error',
        'btn_create_new': 'Create new secret',
        'err_too_large': 'Content too large. The maximum allowed size has been exceeded.',
        'err_not_found': 'Page not found.',
        'err_server': 'Something went wrong. Please try again later.',
        'js_enter_secret': 'Enter a secret.',
        'js_deriving': 'Deriving key...',
        'js_encrypting': 'Encrypting...',
        'js_enter_password': 'Enter a password.',
        'js_sending': 'Sending...',
        'js_create_failed': 'Failed to create the secret.',
        'js_create_error': 'Error creating the secret.',
        'js_copied': 'Copied!',
        'js_copy': 'Copy link',
        'js_not_found': 'Secret not found or already read.',
        'js_not_found_expired': 'Secret not found, expired, or already read.',
        'js_decrypt_failed': 'Failed to decrypt the secret. The link may be corrupted.',
        'js_not_password_mode': 'This secret does not use password mode.',
        'js_wrong_password': 'Wrong password or corrupted data.',
        'ttl_1h': '1 hour',
        'ttl_24h': '24 hours',
        'ttl_3d': '3 days',
        'ttl_7d': '7 days',
        'badge_active': 'Active',
        'badge_consumed': 'Consumed',
        'badge_expired': 'Expired',
        'mode_password_label': 'Password',
        'btn_copy_short': 'Copy',
        'btn_copied_short': 'Copied!',
        'btn_remove': 'Remove',
        'lang_label': 'PT',
        'lang_switch_target': 'pt-BR',
    },
}

_VALID = frozenset(TRANSLATIONS)
_DEFAULT = os.environ.get('DEFAULT_LANGUAGE', 'pt-BR')
if _DEFAULT not in _VALID:
    _DEFAULT = 'pt-BR'


def get_locale():
    for source in (request.args.get('lang'), request.cookies.get('lang'), _DEFAULT):
        if source in _VALID:
            return source
    return 'pt-BR'


def get_t():
    return TRANSLATIONS[get_locale()]
