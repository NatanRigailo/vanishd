import { describe, test, expect, beforeEach } from '@jest/globals';
import History from '../../app/static/history.js';

const STORAGE_KEY = 'vanishd_history';

function makeEntry(overrides = {}) {
  return {
    id: 'test-id',
    url: 'http://localhost/s/test-id#key',
    mode: 'link',
    ttl: 3600,
    createdAt: Date.now(),
    ...overrides,
  };
}

function setupDOM() {
  document.body.innerHTML = `
    <section id="history" class="hidden">
      <button id="clear-history" type="button">Limpar tudo</button>
      <ul id="history-list"></ul>
    </section>`;
}

describe('storage', () => {
  beforeEach(() => localStorage.clear());

  test('add stores entry', () => {
    History.add(makeEntry({ id: '1' }));
    expect(JSON.parse(localStorage.getItem(STORAGE_KEY))).toHaveLength(1);
  });

  test('add prepends newest entry first', () => {
    History.add(makeEntry({ id: '1' }));
    History.add(makeEntry({ id: '2' }));
    const entries = JSON.parse(localStorage.getItem(STORAGE_KEY));
    expect(entries[0].id).toBe('2');
  });

  test('add limits to 50 entries', () => {
    for (let i = 0; i < 55; i++) History.add(makeEntry({ id: String(i) }));
    expect(JSON.parse(localStorage.getItem(STORAGE_KEY))).toHaveLength(50);
  });

  test('remove deletes entry by id', () => {
    History.add(makeEntry({ id: '1' }));
    History.add(makeEntry({ id: '2' }));
    History.remove('1');
    const entries = JSON.parse(localStorage.getItem(STORAGE_KEY));
    expect(entries).toHaveLength(1);
    expect(entries[0].id).toBe('2');
  });

  test('clear removes all entries', () => {
    History.add(makeEntry());
    History.clear();
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  });
});

describe('render', () => {
  beforeEach(() => { setupDOM(); localStorage.clear(); });

  test('hides section when empty', () => {
    History.render();
    expect(document.getElementById('history').classList.contains('hidden')).toBe(true);
  });

  test('shows section when has entries', () => {
    History.add(makeEntry());
    History.render();
    expect(document.getElementById('history').classList.contains('hidden')).toBe(false);
  });

  test('renders active badge for non-expired entry', () => {
    History.add(makeEntry({ ttl: 3600, createdAt: Date.now() }));
    History.render();
    expect(document.querySelector('.badge-success').textContent).toBe('Ativo');
  });

  test('renders expired badge for expired entry', () => {
    History.add(makeEntry({ ttl: 1, createdAt: Date.now() - 10000 }));
    History.render();
    expect(document.querySelector('.badge-danger').textContent).toBe('Expirado');
  });

  test('sets URL via textContent not innerHTML', () => {
    const url = 'http://localhost/s/abc#key';
    History.add(makeEntry({ url }));
    History.render();
    expect(document.querySelector('.history-url').textContent).toBe(url);
  });

  test('shows password mode label', () => {
    History.add(makeEntry({ mode: 'password' }));
    History.render();
    expect(document.querySelector('.history-mode').textContent).toContain('Senha');
  });

  test('remove button deletes entry and re-renders', () => {
    History.add(makeEntry({ id: 'to-remove' }));
    History.render();
    document.querySelector('.history-remove').click();
    expect(JSON.parse(localStorage.getItem(STORAGE_KEY))).toHaveLength(0);
    expect(document.getElementById('history').classList.contains('hidden')).toBe(true);
  });

  test('copy button triggers clipboard write', async () => {
    const written = [];
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: (t) => { written.push(t); return Promise.resolve(); } },
      configurable: true,
    });
    History.add(makeEntry({ url: 'http://localhost/s/x' }));
    History.render();
    document.querySelector('.history-copy').click();
    await Promise.resolve();
    expect(written[0]).toBe('http://localhost/s/x');
  });
});

describe('edge cases', () => {
  beforeEach(() => { setupDOM(); localStorage.clear(); });

  test('renders unknown TTL as raw seconds', () => {
    History.add(makeEntry({ ttl: 999 }));
    History.render();
    expect(document.querySelector('.history-mode').textContent).toContain('999s');
  });

  test('add is silent when localStorage throws', () => {
    const orig = localStorage.setItem.bind(localStorage);
    localStorage.setItem = () => { throw new Error('quota'); };
    expect(() => History.add(makeEntry())).not.toThrow();
    localStorage.setItem = orig;
  });

  test('clear is silent when localStorage throws', () => {
    const orig = localStorage.removeItem.bind(localStorage);
    localStorage.removeItem = () => { throw new Error('quota'); };
    expect(() => History.clear()).not.toThrow();
    localStorage.removeItem = orig;
  });

  test('render returns early when no DOM elements', () => {
    document.body.innerHTML = '';
    expect(() => History.render()).not.toThrow();
  });

  test('load returns empty array on corrupt JSON', () => {
    localStorage.setItem('vanishd_history', '{invalid}');
    History.render();
    expect(document.getElementById('history').classList.contains('hidden')).toBe(true);
  });
});

describe('setup', () => {
  beforeEach(() => { setupDOM(); localStorage.clear(); });

  test('renders on init', () => {
    History.add(makeEntry());
    History.setup();
    expect(document.getElementById('history').classList.contains('hidden')).toBe(false);
  });

  test('clear button wipes history and hides section', () => {
    History.add(makeEntry());
    History.setup();
    document.getElementById('clear-history').click();
    expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
    expect(document.getElementById('history').classList.contains('hidden')).toBe(true);
  });
});
