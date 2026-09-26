#!/usr/bin/env python3
"""Static site generator for tomasveigl — run: python3 _build/build.py
All content lives in _data/*.json (edited through /admin/). Texts default to _build/schema.py."""
import json, os, re, random, math, hashlib, shutil, html as H, urllib.parse
from datetime import date
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import sys; sys.path.insert(0, os.path.join(ROOT, '_build'))
from schema import SCHEMA, defaults

S = defaults()
S.update(json.load(open('_data/site.json')))
LIST = [x for x in json.load(open('_data/listings.json')) if not x.get('hidden')]
POSTS = sorted([p for p in json.load(open('_data/posts.json')) if not p.get('hidden')], key=lambda p: p['date'], reverse=True)
REVS = [r for r in json.load(open('_data/reviews.json')) if not r.get('hidden')]

BASE = 'https://webhunter-navrhy.github.io/tomasveigl/'
esc = H.escape
def T(k): return S.get(k, '')
def TL(k): return S.get(k) or []

TEL = T('contact.phone'); TEL_H = 'tel:' + re.sub(r'[^\d+]', '', TEL)
MAIL = T('contact.email'); ADDR = T('contact.address'); CAL = T('contact.calendar')
R11 = T('contact.reality11')
RATING = T('rating.value'); RCOUNT = T('rating.count'); RSRC = T('rating.source')

ARR = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M1 7h12M8 2l5 5-5 5" stroke="currentColor" stroke-width="1.4"/></svg>'
ARR_L = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M13 7H1M6 2L1 7l5 5" stroke="currentColor" stroke-width="1.4"/></svg>'
PIN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>'
PHONE_I = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z" stroke="currentColor" stroke-width="1.6"/></svg>'

# ------------------------------------------------------------------ text helpers
def md(s):
    """inline markup: *em* (accent), **strong**, ~soft~, newline -> <br>"""
    s = esc(str(s or ''), quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    s = re.sub(r'~(.+?)~', r'<span class="soft">\1</span>', s)
    return s.replace('\n', '<br>')

def paras(s, cls=''):
    parts = [p.strip() for p in re.split(r'\n\s*\n', str(s or '')) if p.strip()]
    return ''.join(('<p class="%s">' % cls if cls and i == 0 else '<p>') + md(p) + '</p>' for i, p in enumerate(parts))

def plain(s): return re.sub(r'[*~]', '', str(s or ''))
def strip_tags(s): return re.sub(r'<[^>]+>', '', s or '')
def fill(s, **kw):
    for k, v in kw.items(): s = s.replace('{' + k + '}', str(v))
    return s

def words(text, start=0):
    """'Slyším\\n*váš* domov.' -> animated word spans; *x* = accent, newline = new line"""
    i = start; lines = []
    for li, line in enumerate(str(text).split('\n')):
        out = []; em = False
        for w in line.split(' '):
            if not w: continue
            core = w.rstrip('.,!?:;'); tail = w[len(core):]
            st = core.startswith('*'); en = core.endswith('*') and len(core.strip('*')) > 0
            if st: em = True
            word = esc(core.strip('*'))
            inner = f'<em>{word}</em>{esc(tail)}' if em else esc(core.strip('*')) + esc(tail)
            if en: em = False
            out.append(f'<span class="w"><span style="--i:{i}">{inner}</span></span>'); i += 1
        lines.append(f'<span class="l{li+1}">{" ".join(out)}</span>')
    return ' '.join(lines), i

def link(h):
    """relative site links get the root prefix; absolute/anchor links stay"""
    h = h or '#'
    return h if re.match(r'^(https?:|mailto:|tel:|#)', h) else '@/' + h.lstrip('/')

class Clean(HTMLParser):
    OK = {'p', 'h2', 'h3', 'h4', 'strong', 'b', 'em', 'i', 'u', 'a', 'ul', 'ol', 'li', 'blockquote', 'br'}
    def __init__(s): super().__init__(convert_charrefs=True); s.out = []
    def handle_starttag(s, t, a):
        if t not in s.OK: return
        if t == 'a':
            href = dict(a).get('href') or ''
            if href.lower().startswith('javascript'): href = '#'
            ext = href.startswith('http')
            tgt = ' target="_blank" rel="noopener"' if ext else ''
            s.out.append('<a href="' + esc(href) + '"' + tgt + '>')
        else: s.out.append(f'<{t}>')
    def handle_endtag(s, t):
        if t in s.OK and t != 'br': s.out.append(f'</{t}>')
    def handle_data(s, d): s.out.append(esc(d, quote=False))
def clean_html(h):
    c = Clean(); c.feed(h or ''); out = ''.join(c.out)
    out = re.sub(r'<p>(\s|<br>)*</p>', '', out)
    return out

def btn(href, text, cls='', magnetic=False, ext=False):
    t = ' target="_blank" rel="noopener"' if ext else ''
    return f'<a href="{href}" class="btn {cls}{" btn-magnetic" if magnetic else ""}"{t}>{esc(text)} <span class="arr">{ARR}</span></a>'

def czdate(d):
    try: y, m, dd = d.split('-'); return f'{int(dd)}. {int(m)}. {y}'
    except Exception: return d

def wave(n=64, seed=1, live=False, cls='', lo=0.18, hi=1.0):
    rnd = random.Random(seed); bars = []
    for k in range(n):
        env = 0.35 + 0.65 * abs(math.sin((k / n) * 3.14159 * 2.2 + seed))
        s = max(lo, min(hi, env * rnd.uniform(0.35, 1.0)))
        d = rnd.uniform(0.7, 1.8); dl = -rnd.uniform(0, 2)
        bars.append(f'<i style="--s:{s:.2f};--d:{d:.2f}s;--dl:{dl:.2f}s;--k:{k}"></i>')
    return f'<div class="wave{" live" if live else ""} {cls}" aria-hidden="true">{"".join(bars)}</div>'
def divider(seed=3, n=110): return f'<div class="wave-divider" aria-hidden="true">{wave(n, seed)}</div>'
def ripples(cls=''): return f'<div class="ripples {cls}" aria-hidden="true"><span></span><span></span><span></span><span></span></div>'
def stars(n): n = max(0, min(5, int(n or 5))); return '★' * n + '☆' * (5 - n)

# ------------------------------------------------------------------ listings
STATUS = {'nabidka': ('nabidka', 'V nabídce', 'live'), 'pripravujeme': ('nabidka', 'Připravujeme', 'live'),
          'rezervace': ('rezervace', 'Rezervace', 'res'), 'prodano': ('prodano', 'Prodáno', 'done'),
          'pronajato': ('pronajato', 'Pronajato', 'done')}
for x in LIST:
    x['st'] = STATUS.get(x.get('status'), STATUS['nabidka'])
    x['has_detail'] = bool((x.get('body') or '').strip() or x.get('lead') or x.get('photos'))
    x['href'] = f'nemovitosti/{x["slug"]}.html' if x['has_detail'] else None
    x['card_img'] = (x.get('photos') or [None])[0] or x.get('thumb') or (x.get('viz') or [''])[0]
    x['name'] = x.get('short') or x['title']
BYSLUG = {x['slug']: x for x in LIST}

def type_key(x):
    t = (x.get('type') or '').lower()
    for key, needle in (('novostavba', 'novostav'), ('chata', 'chat'), ('dum', 'dům'), ('byt', 'byt'), ('pozemek', 'pozem'), ('komercni', 'komer')):
        if needle in t: return key
    return 'jine'

def card(x, r, feat=False, i=0):
    key, lab, kind = x['st']; done = kind == 'done'; href = x.get('href')
    price = f'<span class="price">{esc(x["price"])}</span>' if x.get('price') and not done else ''
    tag = 'a' if href else 'div'
    attrs = f' href="{r}{href}"' if href else ''
    go = f'<span class="go">{ARR}</span>' if href else ''
    stamp = f' data-stamp="{lab}"' if done else ''
    pill = '' if done else f'<span class="pill pill--{kind}">{lab}</span>'
    return (f'<{tag}{attrs} class="card reveal{" is-done" if done else ""}{" feat" if feat else ""}" style="--i:{i % 3}" '
            f'data-status="{key}" data-type="{type_key(x)}">'
            f'<div class="card-media"{stamp}><img src="{r}{x["card_img"]}" alt="{esc(x["name"])}" loading="lazy" decoding="async">{pill}{go}</div>'
            f'<div class="card-meta"><span>{esc(x.get("type") or "")}</span>{price}</div>'
            f'<h3>{esc(x["name"])}</h3>'
            f'<div class="card-meta"><span>{esc(x.get("address") or "")}</span></div></{tag}>')

def cta_card(r, cls='reveal'):
    return (f'<a href="{r}odhad-ceny.html" class="card-cta {cls}">{ripples()}<span class="label" style="color:#C9EEF2">{esc(T("listing.card_label"))}</span>'
            f'<h3>{md(T("listing.card_title"))}</h3>'
            f'<span class="row" style="font-weight:600;font-size:.9rem">{esc(T("listing.card_btn"))} {ARR}</span></a>')

# ------------------------------------------------------------------ layout
NAV = [('pribeh.html', 'Můj příběh'), ('jak-pracuji.html', 'Jak pracuji'), ('nemovitosti.html', 'Nemovitosti'),
       ('sluzby.html', 'Služby'), ('reference.html', 'Reference'), ('blog.html', 'Blog'), ('kontakt.html', 'Kontakt')]

def _ver(f): return hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]

