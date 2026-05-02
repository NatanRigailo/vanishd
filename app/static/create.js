import VanishCrypto from '/static/crypto.js';

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
  if (!secret) { alert('Digite o secret.'); return; }

  const ttl = Number.parseInt(document.getElementById('ttl').value);
  const btn = document.getElementById('submit-btn');
  btn.disabled = true;
  btn.textContent = mode === 'password' ? 'Derivando chave...' : 'Cifrando...';

  try {
    let payload, linkKey;

    if (mode === 'link') {
      const key = await VanishCrypto.generateKey();
      const { ciphertext, iv } = await VanishCrypto.encrypt(secret, key);
      linkKey = await VanishCrypto.exportKey(key);
      payload = { ciphertext, iv, ttl };
    } else {
      const password = document.getElementById('password').value;
      if (!password) { alert('Digite a senha.'); btn.disabled = false; btn.textContent = 'Criar link seguro'; return; }
      const salt = VanishCrypto.randomSalt();
      const key = await VanishCrypto.deriveKey(password, salt);
      const { ciphertext, iv } = await VanishCrypto.encrypt(secret, key);
      payload = { ciphertext, iv, salt: VanishCrypto.saltToB64(salt), ttl };
    }

    btn.textContent = 'Enviando...';
    const res = await fetch('/api/secrets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Falha ao criar o secret.');
    const { id } = await res.json();

    const url = `${location.origin}/s/${id}${linkKey ? '#' + linkKey : ''}`;
    document.getElementById('result-url').textContent = url;
    document.getElementById('result').classList.add('show');
    document.getElementById('secret').value = '';
    if (mode === 'password') document.getElementById('password').value = '';
  } catch (err) {
    alert(err.message || 'Erro ao criar o secret.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Criar link seguro';
  }
});

document.getElementById('copy-btn').addEventListener('click', () => {
  const url = document.getElementById('result-url').textContent;
  navigator.clipboard.writeText(url).then(() => {
    const btn = document.getElementById('copy-btn');
    btn.textContent = 'Copiado!';
    setTimeout(() => { btn.textContent = 'Copiar link'; }, 2000);
  });
});
