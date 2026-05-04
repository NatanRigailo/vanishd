import { describe, test, expect, beforeEach, jest } from '@jest/globals';

const MOCK_SECRET_ID = 'abc123';
const MOCK_KEY_B64 = 'c29tZWtleQ==';

const PT_STRINGS = {
  js_not_found: 'Secret não encontrado ou já foi lido.',
  js_not_found_expired: 'Secret não encontrado, expirado ou já foi lido.',
  js_decrypt_failed: 'Falha ao decifrar o secret. O link pode estar corrompido.',
  js_not_pwd_mode: 'Este secret não usa modo senha.',
  js_wrong_pwd: 'Senha incorreta ou dados corrompidos.',
  js_enter_pwd: 'Digite a senha.',
};

function setupDOM() {
  document.body.innerHTML = `
    <div id="app" data-secret-id="${MOCK_SECRET_ID}"></div>
    <div id="loading" class="hidden"></div>
    <div id="confirm-section"></div>
    <div id="password-section" class="hidden"></div>
    <div id="success-section" class="hidden"></div>
    <div id="error-section" class="hidden"></div>
    <button id="reveal-btn" type="button">Revelar secret</button>
    <button id="decrypt-btn" type="button">Decifrar</button>
    <input id="password" type="password" />
    <div id="secret-content"></div>
    <p id="error-msg"></p>
  `;
  document.body.dataset.i18n = JSON.stringify(PT_STRINGS);
}

function isVisible(id) {
  return !document.getElementById(id).classList.contains('hidden');
}

jest.unstable_mockModule('../../app/static/crypto.js', () => ({
  default: {
    importKey: jest.fn().mockResolvedValue('mock-key'),
    decrypt: jest.fn().mockResolvedValue('my-secret-text'),
    deriveKey: jest.fn().mockResolvedValue('mock-key'),
    b64ToBytes: jest.fn().mockReturnValue(new Uint8Array(16)),
  },
}));

describe('view — link mode', () => {
  let init;

  beforeEach(async () => {
    setupDOM();
    jest.resetModules();
    const mod = await import('../../app/static/view.js');
    init = mod.init;
  });

  test('shows confirm-section on init', () => {
    init(MOCK_SECRET_ID, MOCK_KEY_B64);
    expect(isVisible('confirm-section')).toBe(true);
    expect(isVisible('password-section')).toBe(false);
    expect(isVisible('loading')).toBe(false);
  });

  test('does not fetch before reveal click', () => {
    global.fetch = jest.fn();
    init(MOCK_SECRET_ID, MOCK_KEY_B64);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('shows loading and calls fetch on reveal click', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ciphertext: 'ct', iv: 'iv' }),
    });
    init(MOCK_SECRET_ID, MOCK_KEY_B64);
    document.getElementById('reveal-btn').click();
    await Promise.resolve();
    expect(global.fetch).toHaveBeenCalledWith(`/api/secrets/${MOCK_SECRET_ID}`);
  });

  test('shows success section after reveal with valid response', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ciphertext: 'ct', iv: 'iv' }),
    });
    init(MOCK_SECRET_ID, MOCK_KEY_B64);
    document.getElementById('reveal-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('success-section')).toBe(true);
    expect(document.getElementById('secret-content').textContent).toBe('my-secret-text');
  });

  test('shows error section when fetch returns not-ok', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: false });
    init(MOCK_SECRET_ID, MOCK_KEY_B64);
    document.getElementById('reveal-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('error-section')).toBe(true);
    expect(document.getElementById('error-msg').textContent).toMatch(/não encontrado/);
  });

  test('shows error section when fetch throws', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('network'));
    init(MOCK_SECRET_ID, MOCK_KEY_B64);
    document.getElementById('reveal-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('error-section')).toBe(true);
    expect(document.getElementById('error-msg').textContent).toMatch(/corrompido/);
  });
});

describe('view — password mode', () => {
  let init;

  beforeEach(async () => {
    setupDOM();
    jest.resetModules();
    const mod = await import('../../app/static/view.js');
    init = mod.init;
  });

  test('shows password-section when no key', () => {
    init(MOCK_SECRET_ID, '');
    expect(isVisible('password-section')).toBe(true);
    expect(isVisible('confirm-section')).toBe(false);
    expect(isVisible('loading')).toBe(false);
  });

  test('does not fetch before decrypt click', () => {
    global.fetch = jest.fn();
    init(MOCK_SECRET_ID, '');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('alerts when decrypt clicked with empty password', () => {
    global.alert = jest.fn();
    global.fetch = jest.fn();
    init(MOCK_SECRET_ID, '');
    document.getElementById('decrypt-btn').click();
    expect(global.alert).toHaveBeenCalled();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('calls fetch with password on decrypt click', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ciphertext: 'ct', iv: 'iv', salt: 'c2FsdA==' }),
    });
    init(MOCK_SECRET_ID, '');
    document.getElementById('password').value = 'mypassword';
    document.getElementById('decrypt-btn').click();
    await Promise.resolve();
    expect(global.fetch).toHaveBeenCalledWith(`/api/secrets/${MOCK_SECRET_ID}`);
  });

  test('shows success after correct password', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ciphertext: 'ct', iv: 'iv', salt: 'c2FsdA==' }),
    });
    init(MOCK_SECRET_ID, '');
    document.getElementById('password').value = 'mypassword';
    document.getElementById('decrypt-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('success-section')).toBe(true);
  });

  test('enter key on password input triggers decrypt', () => {
    global.fetch = jest.fn();
    init(MOCK_SECRET_ID, '');
    const clickSpy = jest.spyOn(document.getElementById('decrypt-btn'), 'click');
    const event = new KeyboardEvent('keydown', { key: 'Enter' });
    document.getElementById('password').dispatchEvent(event);
    expect(clickSpy).toHaveBeenCalled();
  });

  test('shows error when secret has no salt', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ciphertext: 'ct', iv: 'iv' }),
    });
    init(MOCK_SECRET_ID, '');
    document.getElementById('password').value = 'mypassword';
    document.getElementById('decrypt-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('error-section')).toBe(true);
    expect(document.getElementById('error-msg').textContent).toMatch(/não usa modo senha/);
  });

  test('shows error when fetch returns not-ok', async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: false });
    init(MOCK_SECRET_ID, '');
    document.getElementById('password').value = 'mypassword';
    document.getElementById('decrypt-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('error-section')).toBe(true);
  });

  test('shows error when fetch throws', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('network'));
    init(MOCK_SECRET_ID, '');
    document.getElementById('password').value = 'mypassword';
    document.getElementById('decrypt-btn').click();
    await new Promise(r => setTimeout(r, 0));
    expect(isVisible('error-section')).toBe(true);
    expect(document.getElementById('error-msg').textContent).toMatch(/incorreta/);
  });
});