def head(title, desc, r, img, path, ld=''):
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#F5F7FA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE}{img}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:type" content="website">
<link rel="canonical" href="{BASE}{path}">{ld}
<meta property="og:locale" content="cs_CZ">
<link rel="icon" type="image/png" href="{r}img/site/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/style.css?v={_ver('assets/css/style.css')}">
<script src="{r}assets/js/main.js?v={_ver('assets/js/main.js')}" defer></script>
</head>'''

def header(r, active):
    links = ''.join(f'<a href="{r}{h}" class="link-u{" active" if h == active else ""}">{t}</a>' for h, t in NAV)
    tb = ''.join(f'<span>{esc(it.get("title", ""))}</span>' for it in TL('topbar.items'))
    return f'''<a class="sr-only" href="#obsah">Přejít k obsahu</a>
<div class="scroll-progress" aria-hidden="true"></div>
<header class="nav">
  <div class="topbar">
    <div class="topbar-inner">
      <span class="tb-left">{tb}<a href="{r}reference.html" class="link-u"><span class="stars">★★★★★</span> {esc(RATING)} na {esc(RSRC)}</a></span>
      <span class="tb-right"><a class="link-u" href="{TEL_H}">{PHONE_I} {esc(TEL)}</a><a class="link-u" href="mailto:{MAIL}">{esc(MAIL)}</a><a class="tb-cal" href="{esc(CAL)}" target="_blank" rel="noopener">Online schůzka {ARR}</a></span>
    </div>
  </div>
  <div class="nav-inner">
    <div class="lockup">
      <a href="{r}index.html" class="brand" aria-label="Mgr. Tomáš Veigl — domů">
        <img class="b-dark" src="{r}img/site/logo2-dark.png" alt="tomasveigl.cz — Slyším váš domov" width="945" height="184">
        <img class="b-light" src="{r}img/site/logo2-light.png" alt="" width="945" height="184">
      </a>
      <span class="brand-sep" aria-hidden="true"></span>
      <a href="{esc(R11)}" class="brand-r11" target="_blank" rel="noopener" aria-label="Reality 11">
        <img class="b-dark" src="{r}img/site/r11-dark.png" alt="reality11" width="600" height="229">
        <img class="b-light" src="{r}img/site/r11-light.png" alt="" width="600" height="229">
      </a>
    </div>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
    <nav class="nav-menu" aria-label="Hlavní navigace">
      {links}
      {btn(r + 'odhad-ceny.html', T('home.hero_cta'), 'btn-magnetic')}
      <a href="{TEL_H}" class="nav-phone"><i></i>{esc(TEL)}</a>
    </nav>
  </div>
</header>'''

def footer(r):
    docs = ''.join(f'<a class="link-u" href="{esc(d.get("url", "#"))}" target="_blank" rel="noopener">{esc(d.get("title", ""))}</a>' for d in TL('footer.docs'))
    return f'''<div class="mbar"><a href="{TEL_H}" class="mbar-call">{PHONE_I} Zavolat</a><a href="{r}odhad-ceny.html" class="mbar-cta">{esc(T('home.hero_cta'))} {ARR}</a></div>
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a href="{r}index.html" class="footer-logo"><img src="{r}img/site/logo2-light.png" alt="tomasveigl.cz — Slyším váš domov" width="945" height="184"></a>
        <img class="footer-powered" src="{r}img/site/powered-light.png" alt="Powered by reality11" width="365" height="61">
        <div style="max-width:34ch;margin-top:1.4rem">{paras(T('footer.text'))}</div>
        <div class="footer-badges"><img src="{r}img/site/rkcr.png" alt="Realitní komora ČR — zlatý člen"></div>
      </div>
      <div><h4>Web</h4><ul>{''.join(f'<li><a class="link-u" href="{r}{h}">{t}</a></li>' for h, t in NAV)}</ul></div>
      <div><h4>Služby</h4><ul>
        <li><a class="link-u" href="{r}odhad-ceny.html">Odhad ceny zdarma</a></li>
        <li><a class="link-u" href="{esc(T('contact.najem'))}" target="_blank" rel="noopener">Pronájem s radostí</a></li>
        <li><a class="link-u" href="{esc(T('contact.vykup'))}" target="_blank" rel="noopener">Klidné řešení — výkup</a></li>
        <li><a class="link-u" href="{esc(CAL)}" target="_blank" rel="noopener">Online schůzka</a></li>
      </ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a class="link-u" href="{TEL_H}">{esc(TEL)}</a></li>
        <li><a class="link-u" href="mailto:{MAIL}">{esc(MAIL)}</a></li>
        <li>{esc(ADDR)}</li>
        <li>IČ: {esc(T('contact.ic'))}</li>
      </ul></div>
    </div>
    <div class="footer-giant" aria-hidden="true">{esc(T('footer.giant'))}</div>
    <div class="footer-bottom">
      <span>© {date.today().year} {esc(T('footer.legal'))}</span>
      <span class="row" style="gap:1.2rem">{docs}<a class="link-u footer-admin" href="{r}admin/"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="4" y="10" width="16" height="11" rx="2" stroke="currentColor" stroke-width="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3" stroke="currentColor" stroke-width="2"/></svg> Administrace</a></span>
    </div>
  </div>
