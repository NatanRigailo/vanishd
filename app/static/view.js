import VanishCrypto from './crypto.js';

function getT() {
  return JSON.parse(document.body.dataset.i18n);
}

const panels = ['loading', 'confirm-section', 'password-section', 'success-section', 'error-section'];

function show(id) {
  panels.forEach(p => document.getElementById(p).classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}

function showSecret(text) {
  document.getElementById('secret-content').textContent = text;
  show('success-section');
}

function showError(msg) {
  document.getElementById('error-msg').textContent = msg;
  show('error-section');
}

async function decryptWithKey(secretId, keyB64) {
  const t = getT();
  try {
    const res = await fetch(`/api/secrets/${secretId}`);
    if (!res.ok) { showError(t.js_not_found_expired); return; }
    const { ciphertext, iv } = await res.json();
    const key = await VanishCrypto.importKey(keyB64);
    showSecret(await VanishCrypto.decrypt(ciphertext, iv, key));
  } catch {
    showError(t.js_decrypt_failed);
  }
}

async function decryptWithPassword(secretId, password) {
  const t = getT();
  try {
    const res = await fetch(`/api/secrets/${secretId}`);
    if (!res.ok) { showError(t.js_not_found_expired); return; }
    const { ciphertext, iv, salt } = await res.json();
    if (!salt) { showError(t.js_not_pwd_mode); return; }
    const key = await VanishCrypto.deriveKey(password, VanishCrypto.b64ToBytes(salt));
    showSecret(await VanishCrypto.decrypt(ciphertext, iv, key));
  } catch {
    showError(t.js_wrong_pwd);
  }
}

export function init(secretId, keyB64) {
  if (keyB64) {
    show('confirm-section');
    document.getElementById('reveal-btn').addEventListener('click', async () => {
      show('loading');
      await decryptWithKey(secretId, keyB64);
    });
  } else {
    show('password-section');
    document.getElementById('decrypt-btn').addEventListener('click', async () => {
      const t = getT();
      const password = document.getElementById('password').value;
      if (!password) { alert(t.js_enter_pwd); return; }
      show('loading');
      await decryptWithPassword(secretId, password);
    });
    document.getElementById('password').addEventListener('keydown', e => {
      if (e.key === 'Enter') document.getElementById('decrypt-btn').click();
    });
  }
}

const secretId = document.getElementById('app').dataset.secretId;
init(secretId, location.hash.slice(1));
