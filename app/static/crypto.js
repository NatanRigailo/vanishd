const VanishCrypto = (() => {
  function _b64(u8) {
    let s = '';
    for (let i = 0; i < u8.length; i++) s += String.fromCharCode(u8[i]);
    return btoa(s);
  }

  function _from64(b64) {
    return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  }

  async function generateKey() {
    return crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
  }

  async function exportKey(key) {
    const raw = await crypto.subtle.exportKey('raw', key);
    return _b64(new Uint8Array(raw));
  }

  async function importKey(b64) {
    return crypto.subtle.importKey('raw', _from64(b64), { name: 'AES-GCM' }, false, ['decrypt']);
  }

  // PBKDF2: 200k iterations, SHA-256 — alinhado com OWASP 2023
  async function deriveKey(password, salt) {
    const keyMaterial = await crypto.subtle.importKey(
      'raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveKey']
    );
    return crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt, iterations: 200000, hash: 'SHA-256' },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );
  }

  async function encrypt(plaintext, key) {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const buf = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      new TextEncoder().encode(plaintext)
    );
    return { ciphertext: _b64(new Uint8Array(buf)), iv: _b64(iv) };
  }

  async function decrypt(ciphertextB64, ivB64, key) {
    const buf = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: _from64(ivB64) },
      key,
      _from64(ciphertextB64)
    );
    return new TextDecoder().decode(buf);
  }

  function randomSalt() {
    return crypto.getRandomValues(new Uint8Array(16));
  }

  return { generateKey, exportKey, importKey, deriveKey, encrypt, decrypt, randomSalt, saltToB64: _b64, b64ToBytes: _from64 };
})();