</footer>'''

PAGES = []
def write(path, title, desc, body, active='', navtheme='dark', img='img/site/telefon.webp'):
    r = '../' * path.count('/')
    ld = LD if path == 'index.html' else ''
    doc = head(title, desc, r, img, '' if path == 'index.html' else path, ld) + f'\n<body data-nav="{navtheme}">\n' + header(r, active) + \
        f'\n<main id="obsah">\n{body.replace("@/", r)}\n</main>\n' + footer(r) + '\n</body>\n</html>\n'
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'w').write(doc); PAGES.append(path)

LD = '\n<script type="application/ld+json">' + json.dumps({
    "@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Mgr. Tomáš Veigl — Slyším váš domov",
    "url": BASE, "image": BASE + "img/site/telefon.webp", "logo": BASE + "img/site/logo2-dark.png",
    "telephone": re.sub(r'[^\d+]', '', TEL), "email": MAIL, "priceRange": "Kč",
    "address": {"@type": "PostalAddress", "streetAddress": ADDR.split(',')[0], "addressLocality": (ADDR.split(',')[-1]).strip(), "addressCountry": "CZ"},
    "areaServed": [it.get('title') for it in TL('home.regions')],
    "memberOf": {"@type": "Organization", "name": "Reality 11", "url": R11},
    "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING.replace(',', '.'), "reviewCount": RCOUNT, "bestRating": "5"},
    "sameAs": [T('contact.facebook'), T('contact.instagram'), T('contact.linkedin')]
}, ensure_ascii=False) + '</script>'

def cta_block(title=None, text=None):
    return f'''<section class="section dark cta">
  {ripples()}
  <div class="container cta-inner">
    <div>
      <p class="label reveal">{esc(T('cta.label'))}</p>
      <h2 class="reveal">{md(title or T('cta.title'))}</h2>
      <p class="lead reveal mt-md">{md(text or T('cta.text'))}</p>
      <div class="row mt-lg reveal">{btn('@/odhad-ceny.html', T('cta.btn'), 'btn--light', True)}{btn(esc(CAL), 'Online schůzka', 'btn--ghost', ext=True)}</div>
    </div>
    <div class="cta-contact reveal">
      <small>Zavolejte mi</small><a class="big link-u" href="{TEL_H}">{esc(TEL)}</a>
      <small>Napište mi</small><a class="big link-u" href="mailto:{MAIL}" style="font-size:clamp(1.4rem,2.2vw,2rem)">{esc(MAIL)}</a>
      <small>Kancelář</small><span>{esc(ADDR)}</span>
    </div>
  </div>
</section>'''

def partners_block(bg=''):
    cells = []
    for k, p in enumerate(TL('partners.items')):
        inner = f'<img src="@/{esc(p.get("image", ""))}" alt="{esc(p.get("title", ""))}" loading="lazy"><small>{esc(p.get("caption", ""))}</small>'
        u = p.get('url')
        cells.append(f'<a class="partner reveal" style="--i:{k % 4}" href="{esc(u)}" target="_blank" rel="noopener">{inner}</a>' if u
                     else f'<div class="partner reveal" style="--i:{k % 4}">{inner}</div>')
    return f'''<section class="section partners {bg}">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">{esc(T('partners.label'))}</p><h2 class="reveal">{md(T('partners.title'))}</h2></div>
    <p class="lead reveal" style="max-width:44ch">{md(T('partners.lead'))}</p></div>
    <div class="partner-grid">{''.join(cells)}</div>
  </div>
</section>'''

def post_card(p, r, i=0):
    return (f'<a href="{r}blog/{p["slug"]}.html" class="post reveal" style="--i:{i % 3}">'
            f'<div class="post-media"><img src="{r}{p.get("image", "")}" alt="" loading="lazy" decoding="async"></div>'
            f'<time datetime="{p["date"]}">{czdate(p["date"])}</time><h3>{esc(p["title"])}</h3><p>{esc((p.get("excerpt") or "")[:220])}</p></a>')

def rev_card(v, reply=False):
    rep = ''
    if reply and v.get('reply'):
        rep = f'<div class="reply"><img src="@/img/site/portrait.webp" alt=""><span><b style="color:var(--text)">Tomáš:</b> {esc(v["reply"])}</span></div>'
    n = int(v.get('stars') or 5)
    return (f'<article class="rev"><span class="stars" aria-label="{n} z 5">{stars(n)}</span>'
            f'<p>{esc(v["text"])}</p>{rep}<footer><b>{esc(v["name"])}</b><span>{esc(v.get("date", ""))}</span></footer></article>')

# ================================================================== HOME
def build_home():
    h1, _ = words(T('home.hero_title'))
    feat = BYSLUG.get(T('home.feature_slug'))
    offers = [x for x in LIST if x.get('home') and x is not feat]
    offer_cards = ''.join(card(x, '@/', i=k) for k, x in enumerate(offers)) + cta_card('@/')
    rev_items = ''.join(rev_card(v) for v in REVS)
    posts = ''.join(post_card(p, '@/', i) for i, p in enumerate(POSTS[:3]))
    mq = ''.join(f'<span>{esc(w.get("title", ""))} <b>✦</b></span>' for w in TL('home.marquee'))
    srows = ''.join(f'<a href="{link(s.get("link"))}" class="srow reveal" data-img="@/{esc(s.get("image", ""))}"><span class="idx">{k+1:02d}</span><h3>{esc(s.get("title", ""))}</h3><p>{esc(s.get("text", ""))}</p><span class="arr">{ARR}</span></a>'
                    for k, s in enumerate(TL('home.services')))
    intents = ''.join(f'<a href="{link(t.get("link"))}" class="intent reveal" style="--i:{k}"><span class="n">{k+1:02d}</span><b>{esc(t.get("title", ""))}</b><small>{esc(t.get("text", ""))}</small><span class="arr">{ARR}</span></a>' for k, t in enumerate(TL('home.intents')))
    sold = [x for x in LIST if x['st'][2] == 'done']
    sold_items = ''.join(f'<a href="@/nemovitosti.html?stav={x["st"][0]}" class="sold-item"><img src="@/{x["card_img"]}" alt="" loading="lazy" decoding="async"><span class="stamp">{x["st"][1]}</span><small>{esc((x.get("address") or "").split(",")[-1].strip())}</small></a>' for x in sold[:26])
    pillars = ''.join(f'<div class="pillar reveal" style="--i:{k}"><span class="n">{k+1:02d}</span><h3>{esc(p.get("title", ""))}</h3><p>{esc(p.get("text", ""))}</p></div>' for k, p in enumerate(TL('home.pillars')))
    lines = ''.join(f'<p class="hear">{md(l.get("title"))}<small>{md(l.get("text"))}</small></p>' for l in TL('home.story_lines'))
    stats = ''
    for k, s in enumerate(TL('home.stats')):
        num = str(s.get('num', '')).strip()
        cnt = num.replace(',', '.')
        numhtml = f'<span data-count="{esc(cnt)}">0</span>' if re.fullmatch(r'\d+(\.\d+)?', cnt) else esc(num)
        stats += f'<div class="stat reveal" style="--i:{k}"><div class="stat-num">{numhtml}<sup>{esc(s.get("suffix", ""))}</sup></div><p>{esc(s.get("text", ""))}</p></div>'
    regions = ''.join(f'<li class="reveal" style="--i:{k}">{esc(g.get("title", ""))} <small>{esc(g.get("text", ""))}</small></li>' for k, g in enumerate(TL('home.regions')))
    feature = ''
    if feat:
        fimg = T('home.feature_image') or feat['card_img']
        facts = ''.join(f'<div><b>{esc(f.get("v", ""))}</b><small>{esc(f.get("l", ""))}</small></div>' for f in feat.get('facts', []))
        place = (feat.get('address') or '').split(',')[0]
        feature = f'''<section class="feature">
  <div class="feature-media parallax"><img src="@/{esc(fimg)}" alt="{esc(feat['name'])}" loading="lazy"></div>
  <div class="feature-inner">
    <div>
      <p class="label reveal">{esc(T('home.feature_label'))}</p>
      <h2 class="reveal">{md(T('home.feature_title'))}</h2>
    </div>
    <div class="feature-card reveal">
      <div class="row" style="justify-content:space-between"><span class="pill pill--live">{esc(feat['name'])}</span></div>
      <div class="price">{esc(feat.get('price', ''))}</div>
      <div class="facts">{facts}</div>
      <div class="muted" style="font-size:.92rem;margin-bottom:1.2rem">{paras(T('home.feature_text'))}</div>
      {btn('@/' + feat['href'], T('home.feature_btn')) if feat.get('href') else ''}
    </div>
  </div>
</section>'''
    body = f'''
