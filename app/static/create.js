import VanishCrypto from './crypto.js';
import History from './history.js';

const t = JSON.parse(document.body.dataset.i18n);
let mode = 'link';

document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    mode = btn.dataset.mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('password-field').classList.toggle('hidden', mode !== 'password');
  });
});

document.getElementById('submit-btn').addEventListener('click', async () => {
  const secret = document.getElementById('secret').value.trim();
  if (!secret) { alert(t.js_enter_secret); return; }

  const ttl = Number.parseInt(document.getElementById('ttl').value);
  const btn = document.getElementById('submit-btn');
  btn.disabled = true;
  btn.textContent = mode === 'password' ? t.js_deriving : t.js_encrypting;

  try {
    let payload, linkKey;

    if (mode === 'link') {
      const key = await VanishCrypto.generateKey();
      const { ciphertext, iv } = await VanishCrypto.encrypt(secret, key);
      linkKey = await VanishCrypto.exportKey(key);
      payload = { ciphertext, iv, ttl };
    } else {
      const password = document.getElementById('password').value;
      if (!password) { alert(t.js_enter_password); btn.disabled = false; btn.textContent = t.btn_create; return; }
      const salt = VanishCrypto.randomSalt();
      const key = await VanishCrypto.deriveKey(password, salt);
      const { ciphertext, iv } = await VanishCrypto.encrypt(secret, key);
      payload = { ciphertext, iv, salt: VanishCrypto.saltToB64(salt), ttl };
    }

    btn.textContent = t.js_sending;
    const res = await fetch('/api/secrets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(t.js_create_failed);
    const { id } = await res.json();

    const url = `${location.origin}/s/${id}${linkKey ? '#' + linkKey : ''}`;
    document.getElementById('result-url').textContent = url;
    document.getElementById('result').classList.add('show');
    document.getElementById('secret').value = '';
    if (mode === 'password') document.getElementById('password').value = '';
    History.add({ id, url, mode, ttl, createdAt: Date.now() });
    History.render();
  } catch (err) {
    alert(err.message || t.js_create_error);
  } finally {
    btn.disabled = false;
    btn.textContent = t.btn_create;
  }
});

History.setup();

document.getElementById('copy-btn').addEventListener('click', () => {
  const url = document.getElementById('result-url').textContent;
  navigator.clipboard.writeText(url).then(() => {
    const btn = document.getElementById('copy-btn');
    btn.textContent = t.js_copied;
    setTimeout(() => { btn.textContent = t.js_copy; }, 2000);
  });
});
