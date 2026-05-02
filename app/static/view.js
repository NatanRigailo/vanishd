import VanishCrypto from './crypto.js';

const secretId = document.getElementById('app').dataset.secretId;
const keyB64 = location.hash.slice(1);
const panels = ['loading', 'password-section', 'success-section', 'error-section'];

function show(id) {
  panels.forEach(p => document.getElementById(p).classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}

function showSecret(text) {
  document.getElementById('secret-content').textContent = text;
  show('success-section');
}

function showError(msg) {
  document.getElementById('error-msg').textContent = msg || 'Secret não encontrado ou já foi lido.';
  show('error-section');
}

async function decryptWithKey() {
  try {
    const res = await fetch(`/api/secrets/${secretId}`);
    if (!res.ok) { showError('Secret não encontrado, expirado ou já foi lido.'); return; }
    const { ciphertext, iv } = await res.json();
    const key = await VanishCrypto.importKey(keyB64);
    showSecret(await VanishCrypto.decrypt(ciphertext, iv, key));
  } catch {
    showError('Falha ao decifrar o secret. O link pode estar corrompido.');
  }
}

async function decryptWithPassword(password) {
  try {
    const res = await fetch(`/api/secrets/${secretId}`);
    if (!res.ok) { showError('Secret não encontrado, expirado ou já foi lido.'); return; }
    const { ciphertext, iv, salt } = await res.json();
    if (!salt) { showError('Este secret não usa modo senha.'); return; }
    const key = await VanishCrypto.deriveKey(password, VanishCrypto.b64ToBytes(salt));
    showSecret(await VanishCrypto.decrypt(ciphertext, iv, key));
  } catch {
    showError('Senha incorreta ou dados corrompidos.');
  }
}

if (keyB64) {
  await decryptWithKey();
} else {
  show('password-section');
  document.getElementById('decrypt-btn').addEventListener('click', async () => {
    const password = document.getElementById('password').value;
    if (!password) { alert('Digite a senha.'); return; }
    show('loading');
    await decryptWithPassword(password);
  });
  document.getElementById('password').addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('decrypt-btn').click();
  });
}