<section class="hero">
  <div class="hero-grid">
    <div class="hero-copy">
      <p class="label fade-up" style="--d:.1s">{esc(T('home.hero_label'))}</p>
      <h1 class="words">{h1}</h1>
      <p class="hero-sub fade-up" style="--d:.75s">{md(T('home.hero_sub'))}</p>
      <div class="hero-actions fade-up" style="--d:.9s">
        {btn('@/odhad-ceny.html', T('home.hero_cta'), '', True)}
        <a href="@/nemovitosti.html" class="link">{esc(T('home.hero_link'))} {ARR}</a>
      </div>
      <div class="hero-proof fade-up mt-lg" style="--d:1.05s"><b>{esc(RATING)}</b><span><span class="stars">★★★★★</span><br>{esc(RCOUNT)} hodnocení na {esc(RSRC)}</span><i class="vr"></i><img src="@/img/site/powered-dark.png" alt="Powered by reality11" width="365" height="61" class="powered"></div>
    </div>
    <div class="hero-figure">
      {ripples()}
      <div class="hero-arch"></div>
      <img class="portrait fade-up" style="--d:.35s" src="@/{esc(T('home.hero_image'))}" alt="Mgr. Tomáš Veigl, realitní makléř" width="826" height="967" fetchpriority="high">
      <div class="hero-tag fade-up" style="--d:1.2s">{wave(18, 7, True)}<span><strong>{esc(T('home.hero_tag_title'))}</strong>{esc(T('home.hero_tag_text'))}</span></div>
    </div>
  </div>
  <div class="scroll-hint" aria-hidden="true"><span class="line"></span>Scroll</div>
  <div class="hero-bottom"><div class="hero-wave">{wave(140, 11, True)}</div></div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">{mq}{mq}</div></div>

<section class="intents">
  <div class="container">
    <p class="label reveal">{esc(T('home.intents_label'))}</p>
    <div class="intent-grid">{intents}</div>
  </div>
</section>

<section class="section statement">
  <div class="container statement-grid">
    <div><p class="label reveal">{esc(T('home.statement_label'))}</p></div>
    <div>
      <p class="statement-text reveal">{md(T('home.statement'))}</p>
      <div class="pillars">{pillars}</div>
      <div class="house-rule reveal mt-lg" aria-hidden="true"><span></span></div>
      <div class="sig reveal"><img src="@/img/site/portrait.webp" alt="" style="background:var(--accent-bright)"><span><b>{esc(T('home.sig_name'))}</b><small>{esc(T('home.sig_role'))}</small></span></div>
    </div>
  </div>
</section>

{feature}

<section class="section offers">
  <div class="container sec-head">
    <div><p class="label reveal">{esc(T('home.offers_label'))}</p><h2 class="reveal">{md(T('home.offers_title'))}</h2></div>
    <div class="side reveal"><a href="@/nemovitosti.html" class="link">Všechny nemovitosti {ARR}</a>
      <div class="arrows" data-rail><button data-dir="prev" aria-label="Předchozí">{ARR_L}</button><button data-dir="next" aria-label="Další">{ARR}</button></div></div>
  </div>
  <div class="rail">{offer_cards}</div>
  <div class="container sold-head">
    <p class="reveal">{md(fill(T('home.sold_text'), n='**' + str(len(sold)) + '**')).replace('<strong>', '<b>').replace('</strong>', '</b>')}</p>
    <a href="@/nemovitosti.html?stav=prodano" class="link reveal">{esc(T('home.sold_link'))} {ARR}</a>
  </div>
  <div class="sold-marquee" aria-label="Prodané a pronajaté nemovitosti"><div class="sold-track">{sold_items}{sold_items}</div></div>
</section>

<section class="section dark story">
  <div class="deco-text drift" style="top:6%;left:-2%" aria-hidden="true">naslouchat</div>
  <div class="container">
    <div class="story-grid">
      <div class="story-aside">
        <p class="label reveal">{esc(T('home.story_label'))}</p>
        <h2 class="reveal">{md(T('home.story_title'))}</h2>
        <figure class="story-photo clip-reveal"><img src="@/{esc(T('home.story_image'))}" alt="Tomáš Veigl" loading="lazy"><figcaption>{wave(14, 5, True)}{esc(T('home.story_caption'))}</figcaption></figure>
      </div>
      <div class="hear-lines">
        {lines}
        <div class="reveal">{btn('@/pribeh.html', 'Celý příběh', 'btn--ghost')}</div>
      </div>
    </div>
    <div class="stats">{stats}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">{esc(T('home.services_label'))}</p><h2 class="reveal">{md(T('home.services_title'))}</h2></div><p class="lead reveal" style="max-width:40ch">{md(T('home.services_lead'))}</p></div>
    <div class="services-list">{srows}</div>
  </div>
  <div class="srow-preview" aria-hidden="true"></div>
</section>

{partners_block('bg-paper')}

<section class="section reviews">
  <div class="container">
    <div class="quote-big">
      <div class="quote-mark reveal" aria-hidden="true">„</div>
      <div>
        <p class="label reveal">{esc(T('home.reviews_label'))}</p>
        <blockquote class="reveal"><p>{md(T('home.quote'))}</p>
        <cite><b>{esc(T('home.quote_name'))}</b><span class="muted">· {esc(T('home.quote_meta'))}</span></cite></blockquote>
        <div class="row mt-lg reveal"><span class="rating-badge"><b>{esc(RATING)}</b><span><span class="stars">★★★★★</span><br>{esc(RCOUNT)} hodnocení · {esc(RSRC)}</span></span><a href="@/reference.html" class="link">Přečíst všechny reference {ARR}</a></div>
      </div>
    </div>
  </div>
  <div class="rev-marquee"><div class="rev-track">{rev_items}{rev_items}</div></div>
</section>

<section class="section">
  <div class="container split">
    <div>
      <p class="label reveal">{esc(T('home.regions_label'))}</p>
      <h2 class="reveal">{md(T('home.regions_title'))}</h2>
      <p class="lead reveal mt-md">{md(T('home.regions_lead'))}</p>
      <div class="reveal mt-lg">{btn('@/kontakt.html', 'Domluvit schůzku', 'btn--ghost')}</div>
    </div>
    <ul class="regions-list">{regions}</ul>
  </div>
</section>

{divider(21)}

<section class="section">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">{esc(T('home.blog_label'))}</p><h2 class="reveal">{md(T('home.blog_title'))}</h2></div><a href="@/blog.html" class="link reveal">Všechny články {ARR}</a></div>
    <div class="posts">{posts}</div>
  </div>
</section>

