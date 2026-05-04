const STORAGE_KEY = 'vanishd_history';
const MAX_ENTRIES = 50;

function getT() {
  return JSON.parse(document.body.dataset.i18n);
}

function _load() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; }
  catch { return []; }
}

function _save(entries) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES))); }
  catch { /* storage unavailable */ }
}

function add(entry) {
  const entries = _load();
  entries.unshift(entry);
  _save(entries);
}

function remove(id) {
  _save(_load().filter(e => e.id !== id));
}

function clear() {
  try { localStorage.removeItem(STORAGE_KEY); }
  catch { /* storage unavailable */ }
}

function _isExpired(entry) {
  return Date.now() > entry.createdAt + entry.ttl * 1000;
}

function _formatDate(ts) {
  const lang = document.documentElement.lang || 'pt-BR';
  return new Date(ts).toLocaleString(lang, {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
}

function _ttlLabel(ttl) {
  const t = getT();
  const map = { 3600: t.ttl_1h, 86400: t.ttl_24h, 259200: t.ttl_3d, 604800: t.ttl_7d };
  return map[ttl] || `${ttl}s`;
}

async function _checkConsumed(id) {
  try {
    const res = await fetch(`/api/secrets/${id}`, { method: 'HEAD' });
    return res.status === 404;
  } catch {
    return false;
  }
}

function _badgeHtml(state) {
  const t = getT();
  const map = {
    active:   ['badge-success', t.badge_active],
    consumed: ['badge-warning', t.badge_consumed],
    expired:  ['badge-danger',  t.badge_expired],
  };
  const [cls, label] = map[state] || map.active;
  return `<span class="badge ${cls}">${label}</span>`;
}

function _buildEntry(entry, state) {
  const t = getT();
  const li = document.createElement('li');
  li.className = 'history-entry';
  li.dataset.id = entry.id;
  const modeLabel = entry.mode === 'link' ? 'Link' : t.mode_pwd_label;
  li.innerHTML = `
    <div class="history-entry-meta">
      ${_badgeHtml(state)}
      <span class="history-mode">${modeLabel} &middot; ${_ttlLabel(entry.ttl)}</span>
      <span class="history-date">${_formatDate(entry.createdAt)}</span>
    </div>
    <div class="history-url"></div>
    <div class="history-actions">
      <button class="btn btn-outline btn-sm history-copy" type="button">${t.btn_copy_short}</button>
      <button class="btn btn-outline btn-sm history-remove" type="button">${t.btn_remove}</button>
    </div>`;

  li.querySelector('.history-url').textContent = entry.url;

  li.querySelector('.history-copy').addEventListener('click', (e) => {
    const t2 = getT();
    navigator.clipboard.writeText(entry.url).then(() => {
      e.target.textContent = t2.btn_copied_short;
      setTimeout(() => { e.target.textContent = t2.btn_copy_short; }, 2000);
    });
  });

  li.querySelector('.history-remove').addEventListener('click', () => {
    remove(entry.id);
    render();
  });

  return li;
}

function render() {
  const section = document.getElementById('history');
  const list = document.getElementById('history-list');
  if (!section || !list) return;

  const entries = _load();
  if (entries.length === 0) { section.classList.add('hidden'); return; }
  section.classList.remove('hidden');

  list.innerHTML = '';
  entries.forEach(entry => {
    const state = _isExpired(entry) ? 'expired' : 'active';
    const li = _buildEntry(entry, state);
    list.appendChild(li);

    if (state === 'active') {
      _checkConsumed(entry.id).then(consumed => {
        if (!consumed) return;
        const badge = li.querySelector('.badge');
        const t = getT();
        if (badge) { badge.className = 'badge badge-warning'; badge.textContent = t.badge_consumed; }
      });
    }
  });
}

function setup() {
  const clearBtn = document.getElementById('clear-history');
  if (clearBtn) clearBtn.addEventListener('click', () => { clear(); render(); });
  render();
}

export default { add, remove, clear, setup, render };
