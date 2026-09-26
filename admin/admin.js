/* =====================================================================
   Administrace tomasveigl.cz
   Data live in the GitHub repo (_data/*.json). Saving = one commit via
   the GitHub API; a GitHub Action rebuilds and deploys the site.
   The repo token is stored AES-GCM-encrypted with the admin password.
   ===================================================================== */
'use strict';
(() => {
const CFG = {
  id: 'tomasveigl', repo: 'webhunter-navrhy/tomasveigl', site: '../',
  api: /^(localhost|127\.0\.0\.1)$/.test(location.hostname) ? 'http://localhost:8787' : 'https://webhunter-admin.webhunter.workers.dev',
};
const FILES = { site: '_data/site.json', listings: '_data/listings.json', posts: '_data/posts.json', reviews: '_data/reviews.json' };
const LABEL = { site: 'Texty a nastavení webu', listings: 'Nemovitosti', posts: 'Blog', reviews: 'Reference' };
const STATUSES = [['nabidka', 'V nabídce'], ['pripravujeme', 'Připravujeme'], ['rezervace', 'Rezervace'], ['prodano', 'Prodáno'], ['pronajato', 'Pronajato']];
const STATUS_L = Object.fromEntries(STATUSES);
const TYPES = ['Rodinný dům', 'Byt', 'Novostavba', 'Chata / chalupa', 'Pozemek', 'Komerční', 'Jiné'];

const S = { sess: null, schema: [], D: {}, snap: {}, pending: {}, preview: {}, def: false, saving: false,
            lf: { status: 'all', q: '' }, pub: { state: 'off', text: '' } };

/* ------------------------------------------------------------ icons */
const I = (d, extra = '') => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ${extra}>${d}</svg>`;
const IC = {
  home: I('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
  dash: I('<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>'),
  building: I('<path d="M3 21h18"/><path d="M5 21V8l7-5 7 5v13"/><path d="M9 21v-5h6v5"/><path d="M10 11h4"/>'),
  pen: I('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>'),
  star: I('<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/>'),
  starF: I('<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z" fill="currentColor"/>'),
  text: I('<path d="M4 6h16M4 12h10M4 18h14"/>'),
  phone: I('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>'),
  gear: I('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'),
  ext: I('<path d="M14 4h6v6"/><path d="M20 4L10 14"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>'),
  plus: I('<path d="M12 5v14M5 12h14"/>'),
  drag: I('<circle cx="9" cy="6" r="1"/><circle cx="15" cy="6" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="9" cy="18" r="1"/><circle cx="15" cy="18" r="1"/>'),
  eye: I('<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/>'),
  eyeOff: I('<path d="M17.9 17.9A10.5 10.5 0 0 1 12 19c-7 0-11-7-11-7a18.7 18.7 0 0 1 5.1-5.9M9.9 5.2A9.9 9.9 0 0 1 12 5c7 0 11 7 11 7a18.5 18.5 0 0 1-2.2 3.2M14.1 14.1a3 3 0 1 1-4.2-4.2"/><path d="M1 1l22 22"/>'),
  trash: I('<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/>'),
  copy: I('<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/>'),
  up: I('<path d="M12 19V5M5 12l7-7 7 7"/>'),
  down: I('<path d="M12 5v14M19 12l-7 7-7-7"/>'),
  x: I('<path d="M18 6L6 18M6 6l12 12"/>', 'stroke-width="2.4"'),
  upload: I('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/>'),
  image: I('<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>'),
  check: I('<path d="M20 6L9 17l-5-5"/>'),
  alert: I('<path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h0"/>'),
  info: I('<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h0"/>'),
  logout: I('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>'),
  menu: I('<path d="M3 6h18M3 12h18M3 18h18"/>'),
  search: I('<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>'),
  chev: I('<path d="M6 9l6 6 6-6"/>'),
  lock: I('<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>'),
  link: I('<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>'),
  download: I('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>'),
  quote: I('<path d="M3 21c3 0 7-1 7-8V5H3v7h4c0 3-2 5-4 5z"/><path d="M14 21c3 0 7-1 7-8V5h-7v7h4c0 3-2 5-4 5z"/>'),
};

/* ------------------------------------------------------------ utils */
const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const slugify = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70);
const today = () => new Date().toISOString().slice(0, 10);
const czDate = (d) => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(d || ''); return m ? `${+m[3]}. ${+m[2]}. ${m[1]}` : (d || ''); };
const ago = (iso) => { if (!iso) return ''; const s = (Date.now() - new Date(iso)) / 1000; if (s < 60) return 'právě teď'; if (s < 3600) return `před ${Math.round(s / 60)} min`; if (s < 86400) return `před ${Math.round(s / 3600)} h`; return czDate(iso); };
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
const move = (arr, from, to) => { if (to < 0 || to >= arr.length || from === to) return; arr.splice(to, 0, arr.splice(from, 1)[0]); };
const src = (p) => !p ? '' : (S.preview[p] || (/^(https?:|data:|blob:)/.test(p) ? p : CFG.site + p));
const clone = (o) => JSON.parse(JSON.stringify(o));
const uid = () => Math.random().toString(36).slice(2, 8);

function toast(title, sub = '', type = '') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = `<span><b>${esc(title)}</b>${sub ? `<small>${esc(sub)}</small>` : ''}</span>`;
  $('#toasts').appendChild(el);
  setTimeout(() => { el.style.transition = 'opacity .4s'; el.style.opacity = '0'; setTimeout(() => el.remove(), 450); }, type === 'err' ? 7000 : 4200);
}

function modal({ title, body, actions = [], wide = false, onMount }) {
  return new Promise((resolve) => {
    const root = $('#modal-root');
    const bg = document.createElement('div');
    bg.className = 'modal-bg';
    bg.innerHTML = `<div class="modal${wide ? ' wide' : ''}" role="dialog" aria-modal="true"><div class="modal-h"><h3>${title}</h3><button class="icon-btn" data-close aria-label="Zavřít">${IC.x}</button></div>
      <div class="modal-b">${body}</div>${actions.length ? `<div class="modal-f">${actions.map((a, i) => `<button class="btn ${a.cls || 'btn-ghost'}" data-a="${i}">${a.label}</button>`).join('')}</div>` : ''}</div>`;
    const close = (v) => { bg.remove(); document.removeEventListener('keydown', onKey); resolve(v); };
    const onKey = (e) => { if (e.key === 'Escape') close(null); };
    bg.addEventListener('click', (e) => {
      if (e.target === bg || e.target.closest('[data-close]')) return close(null);
      const b = e.target.closest('[data-a]');
      if (b) { const a = actions[+b.dataset.a]; const v = a.value !== undefined ? a.value : (a.get ? a.get(bg) : true); if (v === false) return; close(v); }
    });
    document.addEventListener('keydown', onKey);
    root.appendChild(bg);
    if (onMount) onMount(bg, close);
    const f = bg.querySelector('input,textarea,select'); if (f) setTimeout(() => f.focus(), 50);
  });
}
const confirmDlg = (title, text, ok = 'Smazat', cls = 'btn-danger') => modal({ title, body: `<p>${text}</p>`, actions: [{ label: 'Zrušit', value: false }, { label: ok, cls, value: true }] }).then((v) => v === true);

/* ------------------------------------------------------------ server (WebHunter admin API) */
const b64e = (bytes) => { let s = ''; bytes = new Uint8Array(bytes); for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(s); };
const utf8b64 = (str) => b64e(new TextEncoder().encode(str));
function saveSess() { localStorage.setItem('tv_sess_' + CFG.id, JSON.stringify({ t: S.sess, def: S.def, exp: Date.now() + 11.5 * 3600e3 })); }
async function api(path, opt = {}, retried = false) {
  const headers = { ...(opt.body && typeof opt.body === 'string' ? { 'Content-Type': 'application/json' } : {}), ...(opt.headers || {}) };
  if (S.sess) headers.Authorization = 'Bearer ' + S.sess;
  let r;
  try { r = await fetch(`${CFG.api}/api/${CFG.id}${path}`, { ...opt, headers, cache: 'no-store' }); }
  catch { throw new Error('Nelze se spojit se serverem administrace. Zkontrolujte připojení k internetu.'); }
  if (r.status === 401 && path !== '/login' && !retried && S.D.site) {
    if (await reauth()) return api(path, opt, true);   // přihlášení vypršelo uprostřed práce — neztratit rozdělanou práci
  }
  if (!r.ok) { let m = r.statusText; try { m = (await r.json()).error || m; } catch {} const e = new Error(m); e.status = r.status; throw e; }
  return opt.raw ? r.text() : r.json();
}
const readFile = (path) => api('/file?path=' + encodeURIComponent(path) + '&t=' + Date.now(), { raw: true });
async function commit(files, message) {
  // 1) každý soubor nahrát jako blob (tělo jde na GitHub beze změny), 2) jeden commit se všemi soubory
  const out = []; const queue = [...files];
  const worker = async () => {
    while (queue.length) {
      const f = queue.shift();
      const { sha } = await api('/blob', { method: 'POST', body: JSON.stringify({ content: f.b64 ?? utf8b64(f.content), encoding: 'base64' }) });
      out.push({ path: f.path, sha });
    }
  };
  await Promise.all([worker(), worker(), worker()]);
  return (await api('/commit', { method: 'POST', body: JSON.stringify({ files: out, message }) })).sha;
}

/* ------------------------------------------------------------ data + dirty state */
async function loadAll() {
  const [schema, ...files] = await Promise.all([
    fetch('schema.json?t=' + Date.now(), { cache: 'no-store' }).then((r) => r.json()),
    ...Object.values(FILES).map((p) => readFile(p).then(JSON.parse)),
  ]);
  S.schema = schema.schema;
  Object.keys(FILES).forEach((k, i) => { S.D[k] = files[i]; });
  for (const p of S.schema) for (const sec of p.sections) for (const f of sec.fields) if (!(f.key in S.D.site)) S.D.site[f.key] = clone(f.default);
  snapshot();
}
function snapshot(keys = Object.keys(FILES)) { keys.forEach((k) => { S.snap[k] = JSON.stringify(S.D[k]); }); }
const dirtyKeys = () => Object.keys(FILES).filter((k) => JSON.stringify(S.D[k]) !== S.snap[k]);
const changed = debounce(() => updateSavebar(), 120);
function discard() { dirtyKeys().forEach((k) => { S.D[k] = JSON.parse(S.snap[k]); }); updateSavebar(); route(); toast('Změny zahozeny'); }
window.addEventListener('beforeunload', (e) => { if (dirtyKeys().length) { e.preventDefault(); e.returnValue = ''; } });

function validate() {
  const slugs = new Set();
  for (const x of S.D.listings) {
    if (!x.title?.trim()) return `Nemovitost bez názvu — doplňte název.`;
    if (!/^[a-z0-9][a-z0-9_-]*$/.test(x.slug || '')) return `Nemovitost „${x.title}“ má neplatnou adresu (URL). Použijte malá písmena, čísla a pomlčky.`;
    if (slugs.has(x.slug)) return `Dvě nemovitosti mají stejnou adresu „${x.slug}“.`;
    slugs.add(x.slug);
  }
  const ps = new Set();
  for (const p of S.D.posts) {
    if (!p.title?.trim()) return 'Článek bez názvu — doplňte název.';
    if (!/^[a-z0-9][a-z0-9_-]*$/.test(p.slug || '')) return `Článek „${p.title}“ má neplatnou adresu (URL).`;
    if (ps.has(p.slug)) return `Dva články mají stejnou adresu „${p.slug}“.`;
    ps.add(p.slug);
  }
  return null;
}

async function saveAll() {
  const keys = dirtyKeys();
  if (!keys.length || S.saving) return;
  const err = validate(); if (err) return toast('Nelze uložit', err, 'err');
  S.saving = true; updateSavebar();
  const bar = document.createElement('div'); bar.className = 'progress-line'; document.body.appendChild(bar);
  try {
    const files = keys.map((k) => ({ path: FILES[k], content: JSON.stringify(S.D[k], null, 1) + '\n' }));
    const used = JSON.stringify(S.D);
    const imgs = Object.keys(S.pending).filter((p) => used.includes(p));
    imgs.forEach((p) => files.push({ path: p, b64: S.pending[p] }));
    const sha = await commit(files, keys.map((k) => LABEL[k]).join(', ') + (imgs.length ? ` (+${imgs.length} ${imgs.length === 1 ? 'obrázek' : imgs.length < 5 ? 'obrázky' : 'obrázků'})` : ''));
    imgs.forEach((p) => delete S.pending[p]);
    snapshot(keys);
    toast('Uloženo', 'Změny se na webu objeví přibližně za minutu.', 'ok');
    watchPublish(sha);
  } catch (e) {
    toast('Uložení se nepovedlo', e.message, 'err');
  } finally { S.saving = false; bar.remove(); updateSavebar(); }
}

/* ------------------------------------------------------------ publish watcher */
let pubTimer = null;
function setPub(state, text) { S.pub = { state, text }; const el = $('.pub'); if (el) { el.className = 'pub ' + state; el.innerHTML = `<i></i><span>${esc(text)}</span>`; } }
function watchPublish(sha) {
  localStorage.setItem('tv_pub', JSON.stringify({ sha, t: Date.now() }));
  clearInterval(pubTimer);
  setPub('busy', 'Zveřejňuji změny…');
  const started = Date.now();
  pubTimer = setInterval(async () => {
    try {
      const v = await fetch(CFG.site + 'version.json?t=' + Date.now(), { cache: 'no-store' }).then((r) => r.json());
      if (v.sha === sha) { clearInterval(pubTimer); localStorage.removeItem('tv_pub'); setPub('', 'Web je aktuální'); toast('Změny jsou na webu', 'Web byl právě aktualizován.', 'ok'); return; }
    } catch {}
    if (Date.now() - started > 8 * 60000) { clearInterval(pubTimer); setPub('warn', 'Zveřejnění trvá déle'); }
  }, 6000);
}
function initPub() {
  const p = JSON.parse(localStorage.getItem('tv_pub') || 'null');
  if (p && Date.now() - p.t < 10 * 60000) watchPublish(p.sha); else setPub('', 'Web je aktuální');
}

/* ------------------------------------------------------------ images */
async function compress(file, max = 1800) {
  let bmp;
  try { bmp = await createImageBitmap(file); } catch { throw new Error(`Soubor „${file.name}“ nejde načíst. Použijte JPG, PNG nebo WebP.`); }
  const sc = Math.min(1, max / Math.max(bmp.width, bmp.height));
  const w = Math.round(bmp.width * sc), h = Math.round(bmp.height * sc);
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  c.getContext('2d').drawImage(bmp, 0, 0, w, h);
  let blob = await new Promise((r) => c.toBlob(r, 'image/webp', 0.82)), ext = 'webp';
  if (!blob || blob.type !== 'image/webp') { blob = await new Promise((r) => c.toBlob(r, 'image/jpeg', 0.86)); ext = 'jpg'; }
  return { blob, ext };
}
async function upload(file, hint = '') {
  const { blob, ext } = await compress(file);
  const d = new Date();
  const name = (slugify(hint) || slugify(file.name.replace(/\.[^.]+$/, '')) || 'foto').slice(0, 40);
  const path = `img/uploads/${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}/${name}-${uid()}.${ext}`;
  const buf = await blob.arrayBuffer();
  S.pending[path] = b64e(buf);
  S.preview[path] = URL.createObjectURL(blob);
  return path;
}
async function uploadMany(files, hint) {
  const out = [];
  for (const f of files) {
    if (!f.type.startsWith('image/') && !/\.(heic|jpe?g|png|webp)$/i.test(f.name)) continue;
    try { out.push(await upload(f, hint)); } catch (e) { toast('Obrázek se nepodařilo načíst', e.message, 'err'); }
  }
  return out;
}
function allImages() {
  const set = new Set(Object.keys(S.pending));
  const re = /img\/[A-Za-z0-9_\-/.]+\.(?:webp|png|jpe?g)/g;
  (JSON.stringify(S.D).match(re) || []).forEach((p) => set.add(p));
  return [...set];
}
function pickFromLibrary() {
  const imgs = allImages();
  return modal({
    title: 'Knihovna obrázků', wide: true,
    body: `<div class="toolbar"><div class="search">${IC.search}<input type="search" placeholder="Hledat podle názvu souboru…" data-q></div><span class="muted">${imgs.length} obrázků na webu</span></div><div class="lib">${imgs.map((p) => `<button data-p="${esc(p)}" title="${esc(p)}"><img src="${esc(src(p))}" loading="lazy" alt=""></button>`).join('')}</div>`,
    onMount: (bg, close) => {
      bg.querySelector('.lib').addEventListener('click', (e) => { const b = e.target.closest('[data-p]'); if (b) close(b.dataset.p); });
      bg.querySelector('[data-q]').addEventListener('input', (e) => { const q = e.target.value.toLowerCase(); $$('.lib button', bg).forEach((b) => { b.style.display = b.dataset.p.toLowerCase().includes(q) ? '' : 'none'; }); });
    },
  });
}

/* image picker (single) — registry of getters/setters per render */
let IP = [];
function imgPick(get, set, opts = {}) {
  const id = IP.push({ get, set, opts }) - 1;
  const v = get();
  return `<div class="img-pick" data-ip="${id}"><div class="pv">${v ? `<img src="${esc(src(v))}" alt="">` : 'Bez obrázku'}</div>
    <div><div class="bts"><button type="button" class="btn btn-ghost btn-sm" data-ipa="up">${IC.upload} Nahrát</button><button type="button" class="btn btn-ghost btn-sm" data-ipa="lib">${IC.image} Z knihovny</button>${v && !opts.required ? `<button type="button" class="btn btn-ghost btn-sm" data-ipa="rm">Odebrat</button>` : ''}</div>
    ${v ? `<div class="path">${esc(v)}</div>` : ''}</div><input type="file" accept="image/*" hidden></div>`;
}
function bindIP(root) {
  $$('.img-pick', root).forEach((el) => {
    const r = IP[+el.dataset.ip]; if (!r) return;
    const refresh = () => { IP[+el.dataset.ip] = r; const tmp = document.createElement('div'); tmp.innerHTML = imgPick(r.get, r.set, r.opts); const n = tmp.firstElementChild; el.replaceWith(n); bindIP(n.parentElement); r.opts.onChange?.(); };
    const file = el.querySelector('input[type=file]');
    el.addEventListener('click', async (e) => {
      const a = e.target.closest('[data-ipa]')?.dataset.ipa; if (!a) return;
      if (a === 'up') file.click();
      if (a === 'lib') { const p = await pickFromLibrary(); if (p) { r.set(p); changed(); refresh(); } }
      if (a === 'rm') { r.set(''); changed(); refresh(); }
    });
    file.addEventListener('change', async () => { const [p] = await uploadMany([...file.files], r.opts.hint); if (p) { r.set(p); changed(); refresh(); } });
  });
}

/* gallery (multiple images, sortable) */
function galleryHTML(arr, key, contain = false) {
  return `<div class="gal" data-gal="${key}">${arr.map((p, i) => `<div class="gi${contain ? ' contain' : ''}" draggable="true" data-idx="${i}"><img src="${esc(src(p))}" alt="" loading="lazy">${S.pending[p] ? '<span class="new">Nová</span>' : ''}${i === 0 && key === 'photos' ? '<span class="cover">Titulní</span>' : ''}<button type="button" class="x" data-rm="${i}" aria-label="Odebrat">${IC.x}</button></div>`).join('')}</div>
  <label class="drop" data-drop="${key}">${IC.upload}<b>Přetáhněte fotky sem</b> nebo klikněte a vyberte<br><small>Můžete vybrat víc fotek najednou. Automaticky se zmenší a zoptimalizují.</small><input type="file" accept="image/*" multiple hidden></label>
  <div class="row-btns" style="margin-top:.6rem"><button type="button" class="btn btn-ghost btn-sm" data-glib="${key}">${IC.image} Přidat z knihovny</button></div>`;
}
function bindGallery(root, obj, key, hint, rerender) {
  const wrap = $(`[data-gal="${key}"]`, root); if (!wrap) return;
  let from = null;
  wrap.addEventListener('dragstart', (e) => { const it = e.target.closest('.gi'); if (!it) return; from = +it.dataset.idx; it.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', String(from)); });
  wrap.addEventListener('dragover', (e) => { const it = e.target.closest('.gi'); if (!it || from === null) return; e.preventDefault(); $$('.gi.over', wrap).forEach((x) => x.classList.remove('over')); it.classList.add('over'); });
  wrap.addEventListener('drop', (e) => { const it = e.target.closest('.gi'); if (!it || from === null) return; e.preventDefault(); move(obj[key], from, +it.dataset.idx); from = null; changed(); rerender(); });
  wrap.addEventListener('dragend', () => { from = null; $$('.gi', wrap).forEach((x) => x.classList.remove('dragging', 'over')); });
  wrap.addEventListener('click', (e) => { const b = e.target.closest('[data-rm]'); if (!b) return; obj[key].splice(+b.dataset.rm, 1); changed(); rerender(); });
  const drop = $(`[data-drop="${key}"]`, root), input = drop.querySelector('input');
  const add = async (files) => { drop.classList.add('over'); drop.querySelector('b').textContent = 'Nahrávám a optimalizuji…'; const ps = await uploadMany(files, hint); obj[key].push(...ps); if (ps.length) { changed(); toast(`Přidáno ${ps.length} ${ps.length === 1 ? 'obrázek' : ps.length < 5 ? 'obrázky' : 'obrázků'}`, 'Nezapomeňte změny uložit.'); } rerender(); };
  input.addEventListener('change', () => add([...input.files]));
  drop.addEventListener('dragover', (e) => { if (from !== null) return; e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('over'));
  drop.addEventListener('drop', (e) => { if (from !== null) return; e.preventDefault(); add([...e.dataTransfer.files]); });
  $(`[data-glib="${key}"]`, root).addEventListener('click', async () => { const p = await pickFromLibrary(); if (p) { obj[key].push(p); changed(); rerender(); } });
}

/* sortable rows */
function sortable(container, sel, onMove) {
  let from = null;
  container.addEventListener('dragstart', (e) => { const it = e.target.closest(sel); if (!it) return; from = +it.dataset.idx; it.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', String(from)); });
  container.addEventListener('dragover', (e) => { const it = e.target.closest(sel); if (!it || from === null) return; e.preventDefault(); $$(sel + '.over', container).forEach((x) => x.classList.remove('over')); it.classList.add('over'); });
  container.addEventListener('drop', (e) => { const it = e.target.closest(sel); if (!it || from === null) return; e.preventDefault(); const to = +it.dataset.idx; const f = from; from = null; onMove(f, to); });
  container.addEventListener('dragend', () => { from = null; $$(sel, container).forEach((x) => x.classList.remove('dragging', 'over')); });
}

/* rich text (Quill) */
let quillP = null;
function loadQuill() {
  if (quillP) return quillP;
  quillP = new Promise((res, rej) => {
    const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css'; document.head.appendChild(l);
    const s = document.createElement('script'); s.src = 'https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js'; s.onload = () => res(window.Quill); s.onerror = () => { quillP = null; rej(new Error('Editor textu se nepodařilo načíst. Zkontrolujte připojení k internetu.')); };
    document.head.appendChild(s);
  });
  return quillP;
}
async function mountRTE(el, html, onChange, placeholder = 'Začněte psát…') {
  el.innerHTML = '<div class="rte-loading"><span class="spin"></span> Načítám editor textu…</div>';
  try {
    const Quill = await loadQuill();
    if (!el.isConnected) return;
    el.innerHTML = '<div class="rte"><div class="q"></div></div>';
    const q = new Quill(el.querySelector('.q'), { theme: 'snow', placeholder, modules: { toolbar: [[{ header: [2, 3, false] }], ['bold', 'italic', 'underline'], [{ list: 'ordered' }, { list: 'bullet' }], ['blockquote', 'link'], ['clean']] } });
    q.clipboard.dangerouslyPasteHTML(html || '', 'silent'); q.history.clear();
    const tips = { 'ql-bold': 'Tučně', 'ql-italic': 'Kurzíva', 'ql-underline': 'Podtržení', 'ql-blockquote': 'Citace', 'ql-link': 'Odkaz', 'ql-clean': 'Odstranit formátování' };
    Object.entries(tips).forEach(([c, t]) => $$('.' + c, el).forEach((b) => b.setAttribute('title', t)));
    q.on('text-change', debounce((d, o, source) => { let h = q.getSemanticHTML().replace(/&nbsp;/g, ' '); if (/^<p>(<br>)?<\/p>$/.test(h) || !q.getText().trim()) h = ''; onChange(h); }, 250));
  } catch (e) { el.innerHTML = `<div class="banner err">${IC.alert}<span><b>Editor se nenačetl</b>${esc(e.message)}</span></div>`; }
}

const autosize = (ta) => { ta.style.height = 'auto'; ta.style.height = Math.max(ta.scrollHeight + 2, 46) + 'px'; };

/* ------------------------------------------------------------ re-login without losing work */
let reauthP = null;
function reauth() {
  if (reauthP) return reauthP;
  reauthP = modal({
    title: 'Přihlaste se prosím znovu',
    body: `<p>Z bezpečnostních důvodů vypršelo přihlášení. Vaše rozpracované změny zůstávají — po přihlášení se uloží.</p><div class="f" style="margin-top:1rem"><label>Heslo</label><input type="password" data-rpw autocomplete="current-password"></div><p class="hint" data-rerr style="color:var(--danger)"></p>`,
    actions: [{ label: 'Zrušit', value: false }, { label: 'Přihlásit', cls: 'btn-primary', get: (bg) => ({ pw: bg.querySelector('[data-rpw]').value }) }],
    onMount: (bg) => bg.querySelector('[data-rpw]').addEventListener('keydown', (e) => { if (e.key === 'Enter') bg.querySelector('[data-a="1"]').click(); }),
  }).then(async (v) => {
    if (!v) return false;
    try { const r = await api('/login', { method: 'POST', body: JSON.stringify({ password: v.pw }) }); S.sess = r.token; S.def = r.def; saveSess(); return true; }
    catch (e) { toast('Přihlášení se nepovedlo', e.message, 'err'); return false; }
  }).finally(() => { reauthP = null; });
  return reauthP;
}

/* ------------------------------------------------------------ LOGIN */
function renderLogin(msg = '') {
  document.title = 'Přihlášení — Administrace tomasveigl.cz';
  $('#app').innerHTML = `<div class="login">
    <div class="login-art"><div class="rings"><span></span><span></span><span></span><span></span></div>
      <img class="logo" src="../img/site/logo2-light.png" alt="tomasveigl.cz — Slyším váš domov">
      <div><h1>Vítejte v <em>administraci</em></h1><p>Tady spravujete nemovitosti, články, reference i všechny texty webu. Změny se na webu objeví do minuty.</p></div>
      <div class="foot"><img src="../img/site/r11-light.png" alt="reality11"><span>Mgr. Tomáš Veigl · realitní makléř</span></div></div>
    <div class="login-form"><form novalidate>
      <h2>Přihlášení</h2><p class="sub">Zadejte heslo do administrace.</p>
      <div class="f"><label for="pw">Heslo</label><div class="pw-wrap"><input type="password" id="pw" autocomplete="current-password" required><button type="button" data-show>Zobrazit</button></div></div>
      <button class="btn btn-primary btn-lg" style="width:100%;margin-top:1.2rem" type="submit">Přihlásit se</button>
      <p class="err">${esc(msg)}</p>
      <a class="back" href="../">← Zpět na web</a>
    </form></div></div>`;
  const form = $('form'), pw = $('#pw');
  $('[data-show]').addEventListener('click', (e) => { pw.type = pw.type === 'password' ? 'text' : 'password'; e.target.textContent = pw.type === 'password' ? 'Zobrazit' : 'Skrýt'; });
  pw.focus();
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const b = form.querySelector('[type=submit]'); b.disabled = true; b.innerHTML = '<span class="spin" style="border-color:rgba(255,255,255,.3);border-top-color:#fff"></span> Ověřuji…';
    try {
      const r = await api('/login', { method: 'POST', body: JSON.stringify({ password: pw.value }) });
      S.sess = r.token; S.def = r.def; saveSess();
      await boot();
    } catch (err) {
      $('.err').textContent = err.status === 401 ? 'Nesprávné heslo. Zkuste to znovu.' : err.message;
      form.classList.remove('shake'); void form.offsetWidth; form.classList.add('shake'); pw.select();
    }
    finally { b.disabled = false; b.textContent = 'Přihlásit se'; }
  });
}
function logout() {
  if (dirtyKeys().length && !confirm('Máte neuložené změny. Opravdu se odhlásit a zahodit je?')) return;
  localStorage.removeItem('tv_sess_' + CFG.id); S.sess = null; S.snap = {}; S.D = {}; location.hash = ''; renderLogin();
}

/* ------------------------------------------------------------ SHELL */
function pagesNav() { return S.schema.filter((p) => p.id !== 'general'); }
function renderShell() {
  $('#app').innerHTML = `<div class="shell">
    <aside class="side">
      <a class="logo" href="#/"><img src="../img/site/logo2-light.png" alt="tomasveigl.cz"><small>Administrace webu</small></a>
      <nav>
        <a class="item" href="#/" data-nav="dash">${IC.dash}Přehled</a>
        <div class="grp">Obsah</div>
        <a class="item" href="#/nemovitosti" data-nav="nemovitosti">${IC.building}Nemovitosti<span class="count" data-count="listings"></span></a>
        <a class="item" href="#/blog" data-nav="blog">${IC.pen}Blog<span class="count" data-count="posts"></span></a>
        <a class="item" href="#/reference" data-nav="reference">${IC.star}Reference<span class="count" data-count="reviews"></span></a>
        <div class="grp">Web</div>
        <a class="item" href="#/obsah/home" data-nav="obsah">${IC.text}Texty a obrázky</a>
        <div class="sub">${pagesNav().map((p) => `<a href="#/obsah/${p.id}" data-sub="${p.id}">${esc(p.title)}</a>`).join('')}</div>
        <a class="item" href="#/obsah/general" data-nav="general">${IC.phone}Kontakty a firma</a>
        <a class="item" href="#/nastaveni" data-nav="nastaveni">${IC.gear}Nastavení</a>
      </nav>
      <div class="foot">
        <div class="pub"><i></i><span></span></div>
        <a class="item" href="../" target="_blank" rel="noopener" style="display:flex;gap:.75rem;align-items:center;padding:.55rem .75rem;border-radius:9px;color:#C9D3E0;font-size:.88rem">${IC.ext.replace('<svg', '<svg width="17" height="17"')}Otevřít web</a>
        <div class="me"><img src="../img/site/portrait.webp" alt=""><span><b>Tomáš Veigl</b><small>Správce webu</small></span><button data-logout title="Odhlásit">${IC.logout.replace('<svg', '<svg width="17" height="17"')}</button></div>
      </div>
    </aside>
    <div class="main">
      <header class="top"><button class="burger" aria-label="Menu">${IC.menu.replace('<svg', '<svg width="20" height="20"')}</button><div class="crumb"></div><div class="actions"></div></header>
      <div class="page" id="page"></div>
    </div>
  </div>
  <div class="savebar"><span class="txt"></span><button class="btn btn-ghost btn-sm" data-discard>Zahodit</button><button class="btn btn-teal" data-save>${IC.check} Uložit a zveřejnit</button></div>`;
  $('[data-logout]').addEventListener('click', logout);
  $('[data-save]').addEventListener('click', saveAll);
  $('[data-discard]').addEventListener('click', async () => { if (await confirmDlg('Zahodit změny?', 'Všechny neuložené změny se ztratí.', 'Zahodit')) discard(); });
  const side = $('.side');
  $('.burger').addEventListener('click', () => { side.classList.add('open'); const s = document.createElement('div'); s.className = 'scrim'; s.onclick = () => { side.classList.remove('open'); s.remove(); }; document.body.appendChild(s); });
  side.addEventListener('click', (e) => { if (e.target.closest('a') && side.classList.contains('open')) { side.classList.remove('open'); $('.scrim')?.remove(); } });
  window.addEventListener('scroll', () => $('.top')?.classList.toggle('scrolled', scrollY > 8), { passive: true });
  document.addEventListener('keydown', (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); saveAll(); } });
  initPub();
}
function updateNav(key, sub) {
  $$('.side [data-nav]').forEach((a) => a.classList.toggle('on', a.dataset.nav === key));
  $$('.side [data-sub]').forEach((a) => a.classList.toggle('on', a.dataset.sub === sub));
  const c = { listings: S.D.listings.length, posts: S.D.posts.length, reviews: S.D.reviews.length };
  $$('.side [data-count]').forEach((el) => { el.textContent = c[el.dataset.count]; });
}
function updateSavebar() {
  const bar = $('.savebar'); if (!bar) return;
  const keys = dirtyKeys();
  const imgs = Object.keys(S.pending).length;
  bar.classList.toggle('show', keys.length > 0 || S.saving);
  bar.querySelector('.txt').innerHTML = S.saving ? '<b>Ukládám…</b><small>Nahrávám změny na web</small>' : `<b>Neuložené změny</b><small>${keys.map((k) => LABEL[k]).join(', ')}${imgs ? ` · ${imgs} ${imgs === 1 ? 'nový obrázek' : imgs < 5 ? 'nové obrázky' : 'nových obrázků'}` : ''}</small>`;
  bar.querySelector('[data-save]').disabled = S.saving;
  bar.querySelector('[data-discard]').disabled = S.saving;
  updateNav($('.side [data-nav].on')?.dataset.nav, $('.side [data-sub].on')?.dataset.sub);
}
function setTop(crumbs, actions = '') {
  $('.crumb').innerHTML = crumbs.map((c, i) => i < crumbs.length - 1 && c[1] ? `<a href="${c[1]}">${esc(c[0])}</a><span>/</span>` : `<span>${esc(c[0])}</span>`).join('');
  $('.top .actions').innerHTML = actions;
  document.title = crumbs[crumbs.length - 1][0] + ' — Administrace';
}
const page = () => $('#page');

/* ------------------------------------------------------------ router */
const ROUTES = [
  [/^\/?$/, viewDash], [/^\/nemovitosti$/, viewListings], [/^\/nemovitost\/(.+)$/, viewListing],
  [/^\/blog$/, viewPosts], [/^\/clanek\/(.+)$/, viewPost], [/^\/reference$/, viewReviews],
  [/^\/obsah\/(.+)$/, viewTexts], [/^\/nastaveni$/, viewSettings],
];
const FRESH = new Set();
function route() {
  if (!S.D.site) return;
  const h = decodeURIComponent(location.hash.replace(/^#/, '')) || '/';
  IP = [];
  // fresh page element = no event listeners left over from the previous view
  const old = $('#page'); if (old) { const n = document.createElement('div'); n.className = 'page'; n.id = 'page'; old.replaceWith(n); }
  // drop untouched new items when leaving their editor
  for (const it of FRESH) {
    const cur = h.endsWith('/' + (it.id || it.slug));
    if (!cur && !it.title && !(it.photos || []).length && !it.body && !it.image) {
      [S.D.listings, S.D.posts].forEach((arr) => { const i = arr.indexOf(it); if (i > -1) arr.splice(i, 1); });
      FRESH.delete(it);
    } else if (!cur) FRESH.delete(it);
  }
  for (const [re, fn] of ROUTES) { const m = h.match(re); if (m) { window.scrollTo(0, 0); fn(...m.slice(1)); updateSavebar(); return; } }
  location.hash = '#/';
}
window.addEventListener('hashchange', route);

/* ------------------------------------------------------------ DASHBOARD */
function viewDash() {
  updateNav('dash');
  setTop([['Přehled']], `<a class="btn btn-ghost" href="../" target="_blank" rel="noopener">${IC.ext} Otevřít web</a>`);
  const L = S.D.listings;
  const cnt = (s) => L.filter((x) => x.status === s).length;
  const active = cnt('nabidka') + cnt('pripravujeme');
  const done = cnt('prodano') + cnt('pronajato');
  const recent = [...L].sort((a, b) => (b.updated || '').localeCompare(a.updated || '')).slice(0, 6);
  const h = new Date().getHours();
  const hi = h < 10 ? 'Dobré ráno' : h < 18 ? 'Dobrý den' : 'Dobrý večer';
  const cover = (x) => (x.photos || [])[0] || x.thumb || (x.viz || [])[0] || '';
  page().innerHTML = `
    ${S.def ? `<div class="banner warn">${IC.lock}<span><b>Používáte výchozí heslo „admin“</b>Z bezpečnostních důvodů si ho prosím hned změňte.</span><a class="btn btn-primary btn-sm" href="#/nastaveni">Změnit heslo</a></div>` : ''}
    <section class="welcome"><div class="rings"><span></span><span></span><span></span></div>
      <div><h2>${hi}, <em>Tomáši</em>.</h2><p>Na webu máte ${active} ${active === 1 ? 'nemovitost' : active < 5 ? 'nemovitosti' : 'nemovitostí'} v nabídce, ${S.D.posts.length} článků a ${S.D.reviews.length} referencí. Co dnes upravíme?</p>
        <div class="acts"><a class="btn btn-teal" href="#/nemovitost/new">${IC.plus} Přidat nemovitost</a><a class="btn btn-ghost" href="#/clanek/new">${IC.pen} Napsat článek</a><a class="btn btn-ghost" href="../" target="_blank" rel="noopener">${IC.ext} Zobrazit web</a></div></div>
      <div class="avatar"><img src="../img/site/portrait.webp" alt=""></div></section>
    <div class="stats">
      <a class="card stat" href="#/nemovitosti" data-f="nabidka"><small>V nabídce</small><b>${active}</b><div class="bar"><i style="width:${Math.min(100, active / Math.max(1, L.length) * 100 * 4)}%"></i></div></a>
      <a class="card stat" href="#/nemovitosti" data-f="rezervace"><small>Rezervace</small><b>${cnt('rezervace')}</b><div class="bar"><i style="width:${cnt('rezervace') / Math.max(1, L.length) * 400}%;background:var(--res)"></i></div></a>
      <a class="card stat" href="#/nemovitosti" data-f="done"><small>Prodáno a pronajato</small><b>${done}</b><div class="bar"><i style="width:${done / Math.max(1, L.length) * 100}%;background:#98A2B3"></i></div></a>
      <a class="card stat" href="#/blog"><small>Články na blogu</small><b>${S.D.posts.length}</b><div class="bar"><i style="width:100%"></i></div></a>
      <a class="card stat" href="#/reference"><small>Hodnocení</small><b>${esc(S.D.site['rating.value'])}<span style="font-size:1.2rem;color:var(--teal-d)"> ★</span></b><div class="bar"><i style="width:${parseFloat(String(S.D.site['rating.value']).replace(',', '.')) / 5 * 100}%"></i></div></a>
    </div>
    <div class="dash-grid">
      <div class="card"><div class="card-head"><h3>Rychlé akce</h3></div>
        <div class="qa">
          <a href="#/nemovitost/new"><span class="ic">${IC.building}</span><span><b>Přidat nemovitost</b><small>Fotky, popis, cena, parametry</small></span></a>
          <a href="#/clanek/new"><span class="ic">${IC.pen}</span><span><b>Napsat článek</b><small>Novinka na blog</small></span></a>
          <a href="#/reference" data-newrev><span class="ic">${IC.quote}</span><span><b>Přidat referenci</b><small>Hodnocení od klienta</small></span></a>
          <a href="#/obsah/home"><span class="ic">${IC.home}</span><span><b>Upravit úvodní stránku</b><small>Texty, fotky, čísla</small></span></a>
          <a href="#/obsah/general"><span class="ic">${IC.phone}</span><span><b>Kontakty a firma</b><small>Telefon, e-mail, odkazy</small></span></a>
          <a href="#/nastaveni"><span class="ic">${IC.lock}</span><span><b>Heslo a zabezpečení</b><small>Změna hesla, propojení</small></span></a>
        </div>
        <div class="tip"><b>Tip:</b> V textech webu můžete slovo zvýraznit kurzívou v barvě — stačí ho dát do hvězdiček, např. <code>Slyším *váš* domov</code>. Změny uložíte tlačítkem dole nebo zkratkou <span class="kbd">Ctrl</span> + <span class="kbd">S</span>.</div>
      </div>
      <div class="card"><div class="card-head"><h3>Nemovitosti <small>naposledy upravené</small></h3><a class="btn btn-ghost btn-sm" href="#/nemovitosti">Všechny</a></div>
        <ul class="recent">${recent.map((x) => `<li><img src="${esc(src(cover(x)))}" alt="" loading="lazy"><span class="t"><b><a href="#/nemovitost/${esc(x.id)}">${esc(x.short || x.title)}</a></b><small>${x.updated ? 'Upraveno ' + ago(x.updated) : esc(x.address)}</small></span><span class="st st-${x.status}">${STATUS_L[x.status] || ''}</span></li>`).join('')}</ul>
      </div>
    </div>`;
  $$('.stats [data-f]').forEach((a) => a.addEventListener('click', () => { S.lf.status = a.dataset.f === 'done' ? 'done' : a.dataset.f; }));
  $('[data-newrev]')?.addEventListener('click', () => { sessionStorage.setItem('tv_newrev', '1'); });
}

/* ------------------------------------------------------------ LISTINGS */
function viewListings() {
  updateNav('nemovitosti');
  setTop([['Nemovitosti']], `<a class="btn btn-primary" href="#/nemovitost/new">${IC.plus} Přidat nemovitost</a>`);
  const L = S.D.listings;
  const count = (f) => L.filter(f).length;
  const tabs = [['all', 'Vše', () => true], ['nabidka', 'V nabídce', (x) => x.status === 'nabidka'], ['pripravujeme', 'Připravujeme', (x) => x.status === 'pripravujeme'],
    ['rezervace', 'Rezervace', (x) => x.status === 'rezervace'], ['done', 'Prodáno a pronajato', (x) => x.status === 'prodano' || x.status === 'pronajato'],
    ['home', 'Na úvodní stránce', (x) => x.home], ['hidden', 'Skryté', (x) => x.hidden]];
  page().innerHTML = `
    <div class="page-head"><div><h1>Nemovitosti</h1><p>Pořadí změníte přetažením řádku za úchyt vlevo. Hvězdička = zobrazit na úvodní stránce, oko = viditelnost na webu.</p></div></div>
    <div class="toolbar"><div class="seg" data-tabs>${tabs.map(([k, l, f]) => `<button data-t="${k}" class="${S.lf.status === k ? 'on' : ''}">${k.length > 3 && STATUS_L[k] ? `<span class="dot dot-${k}"></span>` : ''}${l}<sup>${count(f)}</sup></button>`).join('')}</div>
      <div class="search">${IC.search}<input type="search" placeholder="Hledat název nebo adresu…" value="${esc(S.lf.q)}" data-q></div></div>
    <div class="card"><ul class="rows" data-rows></ul></div>`;
  const rows = $('[data-rows]');
  const cover = (x) => (x.photos || [])[0] || x.thumb || (x.viz || [])[0] || '';
  const draw = () => {
    const f = tabs.find((t) => t[0] === S.lf.status)?.[2] || (() => true);
    const q = S.lf.q.trim().toLowerCase();
    const canDrag = S.lf.status === 'all' && !q;
    const items = L.map((x, i) => [x, i]).filter(([x]) => f(x) && (!q || (x.title + ' ' + x.short + ' ' + x.address).toLowerCase().includes(q)));
    rows.innerHTML = items.length ? items.map(([x, i]) => `<li class="row${x.hidden ? ' is-hidden' : ''}" data-idx="${i}" ${canDrag ? 'draggable="true"' : ''}>
      <span class="handle" title="${canDrag ? 'Přetáhněte pro změnu pořadí' : 'Pořadí lze měnit v záložce Vše bez hledání'}">${canDrag ? IC.drag : ''}</span>
      <a href="#/nemovitost/${esc(x.id)}"><img class="thumb" src="${esc(src(cover(x)))}" alt="" loading="lazy"></a>
      <div class="ttl"><a href="#/nemovitost/${esc(x.id)}">${esc(x.short || x.title)}</a><small>${esc(x.type || '')}${x.address ? ' · ' + esc(x.address) : ''}</small></div>
      <div class="price">${esc(x.price || '—')}<small>${esc(x.price_label || '')}</small></div>
      <div class="stcell"><select class="st-sel st st-${x.status}" data-st="${i}" aria-label="Stav">${STATUSES.map(([k, l]) => `<option value="${k}" ${x.status === k ? 'selected' : ''}>${l}</option>`).join('')}</select></div>
      <div class="acts">
        <button class="icon-btn${x.home ? ' on' : ''}" data-home="${i}" title="${x.home ? 'Zobrazuje se na úvodní stránce' : 'Zobrazit na úvodní stránce'}">${x.home ? IC.starF : IC.star}</button>
        <button class="icon-btn" data-hide="${i}" title="${x.hidden ? 'Skryto — kliknutím zobrazíte' : 'Viditelné — kliknutím skryjete'}">${x.hidden ? IC.eyeOff : IC.eye}</button>
        <button class="icon-btn" data-dup="${i}" title="Duplikovat">${IC.copy}</button>
        <button class="icon-btn danger" data-del="${i}" title="Smazat">${IC.trash}</button>
      </div></li>`).join('') : `<li class="empty"><b>Nic tu není</b>V tomto filtru nejsou žádné nemovitosti.</li>`;
  };
  draw();
  $('[data-tabs]').addEventListener('click', (e) => { const b = e.target.closest('[data-t]'); if (!b) return; S.lf.status = b.dataset.t; $$('[data-t]').forEach((x) => x.classList.toggle('on', x === b)); draw(); });
  $('[data-q]').addEventListener('input', (e) => { S.lf.q = e.target.value; draw(); });
  sortable(rows, '.row', (a, b) => { move(L, a, b); changed(); draw(); });
  rows.addEventListener('change', (e) => { const s = e.target.closest('[data-st]'); if (s) { const x = L[+s.dataset.st]; x.status = s.value; x.updated = new Date().toISOString(); changed(); draw(); } });
  rows.addEventListener('click', async (e) => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.home) { const x = L[+b.dataset.home]; x.home = !x.home; changed(); draw(); }
    if (b.dataset.hide) { const x = L[+b.dataset.hide]; x.hidden = !x.hidden; changed(); draw(); toast(x.hidden ? 'Nemovitost bude skrytá' : 'Nemovitost bude viditelná', 'Projeví se po uložení.'); }
    if (b.dataset.dup) { const x = clone(L[+b.dataset.dup]); x.title += ' (kopie)'; x.slug = uniqueSlug(slugify(x.slug + '-kopie')); x.id = x.slug; x.updated = new Date().toISOString(); L.splice(+b.dataset.dup + 1, 0, x); changed(); draw(); toast('Nemovitost zduplikována'); }
    if (b.dataset.del) { const x = L[+b.dataset.del]; if (await confirmDlg('Smazat nemovitost?', `„${esc(x.short || x.title)}“ zmizí z webu i s vlastní stránkou. Pokud jen nechcete, aby byla vidět, použijte raději skrytí (ikona oka).`)) { L.splice(+b.dataset.del, 1); changed(); draw(); toast('Nemovitost smazána', 'Projeví se po uložení.'); } }
  });
}
function uniqueSlug(base, self = null, list = S.D.listings) {
  base = base || 'nemovitost'; let s = base, k = 2;
  while (list.some((x) => x.slug === s && x !== self)) s = `${base}-${k++}`;
  return s;
}

function viewListing(id) {
  updateNav('nemovitosti');
  const L = S.D.listings;
  if (id === 'new') {
    const x = { id: '', slug: '', title: '', short: '', type: 'Rodinný dům', status: 'nabidka', address: '', price: '', price_label: 'Cena',
      facts: [{ v: '', l: 'Dispozice' }, { v: '', l: 'Užitná plocha' }, { v: '', l: 'Pozemek' }], lead: '', body: '', photos: [], plans: [], viz: [], thumb: '',
      home: true, hidden: false, seo_desc: '', updated: new Date().toISOString() };
    x.slug = x.id = uniqueSlug('nova-nemovitost'); x._new = true;
    L.unshift(x); FRESH.add(x); changed();
    history.replaceState(null, '', '#/nemovitost/' + x.id);
    return viewListing(x.id);
  }
  const x = L.find((i) => i.id === id);
  if (!x) { page().innerHTML = `<div class="empty"><b>Nemovitost nenalezena</b><a class="btn btn-ghost" href="#/nemovitosti">Zpět na seznam</a></div>`; return; }
  const isNew = !!x._new; delete x._new;
  const live = () => CFG.site + 'nemovitosti/' + x.slug + '.html';
  const hasPage = () => !!((x.body || '').trim() || x.lead || (x.photos || []).length);
  setTop([['Nemovitosti', '#/nemovitosti'], [x.short || x.title || 'Nová nemovitost']], `${hasPage() ? `<a class="btn btn-ghost" href="${esc(live())}" target="_blank" rel="noopener">${IC.ext} Na webu</a>` : ''}<button class="btn btn-teal" data-save2>${IC.check} Uložit</button>`);
  const feat = () => S.D.site['home.feature_slug'] === x.slug;
  const touch = () => { x.updated = new Date().toISOString(); changed(); preview(); };
  page().innerHTML = `
    <div class="page-head"><div><h1>${isNew ? 'Nová <em>nemovitost</em>' : esc(x.short || x.title)}</h1><p>${isNew ? 'Vyplňte základní údaje, přidejte fotky a popis. Nakonec uložte — nemovitost se objeví na webu.' : 'Upravte údaje, fotky nebo popis. Změny se projeví po uložení.'}</p></div></div>
    <div class="ed">
      <div>
        <section class="card sec"><div class="card-head"><h3><span class="n">1</span>Základní údaje</h3></div><div class="card-pad fgrid">
          <div class="f big full"><label for="l-title">Název nemovitosti</label><input type="text" id="l-title" data-f="title" value="${esc(x.title)}" placeholder="např. Rodinný dům 4+kk se zahradou, Hradec Králové"></div>
          <div class="f full"><label for="l-short">Krátký název <span class="opt">na kartičky, max. ~45 znaků</span></label><input type="text" id="l-short" data-f="short" value="${esc(x.short)}" placeholder="např. Rodinný dům 4+kk, Vinary"></div>
          <div class="f"><label for="l-type">Typ</label><select id="l-type" data-f="type">${TYPES.map((t) => `<option ${x.type === t ? 'selected' : ''}>${t}</option>`).join('')}</select></div>
          <div class="f"><label for="l-addr">Adresa / lokalita</label><input type="text" id="l-addr" data-f="address" value="${esc(x.address)}" placeholder="Ulice, obec"></div>
          <div class="f full"><div class="lab">Stav</div><div class="seg" data-status>${STATUSES.map(([k, l]) => `<button type="button" data-s="${k}" class="${x.status === k ? 'on' : ''}"><span class="dot dot-${k}"></span>${l}</button>`).join('')}</div></div>
          <div class="f"><label for="l-pl">Popisek ceny</label><select id="l-pl" data-f="price_label">${['Cena', 'Nájem', 'Cena od', 'Cena za m²'].map((t) => `<option ${x.price_label === t ? 'selected' : ''}>${t}</option>`).join('')}</select></div>
          <div class="f"><label for="l-price">Cena</label><input type="text" id="l-price" data-f="price" value="${esc(x.price)}" placeholder="např. 4 250 000 Kč"><div class="hint">Nechte prázdné pro „Na dotaz“.</div></div>
        </div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">2</span>Parametry <small>zobrazí se v pruhu pod fotkou</small></h3><button class="btn btn-ghost btn-sm" data-addfact>${IC.plus} Přidat</button></div><div class="card-pad"><div class="facts" data-facts></div></div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">3</span>Popis</h3></div><div class="card-pad" style="display:grid;gap:1.1rem">
          <div class="f"><label for="l-lead">Úvodní věta (perex)</label><textarea id="l-lead" data-f="lead" rows="3" placeholder="Jedna až dvě věty, které nemovitost vystihnou. Zobrazí se velkým písmem nad popisem.">${esc(x.lead)}</textarea></div>
          <div class="f"><div class="lab">Podrobný popis</div><div data-rte></div><div class="hint">Nadpisy, tučné písmo, odrážky i odkazy nastavíte v liště nad textem.</div></div>
        </div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">4</span>Fotografie <small>první fotka je titulní</small></h3><span class="muted" data-cnt="photos"></span></div><div class="card-pad" data-galwrap="photos"></div></section>
        <section class="card sec"><div class="card-head"><h3><span class="n">5</span>Půdorysy <small>nepovinné</small></h3><span class="muted" data-cnt="plans"></span></div><div class="card-pad" data-galwrap="plans"></div></section>
        <section class="card sec"><div class="card-head"><h3><span class="n">6</span>Vizualizace <small>nepovinné — „Jak to může vypadat“</small></h3><span class="muted" data-cnt="viz"></span></div><div class="card-pad" data-galwrap="viz"></div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">7</span>Adresa stránky a vyhledávače</h3></div><div class="card-pad fgrid">
          <div class="f full"><label for="l-slug">Adresa stránky (URL)</label><div class="affix"><span>…/nemovitosti/</span><input type="text" id="l-slug" data-f="slug" value="${esc(x.slug)}"></div><div class="hint">Jen malá písmena bez diakritiky, čísla a pomlčky. ${isNew ? 'Vyplní se samo podle názvu.' : 'Změna adresy rozbije staré odkazy na tuto nemovitost.'}</div></div>
          <div class="f full"><label for="l-seo">Popis pro Google <span class="opt">nepovinné</span></label><textarea id="l-seo" data-f="seo_desc" rows="2" placeholder="Když necháte prázdné, použije se úvodní věta.">${esc(x.seo_desc)}</textarea></div>
          <div class="f full"><div class="lab">Náhledový obrázek na kartičce <span class="opt">použije se jen když nejsou fotky</span></div>${imgPick(() => x.thumb, (v) => { x.thumb = v; touch(); })}</div>
        </div></section>
      </div>
      <aside class="ed-side">
        <div class="card pv-card"><div class="pv-label">Náhled kartičky</div><div style="padding:.8rem 1.1rem 0"><div class="img" style="border-radius:10px;overflow:hidden" data-pv-img></div></div><div class="body" data-pv-body></div></div>
        <div class="card"><div class="side-list">
          <label class="tog"><span>Na úvodní stránce<small>V pásu „Aktuální nabídka“</small></span><input type="checkbox" data-t="home" ${x.home ? 'checked' : ''}><span class="sw"></span></label>
          <label class="tog"><span>Hlavní nemovitost<small>Velká fotka přes celou šířku úvodu</small></span><input type="checkbox" data-feat ${feat() ? 'checked' : ''}><span class="sw"></span></label>
          <label class="tog"><span>Skrýt z webu<small>Zůstane jen v administraci</small></span><input type="checkbox" data-t="hidden" ${x.hidden ? 'checked' : ''}><span class="sw"></span></label>
        </div></div>
        <div class="card card-pad" style="display:grid;gap:.6rem">
          <button class="btn btn-primary btn-lg" data-save3>${IC.check} Uložit a zveřejnit</button>
          <button class="btn btn-ghost" data-dup>${IC.copy} Duplikovat</button>
          <button class="btn btn-danger" data-del>${IC.trash} Smazat nemovitost</button>
          <p class="hint" style="text-align:center">${x.updated ? 'Naposledy upraveno ' + ago(x.updated) : ''}</p>
        </div>
      </aside>
    </div>`;
  const root = page();
  let slugTouched = !isNew;
  const preview = () => {
    const c = (x.photos || [])[0] || x.thumb || (x.viz || [])[0];
    $('[data-pv-img]', root).innerHTML = `<div class="img">${c ? `<img src="${esc(src(c))}" alt="">` : ''}<span class="st st-${x.status}">${STATUS_L[x.status]}</span></div>`;
    $('[data-pv-body]', root).innerHTML = `<small><span>${esc(x.type)}</span><span>${esc(x.price || 'Na dotaz')}</span></small><b>${esc(x.short || x.title || 'Název nemovitosti')}</b><small>${esc(x.address || 'Adresa')}</small>`;
    ['photos', 'plans', 'viz'].forEach((k) => { const el = $(`[data-cnt="${k}"]`, root); if (el) el.textContent = (x[k] || []).length ? `${x[k].length} ks` : ''; });
  };
  root.addEventListener('input', (e) => {
    const f = e.target.dataset.f; if (!f) return;
    let v = e.target.value;
    if (f === 'slug') { v = slugify(v) || ''; slugTouched = true; }
    x[f] = v;
    if (f === 'title' && !slugTouched) { x.slug = uniqueSlug(slugify(v) || 'nova-nemovitost', x); $('#l-slug').value = x.slug; }
    if (f === 'slug') x.id = x.id; // keep stable id for routing
    touch();
  });
  $('#l-slug').addEventListener('blur', (e) => { x.slug = uniqueSlug(slugify(e.target.value) || 'nemovitost', x); e.target.value = x.slug; touch(); });
  $('[data-status]', root).addEventListener('click', (e) => { const b = e.target.closest('[data-s]'); if (!b) return; x.status = b.dataset.s; $$('[data-s]', root).forEach((i) => i.classList.toggle('on', i === b)); touch(); });
  root.addEventListener('change', (e) => {
    if (e.target.dataset.t) { x[e.target.dataset.t] = e.target.checked; touch(); }
    if (e.target.hasAttribute('data-feat')) { if (e.target.checked) { S.D.site['home.feature_slug'] = x.slug; S.D.site['home.feature_image'] = (x.photos || [])[0] || x.thumb || ''; toast('Nastaveno jako hlavní nemovitost', 'Fotku na úvodu můžete změnit v Texty a obrázky → Úvodní stránka.'); } else if (feat()) { S.D.site['home.feature_slug'] = ''; } changed(); }
  });
  // facts
  const drawFacts = () => {
    $('[data-facts]', root).innerHTML = (x.facts || []).map((f, i) => `<div class="fact"><input class="in" type="text" data-fv="${i}" value="${esc(f.v)}" placeholder="Hodnota (např. 4+kk)"><input class="in" type="text" data-fl="${i}" value="${esc(f.l)}" placeholder="Popisek (např. Dispozice)"><button class="icon-btn danger" data-frm="${i}" title="Odebrat">${IC.trash}</button></div>`).join('') || '<p class="muted">Zatím žádné parametry.</p>';
  };
  drawFacts();
  $('[data-facts]', root).addEventListener('input', (e) => { const t = e.target; if (t.dataset.fv) x.facts[+t.dataset.fv].v = t.value; if (t.dataset.fl) x.facts[+t.dataset.fl].l = t.value; touch(); e.stopPropagation(); });
  $('[data-facts]', root).addEventListener('click', (e) => { const b = e.target.closest('[data-frm]'); if (b) { x.facts.splice(+b.dataset.frm, 1); drawFacts(); touch(); } });
  $('[data-addfact]', root).addEventListener('click', () => { (x.facts ||= []).push({ v: '', l: '' }); drawFacts(); touch(); $$('[data-fv]', root).pop()?.focus(); });
  // galleries
  ['photos', 'plans', 'viz'].forEach((k) => {
    x[k] ||= [];
    const wrap = $(`[data-galwrap="${k}"]`, root);
    const draw = () => { wrap.innerHTML = galleryHTML(x[k], k, k === 'plans'); bindGallery(wrap, x, k, x.short || x.title, () => { draw(); touch(); }); };
    draw();
  });
  mountRTE($('[data-rte]', root), x.body, (h) => { x.body = h; touch(); }, 'Popište nemovitost — dispozici, stav, okolí, pro koho je ideální…');
  bindIP(root);
  preview();
  const save = () => saveAll();
  $('[data-save2]').addEventListener('click', save); $('[data-save3]', root).addEventListener('click', save);
  $('[data-dup]', root).addEventListener('click', () => { const c = clone(x); c.title = (c.title || '') + ' (kopie)'; c.slug = c.id = uniqueSlug(slugify(x.slug + '-kopie')); c.updated = new Date().toISOString(); L.splice(L.indexOf(x) + 1, 0, c); changed(); toast('Vytvořena kopie', 'Upravujete teď kopii.'); location.hash = '#/nemovitost/' + c.id; });
  $('[data-del]', root).addEventListener('click', async () => { if (await confirmDlg('Smazat nemovitost?', `„${esc(x.short || x.title || 'Nová nemovitost')}“ zmizí z webu. Pokud ji jen nechcete ukazovat, použijte raději „Skrýt z webu“.`)) { L.splice(L.indexOf(x), 1); if (feat()) S.D.site['home.feature_slug'] = ''; changed(); location.hash = '#/nemovitosti'; toast('Nemovitost smazána', 'Projeví se po uložení.'); } });
  if (isNew) setTimeout(() => $('#l-title')?.focus(), 60);
}

/* ------------------------------------------------------------ POSTS */
function viewPosts() {
  updateNav('blog');
  setTop([['Blog']], `<a class="btn btn-primary" href="#/clanek/new">${IC.plus} Napsat článek</a>`);
  const P = S.D.posts;
  const sorted = [...P].sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  page().innerHTML = `<div class="page-head"><div><h1>Blog</h1><p>Články se na webu řadí podle data — nejnovější je vždy první a zvýrazněný.</p></div></div>
    <div class="post-grid">
      <a class="card pc" href="#/clanek/new" style="border:1.5px dashed #C9D2DE;box-shadow:none;background:transparent;display:grid;place-items:center;min-height:260px;text-align:center;color:var(--muted)"><span>${IC.plus.replace('<svg', '<svg width="30" height="30"')}<br><b style="font-family:var(--serif);font-weight:400;font-size:1.5rem;color:var(--text)">Nový článek</b></span></a>
      ${sorted.map((p) => `<a class="card pc" href="#/clanek/${esc(p.slug)}"${p.hidden ? ' style="opacity:.55"' : ''}><div class="img">${p.image ? `<img src="${esc(src(p.image))}" alt="" loading="lazy">` : ''}</div><div class="b"><small><span>${czDate(p.date)}</span>${p.hidden ? '<span class="st st-hidden">Skryto</span>' : ''}</small><b>${esc(p.title)}</b></div></a>`).join('')}
    </div>`;
}
function viewPost(slug) {
  updateNav('blog');
  const P = S.D.posts;
  if (slug === 'new') {
    const p = { slug: '', title: '', date: today(), image: '', excerpt: '', body: '', hidden: false };
    p.slug = uniqueSlug('novy-clanek', p, P); p._new = true; P.unshift(p); FRESH.add(p); changed();
    history.replaceState(null, '', '#/clanek/' + p.slug);
    return viewPost(p.slug);
  }
  const p = P.find((i) => i.slug === slug);
  if (!p) { page().innerHTML = `<div class="empty"><b>Článek nenalezen</b><a class="btn btn-ghost" href="#/blog">Zpět na blog</a></div>`; return; }
  const isNew = !!p._new; delete p._new;
  let slugTouched = !isNew;
  setTop([['Blog', '#/blog'], [p.title || 'Nový článek']], `${!isNew ? `<a class="btn btn-ghost" href="${CFG.site}blog/${esc(p.slug)}.html" target="_blank" rel="noopener">${IC.ext} Na webu</a>` : ''}<button class="btn btn-teal" data-save2>${IC.check} Uložit</button>`);
  page().innerHTML = `<div class="page-head"><div><h1>${isNew ? 'Nový <em>článek</em>' : 'Upravit článek'}</h1></div></div>
    <div class="ed"><div>
      <section class="card sec"><div class="card-pad fgrid">
        <div class="f big full"><label for="p-title">Nadpis článku</label><input type="text" id="p-title" data-f="title" value="${esc(p.title)}" placeholder="Např. Jak se připravit na prodej domu"></div>
        <div class="f full"><label for="p-ex">Perex <span class="opt">krátké shrnutí na kartičku</span></label><textarea id="p-ex" data-f="excerpt" rows="3">${esc(p.excerpt)}</textarea></div>
        <div class="f full"><div class="lab">Text článku</div><div data-rte></div></div>
      </div></section>
    </div>
    <aside class="ed-side">
      <div class="card card-pad" style="display:grid;gap:1rem">
        <div class="f"><div class="lab">Titulní obrázek</div>${imgPick(() => p.image, (v) => { p.image = v; changed(); }, { hint: p.title })}</div>
        <div class="f"><label for="p-date">Datum</label><input type="date" id="p-date" data-f="date" value="${esc(p.date)}"></div>
        <div class="f"><label for="p-slug">Adresa (URL)</label><div class="affix"><span>…/blog/</span><input type="text" id="p-slug" data-f="slug" value="${esc(p.slug)}"></div></div>
        <label class="tog" style="justify-content:space-between"><span>Skrýt z webu</span><input type="checkbox" data-hide ${p.hidden ? 'checked' : ''}><span class="sw"></span></label>
      </div>
      <div class="card card-pad" style="display:grid;gap:.6rem">
        <button class="btn btn-primary btn-lg" data-save3>${IC.check} Uložit a zveřejnit</button>
        <button class="btn btn-danger" data-del>${IC.trash} Smazat článek</button>
      </div>
    </aside></div>`;
  const root = page();
  root.addEventListener('input', (e) => {
    const f = e.target.dataset.f; if (!f) return;
    if (f === 'slug') { slugTouched = true; p.slug = slugify(e.target.value); }
    else p[f] = e.target.value;
    if (f === 'title' && !slugTouched) { p.slug = uniqueSlug(slugify(p.title) || 'novy-clanek', p, P); $('#p-slug').value = p.slug; }
    changed();
  });
  $('#p-slug').addEventListener('blur', (e) => { p.slug = uniqueSlug(slugify(e.target.value) || 'clanek', p, P); e.target.value = p.slug; history.replaceState(null, '', '#/clanek/' + p.slug); changed(); });
  $('#p-title').addEventListener('blur', () => { if (!slugTouched) history.replaceState(null, '', '#/clanek/' + p.slug); });
  $('[data-hide]', root).addEventListener('change', (e) => { p.hidden = e.target.checked; changed(); });
  mountRTE($('[data-rte]', root), p.body, (h) => { p.body = h; changed(); }, 'Napište článek… Nadpisy a odrážky nastavíte v liště nahoře.');
  bindIP(root);
  $('[data-save2]').addEventListener('click', saveAll); $('[data-save3]', root).addEventListener('click', saveAll);
  $('[data-del]', root).addEventListener('click', async () => { if (await confirmDlg('Smazat článek?', `„${esc(p.title || 'Nový článek')}“ zmizí z webu.`)) { P.splice(P.indexOf(p), 1); changed(); location.hash = '#/blog'; } });
  if (isNew) setTimeout(() => $('#p-title')?.focus(), 60);
}

/* ------------------------------------------------------------ REVIEWS */
function viewReviews() {
  updateNav('reference');
  setTop([['Reference']], `<button class="btn btn-primary" data-add>${IC.plus} Přidat referenci</button>`);
  const V = S.D.reviews;
  const draw = () => {
    page().innerHTML = `<div class="page-head"><div><h1>Reference</h1><p>Hodnocení klientů. Na webu se zobrazují v tomto pořadí — na úvodní stránce v běžícím pásu, na stránce Reference všechna i s vašimi odpověďmi.</p></div>
      <div class="card card-pad" style="display:flex;gap:1.2rem;align-items:center;padding:1rem 1.3rem"><b style="font-family:var(--serif);font-weight:400;font-size:2.6rem;line-height:1">${esc(S.D.site['rating.value'])}</b><span class="muted" style="font-size:.84rem">${esc(S.D.site['rating.count'])} hodnocení · ${esc(S.D.site['rating.source'])}<br><a href="#/obsah/general" style="color:var(--teal-d);font-weight:600">Upravit souhrnné hodnocení</a></span></div></div>
      <div class="rev-grid">${V.map((r, i) => `<article class="card rv${r.hidden ? ' is-hidden' : ''}"><span class="stars">${'★'.repeat(r.stars || 5)}${'☆'.repeat(5 - (r.stars || 5))}</span><p>${esc(r.text)}</p>${r.reply ? `<p class="muted" style="font-size:.82rem;-webkit-line-clamp:2">↳ ${esc(r.reply)}</p>` : ''}
        <footer><span><b>${esc(r.name)}</b><br><small class="muted">${esc(r.date)}${r.hidden ? ' · skryto' : ''}</small></span><span class="acts">
          <button class="icon-btn" data-up="${i}" title="Posunout výš">${IC.up}</button><button class="icon-btn" data-down="${i}" title="Posunout níž">${IC.down}</button>
          <button class="icon-btn" data-hide="${i}" title="${r.hidden ? 'Zobrazit' : 'Skrýt'}">${r.hidden ? IC.eyeOff : IC.eye}</button>
          <button class="icon-btn" data-edit="${i}" title="Upravit">${IC.pen}</button><button class="icon-btn danger" data-del="${i}" title="Smazat">${IC.trash}</button></span></footer></article>`).join('')}</div>`;
  };
  const edit = async (r, isNew) => {
    let stars = r.stars || 5;
    const v = await modal({
      title: isNew ? 'Nová reference' : 'Upravit referenci',
      body: `<div class="fgrid"><div class="f"><label>Jméno klienta</label><input type="text" data-n value="${esc(r.name)}"></div><div class="f"><label>Datum</label><input type="text" data-d value="${esc(r.date)}" placeholder="např. 07.05.2026"></div>
        <div class="f full"><div class="lab">Hodnocení</div><div class="star-pick">${[1, 2, 3, 4, 5].map((n) => `<button type="button" data-star="${n}" class="${n <= stars ? 'on' : ''}">★</button>`).join('')}</div></div>
        <div class="f full"><label>Text hodnocení</label><textarea data-t rows="5">${esc(r.text)}</textarea></div>
        <div class="f full"><label>Vaše odpověď <span class="opt">nepovinné</span></label><textarea data-r rows="3">${esc(r.reply)}</textarea></div></div>`,
      actions: [{ label: 'Zrušit', value: false }, { label: isNew ? 'Přidat' : 'Hotovo', cls: 'btn-primary', get: (bg) => {
        const n = $('[data-n]', bg).value.trim(), t = $('[data-t]', bg).value.trim();
        if (!n || !t) { toast('Doplňte jméno a text', '', 'err'); return false; }
        return { name: n, date: $('[data-d]', bg).value.trim(), text: t, reply: $('[data-r]', bg).value.trim(), stars };
      } }],
      onMount: (bg) => bg.querySelector('.star-pick').addEventListener('click', (e) => { const b = e.target.closest('[data-star]'); if (!b) return; stars = +b.dataset.star; $$('[data-star]', bg).forEach((x) => x.classList.toggle('on', +x.dataset.star <= stars)); }),
    });
    if (!v) return false;
    Object.assign(r, v); return true;
  };
  draw();
  const add = async () => { const r = { name: '', stars: 5, date: new Date().toLocaleDateString('cs-CZ', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\s/g, ''), text: '', reply: '', hidden: false }; if (await edit(r, true)) { V.unshift(r); changed(); draw(); toast('Reference přidána', 'Nezapomeňte uložit.'); } };
  $('[data-add]').addEventListener('click', add);
  page().addEventListener('click', async (e) => {
    const b = e.target.closest('button'); if (!b) return; const d = b.dataset;
    if (d.up) { move(V, +d.up, +d.up - 1); changed(); draw(); }
    if (d.down) { move(V, +d.down, +d.down + 1); changed(); draw(); }
    if (d.hide) { V[+d.hide].hidden = !V[+d.hide].hidden; changed(); draw(); }
    if (d.edit) { if (await edit(V[+d.edit], false)) { changed(); draw(); } }
    if (d.del) { if (await confirmDlg('Smazat referenci?', `Reference od „${esc(V[+d.del].name)}“ bude odstraněna.`)) { V.splice(+d.del, 1); changed(); draw(); } }
  });
  if (sessionStorage.getItem('tv_newrev')) { sessionStorage.removeItem('tv_newrev'); add(); }
}

/* ------------------------------------------------------------ TEXTS (schema driven) */
const MDHELP = `<div class="md-help"><span><code>*slovo*</code> → <em>zvýraznění</em></span><span><code>**slovo**</code> → <b>tučně</b></span><span>Enter → nový řádek</span></div>`;
function fieldHTML(f, get, set, ctx) {
  const v = get() ?? '';
  const id = 'f' + uid();
  const lab = `<label for="${id}">${esc(f.label)}</label>`;
  const hint = f.hint ? `<div class="hint">${esc(f.hint)}</div>` : '';
  ctx.bind.push([id, set]);
  switch (f.kind) {
    case 'md': return `<div class="f">${lab}<textarea class="short" id="${id}" data-auto rows="1">${esc(v)}</textarea>${MDHELP}${hint}</div>`;
    case 'textarea': return `<div class="f">${lab}<textarea id="${id}" data-auto rows="4">${esc(v)}</textarea>${hint}</div>`;
    case 'image': ctx.bind.pop(); return `<div class="f"><div class="lab">${esc(f.label)}</div>${imgPick(get, (x) => { set(x); }, { hint: f.label })}${hint}</div>`;
    case 'listing': return `<div class="f">${lab}<select id="${id}"><option value="">— žádná —</option>${S.D.listings.filter((x) => !x.hidden).map((x) => `<option value="${esc(x.slug)}" ${x.slug === v ? 'selected' : ''}>${esc(x.short || x.title)}</option>`).join('')}</select>${hint}</div>`;
    case 'bool': return `<div class="f"><label class="tog"><input type="checkbox" id="${id}" ${v ? 'checked' : ''}><span class="sw"></span>${esc(f.label)}</label>${hint}</div>`;
    default: return `<div class="f">${lab}<input type="text" id="${id}" value="${esc(v)}">${hint}</div>`;
  }
}
function bindFields(root, ctx) {
  ctx.bind.forEach(([id, set]) => {
    const el = root.querySelector('#' + id); if (!el) return;
    const ev = el.type === 'checkbox' || el.tagName === 'SELECT' ? 'change' : 'input';
    el.addEventListener(ev, () => { set(el.type === 'checkbox' ? el.checked : el.value); changed(); if (el.dataset.auto !== undefined) autosize(el); });
    if (el.dataset.auto !== undefined) requestAnimationFrame(() => autosize(el));
  });
  ctx.bind = [];
}
function listEditor(f) {
  const arr = S.D.site[f.key] ||= [];
  const wrap = document.createElement('div');
  wrap.className = 'f full';
  let open = -1;
  const titleOf = (it, i) => { const t = it[f.title] ?? it[f.fields[0]?.name]; return String(t ?? '').replace(/[*~]/g, '').trim() || `Položka ${i + 1}`; };
  const draw = () => {
    const ctx = { bind: [] };
    wrap.innerHTML = `<div class="lab">${esc(f.label)}<span class="opt">${arr.length} ${arr.length === 1 ? 'položka' : arr.length < 5 && arr.length ? 'položky' : 'položek'}</span></div>${f.hint ? `<div class="hint" style="margin:-.1rem 0 .5rem">${esc(f.hint)}</div>` : ''}
      <div class="li-ed">${arr.map((it, i) => `<div class="li${i === open ? ' open' : ''}" data-i="${i}"><div class="li-h" data-tg="${i}"><span class="num">${i + 1}</span><span class="t">${esc(titleOf(it, i))}${f.fields.find((x) => x.name === 'phase') && it.phase ? ` <small>· ${esc(it.phase)}</small>` : ''}</span>
        <button type="button" class="icon-btn" data-mu="${i}" title="Výš">${IC.up}</button><button type="button" class="icon-btn" data-md="${i}" title="Níž">${IC.down}</button><button type="button" class="icon-btn danger" data-rm="${i}" title="Odebrat">${IC.trash}</button><span class="icon-btn" aria-hidden="true" style="transform:rotate(${i === open ? 180 : 0}deg)">${IC.chev}</span></div>
        <div class="li-b">${i === open ? f.fields.map((ff) => fieldHTML(ff, () => it[ff.name], (v) => { it[ff.name] = v; const t = wrap.querySelector(`.li[data-i="${i}"] .li-h .t`); if (t && (ff.name === f.title || ff.name === f.fields[0].name)) t.textContent = titleOf(it, i); }, ctx)).join('') : ''}</div></div>`).join('')}
      <button type="button" class="btn btn-ghost btn-sm li-add" data-add>${IC.plus} Přidat položku</button></div>`;
    bindFields(wrap, ctx); bindIP(wrap);
  };
  wrap.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-mu],[data-md],[data-rm],[data-add],[data-tg]'); if (!b) return;
    const d = b.dataset;
    if (d.mu !== undefined) { e.stopPropagation(); move(arr, +d.mu, +d.mu - 1); if (open === +d.mu) open--; changed(); draw(); return; }
    if (d.md !== undefined) { e.stopPropagation(); move(arr, +d.md, +d.md + 1); if (open === +d.md) open++; changed(); draw(); return; }
    if (d.rm !== undefined) { e.stopPropagation(); if (await confirmDlg('Odebrat položku?', `„${esc(titleOf(arr[+d.rm], +d.rm))}“ bude odebrána.`, 'Odebrat')) { arr.splice(+d.rm, 1); open = -1; changed(); draw(); } return; }
    if (d.add !== undefined) { const it = Object.fromEntries(f.fields.map((x) => [x.name, x.kind === 'bool' ? false : ''])); if (arr.length && f.fields.some((x) => x.name === 'phase')) it.phase = arr[arr.length - 1].phase; arr.push(it); open = arr.length - 1; changed(); draw(); wrap.querySelector('.li.open input, .li.open textarea')?.focus(); return; }
    if (d.tg !== undefined) { open = open === +d.tg ? -1 : +d.tg; draw(); }
  });
  draw();
  return wrap;
}
function viewTexts(pid) {
  const p = S.schema.find((x) => x.id === pid) || S.schema[0];
  updateNav(p.id === 'general' ? 'general' : 'obsah', p.id);
  const pageUrl = { home: '', story: 'pribeh.html', process: 'jak-pracuji.html', listing: 'nemovitosti.html', services: 'sluzby.html', reference: 'reference.html', blogpage: 'blog.html', estimate: 'odhad-ceny.html', contactpage: 'kontakt.html' }[p.id];
  setTop([['Texty a obrázky', '#/obsah/home'], [p.title]], `${pageUrl !== undefined ? `<a class="btn btn-ghost" href="${CFG.site}${pageUrl}" target="_blank" rel="noopener">${IC.ext} Stránka na webu</a>` : ''}<button class="btn btn-teal" data-save2>${IC.check} Uložit</button>`);
  page().innerHTML = `<div class="page-head"><div><h1>${p.id === 'general' ? 'Kontakty a <em>firma</em>' : esc(p.title)}</h1><p>${p.id === 'general' ? 'Údaje, které se opakují na celém webu — v hlavičce, patičce, kontaktech i na kartách nemovitostí.' : 'Upravte texty a obrázky této stránky. Sekce otevřete kliknutím.'}</p></div></div>
    ${p.id !== 'general' ? `<nav class="tabs">${pagesNav().map((x) => `<a href="#/obsah/${x.id}" class="${x.id === p.id ? 'on' : ''}">${esc(x.title)}</a>`).join('')}</nav>` : ''}
    <div data-secs></div>`;
  const secs = $('[data-secs]');
  p.sections.forEach((sec, si) => {
    const d = document.createElement('details');
    d.className = 'card acc'; if (si === 0 || (p.id === 'general' && si < 2)) d.open = true;
    d.innerHTML = `<summary>${esc(sec.title)} <small>${sec.fields.length} ${sec.fields.length === 1 ? 'pole' : sec.fields.length < 5 ? 'pole' : 'polí'}</small><span class="chev">${IC.chev.replace('<svg', '<svg width="18" height="18"')}</span></summary><div class="acc-body"></div>`;
    const body = d.querySelector('.acc-body');
    const ctx = { bind: [] };
    let html = '';
    const lists = [];
    sec.fields.forEach((f) => {
      if (f.kind === 'list') { html += `<div data-list-slot="${lists.length}"></div>`; lists.push(f); }
      else html += fieldHTML(f, () => S.D.site[f.key], (v) => { S.D.site[f.key] = v; }, ctx);
    });
    body.innerHTML = html;
    bindFields(body, ctx); bindIP(body);
    lists.forEach((f, i) => body.querySelector(`[data-list-slot="${i}"]`).replaceWith(listEditor(f)));
    d.addEventListener('toggle', () => { if (d.open) $$('textarea[data-auto]', d).forEach(autosize); });
    secs.appendChild(d);
  });
  $('[data-save2]').addEventListener('click', saveAll);
}

/* ------------------------------------------------------------ SETTINGS */
function viewSettings() {
  updateNav('nastaveni');
  setTop([['Nastavení']]);
  page().innerHTML = `<div class="page-head"><div><h1>Nastavení</h1><p>Heslo do administrace, stav webu a zálohy.</p></div></div>
    <div class="dash-grid">
      <div style="display:grid;gap:1.4rem;align-content:start">
        <section class="card"><div class="card-head"><h3>Heslo do administrace</h3>${S.def ? '<span class="st st-rezervace">Výchozí heslo</span>' : '<span class="st st-nabidka">Nastaveno</span>'}</div>
          <form class="card-pad fgrid" data-pw>
            <div class="f full"><label>Současné heslo</label><input type="password" name="old" autocomplete="current-password"></div>
            <div class="f"><label>Nové heslo</label><input type="password" name="n1" autocomplete="new-password" minlength="8"></div>
            <div class="f"><label>Nové heslo znovu</label><input type="password" name="n2" autocomplete="new-password"></div>
            <div class="full" style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap"><span class="hint" style="margin:0">Alespoň 8 znaků. Po změně se odhlásí všechna ostatní zařízení.</span><button class="btn btn-primary" type="submit">Změnit heslo</button></div>
          </form></section>
        <section class="card"><div class="card-head"><h3>Zabezpečení</h3><span class="st st-nabidka">Chráněno</span></div>
          <div class="card-pad" style="display:grid;gap:.7rem;font-size:.9rem;color:#344054">
            <p>Heslo se ověřuje na zabezpečeném serveru a nikde na webu není uložené. Po 8 chybných pokusech se přihlašování na 15 minut zablokuje.</p>
            <p>Přihlášení platí 12 hodin, pak vás administrace požádá o heslo znovu — rozpracované změny se přitom neztratí.</p>
          </div></section>
      </div>
      <div style="display:grid;gap:1.4rem;align-content:start">
        <section class="card"><div class="card-head"><h3>Stav webu</h3></div><div class="card-pad" style="display:grid;gap:.8rem">
          <div class="pub ${S.pub.state}" style="background:var(--line-2);color:var(--text)"><i></i><span>${esc(S.pub.text)}</span></div>
          <p class="muted" style="font-size:.86rem">Po uložení se web automaticky přegeneruje a zveřejní. Obvykle to trvá 30–90 sekund.</p>
          <a class="btn btn-ghost" href="../" target="_blank" rel="noopener">${IC.ext} Otevřít web</a>
        </div></section>
        <section class="card"><div class="card-head"><h3>Záloha dat</h3></div><div class="card-pad" style="display:grid;gap:.8rem">
          <p class="muted" style="font-size:.86rem">Stáhněte si kompletní obsah webu (nemovitosti, články, reference a texty) do jednoho souboru. Každé uložení se navíc automaticky archivuje, takže se dá vrátit i starší verze.</p>
          <button class="btn btn-ghost" data-backup>${IC.download} Stáhnout zálohu</button>
        </div></section>
        <section class="card"><div class="card-pad" style="display:grid;gap:.6rem"><button class="btn btn-ghost" data-lo>${IC.logout} Odhlásit se</button></div></section>
      </div>
    </div>`;
  $('[data-lo]').addEventListener('click', logout);
  $('[data-backup]').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({ exported: new Date().toISOString(), ...S.D }, null, 1)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${CFG.id}-zaloha-${today()}.json`; a.click();
  });
  $('[data-pw]').addEventListener('submit', async (e) => {
    e.preventDefault(); const f = e.target; const b = f.querySelector('[type=submit]');
    const old = f.old.value, n1 = f.n1.value, n2 = f.n2.value;
    if (n1.length < 8) return toast('Nové heslo je příliš krátké', 'Použijte alespoň 8 znaků.', 'err');
    if (n1 !== n2) return toast('Hesla se neshodují', '', 'err');
    b.disabled = true; b.textContent = 'Měním…';
    try {
      const r = await api('/password', { method: 'POST', body: JSON.stringify({ old, password: n1 }) });
      S.sess = r.token; S.def = false; saveSess();
      toast('Heslo změněno', 'Příště se přihlaste novým heslem.', 'ok'); viewSettings();
    } catch (err) { toast('Heslo se nepodařilo změnit', err.message, 'err'); }
    finally { b.disabled = false; b.textContent = 'Změnit heslo'; }
  });
}

/* ------------------------------------------------------------ boot */
async function boot() {
  $('#app').innerHTML = `<div class="boot"><img src="../img/site/logo2-dark.png" alt=""><span class="muted" style="display:flex;gap:.7rem;align-items:center"><span class="spin"></span> Načítám obsah webu…</span></div>`;
  try { await loadAll(); }
  catch (e) {
    if (e.status === 401) { localStorage.removeItem('tv_sess_' + CFG.id); S.sess = null; return renderLogin('Přihlášení vypršelo. Přihlaste se prosím znovu.'); }
    $('#app').innerHTML = `<div class="boot"><div class="banner err" style="max-width:520px">${IC.alert}<span><b>Obsah se nepodařilo načíst</b>${esc(e.message)}</span><button class="btn btn-ghost btn-sm" onclick="location.reload()">Zkusit znovu</button></div></div>`;
    return;
  }
  renderShell(); route();
}
const sess = JSON.parse(localStorage.getItem('tv_sess_' + CFG.id) || 'null');
if (sess && sess.exp > Date.now()) { S.sess = sess.t; S.def = !!sess.def; boot(); } else renderLogin();
})();