{cta_block()}
'''
    write('index.html', T('home.seo_title'), T('home.seo_desc'), body)

# ================================================================== PŘÍBĚH
def build_story():
    h1, _ = words(T('story.hero_title'))
    lines = ''.join(f'<p class="hear">{md(l.get("title"))}<small>{md(l.get("text"))}</small></p>' for l in TL('story.lines'))
    tl = ''.join(f'<div class="tl reveal" style="--i:{k}"><b>{esc(t.get("title", ""))}</b><p>{esc(t.get("text", ""))}</p></div>' for k, t in enumerate(TL('story.timeline')))
    badges = ''.join(f'<div class="badge-card reveal" style="--i:{k}"><b>{esc(b.get("title", ""))}</b><small>{md(b.get("text"))}</small></div>' for k, b in enumerate(TL('story.badges')))
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container phero-grid">
    <div>
      <nav class="crumbs"><a href="@/index.html">Domů</a><span>Můj příběh</span></nav>
      <p class="label fade-up" style="--d:.1s">Můj příběh</p>
      <h1 class="words" style="max-width:13ch">{h1}</h1>
      <p class="lead fade-up" style="--d:.8s">{md(T('story.hero_lead'))}</p>
    </div>
    <figure class="portrait-hero clip-reveal"><div class="img"><img src="@/{esc(T('story.hero_image'))}" alt="Tomáš Veigl" loading="eager"></div></figure>
  </div>
</section>

<section class="section dark story">
  <div class="deco-text drift" style="bottom:4%;left:-4%" aria-hidden="true">ticho</div>
  <div class="container">
    <div class="story-grid">
      <div class="story-aside">
        <p class="label reveal">{esc(T('story.dark_label'))}</p>
        <h2 class="reveal">{md(T('story.dark_title'))}</h2>
        <p class="lead reveal">{md(T('story.dark_lead'))}</p>
      </div>
      <div class="hear-lines">{lines}</div>
    </div>
    <div class="timeline">{tl}</div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <figure class="frame clip-reveal" style="aspect-ratio:5/4"><img src="@/{esc(T('story.family_image'))}" alt="Tomáš s rodinou" loading="lazy"></figure>
    <div>
      <p class="label reveal">{esc(T('story.family_label'))}</p>
      <h2 class="reveal">{md(T('story.family_title'))}</h2>
      <div class="prose mt-md reveal">
        {paras(T('story.family_text'), 'dropcap')}
        <p class="serif" style="font-family:var(--font-display);font-size:1.9rem;line-height:1.2">{md(T('story.family_quote'))}</p>
      </div>
    </div>
  </div>
</section>

<section class="section bg-alt">
  <div class="container split flip">
    <figure class="frame clip-reveal" style="background:var(--paper);padding:1rem"><img src="@/{esc(T('story.awards_image'))}" alt="Certifikáty a ocenění" loading="lazy" style="object-fit:contain"></figure>
    <div>
      <p class="label reveal">{esc(T('story.awards_label'))}</p>
      <h2 class="reveal">{md(T('story.awards_title'))}</h2>
      <div class="prose mt-md reveal">{paras(T('story.awards_text'))}</div>
      <div class="badges mt-lg">{badges}</div>
    </div>
  </div>
</section>

{cta_block(T('story.cta_title'), T('story.cta_text'))}
'''
    write('pribeh.html', T('story.seo_title'), T('story.seo_desc'), body, 'pribeh.html')

# ================================================================== JAK PRACUJI
def build_process():
    steps = TL('process.steps')
    h1, _ = words(fill(T('process.hero_title'), n=len(steps)))
    items = ''; last = None
    soc = f'<div class="row" style="gap:1.4rem"><a class="link" href="{esc(T("contact.facebook"))}" target="_blank" rel="noopener">Facebook</a><a class="link" href="{esc(T("contact.instagram"))}" target="_blank" rel="noopener">Instagram</a><a class="link" href="{esc(T("contact.linkedin"))}" target="_blank" rel="noopener">LinkedIn</a></div>'
    for k, s in enumerate(steps):
        ph = s.get('phase', '')
        if ph != last:
            items += f'<div class="phase-title">{esc(ph)}</div>'; last = ph
        img = s.get('image')
        im = f'<div class="step-img clip-reveal {"contain" if s.get("contain") else ""}"><img src="@/{esc(img)}" alt="{esc(s.get("title", ""))}" loading="lazy"></div>' if img else ''
        extra = soc if 'sociální sít' in (s.get('title') or '').lower() else ''
        items += f'<article class="step" data-phase="{esc(ph)}"><span class="k">Krok {k+1:02d}</span><h3>{esc(s.get("title", ""))}</h3>{paras(s.get("text"))}{extra}{im}</article>'
    dots = '<i></i>' * len(steps)
    first_phase = steps[0].get('phase', '') if steps else ''
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Jak pracuji</span></nav>
    <p class="label fade-up" style="--d:.1s">Jak pracuji</p>
    <h1 class="words" style="max-width:12ch">{h1}</h1>
    <p class="lead fade-up" style="--d:.8s">{md(T('process.hero_lead'))}</p>
  </div>
</section>
{divider(8)}
<section class="section" style="padding-top:var(--gap-lg)">
  <div class="container steps-wrap">
    <aside class="steps-aside">
      <div class="step-counter" data-step-counter>01<small>/ {len(steps)}</small></div>
      <div class="step-phase" data-step-phase>{esc(first_phase)}</div>
      <div class="phase-dots" aria-hidden="true">{dots}</div>
      <div class="extra mt-lg">{btn('@/kontakt.html', T('process.aside_btn'), '', True)}</div>
    </aside>
    <div class="steps">{items}</div>
  </div>
</section>
{cta_block(T('process.cta_title'), T('process.cta_text'))}
'''
    write('jak-pracuji.html', fill(T('process.seo_title'), n=len(steps)), T('process.seo_desc'), body, 'jak-pracuji.html')

# ================================================================== NEMOVITOSTI
ORDER = {'nabidka': 0, 'pripravujeme': 1, 'rezervace': 2, 'prodano': 3, 'pronajato': 3}
def build_listing():
    feat = BYSLUG.get(T('home.feature_slug'))
    items = sorted(LIST, key=lambda x: (0 if x is feat else 1, ORDER.get(x.get('status'), 4), 0 if x['has_detail'] else 1))
    cards = []; inserted = False
    for k, x in enumerate(items):
        if not inserted and x['st'][2] == 'done':
            cards.append(cta_card('@/', 'reveal card" data-status="nabidka" data-type="all')); inserted = True
        cards.append(card(x, '@/', feat=(k == 0 and x is feat), i=k))
    if not inserted: cards.append(cta_card('@/', 'reveal card" data-status="nabidka" data-type="all'))
    from collections import Counter
    c = Counter(x['st'][0] for x in LIST)
    chips = [('all', 'Vše', len(LIST)), ('nabidka', 'V nabídce', c['nabidka']), ('rezervace', 'Rezervace', c['rezervace']),
             ('prodano', 'Prodáno', c['prodano']), ('pronajato', 'Pronajato', c['pronajato'])]
    chip_html = ''.join(f'<button class="chip{" on" if k == "all" else ""}" data-status-filter="{k}">{t}<sup>{n}</sup></button>' for k, t, n in chips)
    h1, _ = words(T('listing.hero_title'))
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container phero-grid">
    <div>
      <nav class="crumbs"><a href="@/index.html">Domů</a><span>Nemovitosti</span></nav>
      <p class="label fade-up" style="--d:.1s">Nemovitosti</p>
      <h1 class="words" style="max-width:15ch;font-size:clamp(3rem,7vw,7rem)">{h1}</h1>
    </div>
    <div class="fade-up" style="--d:.8s">
      <p class="lead">{md(T('listing.hero_lead'))}</p>
      <div class="row mt-md" style="gap:2rem"><div><b style="font-family:var(--font-display);font-size:3rem;font-weight:400;line-height:1">{c['prodano']}</b><br><small class="muted">prodaných na webu</small></div><div><b style="font-family:var(--font-display);font-size:3rem;font-weight:400;line-height:1">{c['pronajato']}</b><br><small class="muted">pronajatých</small></div></div>
    </div>
  </div>
</section>
<section class="section" style="padding-top:var(--gap-md)">
  <div class="container">
    <div class="filter-bar">
      <div class="filters" role="group" aria-label="Stav">{chip_html}</div>
      <label><span class="sr-only">Typ nemovitosti</span><select data-type-filter>
        <option value="all">Všechny typy</option><option value="dum">Rodinné domy</option><option value="byt">Byty</option>
        <option value="novostavba">Novostavby</option><option value="chata">Chaty a chalupy</option><option value="pozemek">Pozemky</option><option value="komercni">Komerční</option>
      </select></label>
    </div>
    <div class="grid-list" data-grid>{''.join(cards)}</div>
    <p class="empty-note">{md(T('listing.empty'))}</p>
  </div>
</section>
{cta_block(T('listing.cta_title'), T('listing.cta_text'))}
'''
    write('nemovitosti.html', T('listing.seo_title'), T('listing.seo_desc'), body, 'nemovitosti.html')

def gallery(imgs, cls='', limit=8):
    if not imgs: return ''
    links = []
    for k, p in enumerate(imgs):
        hidden = k >= limit
        more = f' class="more" data-more="+{len(imgs) - limit}"' if (k == limit - 1 and len(imgs) > limit) else ''
        links.append(f'<a href="@/{esc(p)}"{more}{" hidden" if hidden else ""}><img src="@/{esc(p)}" alt="" loading="lazy" decoding="async"></a>')
    return f'<div class="gal {cls}" data-lb>{"".join(links)}</div>'

def build_details():
    for x in LIST:
        if not x['has_detail']: continue
        key, lab, kind = x['st']
        lead = x.get('lead') or ''
        lead_html = f'<p class="lead-quote reveal">{esc(lead)}</p>' if lead else ''
        hero = x['card_img']
        bar = (f'<div><small>{esc(x.get("price_label") or "Cena")}</small><b class="price">{esc(x.get("price") or "Na dotaz")}</b></div>'
               + ''.join(f'<div><small>{esc(f.get("l", ""))}</small><b>{esc(f.get("v", ""))}</b></div>' for f in x.get('facts', [])))
        pool = [o for o in LIST if o['has_detail'] and o is not x]
        others = [o for o in pool if o['st'][0] == 'nabidka' and o.get('type') != 'Novostavba'][:3]
        if len(others) < 3: others += [o for o in pool if o not in others][:3 - len(others)]
        h2 = 'class="reveal mt-xl" style="font-size:clamp(2rem,3.4vw,3rem);margin-bottom:var(--gap-md)"'
        sec_ph = f'<h2 {h2}>Fotografie</h2>{gallery(x["photos"])}' if x.get('photos') else ''
        sec_pl = f'<h2 {h2}>Půdorysy</h2>{gallery(x["plans"], "plans", 6)}' if x.get('plans') else ''
        sec_vz = f'<h2 {h2}>Jak to <em>může</em> vypadat</h2><p class="muted" style="margin-bottom:var(--gap-md)">{esc(T("detail.viz_note"))}</p>{gallery(x["viz"], "", 6)}' if x.get('viz') else ''
        body = f'''
<section class="dhero">
  <div class="feature-media parallax"><img src="@/{esc(hero)}" alt="{esc(x['name'])}" fetchpriority="high"></div>
  <div class="dhero-inner">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span><a href="@/nemovitosti.html">Nemovitosti</a></span><span>{esc(x['name'])}</span></nav>
    <span class="pill pill--{kind} fade-up" style="--d:.1s">{lab}</span>
    <h1 class="fade-up" style="--d:.2s">{esc(x['title'])}</h1>
    <p class="addr fade-up" style="--d:.35s">{PIN} {esc(x.get('address') or '')}</p>
  </div>
</section>
<div class="dbar"><div class="dbar-inner">{bar}</div></div>
<section class="section">
  <div class="container dgrid">
    <article>
      {lead_html}
      <div class="prose reveal">{clean_html(x.get('body'))}</div>
      {sec_ph}{sec_pl}{sec_vz}
    </article>
    <aside class="dside">
      <div class="agent-card">
        {ripples()}
        <div class="who"><img src="@/img/site/portrait.webp" alt=""><span><b>Tomáš Veigl</b><small>{esc(T('detail.agent_sub'))}</small></span></div>
        <a class="tel link-u" href="{TEL_H}">{esc(TEL)}</a>
        <a class="mail link-u" href="mailto:{MAIL}?subject={urllib.parse.quote(x['name'])}">{esc(MAIL)}</a>
        {btn('@/kontakt.html?nemovitost=' + urllib.parse.quote(x['name']), T('detail.btn'), 'btn--light')}
      </div>
      <div class="badge-card" style="flex-direction:row;align-items:center;gap:1rem"><b style="font-size:2.2rem">{esc(RATING)}</b><small><span class="stars">★★★★★</span><br>{esc(RCOUNT)} hodnocení klientů na {esc(RSRC)}</small></div>
    </aside>
  </div>
</section>
<section class="section bg-alt">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">Mohlo by vás zajímat</p><h2 class="reveal">Další <em>nemovitosti</em></h2></div><a href="@/nemovitosti.html" class="link reveal">Všechny nemovitosti {ARR}</a></div>
    <div class="grid-list">{''.join(card(o, '@/', i=k) for k, o in enumerate(others))}</div>
  </div>
</section>
<div class="lb" role="dialog" aria-label="Galerie"><img alt=""><button class="x" aria-label="Zavřít">✕</button><button class="p" aria-label="Předchozí">{ARR_L}</button><button class="n" aria-label="Další">{ARR}</button><span class="c"></span></div>
'''
        desc = x.get('seo_desc') or lead[:155] or x['title']
        write(x['href'], f"{x['name']} — {x.get('price') or 'na dotaz'} | Tomáš Veigl", desc, body, 'nemovitosti.html', 'light', hero)

# ================================================================== SLUŽBY
def build_services():
    nb = [x for x in LIST if x.get('type') == 'Novostavba' and x['st'][0] != 'prodano' and x['has_detail']]
    h1, _ = words(T('services.hero_title'))
    points = ''.join(f'<li class="reveal" style="font-size:clamp(1.5rem,2.6vw,2.2rem)">{esc(p.get("title", ""))} <small>{esc(p.get("text", ""))}</small></li>' for p in TL('services.sale_points'))
    guar = ''.join(f'<div class="reveal" style="--i:{k}"><b>{esc(g.get("title", ""))}</b><p>{esc(g.get("text", ""))}</p></div>' for k, g in enumerate(TL('services.guarantees')))
    newbuild = f'''<section class="section bg-alt" id="novostavby">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">04 — Novostavby</p><h2 class="reveal">{md(T('services.new_title'))}</h2></div><p class="lead reveal" style="max-width:42ch">{md(T('services.new_text'))}</p></div>
    <div class="grid-list">{''.join(card(x, '@/', i=k) for k, x in enumerate(nb))}</div>
  </div>
</section>''' if nb else ''
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Služby</span></nav>
    <p class="label fade-up" style="--d:.1s">Služby</p>
    <h1 class="words" style="max-width:14ch">{h1}</h1>
    <div class="row mt-md fade-up" style="--d:.8s;gap:.5rem">
      <a class="chip" href="#prodej">Prodej</a><a class="chip" href="#pronajem">Pronájem a správa</a><a class="chip" href="#vykup">Výkup</a>{'<a class="chip" href="#novostavby">Novostavby</a>' if nb else ''}<a class="chip" href="@/odhad-ceny.html">Odhad ceny</a>
    </div>
  </div>
</section>

<section class="section" id="prodej" style="padding-top:var(--gap-lg)">
  <div class="container svc">
    <figure class="svc-media clip-reveal"><img src="@/{esc(T('services.sale_image'))}" alt="" loading="lazy"></figure>
    <div>
      <p class="label reveal">01 — Prodej</p>
      <h2 class="reveal">{md(T('services.sale_title'))}</h2>
      <div class="prose mt-md reveal">{paras(T('services.sale_text'))}</div>
      <ul class="regions-list mt-lg">{points}</ul>
      <div class="mt-lg reveal">{btn('@/jak-pracuji.html', f'Všech {len(TL("process.steps"))} kroků')}</div>
    </div>
  </div>
</section>

<section class="section dark" id="pronajem">
  <div class="container">
    <div class="split">
      <div>
        <p class="label reveal">02 — Pronájem s radostí</p>
        <h2 class="reveal">{md(T('services.rent_title'))}</h2>
        <p class="lead reveal mt-md">{md(T('services.rent_text'))}</p>
        <div class="row mt-lg reveal">{btn(esc(T('contact.najem')), 'Pronájem s radostí', 'btn--light', ext=True)}</div>
      </div>
      <figure class="frame clip-reveal" style="aspect-ratio:4/3.4"><img src="@/{esc(T('services.rent_image'))}" alt="" loading="lazy"></figure>
    </div>
    <div class="guarantees">{guar}</div>
  </div>
</section>

<section class="section" id="vykup">
  <div class="container split flip">
    <figure class="frame clip-reveal" style="aspect-ratio:1"><img src="@/{esc(T('services.buy_image'))}" alt="" loading="lazy"></figure>
    <div>
      <p class="label reveal">03 — Klidné řešení</p>
      <h2 class="reveal">{md(T('services.buy_title'))}</h2>
      <div class="prose mt-md reveal">{paras(T('services.buy_text'))}</div>
      <div class="row mt-lg reveal">{btn(esc(T('contact.vykup')), 'Klidné řešení', '', ext=True)}<a href="{TEL_H}" class="link">Raději zavolám {ARR}</a></div>
    </div>
  </div>
</section>

{partners_block('bg-paper')}

{newbuild}

{cta_block()}
'''
    write('sluzby.html', T('services.seo_title'), T('services.seo_desc'), body, 'sluzby.html')

# ================================================================== REFERENCE
def build_reference():
    kw = dict(rating=RATING, count=RCOUNT)
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container phero-grid">
    <div>
      <nav class="crumbs"><a href="@/index.html">Domů</a><span>Reference</span></nav>
      <p class="label fade-up" style="--d:.1s">Reference</p>
      <h1 class="words">{words(T('reference.hero_title'))[0]}</h1>
      <p class="lead fade-up" style="--d:.8s">{md(T('reference.hero_lead'))}</p>
    </div>
    <div class="fade-up" style="--d:.5s">
      <div class="big-rating">{esc(RATING)}</div>
      <p class="row mt-sm" style="gap:.8rem"><span class="stars" style="font-size:1.2rem">★★★★★</span><span class="muted">{esc(RCOUNT)} hodnocení · {esc(RSRC)}</span></p>
    </div>
  </div>
</section>
{divider(13)}
<section class="section" style="padding-top:var(--gap-lg)">
  <div class="container">
    <div class="masonry">{''.join(f'<div class="reveal" style="--i:{k % 3};break-inside:avoid">{rev_card(v, True)}</div>' for k, v in enumerate(REVS))}</div>
    <div class="center mt-lg reveal">{btn(esc(T('rating.url')), f'Všech {RCOUNT} hodnocení na {RSRC}', 'btn--ghost', ext=True)}</div>
  </div>
</section>
{cta_block(T('reference.cta_title'), T('reference.cta_text'))}
'''
    write('reference.html', fill(T('reference.seo_title'), **kw), fill(T('reference.seo_desc'), **kw), body, 'reference.html')

# ================================================================== BLOG
def build_blog():
    if POSTS:
        first, rest = POSTS[0], POSTS[1:]
        feat = f'''<a href="@/blog/{first['slug']}.html" class="split post reveal" style="gap:var(--gap-lg)">
      <div class="post-media" style="aspect-ratio:4/3"><img src="@/{first.get('image', '')}" alt="" loading="eager"></div>
      <div><time datetime="{first['date']}">{czdate(first['date'])} · Nejnovější</time><h3 style="font-size:clamp(2rem,3.6vw,3.4rem);margin:.6rem 0 1rem">{esc(first['title'])}</h3><p style="-webkit-line-clamp:5">{esc(first.get('excerpt', ''))}</p><span class="link mt-md" style="display:inline-flex">Číst článek {ARR}</span></div></a>'''
    else: feat, rest = '', []
    grid = ''.join(post_card(p, '@/', k) for k, p in enumerate(rest))
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Blog</span></nav>
    <p class="label fade-up" style="--d:.1s">Blog</p>
    <h1 class="words" style="max-width:12ch">{words(T('blog.hero_title'))[0]}</h1>
    <p class="lead fade-up" style="--d:.8s">{md(T('blog.hero_lead'))}</p>
  </div>
</section>
<section class="section" style="padding-top:var(--gap-md)">
  <div class="container">
    {feat}
    <div class="grid-list mt-xl" style="grid-template-columns:repeat(auto-fill,minmax(300px,1fr))">{grid}</div>
  </div>
</section>
{cta_block()}
'''
    write('blog.html', T('blog.seo_title'), T('blog.seo_desc'), body, 'blog.html')
    for p in POSTS:
        rel = [q for q in POSTS if q is not p][:3]
        body = f'''
<section class="article-hero">
  <div class="narrow">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span><a href="@/blog.html">Blog</a></span></nav>
    <p class="label fade-up" style="--d:.05s">{czdate(p['date'])}</p>
    <h1 class="fade-up" style="--d:.15s">{esc(p['title'])}</h1>
    <div class="byline fade-up" style="--d:.3s"><img src="@/img/site/portrait.webp" alt=""><span><b>Mgr. Tomáš Veigl</b>Realitní makléř · Hradec Králové</span></div>
  </div>
</section>
{f'<figure class="article-cover clip-reveal"><img src="@/{esc(p["image"])}" alt="" fetchpriority="high"></figure>' if p.get('image') else ''}
<section class="section" style="padding-top:var(--gap-lg)">
  <div class="narrow prose">{clean_html(p.get('body'))}</div>
  <div class="narrow mt-xl" style="border-top:1px solid var(--line);padding-top:var(--gap-md)">
    <div class="sig"><img src="@/img/site/portrait.webp" alt="" style="background:var(--accent)"><span><b>{esc(T('blog.question'))}</b><small>Zavolejte mi na <a class="link-u" href="{TEL_H}">{esc(TEL)}</a> — rád poradím.</small></span></div>
  </div>
</section>
<section class="section bg-alt">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">Blog</p><h2 class="reveal">Další <em>články</em></h2></div><a href="@/blog.html" class="link reveal">Všechny články {ARR}</a></div>
    <div class="grid-list">{''.join(post_card(q, '@/', i) for i, q in enumerate(rel))}</div>
  </div>
</section>
'''
        write(f'blog/{p["slug"]}.html', f'{p["title"]} | Tomáš Veigl', (p.get('excerpt') or p['title'])[:155], body, 'blog.html', 'dark', p.get('image') or 'img/site/telefon.webp')

# ================================================================== ODHAD
def build_estimate():
    h1, _ = words(T('estimate.hero_title'))
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Odhad ceny zdarma</span></nav>
    <p class="label fade-up" style="--d:.1s">Odhad ceny zdarma</p>
    <h1 class="words" style="max-width:13ch">{h1}</h1>
  </div>
</section>
<section class="section" style="padding-top:var(--gap-md)">
  <div class="container dgrid side-wide">
    <div>
      <p class="lead-quote reveal">{md(T('estimate.quote'))}</p>
      <form class="form reveal" data-demo>
        <fieldset class="field full"><legend>Typ nemovitosti</legend><div class="opts">
          {''.join(f'<input type="radio" name="typ" id="t{k}" {"checked" if k == 0 else ""}><label for="t{k}">{t}</label>' for k, t in enumerate(['Rodinný dům', 'Byt', 'Chata / chalupa', 'Pozemek', 'Komerční']))}
        </div></fieldset>
        <div class="field full"><label for="adr">Adresa nemovitosti</label><input id="adr" placeholder="Např. Gočárova 12, Hradec Králové" required></div>
        <div class="field"><label for="plo">Plocha (m²)</label><input id="plo" inputmode="numeric" placeholder="např. 85"></div>
        <div class="field"><label for="disp">Dispozice</label><select id="disp"><option>1+kk / 1+1</option><option>2+kk / 2+1</option><option selected>3+kk / 3+1</option><option>4+kk / 4+1</option><option>5 a více pokojů</option><option>Nevím / netýká se</option></select></div>
        <fieldset class="field full"><legend>Stav</legend><div class="opts">
          {''.join(f'<input type="radio" name="stav" id="s{k}" {"checked" if k == 1 else ""}><label for="s{k}">{t}</label>' for k, t in enumerate(['Novostavba', 'Dobrý', 'Po rekonstrukci', 'Před rekonstrukcí']))}
        </div></fieldset>
        <div class="field"><label for="jm">Jméno</label><input id="jm" autocomplete="name" required></div>
        <div class="field"><label for="tel">Telefon</label><input id="tel" type="tel" autocomplete="tel" required></div>
        <div class="field full"><label for="em">E-mail</label><input id="em" type="email" autocomplete="email"></div>
        <div class="field full"><label for="pozn">Cokoli dalšího, co bych měl slyšet</label><textarea id="pozn" placeholder="Proč prodáváte, kdy byste se chtěli stěhovat…"></textarea></div>
        <div class="full row" style="justify-content:space-between"><p class="form-note">Odesláním souhlasíte se zpracováním osobních údajů za účelem odhadu.</p><button type="submit" class="btn btn-magnetic">Poslat žádost <span class="arr">{ARR}</span></button></div>
      </form>
      <p class="form-ok">{esc(T('estimate.thanks'))}</p>
    </div>
    <aside class="dside">
      <div class="agent-card">
        {ripples()}
        <div class="who"><img src="@/img/site/portrait.webp" alt=""><span><b>Raději osobně?</b><small>Zavolejte, nebo si vyberte termín</small></span></div>
        <a class="tel link-u" href="{TEL_H}">{esc(TEL)}</a>
        <a class="mail link-u" href="mailto:{MAIL}">{esc(MAIL)}</a>
        {btn(esc(CAL), 'Online schůzka', 'btn--light', ext=True)}
      </div>
      <div class="prose" style="font-size:.95rem;color:var(--muted)">{paras(T('estimate.aside'))}</div>
    </aside>
  </div>
</section>
'''
    write('odhad-ceny.html', T('estimate.seo_title'), T('estimate.seo_desc'), body, 'odhad-ceny.html')

# ================================================================== KONTAKT
def build_contact():
    h1, _ = words(T('contactpage.hero_title'))
    q = 'https://www.google.com/maps?q=' + urllib.parse.quote_plus(ADDR) + '&output=embed'
    a_tel = T('contact.assistant_phone'); a_tel_h = 'tel:' + re.sub(r'[^\d+]', '', a_tel)
    initials = ''.join(w[0] for w in T('contact.assistant_name').split()[:2]).upper()
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Kontakt</span></nav>
    <p class="label fade-up" style="--d:.1s">Kontakt</p>
    <h1 class="words">{h1}</h1>
  </div>
</section>
<section class="section" style="padding-top:var(--gap-md)">
  <div class="container split" style="align-items:start">
    <div class="contact-big">
      <small class="reveal" style="margin-top:0">Telefon</small><a class="cb reveal" href="{TEL_H}">{esc(TEL)}</a>
      <small class="reveal">E-mail</small><a class="cb reveal" href="mailto:{MAIL}" style="font-size:clamp(1.8rem,4vw,3.6rem)">{esc(MAIL)}</a>
      <small class="reveal">Kancelář</small><p class="reveal" style="font-size:1.15rem">{esc(ADDR)}</p>
      <div class="row mt-lg reveal">{btn(esc(CAL), 'Online schůzka', '', True, ext=True)}{btn('@/odhad-ceny.html', 'Odhad ceny', 'btn--ghost')}</div>
      <div class="mt-xl">
        <div class="person reveal"><img src="@/img/site/portrait.webp" alt=""><span><b>Mgr. Tomáš Veigl</b><br><small class="muted">Realitní makléř · {esc(TEL)} · {esc(MAIL)}</small></span></div>
        <div class="person reveal"><span style="width:58px;height:58px;border-radius:50%;background:var(--bg-alt);display:grid;place-items:center;font-family:var(--font-display);font-size:1.5rem;flex:none">{esc(initials)}</span><span><b>{esc(T('contact.assistant_name'))}</b><br><small class="muted">{esc(T('contact.assistant_role'))} · <a class="link-u" href="{a_tel_h}">{esc(a_tel)}</a> · <a class="link-u" href="mailto:{esc(T('contact.assistant_email'))}">{esc(T('contact.assistant_email'))}</a></small></span></div>
        <div class="row reveal mt-md" style="gap:1.4rem"><a class="link" href="{esc(T('contact.facebook'))}" target="_blank" rel="noopener">Facebook</a><a class="link" href="{esc(T('contact.instagram'))}" target="_blank" rel="noopener">Instagram</a><a class="link" href="{esc(T('contact.linkedin'))}" target="_blank" rel="noopener">LinkedIn</a></div>
      </div>
    </div>
    <div>
      <div class="map clip-reveal"><iframe src="{q}" loading="lazy" title="Mapa — kancelář" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <form class="form mt-lg reveal" data-demo>
        <div class="field"><label for="cj">Jméno</label><input id="cj" autocomplete="name" required></div>
        <div class="field"><label for="ct">Telefon</label><input id="ct" type="tel" autocomplete="tel" required></div>
        <div class="field full"><label for="cz">Zpráva</label><textarea id="cz" placeholder="Co plánujete? Prodej, pronájem, koupě…"></textarea></div>
        <div class="full row" style="justify-content:space-between"><p class="form-note">Ozvu se obvykle do několika hodin.</p><button type="submit" class="btn">Odeslat <span class="arr">{ARR}</span></button></div>
      </form>
      <p class="form-ok">{esc(T('contactpage.thanks'))}</p>
    </div>
  </div>
</section>
<section class="section dark" style="padding-block:var(--gap-xl)">
  <div class="container row" style="justify-content:space-between;gap:2rem">
    <p class="reveal" style="font-family:var(--font-display);font-size:clamp(1.8rem,3.4vw,3rem);line-height:1.15;max-width:24ch">{md(T('contactpage.band')).replace('<em>', '<em style="color:#73C7D2">')}</p>
    <div class="reveal" style="color:#73C7D2;width:min(420px,100%)">{wave(60, 17, True)}</div>
  </div>
</section>
'''
    write('kontakt.html', T('contactpage.seo_title'), f'Zavolejte {TEL}, napište na {MAIL} nebo si domluvte online schůzku. Kancelář: {ADDR}.', body, 'kontakt.html')

def build_404():
    body = f'''<section class="phero" style="min-height:80svh">{ripples()}<div class="container"><p class="label">404</p><h1>Tady je <em>ticho</em>.</h1><p class="lead mt-md">Tahle stránka neexistuje. Ale já vás slyším — zkuste to přes úvodní stránku.</p><div class="mt-lg">{btn(BASE + 'index.html', 'Zpět domů')}</div></div></section>'''
    write('404.html', 'Stránka nenalezena | Tomáš Veigl', 'Stránka nenalezena.', body)

def build_admin_assets():
    os.makedirs('admin', exist_ok=True)
    json.dump({'schema': SCHEMA}, open('admin/schema.json', 'w'), ensure_ascii=False)
    json.dump({'sha': os.environ.get('GITHUB_SHA', 'local'), 'built': date.today().isoformat()}, open('version.json', 'w'))

if __name__ == '__main__':
    for d in ('nemovitosti', 'blog'):   # remove pages of deleted items
        shutil.rmtree(d, ignore_errors=True)
    build_home(); build_story(); build_process(); build_listing(); build_details()
    build_services(); build_reference(); build_blog(); build_estimate(); build_contact(); build_404()
    build_admin_assets()
    print(f'{len(PAGES)} pages built')
