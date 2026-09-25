#!/usr/bin/env python3
"""Static site generator for tomasveigl — run: python3 _build/build.py"""
import json, os, re, random, html as H
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
LIST = json.load(open('_data/listings.json'))
POSTS = json.load(open('_data/posts.json'))
REV = json.load(open('_data/reviews.json'))
POSTS.sort(key=lambda p: p['date'], reverse=True)

TEL = '+420 737 132 041'; TEL_H = 'tel:+420737132041'
MAIL = 'reality@tomasveigl.cz'
ADDR = 'Třída Edvarda Beneše 1526/78, Hradec Králové'
CAL = 'https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2FVFpnfyA8WAejvXm4w3nQwt5CBjg56ZaEEC5JL69R0093WGU7qkEl2kyTliHDKM-0qVM6m2pB'
FIRMY = REV['url']
OLD = 'https://www.tomasveigl.cz/wp-content/uploads/2025/05/'
ARR = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M1 7h12M8 2l5 5-5 5" stroke="currentColor" stroke-width="1.4"/></svg>'
ARR_L = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M13 7H1M6 2L1 7l5 5" stroke="currentColor" stroke-width="1.4"/></svg>'
PIN = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="10" r="2.5" stroke="currentColor" stroke-width="1.5"/></svg>'

esc = H.escape
BASE = 'https://webhunter-navrhy.github.io/tomasveigl/'
R11 = 'https://www.reality11.cz/'
PHONE_I = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z" stroke="currentColor" stroke-width="1.6"/></svg>'

# ------------------------------------------------------------------ helpers
def wave(n=64, seed=1, live=False, cls='', lo=0.18, hi=1.0):
    rnd = random.Random(seed)
    bars = []
    for k in range(n):
        env = 0.35 + 0.65 * abs(__import__('math').sin((k / n) * 3.14159 * 2.2 + seed))
        s = max(lo, min(hi, env * rnd.uniform(0.35, 1.0)))
        d = rnd.uniform(0.7, 1.8); dl = -rnd.uniform(0, 2)
        bars.append(f'<i style="--s:{s:.2f};--d:{d:.2f}s;--dl:{dl:.2f}s;--k:{k}"></i>')
    return f'<div class="wave{" live" if live else ""} {cls}" aria-hidden="true">{"".join(bars)}</div>'

def divider(seed=3, n=110):
    return f'<div class="wave-divider" aria-hidden="true">{wave(n, seed)}</div>'

def ripples(cls=''):
    return f'<div class="ripples {cls}" aria-hidden="true"><span></span><span></span><span></span><span></span></div>'

def words(text, start=0):
    """'Slyším\\n_váš_ domov.' -> split word spans; _x_ = <em>, \\n = new line span"""
    i = start; lines = []
    for li, line in enumerate(text.split('\n')):
        out = []
        em = False
        for w in line.split(' '):
            core = w.rstrip('.,!?'); tail = w[len(core):]
            start = core.startswith('_'); end = core.endswith('_') and len(core) > 1
            if start: em = True
            word = core.strip('_')
            inner = f'<em>{word}</em>{tail}' if em else w
            if end: em = False
            out.append(f'<span class="w"><span style="--i:{i}">{inner}</span></span>')
            i += 1
        lines.append(f'<span class="l{li+1}">{" ".join(out)}</span>')
    return ' '.join(lines), i

def btn(href, text, cls='', magnetic=False, ext=False):
    t = ' target="_blank" rel="noopener"' if ext else ''
    return f'<a href="{href}" class="btn {cls}{" btn-magnetic" if magnetic else ""}"{t}>{text} <span class="arr">{ARR}</span></a>'

def czdate(d):
    y, m, dd = d.split('-'); return f'{int(dd)}. {int(m)}. {y}'

def strip_tags(s): return re.sub(r'<[^>]+>', '', s)

# ------------------------------------------------------------------ listings
STATUS = {'Aktuálně': ('nabidka', 'V nabídce', 'live'), 'Připravujeme': ('nabidka', 'Připravujeme', 'live'),
          'V rezervaci': ('rezervace', 'Rezervace', 'res'), 'Prodáno': ('prodano', 'Prodáno', 'done'),
          'Pronajato': ('pronajato', 'Pronajato', 'done')}
SHORT = {  # slug -> (short title, type, facts[(value,label)])
 'rodinny-dum-4kk-vinary-u-noveho-bydzova': ('Rodinný dům 4+kk, Vinary', 'Rodinný dům', [('4+kk','Dispozice'),('114 m²','Užitná plocha'),('1 800 m²','Pozemek')]),
 'bytrychnov': ('Byt 3+1 s balkonem, Rychnov nad Kněžnou', 'Byt', [('3+1','Dispozice'),('72 m²','Plocha dle LV'),('Balkon','+ sklep, komora')]),
 'garsonkahradec': ('Byt 1+kk s lodžií, Hradec Králové', 'Byt', [('1+kk','Dispozice'),('31 m²','Celková plocha'),('6,4 m²','Zasklená lodžie')]),
 'prodej-bytu-3-1-pilnikov-101-m2': ('Velký byt 3+1, Pilníkov', 'Byt', [('3+1','Dispozice'),('101 m²','Podlahová plocha'),('Krb','Krbová kamna')]),
 'dum_s_garazi_kricen': ('Rodinný dům s garáží, Křičeň', 'Rodinný dům', [('2+1 + 2. NP','Dispozice'),('750 m²','Pozemek'),('Garáž','+ krbová kamna')]),
 'sklada': ('Sklad 410 m², Červeněves', 'Komerční', [('410 m²','Užitná plocha'),('230/400 V','Elektřina'),('Ihned','K užívání')]),
 'sklade': ('Sklad 710 m², Červeněves', 'Komerční', [('710 m²','Užitná plocha'),('8 m','Výška skladu'),('Rampa','Nájezdová')]),
 'prodej-rodinneho-domu-s-garazi-a-velkym-pozemkem-pred-rekonstrukci': ('Rodinný dům s velkým pozemkem, Sendražice', 'Rodinný dům', [('3+1','Dispozice'),('87 m²','Podlahová plocha'),('1 455 m²','Pozemek')]),
 'dum-dobrichov': ('Rodinný dům 2+1, Dobřichov', 'Rodinný dům', [('2+1','Dispozice'),('59 m²','Plocha'),('237 m²','Pozemek')]),
 'dumvysocina': ('Rodinný dům s garáží, Příštpo', 'Rodinný dům', [('3+1','Dispozice'),('82 m²','Užitná plocha'),('360 m²','Pozemek')]),
 'novostavbachlumec': ('Novostavba CLASSIC 63, Chlumec n. C.', 'Novostavba', [('3+kk','Dispozice'),('62,7 m²','Užitná plocha'),('PURLIVE','Nízkoenergetický')]),
 'novostavbahradeckralove': ('Novostavba AMBIENT 94, Hradec Králové', 'Novostavba', [('4+1','Dispozice'),('94 m²','Užitná plocha'),('PURLIVE','Nízkoenergetický')]),
 'novostavbakolin': ('Novostavba SWING 116, Kolín', 'Novostavba', [('4+kk','Dispozice'),('116 m²','Užitná plocha'),('PURLIVE','Nízkoenergetický')]),
 'novostavba-prelouc': ('Novostavba CLASSIC 93, Přelouč', 'Novostavba', [('4+kk','Dispozice'),('92,4 m²','Užitná plocha'),('PURLIVE','Nízkoenergetický')]),
 'novostavba-pardubice': ('Novostavba AMBIENT 105, Pardubice', 'Novostavba', [('5+kk','Dispozice'),('105 m²','Užitná plocha'),('PURLIVE','Nízkoenergetický')]),
 'novostavba-kutna-hora': ('Novostavba SWING 125, Kutná Hora', 'Novostavba', [('5+kk','Dispozice'),('125 m²','Užitná plocha'),('PURLIVE','Nízkoenergetický')]),
}
def fmt_price(p):
    p = p.replace('Kč', '').replace('+ poplatky', '').strip()
    digits = re.sub(r'\D', '', p)
    if not digits: return p
    n = int(digits)
    if n > 1000000000: n = int(str(n)[:5])  # typo guard
    s = f'{n:,}'.replace(',', ' ') + ' Kč'
    return s
for x in LIST:
    x['st'] = STATUS.get(x.get('status', 'Aktuálně'), STATUS['Aktuálně'])
    x['typ'] = (x.get('type') or '').replace('Komerční prostory', 'Komerční').replace('Komerční objekty', 'Komerční')
    if x.get('detail'):
        x['short'], x['typ2'], x['facts'] = SHORT[x['slug']]
        x['pr'] = fmt_price(x['price']) + (' / měs.' if x['slug'].startswith('sklad') else '')
        x['href'] = f'nemovitosti/{x["slug"]}.html'
        x['card_img'] = x['imgs']['photos'][0] if x['imgs']['photos'] else x['file']
    if 'mobilního domu' in x['title'] or 'novostavb' in x['title'].lower() or 'Výstavba' in x['title']:
        x['typ'] = 'Novostavba'
BYSLUG = {x.get('slug'): x for x in LIST if x.get('slug')}

def type_key(x):
    t = (x.get('typ2') or x['typ']).lower()
    if 'novostav' in t: return 'novostavba'
    if 'chat' in t or 'chalup' in t: return 'chata'
    if 'dům' in t: return 'dum'
    if 'byt' in t: return 'byt'
    if 'pozem' in t: return 'pozemek'
    if 'komer' in t: return 'komercni'
    return 'jine'

def card(x, r, feat=False, i=0):
    key, lab, kind = x['st']
    done = kind == 'done'
    img = x.get('card_img') or x['file']
    title = x.get('short') or x['title']
    href = x.get('href')
    price = f'<span class="price">{x["pr"]}</span>' if x.get('pr') else ''
    tag = 'a' if href else 'div'
    attrs = f' href="{r}{href}"' if href else ''
    go = f'<span class="go">{ARR}</span>' if href else ''
    stamp = f' data-stamp="{lab}"' if done else ''
    pill = '' if done else f'<span class="pill pill--{kind}">{lab}</span>'
    return (f'<{tag}{attrs} class="card reveal{" is-done" if done else ""}{" feat" if feat else ""}" style="--i:{i % 3}" '
            f'data-status="{key}" data-type="{type_key(x)}">'
            f'<div class="card-media"{stamp}><img src="{r}{img}" alt="{esc(title)}" loading="lazy" decoding="async">{pill}{go}</div>'
            f'<div class="card-meta"><span>{esc(x.get("typ2") or x["typ"])}</span>{price}</div>'
            f'<h3>{esc(title)}</h3>'
            f'<div class="card-meta"><span>{esc(x.get("addr") or "")}</span></div></{tag}>')

def cta_card(r, cls='reveal'):
    return (f'<a href="{r}odhad-ceny.html" class="card-cta {cls}">{ripples()}<span class="label" style="color:#C9EEF2">Prodáváte?</span>'
            f'<h3>Tady je místo pro <em>vaši</em> nemovitost.</h3>'
            f'<span class="row" style="font-weight:600;font-size:.9rem">Odhad ceny zdarma {ARR}</span></a>')

# ------------------------------------------------------------------ layout
NAV = [('pribeh.html', 'Můj příběh'), ('jak-pracuji.html', 'Jak pracuji'), ('nemovitosti.html', 'Nemovitosti'),
       ('sluzby.html', 'Služby'), ('reference.html', 'Reference'), ('blog.html', 'Blog'), ('kontakt.html', 'Kontakt')]

import hashlib
def _ver(f): return hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]
def head(title, desc, r, img='img/site/telefon.webp', path='', ld=''):
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
    return f'''<a class="sr-only" href="#obsah">Přejít k obsahu</a>
<div class="scroll-progress" aria-hidden="true"></div>
<header class="nav">
  <div class="topbar">
    <div class="topbar-inner">
      <span class="tb-left"><span>Zlatý člen Realitní komory ČR</span><span>Realiťák roku 2023 · 2. místo, okres HK</span><a href="{r}reference.html" class="link-u"><span class="stars">★★★★★</span> 4,8 na Firmy.cz</a></span>
      <span class="tb-right"><a class="link-u" href="{TEL_H}">{PHONE_I} {TEL}</a><a class="link-u" href="mailto:{MAIL}">{MAIL}</a><a class="tb-cal" href="{CAL}" target="_blank" rel="noopener">Online schůzka {ARR}</a></span>
    </div>
  </div>
  <div class="nav-inner">
    <div class="lockup">
      <a href="{r}index.html" class="brand" aria-label="Mgr. Tomáš Veigl — domů">
        <img class="b-dark" src="{r}img/site/logo-nav-dark.png" alt="Mgr. Tomáš Veigl" width="1460" height="300">
        <img class="b-light" src="{r}img/site/logo-nav-light.png" alt="" width="1460" height="300">
      </a>
      <span class="brand-sep" aria-hidden="true"></span>
      <a href="{R11}" class="brand-r11" target="_blank" rel="noopener" aria-label="Reality 11">
        <img class="b-dark" src="{r}img/site/r11-dark.png" alt="reality11" width="600" height="229">
        <img class="b-light" src="{r}img/site/r11-light.png" alt="" width="600" height="229">
      </a>
    </div>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
    <nav class="nav-menu" aria-label="Hlavní navigace">
      {links}
      {btn(r + 'odhad-ceny.html', 'Odhad ceny zdarma', 'btn-magnetic')}
      <a href="{TEL_H}" class="nav-phone"><i></i>{TEL}</a>
    </nav>
  </div>
</header>'''

def footer(r):
    return f'''<div class="mbar"><a href="{TEL_H}" class="mbar-call">{PHONE_I} Zavolat</a><a href="{r}odhad-ceny.html" class="mbar-cta">Odhad ceny zdarma {ARR}</a></div>
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a href="{r}index.html" class="footer-logo"><img src="{r}img/site/logo-stack-light.png" alt="Mgr. Tomáš Veigl" width="831" height="470"></a>
        <img class="footer-powered" src="{r}img/site/powered-light.png" alt="Powered by reality11" width="365" height="61">
        <p style="max-width:34ch;margin-top:1.4rem">Realitní makléř z Hradce Králové. Slyším díky technice, rozumím díky srdci.</p>
        <div class="footer-badges"><img src="{r}img/site/rkcr.png" alt="Realitní komora ČR — zlatý člen"></div>
      </div>
      <div><h4>Web</h4><ul>{''.join(f'<li><a class="link-u" href="{r}{h}">{t}</a></li>' for h, t in NAV)}</ul></div>
      <div><h4>Služby</h4><ul>
        <li><a class="link-u" href="{r}odhad-ceny.html">Odhad ceny zdarma</a></li>
        <li><a class="link-u" href="https://najemsradosti.cz/" target="_blank" rel="noopener">Pronájem s radostí</a></li>
        <li><a class="link-u" href="https://klidnereseni.cz/" target="_blank" rel="noopener">Klidné řešení — výkup</a></li>
        <li><a class="link-u" href="{CAL}" target="_blank" rel="noopener">Online schůzka</a></li>
      </ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a class="link-u" href="{TEL_H}">{TEL}</a></li>
        <li><a class="link-u" href="mailto:{MAIL}">{MAIL}</a></li>
        <li>{ADDR}</li>
        <li>IČ: 684 56 255</li>
      </ul></div>
    </div>
    <div class="footer-giant" aria-hidden="true">Slyším váš domov</div>
    <div class="footer-bottom">
      <span>© {date.today().year} Mgr. Tomáš Veigl · Powered by REALITY 11 · Fyzická osoba zapsaná v živnostenském rejstříku</span>
      <span class="row" style="gap:1.2rem">
        <a class="link-u" href="{OLD}informace_o_ochrane_osobnich_udaju_-_gdpr.pdf" target="_blank" rel="noopener">GDPR</a>
        <a class="link-u" href="{OLD}reklamacni_rad.pdf" target="_blank" rel="noopener">Reklamační řád</a>
        <a class="link-u" href="{OLD}informace_o_vnitrnim_oznamovacim_systemu.pdf" target="_blank" rel="noopener">Oznamovací systém</a>
        <a class="link-u" href="{OLD}system_vnitrnich_zasad.pdf" target="_blank" rel="noopener">Vnitřní zásady</a>
      </span>
    </div>
  </div>
</footer>'''

def write(path, title, desc, body, active='', navtheme='dark', img='img/site/telefon.webp'):
    r = '../' * path.count('/')
    ld = LD if path == 'index.html' else ''
    doc = head(title, desc, r, img, '' if path == 'index.html' else path, ld) + f'\n<body data-nav="{navtheme}">\n' + header(r, active) + \
        f'\n<main id="obsah">\n{body.replace("@/", r)}\n</main>\n' + footer(r) + '\n</body>\n</html>\n'
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'w').write(doc)
    PAGES.append(path)
PAGES = []
LD = '\n<script type="application/ld+json">' + json.dumps({
    "@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Mgr. Tomáš Veigl — Slyším váš domov",
    "url": BASE, "image": BASE + "img/site/telefon.webp", "logo": BASE + "img/site/logo-full-color.png",
    "telephone": "+420737132041", "email": MAIL, "priceRange": "Kč",
    "address": {"@type": "PostalAddress", "streetAddress": "Třída Edvarda Beneše 1526/78", "addressLocality": "Hradec Králové", "addressCountry": "CZ"},
    "areaServed": ["Královéhradecký kraj", "Pardubický kraj", "Kutná Hora", "Kolín", "Praha-východ"],
    "memberOf": {"@type": "Organization", "name": "Reality 11", "url": R11},
    "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "reviewCount": "35", "bestRating": "5"},
    "sameAs": ["https://www.facebook.com/realityveigl", "https://www.instagram.com/realitak_s_kochleary", "https://www.linkedin.com/in/mgr-tom%C3%A1%C5%A1-veigl/"]
}, ensure_ascii=False) + '</script>'

def cta_block(title='Kolik má váš domov <em>hodnotu</em>?', text='Nezávazně a zdarma. Přijedu, poslechnu si, co od prodeje čekáte, a řeknu vám reálnou cenu — ne číslo z kalkulačky.'):
    return f'''<section class="section dark cta">
  {ripples()}
  <div class="container cta-inner">
    <div>
      <p class="label reveal">Odhad ceny zdarma</p>
      <h2 class="reveal">{title}</h2>
      <p class="lead reveal mt-md">{text}</p>
      <div class="row mt-lg reveal">{btn('@/odhad-ceny.html', 'Chci odhad ceny', 'btn--light', True)}{btn(CAL, 'Online schůzka', 'btn--ghost', ext=True)}</div>
    </div>
    <div class="cta-contact reveal">
      <small>Zavolejte mi</small><a class="big link-u" href="{TEL_H}">{TEL}</a>
      <small>Napište mi</small><a class="big link-u" href="mailto:{MAIL}" style="font-size:clamp(1.4rem,2.2vw,2rem)">{MAIL}</a>
      <small>Kancelář</small><span>{ADDR}</span>
    </div>
  </div>
</section>'''

PARTNERS = [('r11', 'img/site/r11-dark.png', 'Realitní síť', R11), ('rkcr', 'img/partners/rkcr.png', 'Zlatý člen', None),
            ('abes', 'img/partners/abes.png', 'Právní servis', None), ('rezek', 'img/partners/rezek.png', 'Advokátní kancelář', None),
            ('unicredit', 'img/partners/unicredit.png', 'Úschova peněz', 'https://www.unicreditbank.cz/'), ('sreality', 'img/partners/sreality.png', 'Inzerce', 'https://www.sreality.cz/'),
            ('idnes', 'img/partners/idnes.png', 'Inzerce', 'https://reality.idnes.cz/'), ('ceskereality', 'img/partners/ceskereality.png', 'Inzerce', 'https://www.ceskereality.cz/')]
def partners_block(bg=''):
    cells = ''.join((f'<a class="partner reveal" style="--i:{k % 4}" href="{u}" target="_blank" rel="noopener">' if u else f'<div class="partner reveal" style="--i:{k % 4}">') +
                    f'<img src="@/{img}" alt="{n}" loading="lazy"><small>{cap}</small>' + ('</a>' if u else '</div>')
                    for k, (n, img, cap, u) in enumerate(PARTNERS))
    return f'''<section class="section partners {bg}">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">Bezpečný obchod</p><h2 class="reveal">Za každým obchodem stojí <em>ověření</em> partneři</h2></div>
    <p class="lead reveal" style="max-width:44ch">Smlouvy připravuje ABES nebo advokátní kancelář Rezek – Petráš, peníze putují přes úschovu UniCredit Bank a vaši nemovitost uvidí lidé na největších realitních portálech.</p></div>
    <div class="partner-grid">{cells}</div>
  </div>
</section>'''

def post_card(p, r, i=0):
    return (f'<a href="{r}blog/{p["slug"]}.html" class="post reveal" style="--i:{i % 3}">'
            f'<div class="post-media"><img src="{r}{p.get("file","")}" alt="" loading="lazy" decoding="async"></div>'
            f'<time datetime="{p["date"]}">{czdate(p["date"])}</time><h3>{esc(p["title"])}</h3><p>{esc(p["excerpt"][:220])}</p></a>')

def rev_card(v, reply=False):
    rep = ''
    if reply and v.get('reply'):
        t = re.sub(r'^tomasveigl\.cz - Slyším váš domov:\s*', '', v['reply'])
        rep = f'<div class="reply"><img src="@/img/site/portrait.webp" alt=""><span><b style="color:var(--text)">Tomáš:</b> {esc(t)}</span></div>'
    d = v['date'].replace(' ', '')
    return (f'<article class="rev"><span class="stars" aria-label="{v["stars"]} z 5">{"★" * v["stars"]}{"☆" * (5 - v["stars"])}</span>'
            f'<p>{esc(v["text"])}</p>{rep}<footer><b>{esc(v["name"])}</b><span>{d}</span></footer></article>')

# ================================================================== HOME
def build_home():
    h1, n = words('Slyším\n_váš_ domov.')
    feat = BYSLUG['rodinny-dum-4kk-vinary-u-noveho-bydzova']
    offers = ['bytrychnov', 'dum_s_garazi_kricen', 'garsonkahradec', 'prodej-bytu-3-1-pilnikov-101-m2', 'dum-dobrichov', 'prodej-rodinneho-domu-s-garazi-a-velkym-pozemkem-pred-rekonstrukci']
    offer_cards = ''.join(card(BYSLUG[s], '@/', i=k) for k, s in enumerate(offers)) + cta_card('@/')
    revs = REV['reviews']
    rev_items = ''.join(rev_card(v) for v in revs)
    posts = ''.join(post_card(p, '@/', i) for i, p in enumerate(POSTS[:3]))
    marquee_words = ['Hradec Králové', 'Pardubice', 'Kutná Hora', 'Kolín', 'Praha-východ', 'Prodej', 'Pronájem a správa', 'Výkup', 'Odhad ceny zdarma']
    mq = ''.join(f'<span>{w} <b>✦</b></span>' for w in marquee_words)
    services = [
        ('Prodej nemovitosti', 'Od úvodní schůzky přes profi fotky, video, dron a 3D scan až po předání klíčů a přepis energií. 21 kroků, nic nechybí.', 'jak-pracuji.html', 'img/site/street.webp'),
        ('Pronájem a správa', 'Pronájem s radostí: opravy 24/7, garance nájmu až 600 000 Kč a právní asistence po celé republice.', 'sluzby.html#pronajem', 'img/site/najem.webp'),
        ('Výkup nemovitosti', 'Klidné řešení pro rozvod, dluhy nebo dědictví. Rychle, férově a bez zbytečného čekání.', 'sluzby.html#vykup', 'img/site/klidne.webp'),
        ('Novostavby na klíč', 'Nízkoenergetické domy PURLIVE v Hradci, Pardubicích, Kolíně i Kutné Hoře — od 1,3 mil. Kč.', 'sluzby.html#novostavby', BYSLUG['novostavbakolin']['card_img']),
        ('Odhad ceny zdarma', 'Zkušenost, ne kalkulačka. Řeknu vám, za kolik se vaše nemovitost reálně prodá — a proč.', 'odhad-ceny.html', 'img/site/dron1.webp'),
    ]
    srows = ''.join(f'<a href="@/{h}" class="srow reveal" data-img="@/{img}"><span class="idx">0{k+1}</span><h3>{t}</h3><p>{d}</p><span class="arr">{ARR}</span></a>'
                    for k, (t, d, h, img) in enumerate(services))
    q = revs[1]
    INT = [('Chci prodat', 'Odhad ceny zdarma a prodej za nejvyšší možnou cenu.', 'odhad-ceny.html'),
           ('Chci pronajmout', 'Pronájem s radostí — garance nájmu až 600 000 Kč.', 'sluzby.html#pronajem'),
           ('Hledám bydlení', 'Domy, byty, chalupy a novostavby v nabídce.', 'nemovitosti.html'),
           ('Potřebuji to rychle', 'Rozvod, dluhy, dědictví? Výkup nebo chytrý prodej.', 'sluzby.html#vykup')]
    intents = ''.join(f'<a href="@/{h}" class="intent reveal" style="--i:{k}"><span class="n">0{k+1}</span><b>{t}</b><small>{d}</small><span class="arr">{ARR}</span></a>' for k, (t, d, h) in enumerate(INT))
    sold = [x for x in LIST if x['st'][2] == 'done'][:26]
    sold_items = ''.join(f'<a href="@/nemovitosti.html?stav={x["st"][0]}" class="sold-item"><img src="@/{x["file"]}" alt="" loading="lazy" decoding="async"><span class="stamp">{x["st"][1]}</span><small>{esc((x.get("addr") or "").split(",")[-1].strip())}</small></a>' for x in sold)
    n_done = sum(1 for x in LIST if x['st'][2] == 'done')
    body = f'''
<section class="hero">
  <div class="hero-grid">
    <div class="hero-copy">
      <p class="label fade-up" style="--d:.1s">Realitní makléř · Hradec Králové</p>
      <h1 class="words">{h1}</h1>
      <p class="hero-sub fade-up" style="--d:.75s">Jsem Tomáš Veigl. Prodávám a pronajímám domy, byty i chalupy ve východních Čechách. Díky kochleárnímu implantátu jsem se znovu naučil slyšet — a hlavně <strong>naslouchat</strong>. Vám i vašemu domovu.</p>
      <div class="hero-actions fade-up" style="--d:.9s">
        {btn('@/odhad-ceny.html', 'Odhad ceny zdarma', '', True)}
        <a href="@/nemovitosti.html" class="link">Nemovitosti v nabídce {ARR}</a>
      </div>
      <div class="hero-proof fade-up mt-lg" style="--d:1.05s"><b>4,8</b><span><span class="stars">★★★★★</span><br>35 hodnocení na Firmy.cz</span><i class="vr"></i><img src="@/img/site/powered-dark.png" alt="Powered by reality11" width="365" height="61" class="powered"></div>
    </div>
    <div class="hero-figure">
      {ripples()}
      <div class="hero-arch"></div>
      <img class="portrait fade-up" style="--d:.35s" src="@/img/site/portrait.webp" alt="Mgr. Tomáš Veigl, realitní makléř" width="826" height="967" fetchpriority="high">
      <div class="hero-tag fade-up" style="--d:1.2s">{wave(18, 7, True)}<span><strong>200+ prodaných</strong>nemovitostí za 10 let</span></div>
    </div>
  </div>
  <div class="scroll-hint" aria-hidden="true"><span class="line"></span>Scroll</div>
  <div class="hero-bottom"><div class="hero-wave">{wave(140, 11, True)}</div></div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">{mq}{mq}</div></div>

<section class="intents">
  <div class="container">
    <p class="label reveal">S čím přicházíte?</p>
    <div class="intent-grid">{intents}</div>
  </div>
</section>

<section class="section statement">
  <div class="container statement-grid">
    <div><p class="label reveal">Co ode mě čekat</p></div>
    <div>
      <p class="statement-text reveal">Cílím na <em>nejvyšší možnou cenu</em>, ne na nejrychlejší podpis. <span class="soft">Co si domluvíme, to platí.</span> Ozvu se, když to slíbím. A protože vím přesně, co zařídit, <span class="soft">nestřílím naslepo</span> — šetřím váš čas i nervy.</p>
      <div class="pillars">
        <div class="pillar reveal" style="--i:0"><span class="n">01</span><h3>Lepší cena</h3><p>Vždy cílím na nejvyšší možnou cenu, i když to chce špičkovou přípravu a pořádnou porci času.</p></div>
        <div class="pillar reveal" style="--i:1"><span class="n">02</span><h3>Spolehlivost</h3><p>Ozývám se, jak jsem slíbil, plním, co očekáváte — a vždy jednám ve vašem zájmu.</p></div>
        <div class="pillar reveal" style="--i:2"><span class="n">03</span><h3>Úspora času</h3><p>Vím, co a jak zařídit, aby prodej proběhl bezpečně a s požadovaným výsledkem.</p></div>
      </div>
      <div class="house-rule reveal mt-lg" aria-hidden="true"><span></span></div>
      <div class="sig reveal"><img src="@/img/site/portrait.webp" alt="" style="background:var(--accent-bright)"><span><b>Mgr. Tomáš Veigl</b><small>Realitní makléř · Powered by reality11 · zlatý člen RK ČR</small></span></div>
    </div>
  </div>
</section>

<section class="feature">
  <div class="feature-media parallax"><img src="@/{feat['imgs']['photos'][5]}" alt="Obývací pokoj s krbovými kamny, Vinary" loading="lazy"></div>
  <div class="feature-inner">
    <div>
      <p class="label reveal">Právě připravujeme</p>
      <h2 class="reveal">Dům, kam se <em>budete těšit</em> celý týden.</h2>
    </div>
    <div class="feature-card reveal">
      <div class="row" style="justify-content:space-between"><span class="pill pill--live">Vinary u Nového Bydžova</span></div>
      <div class="price">{feat['pr']}</div>
      <div class="facts">{''.join(f'<div><b>{v}</b><small>{l}</small></div>' for v, l in feat['facts'])}</div>
      <p class="muted" style="font-size:.92rem;margin-bottom:1.2rem">Kompletně zrekonstruovaný interiér, tepelné čerpadlo, podlahové topení a zahrada, kde nemusíte počítat každý metr.</p>
      {btn('@/' + feat['href'], 'Prohlédnout dům')}
    </div>
  </div>
</section>

<section class="section offers">
  <div class="container sec-head">
    <div><p class="label reveal">Aktuální nabídka</p><h2 class="reveal">Domovy, které <em>hledají</em> nové lidi</h2></div>
    <div class="side reveal"><a href="@/nemovitosti.html" class="link">Všechny nemovitosti {ARR}</a>
      <div class="arrows" data-rail><button data-dir="prev" aria-label="Předchozí">{ARR_L}</button><button data-dir="next" aria-label="Další">{ARR}</button></div></div>
  </div>
  <div class="rail">{offer_cards}</div>
  <div class="container sold-head">
    <p class="reveal"><b>{n_done}</b> domovů na tomhle webu už má nové majitele nebo nájemníky.</p>
    <a href="@/nemovitosti.html?stav=prodano" class="link reveal">Prodané a pronajaté {ARR}</a>
  </div>
  <div class="sold-marquee" aria-label="Prodané a pronajaté nemovitosti"><div class="sold-track">{sold_items}{sold_items}</div></div>
</section>

<section class="section dark story">
  <div class="deco-text drift" style="top:6%;left:-2%" aria-hidden="true">naslouchat</div>
  <div class="container">
    <div class="story-grid">
      <div class="story-aside">
        <p class="label reveal">Můj příběh</p>
        <h2 class="reveal">Proč umím <em>naslouchat</em> lépe než ostatní?</h2>
        <figure class="story-photo clip-reveal"><img src="@/img/site/telefon.webp" alt="Tomáš Veigl v centru Hradce Králové" loading="lazy"><figcaption>{wave(14, 5, True)}Hradec Králové, můj domov</figcaption></figure>
      </div>
      <div class="hear-lines">
        <p class="hear">Kariéru v realitách jsem začal s horším sluchem. Svět ale časem <em>utichal</em> čím dál víc.<small>Vyvinula se u mě těžká percepční ztráta sluchu. Pro makléře, pro kterého je komunikace vším, to bylo jako prodávat se zavázanýma očima.</small></p>
        <p class="hear">Pak přišel <em>kochleární implantát</em>. A s ním se vrátil zvuk.<small>Implantát obchází poškozené části ucha a posílá signál přímo do sluchového nervu. Vrátil mi sluch — a mnohem víc než jen to.</small></p>
        <p class="hear">Kdo jednou ztratil sluch, začne <em>doopravdy naslouchat</em>.<small>Nejen ušima, ale hlavně srdcem. Proto slyším i to, co klienti neříkají nahlas: obavy, přání a to, co pro ně domov znamená.</small></p>
        <div class="reveal">{btn('@/pribeh.html', 'Celý příběh', 'btn--ghost')}</div>
      </div>
    </div>
    <div class="stats">
      <div class="stat reveal" style="--i:0"><div class="stat-num"><span data-count="200">0</span><sup>+</sup></div><p>prodaných a pronajatých nemovitostí</p></div>
      <div class="stat reveal" style="--i:1"><div class="stat-num"><span data-count="10">0</span><sup>let</sup></div><p>zkušeností v realitách</p></div>
      <div class="stat reveal" style="--i:2"><div class="stat-num"><span data-count="4.8">0</span><sup>★</sup></div><p>průměrné hodnocení z 35 recenzí</p></div>
      <div class="stat reveal" style="--i:3"><div class="stat-num"><span data-count="2">0</span><sup>. místo</sup></div><p>Realiťák roku 2023, okres Hradec Králové</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">Služby</p><h2 class="reveal">S čím vám <em>pomůžu</em></h2></div><p class="lead reveal" style="max-width:40ch">Prodej je jen začátek. Postarám se i o pronájem, výkup nebo stavbu nového domu — vždycky s jedním člověkem na telefonu.</p></div>
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
        <p class="label reveal">Reference</p>
        <blockquote class="reveal"><p>Hledáte makléře, kterému na klientech <em>opravdu záleží</em>? Pan Veigl je ta nejlepší volba.</p>
        <cite><b>{q['name']}</b><span class="muted">· Firmy.cz · {q['date'].replace(' ', '')}</span></cite></blockquote>
        <div class="row mt-lg reveal"><span class="rating-badge"><b>4,8</b><span><span class="stars">★★★★★</span><br>35 hodnocení · Firmy.cz</span></span><a href="@/reference.html" class="link">Přečíst všechny reference {ARR}</a></div>
      </div>
    </div>
  </div>
  <div class="rev-marquee"><div class="rev-track">{rev_items}{rev_items}</div></div>
</section>

<section class="section">
  <div class="container split">
    <div>
      <p class="label reveal">Kde působím</p>
      <h2 class="reveal">Znám to tu <em>jako své boty</em></h2>
      <p class="lead reveal mt-md">Mám přehled o vývoji cen ve východních Čechách a díky zkušenostem vím, jak vám tady zajistit nejvýhodnější prodej. Ale klidně přijedu kamkoli v Česku.</p>
      <div class="reveal mt-lg">{btn('@/kontakt.html', 'Domluvit schůzku', 'btn--ghost')}</div>
    </div>
    <ul class="regions-list">
      <li class="reveal" style="--i:0">Královéhradecko <small>HK · Nový Bydžov · Rychnov</small></li>
      <li class="reveal" style="--i:1">Pardubicko <small>Pardubice · Přelouč · Chrudim</small></li>
      <li class="reveal" style="--i:2">Kutnohorsko <small>Kutná Hora · Čáslav</small></li>
      <li class="reveal" style="--i:3">Kolínsko <small>Kolín · Velim</small></li>
      <li class="reveal" style="--i:4">Praha-východ <small>a celá ČR</small></li>
    </ul>
  </div>
</section>

{divider(21)}

<section class="section">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">Blog</p><h2 class="reveal">Novinky ze <em>světa realit</em></h2></div><a href="@/blog.html" class="link reveal">Všechny články {ARR}</a></div>
    <div class="posts">{posts}</div>
  </div>
</section>

{cta_block()}
'''
    write('index.html', 'Tomáš Veigl — realitní makléř, Hradec Králové | Slyším váš domov',
          'Realitní makléř Mgr. Tomáš Veigl — prodej, pronájem a výkup nemovitostí v Hradci Králové, Pardubicích, Kutné Hoře a Kolíně. 200+ prodaných nemovitostí, hodnocení 4,8.', body)

# ================================================================== PŘÍBĚH
def build_story():
    h1, _ = words('Slyším díky technice.\n_Rozumím_ díky srdci.')
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container phero-grid">
    <div>
      <nav class="crumbs"><a href="@/index.html">Domů</a><span>Můj příběh</span></nav>
      <p class="label fade-up" style="--d:.1s">Můj příběh</p>
      <h1 class="words" style="max-width:13ch">{h1}</h1>
      <p class="lead fade-up" style="--d:.8s">Realitní makléř, ale také veselý člověk, manžel a táta. A člověk, který ví, jaké to je, když svět zničehonic ztichne.</p>
    </div>
    <figure class="portrait-hero clip-reveal"><div class="img"><img src="@/img/site/whatsapp1.webp" alt="Tomáš Veigl telefonuje s klientem" loading="eager"></div></figure>
  </div>
</section>

<section class="section dark story">
  <div class="deco-text drift" style="bottom:4%;left:-4%" aria-hidden="true">ticho</div>
  <div class="container">
    <div class="story-grid">
      <div class="story-aside">
        <p class="label reveal">Proč umím naslouchat</p>
        <h2 class="reveal">Od <em>ticha</em> ke každému slovu.</h2>
        <p class="lead reveal">Scrollujte pomalu. Tak nějak to znělo, když se mi sluch vracel.</p>
      </div>
      <div class="hear-lines">
        <p class="hear">Svou kariéru v realitách jsem začal s horším sluchem. V průběhu let se ale vyvinula <em>těžká percepční ztráta</em> sluchu.<small>Neuvěřitelně mi to ztížilo práci. Pro realitního makléře je komunikace vším — musím rozumět klientům, jednat jejich jménem a vysvětlit každý důležitý detail o nemovitosti. Ztráta sluchu mi bránila poskytovat služby, na které jsem byl zvyklý.</small></p>
        <p class="hear">Rozhodl jsem se pro operaci <em>kochleárního implantátu</em>. Změnila mi život.<small>Kochleární implantát obchází poškozené části ucha a posílá elektrické signály přímo do sluchového nervu. Implantát mi vrátil sluch — a nejen to.</small></p>
        <p class="hear">Protože vím, jaké je o sluch přijít, <em>vnímám víc</em>. Okolí, lidi i to, co mi klienti opravdu říkají.<small>Díky kochleární technologii mohu znovu naplno komunikovat. Implantát vrátil mou kariéru na správnou cestu — a mně dal schopnost pozorně naslouchat přesně tomu, co moji klienti chtějí.</small></p>
      </div>
    </div>
    <div class="timeline">
      <div class="tl reveal" style="--i:0"><b>Začátky</b><p>První obchody v realitách — už tehdy s horším sluchem.</p></div>
      <div class="tl reveal" style="--i:1"><b>Ticho</b><p>Těžká percepční ztráta sluchu. Každý telefonát je boj.</p></div>
      <div class="tl reveal" style="--i:2"><b>Implantát</b><p>Operace, která mi vrátila zvuk — i chuť do práce.</p></div>
      <div class="tl reveal" style="--i:3"><b>2023</b><p>2. místo v soutěži Realiťák roku, okres Hradec Králové.</p></div>
      <div class="tl reveal" style="--i:4"><b>2024</b><p>3. místo v soutěži Realiťák roku, okres Hradec Králové.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <figure class="frame clip-reveal" style="aspect-ratio:5/4"><img src="@/img/site/rodina.webp" alt="Tomáš s rodinou a psy Corou a Kyrou" loading="lazy"></figure>
    <div>
      <p class="label reveal">Kdo jsem</p>
      <h2 class="reveal">Realitní makléř, ale také <em>veselý člověk</em>, manžel a táta</h2>
      <div class="prose mt-md reveal">
        <p class="dropcap">Nejen prací živ je člověk. Kromě toho, že jsem realiťák, jsem hlavně člověk z masa a kostí. Volný čas se snažím co nejvíc trávit s rodinou.</p>
        <p>S dcerou Natálkou jezdíme na kole a koloběžce a lyžujeme. Doma máme dva psy — Coru (maďarský ohař) a Kyru (německý ohař), se kterými trávíme čas na louce nebo na procházkách v lese.</p>
        <p>V práci mi pomáhá manželka <strong>Radka Veiglová</strong> jako asistentka. Takže když voláte nám, voláte vlastně rodinné firmě.</p>
        <p class="serif" style="font-family:var(--font-display);font-size:1.9rem;line-height:1.2">Nuda? Tak to u nás <em>absolutně</em> nehledejte.</p>
      </div>
    </div>
  </div>
</section>

<section class="section bg-alt">
  <div class="container split flip">
    <figure class="frame clip-reveal" style="background:var(--paper);padding:1rem"><img src="@/img/site/certifikaty.webp" alt="Certifikáty a ocenění Realiťák roku" loading="lazy" style="object-fit:contain"></figure>
    <div>
      <p class="label reveal">Ocenění a vzdělávání</p>
      <h2 class="reveal">Proč se účastním <em>Realiťáka roku</em>?</h2>
      <div class="prose mt-md reveal">
        <p>Věřím, že kvalitní práce si zaslouží být vidět. Soutěž mě motivuje se neustále zlepšovat a posouvat dál — a je úzce propojená se vzděláváním. Mám díky ní přístup k aktuálním trendům, novinkám v legislativě a zkušenostem od špiček v oboru.</p>
        <p>V pravidelných rozhovorech Realiťáka roku můžete nahlédnout do mého přístupu k realitám: co mě motivuje, jak pracuji s klienty a proč mě tahle práce opravdu baví.</p>
      </div>
      <div class="badges mt-lg">
        <div class="badge-card reveal" style="--i:0"><b>2.</b><small>místo · Realiťák roku 2023<br>okres Hradec Králové</small></div>
        <div class="badge-card reveal" style="--i:1"><b>3.</b><small>místo · Realiťák roku 2024<br>okres Hradec Králové</small></div>
        <div class="badge-card reveal" style="--i:2"><b>Zlatý</b><small>člen Realitní komory<br>České republiky</small></div>
      </div>
    </div>
  </div>
</section>

{cta_block('Pojďme si <em>promluvit</em>.', 'Rád si vyslechnu, co plánujete. Osobně u vás, v kanceláři v Hradci Králové nebo online — jak je vám to příjemnější.')}
'''
    write('pribeh.html', 'Můj příběh — Tomáš Veigl | Slyším váš domov',
          'Realitní makléř s kochleárním implantátem. Příběh Tomáše Veigla o tom, proč umí naslouchat lépe než ostatní.', body, 'pribeh.html')

# ================================================================== JAK PRACUJI
STEPS = [
 ('Příprava', 'Úvodní schůzka', 'Sejdeme se přímo u vás doma — v domě nebo bytě, který chcete prodat. Seznámíme se, projdeme stav nemovitosti a teprve pak řeknu, za kolik ji můžeme prodat, jak ji nabídnout, kolik to bude stát a jak dlouho to může trvat. Připravím i seznam podkladů: list vlastnictví, plány, případné nájemní smlouvy.', 'street.webp', ''),
 ('Příprava', 'Strategický marketingový plán a analýza ceny', 'Podrobně analyzuji trh, konkurenci a specifika vaší nemovitosti. Navrhnu optimální prodejní cenu a marketingový plán — cílenou reklamu, online prezentaci i prodejní strategii. Cílem je maximalizovat hodnotu a oslovit co nejširší okruh kupců.', None, ''),
 ('Příprava', 'TOP texty a přesné informace', 'Dobré texty prodávají — zaujmou, budí důvěru a přesvědčí. Jasné a pravdivé informace šetří čas všem a předejdou zbytečným komplikacím. Férovost a transparentnost jsou základ dobrého obchodu.', None, ''),
 ('Příprava', 'PENB', 'Průkaz energetické náročnosti budovy ukazuje, kolik energie nemovitost spotřebuje, a kupující hned ví, jaké budou náklady na provoz. Ze zákona je povinný při prodeji i pronájmu — jeho zajištění je samozřejmou součástí mé služby.', 'penb.webp', 'contain'),
 ('Prezentace', 'Vizualizace', 'Prázdný nebo zastaralý prostor vizualizuji tak, aby si zájemci dokázali představit, jak by v něm mohli žít. Virtuální home staging pomáhá vidět potenciál místo nedostatků — a to prodává.', 'vizu1.webp', ''),
 ('Prezentace', 'Půdorysy', 'Pro každou nemovitost připravuji půdorys tak, jak vypadá teď, a zároveň návrh možného budoucího řešení. Zájemci tak na první pohled vidí, jak by prostor mohl fungovat pro ně.', 'pudorys.webp', 'contain'),
 ('Prezentace', 'Video', 'Video během pár vteřin vzbudí emoci a přiblíží atmosféru místa. Díky videoprohlídce si zájemce udělá jasnou představu, aniž by musel hned přijet — a to šetří čas a zvyšuje šanci na rychlý prodej.', None, ''),
 ('Prezentace', 'Využití dronu', 'Letecké záběry ukážou, co z ulice nevidíte: celý pozemek, okolí, přírodu i dostupnost. U domů, chalup a pozemků je dron často tím, co zájemce přesvědčí přijet na prohlídku.', 'dron1.webp', ''),
 ('Prezentace', '3D scan nemovitosti', 'Zájemci si celou nemovitost projdou online, jako by tam skutečně byli — kdykoli a odkudkoli. Scan zvyšuje zájem a pomáhá odfiltrovat jen opravdu vážné zájemce.', None, ''),
 ('Prezentace', 'Samostatná webová stránka', 'Každá nemovitost, kterou prodávám nebo pronajímám, dostane vlastní webovou stránku. Bez rušivých inzerátů a konkurence — se všemi fotkami, videem, půdorysy a kontaktem na jednom místě.', 'scan3d.webp', 'contain'),
 ('Marketing', 'Realitní portály', 'Inzeruji na největších realitních portálech s maximální viditelností. Každý inzerát TOPuji 2× až 3× týdně, aby se držel na předních pozicích a oslovil co nejvíc zájemců.', 'portaly.webp', 'contain'),
 ('Marketing', 'Reklamní plachty', 'Plachta přitahuje pozornost přímo tam, kde nemovitost stojí. Zaujme kolemjdoucí i sousedy, kteří často někoho znají — a mnohdy se právě díky ní ozve ten správný zájemce.', 'plachta.webp', ''),
 ('Marketing', 'Katalog nemovitosti', 'Každý zájemce ode mě při prohlídce dostane tištěný katalog se všemi informacemi, fotkami a půdorysy. Pomáhá mu nabídku si zapamatovat a vrátit se k ní doma.', 'katalog.webp', 'contain'),
 ('Marketing', 'Sociální sítě', 'Na Facebooku, Instagramu i LinkedInu pravidelně sdílím novinky z trhu, zajímavé nemovitosti, zákulisí práce a užitečné rady. Nabídky se tak dostanou k mnohem většímu počtu lidí.', None, ''),
 ('Marketing', 'Aukce nemovitosti', 'U velmi žádaných domů, bytů nebo pozemků využívám aukci. Z prodeje se stává férová a transparentní soutěž — a prodávající často získá vyšší cenu, než čekal.', 'aukce.webp', 'contain'),
 ('Bezpečný obchod', 'Výkup nemovitosti', 'Rozvod, dluhy, dědictví nebo nutnost rychle se stěhovat — v takových situacích nabízím výkup. Považuji ho za krajní, ale férové řešení: peníze bez zbytečného čekání a starostí.', None, ''),
 ('Bezpečný obchod', 'Právní servis a úschova', 'Veškeré právní kroky řeším se společností ABES, případně s advokátní kanceláří Rezek – Petráš. Finanční úschovu zajišťuji výhradně přes UniCredit Bank. Vše transparentní a pod kontrolou.', 'pravni.webp', 'contain'),
 ('Bezpečný obchod', 'Předání nemovitosti', 'Třešnička na dortu, kdy vše do sebe zapadne. Společně projdeme nemovitost, sepíšeme předávací protokol, nafotíme stav a doladíme poslední detaily. Tady končí práce a začíná nový domov.', None, ''),
 ('Bezpečný obchod', 'Přepis energií', 'Předáním moje práce nekončí. Společně jdeme přepsat energie, pomůžu s formuláři a vysvětlím postup, aby se nový majitel mohl v klidu zabydlet.', None, ''),
 ('Něco navíc', 'Realiťák roku', 'Soutěž mě motivuje zlepšovat se a dává mi přístup k trendům, legislativě a zkušenostem špiček oboru. V okrese Hradec Králové jsem v roce 2023 skončil 2., v roce 2024 3.', 'certifikaty.webp', 'contain'),
 ('Něco navíc', 'Rozhovory', 'V rozhovorech projektu Realiťák roku můžete nahlédnout do mého přístupu: co mě motivuje, jak pracuji s klienty a proč mě tahle práce opravdu baví. Za každým prodejem stojí opravdový člověk.', None, ''),
]
def build_process():
    h1, _ = words('21 kroků\nk _prodanému_ domovu')
    items = ''; last = None
    for k, (ph, t, d, img, mode) in enumerate(STEPS):
        if ph != last:
            items += f'<div class="phase-title">{ph}</div>'; last = ph
        im = f'<div class="step-img clip-reveal {mode}"><img src="@/img/site/{img}" alt="{esc(t)}" loading="lazy"></div>' if img else ''
        extra = ''
        if t == 'Sociální sítě':
            extra = '<div class="row" style="gap:1.4rem"><a class="link" href="https://www.facebook.com/realityveigl" target="_blank" rel="noopener">Facebook</a><a class="link" href="https://www.instagram.com/realitak_s_kochleary" target="_blank" rel="noopener">Instagram</a><a class="link" href="https://www.linkedin.com/in/mgr-tom%C3%A1%C5%A1-veigl/" target="_blank" rel="noopener">LinkedIn</a></div>'
        items += f'<article class="step" data-phase="{ph}"><span class="k">Krok {k+1:02d}</span><h3>{t}</h3><p>{d}</p>{extra}{im}</article>'
    dots = '<i></i>' * len(STEPS)
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Jak pracuji</span></nav>
    <p class="label fade-up" style="--d:.1s">Jak pracuji</p>
    <h1 class="words" style="max-width:12ch">{h1}</h1>
    <p class="lead fade-up" style="--d:.8s">Prodej nemovitosti není inzerát a čekání. Je to řemeslo. Tady je všechno, co pro vás udělám — od první kávy u vás v kuchyni až po přepis energií.</p>
  </div>
</section>
{divider(8)}
<section class="section" style="padding-top:var(--gap-lg)">
  <div class="container steps-wrap">
    <aside class="steps-aside">
      <div class="step-counter" data-step-counter>01<small>/ 21</small></div>
      <div class="step-phase" data-step-phase>Příprava</div>
      <div class="phase-dots" aria-hidden="true">{dots}</div>
      <div class="extra mt-lg">{btn('@/kontakt.html', 'Chci začít krokem 1', '', True)}</div>
    </aside>
    <div class="steps">{items}</div>
  </div>
</section>
{cta_block('Začneme <em>krokem jedna</em>?', 'Úvodní schůzka je nezávazná. Přijedu, prohlédnu si nemovitost a řeknu vám, jak bych ji prodával — a za kolik.')}
'''
    write('jak-pracuji.html', 'Jak pracuji — 21 kroků k prodanému domovu | Tomáš Veigl',
          'Od úvodní schůzky přes vizualizace, dron, 3D scan a portály až po předání a přepis energií. Kompletní servis realitního makléře Tomáše Veigla.', body, 'jak-pracuji.html')

# ================================================================== NEMOVITOSTI
def build_listing():
    order = {'Aktuálně': 0, 'Připravujeme': 1, 'V rezervaci': 2, 'Prodáno': 3, 'Pronajato': 3}
    items = sorted(LIST, key=lambda x: (order.get(x.get('status', 'Aktuálně'), 4), 0 if x.get('detail') else 1))
    # put Vinary first as featured
    items.sort(key=lambda x: 0 if x.get('slug') == 'rodinny-dum-4kk-vinary-u-noveho-bydzova' else 1)
    cards = []; inserted = False
    for k, x in enumerate(items):
        if not inserted and x['st'][0] in ('prodano', 'pronajato'):
            cards.append(cta_card('@/', 'reveal card" data-status="nabidka" data-type="all'))
            inserted = True
        cards.append(card(x, '@/', feat=(k == 0), i=k))
    from collections import Counter
    c = Counter(x['st'][0] for x in LIST)
    chips = [('all', 'Vše', len(LIST)), ('nabidka', 'V nabídce', c['nabidka']), ('rezervace', 'Rezervace', c['rezervace']),
             ('prodano', 'Prodáno', c['prodano']), ('pronajato', 'Pronajato', c['pronajato'])]
    chip_html = ''.join(f'<button class="chip{" on" if k == "all" else ""}" data-status-filter="{k}">{t}<sup>{n}</sup></button>' for k, t, n in chips)
    h1, _ = words('Domy, byty a chalupy,\nkteré _hledají_ nové lidi')
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
      <p class="lead">Aktuální nabídka i to, co už má nové majitele. Každá nemovitost dostala vlastní prezentaci, fotky, půdorysy a péči.</p>
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
    <p class="empty-note">V této kombinaci teď nic nemám. Ale ozvěte se — často vím o nemovitostech dřív, než jdou na portály.</p>
  </div>
</section>
{cta_block('Hledáte, co <em>tu není</em>?', 'Řekněte mi, co hledáte. Často vím o nemovitostech dřív, než se objeví na portálech — a rád vám dám vědět jako prvnímu.')}
'''
    write('nemovitosti.html', 'Nemovitosti v nabídce — Tomáš Veigl, realitní makléř',
          'Aktuální nabídka domů, bytů, chalup a novostaveb ve východních Čechách i reference prodaných a pronajatých nemovitostí.', body, 'nemovitosti.html')

def prose(blocks, hl='h3'):
    out = []
    for b in blocks:
        if b['t'] != 'ul': b = dict(b, v=re.sub(r'\(?\s*Rozsah_dodavky__Stavba_k_dokonceni_PURLIVE\s*\)?', '(rozsah dodávky: stavba k dokončení PURLIVE)', b['v']))
        if b['t'] == 'ul':
            out.append('<ul>' + ''.join(f'<li>{v}</li>' for v in b['v']) + '</ul>')
        elif b['t'] == 'h':
            out.append(f'<{hl}>{strip_tags(b["v"])}</{hl}>')
        else:
            v = b['v']
            if re.fullmatch(r'<strong>[^<]{3,90}</strong>', v.strip()):
                out.append(f'<{hl}>{strip_tags(v)}</{hl}>')
            else:
                out.append(f'<p>{v}</p>')
    return '\n'.join(out)

def gallery(imgs, cls='', limit=8):
    if not imgs: return ''
    links = []
    for k, p in enumerate(imgs):
        hidden = k >= limit
        more = f' class="more" data-more="+{len(imgs) - limit}"' if (k == limit - 1 and len(imgs) > limit) else ''
        links.append(f'<a href="@/{p}"{more}{" hidden" if hidden else ""}><img src="@/{p}" alt="" loading="lazy" decoding="async"></a>')
    return f'<div class="gal {cls}" data-lb>{"".join(links)}</div>'

def build_details():
    for x in LIST:
        if not x.get('detail'): continue
        key, lab, kind = x['st']
        blocks = [b for b in x['body']]
        # lead = first paragraph(s) until 220 chars
        lead = []; rest = list(blocks)
        while rest and rest[0]['t'] == 'p' and sum(len(strip_tags(l)) for l in lead) < 160:
            lead.append(strip_tags(rest.pop(0)['v']))
        lead_html = f'<p class="lead-quote reveal">{esc(" ".join(lead))}</p>' if lead else ''
        hero = x['imgs']['photos'][0] if x['imgs']['photos'] else x['imgs']['viz'][0]
        facts = x['facts']
        bar = f'<div><small>{"Nájem" if x["slug"].startswith("sklad") else "Cena"}</small><b class="price">{x["pr"]}</b></div>' + ''.join(f'<div><small>{l}</small><b>{v}</b></div>' for v, l in facts)
        others = [o for o in LIST if o.get('detail') and o is not x and o['st'][0] == 'nabidka' and o['typ2'] != 'Novostavba'][:3]
        if len(others) < 3: others += [o for o in LIST if o.get('detail') and o is not x and o not in others][:3 - len(others)]
        sec_ph = f'<h2 class="reveal mt-xl" style="font-size:clamp(2rem,3.4vw,3rem);margin-bottom:var(--gap-md)">Fotografie</h2>{gallery(x["imgs"]["photos"])}' if x['imgs']['photos'] else ''
        sec_pl = f'<h2 class="reveal mt-xl" style="font-size:clamp(2rem,3.4vw,3rem);margin-bottom:var(--gap-md)">Půdorysy</h2>{gallery(x["imgs"]["plans"], "plans", 6)}' if x['imgs']['plans'] else ''
        sec_vz = f'<h2 class="reveal mt-xl" style="font-size:clamp(2rem,3.4vw,3rem);margin-bottom:var(--gap-md)">Jak to <em>může</em> vypadat</h2><p class="muted" style="margin-bottom:var(--gap-md)">Ilustrativní vizualizace možného budoucího řešení.</p>{gallery(x["imgs"]["viz"], "", 6)}' if x['imgs']['viz'] else ''
        body = f'''
<section class="dhero">
  <div class="feature-media parallax"><img src="@/{hero}" alt="{esc(x['short'])}" fetchpriority="high"></div>
  <div class="dhero-inner">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span><a href="@/nemovitosti.html">Nemovitosti</a></span><span>{esc(x['short'])}</span></nav>
    <span class="pill pill--{kind} fade-up" style="--d:.1s">{lab}</span>
    <h1 class="fade-up" style="--d:.2s">{esc(x['title'])}</h1>
    <p class="addr fade-up" style="--d:.35s">{PIN} {esc(x.get('addr') or '')}</p>
  </div>
</section>
<div class="dbar"><div class="dbar-inner">{bar}</div></div>
<section class="section">
  <div class="container dgrid">
    <article>
      {lead_html}
      <div class="prose reveal">{prose(rest)}</div>
      {sec_ph}{sec_pl}{sec_vz}
    </article>
    <aside class="dside">
      <div class="agent-card">
        {ripples()}
        <div class="who"><img src="@/img/site/portrait.webp" alt=""><span><b>Tomáš Veigl</b><small>Váš makléř pro tuto nemovitost</small></span></div>
        <a class="tel link-u" href="{TEL_H}">{TEL}</a>
        <a class="mail link-u" href="mailto:{MAIL}?subject={esc(x['short'])}">{MAIL}</a>
        {btn('@/kontakt.html?nemovitost=' + __import__('urllib.parse').parse.quote(x['short']), 'Domluvit prohlídku', 'btn--light')}
      </div>
      <div class="badge-card" style="flex-direction:row;align-items:center;gap:1rem"><b style="font-size:2.2rem">4,8</b><small><span class="stars">★★★★★</span><br>35 hodnocení klientů na Firmy.cz</small></div>
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
        write(x['href'], f"{x['short']} — {x['pr']} | Tomáš Veigl", strip_tags(' '.join(lead))[:155] or x['title'], body, 'nemovitosti.html', 'light', hero)

# ================================================================== SLUŽBY
def build_services():
    nb = [BYSLUG[s] for s in ['novostavbachlumec', 'novostavbahradeckralove', 'novostavbakolin', 'novostavba-prelouc', 'novostavba-pardubice', 'novostavba-kutna-hora']]
    h1, _ = words('Prodej, pronájem, výkup.\n_Klidně_ a férově.')
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Služby</span></nav>
    <p class="label fade-up" style="--d:.1s">Služby</p>
    <h1 class="words" style="max-width:14ch">{h1}</h1>
    <div class="row mt-md fade-up" style="--d:.8s;gap:.5rem">
      <a class="chip" href="#prodej">Prodej</a><a class="chip" href="#pronajem">Pronájem a správa</a><a class="chip" href="#vykup">Výkup</a><a class="chip" href="#novostavby">Novostavby</a><a class="chip" href="@/odhad-ceny.html">Odhad ceny</a>
    </div>
  </div>
</section>

<section class="section" id="prodej" style="padding-top:var(--gap-lg)">
  <div class="container svc">
    <figure class="svc-media clip-reveal"><img src="@/img/site/dron2.webp" alt="Letecký pohled na prodávaný dům" loading="lazy"></figure>
    <div>
      <p class="label reveal">01 — Prodej</p>
      <h2 class="reveal">Prodám váš dům za <em>nejvyšší možnou</em> cenu</h2>
      <div class="prose mt-md reveal">
        <p>Nestačí vyfotit pokoje a dát inzerát na portál. Každá nemovitost ode mě dostane strategii, profesionální fotky, video, dron, 3D scan, vizualizace, půdorysy, vlastní web, tištěný katalog i plachtu na plot.</p>
        <p>Inzeráty TOPuji 2–3× týdně, smlouvy připravuje ABES nebo AK Rezek – Petráš a peníze putují přes úschovu UniCredit Bank. Po předání s vámi jdu přepsat i energie.</p>
      </div>
      <ul class="regions-list mt-lg" style="--x:1">
        <li class="reveal" style="font-size:clamp(1.5rem,2.6vw,2.2rem)">Profi fotky, video a dron <small>Prezentace</small></li>
        <li class="reveal" style="font-size:clamp(1.5rem,2.6vw,2.2rem)">3D scan a vizualizace <small>Prezentace</small></li>
        <li class="reveal" style="font-size:clamp(1.5rem,2.6vw,2.2rem)">Portály, sítě, plachty <small>Marketing</small></li>
        <li class="reveal" style="font-size:clamp(1.5rem,2.6vw,2.2rem)">Právní servis a úschova <small>Bezpečnost</small></li>
      </ul>
      <div class="mt-lg reveal">{btn('@/jak-pracuji.html', 'Všech 21 kroků')}</div>
    </div>
  </div>
</section>

<section class="section dark" id="pronajem">
  <div class="container">
    <div class="split">
      <div>
        <p class="label reveal">02 — Pronájem s radostí</p>
        <h2 class="reveal">My se staráme, <em>vy si užíváte</em> života</h2>
        <p class="lead reveal mt-md">Pronájem bez nočních telefonátů a strachu z neplatiče. Najdu spolehlivého nájemníka, postarám se o správu a vy máte garance, které běžný pronájem nenabízí.</p>
        <div class="row mt-lg reveal">{btn('https://najemsradosti.cz/', 'Pronájem s radostí', 'btn--light', ext=True)}</div>
      </div>
      <figure class="frame clip-reveal" style="aspect-ratio:4/3.4"><img src="@/img/site/najem.webp" alt="Spokojená rodina v pronajatém bytě" loading="lazy"></figure>
    </div>
    <div class="guarantees">
      <div class="reveal" style="--i:0"><b>600 000 Kč</b><p>zaplacení nájmu za nájemníka při nemoci nebo ztrátě zaměstnání</p></div>
      <div class="reveal" style="--i:1"><b>250 000 Kč</b><p>proplacení škod způsobených nájemníkem</p></div>
      <div class="reveal" style="--i:2"><b>100 000 Kč</b><p>proplacení dluhu při sporu s nájemcem kvůli nezaplacenému nájmu</p></div>
      <div class="reveal" style="--i:3"><b>24/7</b><p>opravy závad a havárií i právní asistence — po celé ČR</p></div>
    </div>
  </div>
</section>

<section class="section" id="vykup">
  <div class="container split flip">
    <figure class="frame clip-reveal" style="aspect-ratio:1"><img src="@/img/site/klidne.webp" alt="Pár doma na gauči" loading="lazy"></figure>
    <div>
      <p class="label reveal">03 — Klidné řešení</p>
      <h2 class="reveal">Výkup, když <em>čas</em> hraje roli</h2>
      <div class="prose mt-md reveal">
        <p>Rozvod, dluhy, dědictví nebo nutnost rychle se stěhovat. Jsou situace, kdy je potřeba jednat opravdu rychle — a tehdy nabízím výkup nemovitosti.</p>
        <p>Považuji ho za krajní, ale férové řešení. Nejdřív vám ale vysvětlím možnosti a pomůžu najít další postup. <strong>Ne vždy je potřeba výkup. Někdy stačí dobře nastavený prodej.</strong></p>
      </div>
      <div class="row mt-lg reveal">{btn('https://klidnereseni.cz/', 'Klidné řešení', '', ext=True)}<a href="{TEL_H}" class="link">Raději zavolám {ARR}</a></div>
    </div>
  </div>
</section>

{partners_block('bg-paper')}

<section class="section bg-alt" id="novostavby">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">04 — Novostavby</p><h2 class="reveal">Nový dům <em>bez starostí</em> se stavbou</h2></div><p class="lead reveal" style="max-width:42ch">Nízkoenergetické dřevostavby systému PURLIVE ve stavu k dokončení. Ceny včetně 12% DPH.</p></div>
    <div class="grid-list">{''.join(card(x, '@/', i=k) for k, x in enumerate(nb))}</div>
  </div>
</section>

{cta_block()}
'''
    write('sluzby.html', 'Služby — prodej, pronájem, výkup a novostavby | Tomáš Veigl',
          'Prodej nemovitostí v 21 krocích, Pronájem s radostí s garancemi až 600 000 Kč, výkup Klidné řešení a novostavby PURLIVE.', body, 'sluzby.html')

# ================================================================== REFERENCE
def build_reference():
    cards = ''.join(f'<div class="reveal" style="--i:{k % 3}">{rev_card(v, True)}</div>' for k, v in enumerate(REV['reviews']))
    cards = cards.replace('<div class="reveal"', '<div class="reveal"')
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container phero-grid">
    <div>
      <nav class="crumbs"><a href="@/index.html">Domů</a><span>Reference</span></nav>
      <p class="label fade-up" style="--d:.1s">Reference</p>
      <h1 class="words">{words('Co o mně _říkají_ klienti')[0]}</h1>
      <p class="lead fade-up" style="--d:.8s">Skutečná hodnocení z Firmy.cz — včetně mých odpovědí. Protože naslouchat znamená i odpovědět.</p>
    </div>
    <div class="fade-up" style="--d:.5s">
      <div class="big-rating">4,8</div>
      <p class="row mt-sm" style="gap:.8rem"><span class="stars" style="font-size:1.2rem">★★★★★</span><span class="muted">35 hodnocení · Firmy.cz</span></p>
    </div>
  </div>
</section>
{divider(13)}
<section class="section" style="padding-top:var(--gap-lg)">
  <div class="container">
    <div class="masonry">{''.join(f'<div class="reveal" style="--i:{k % 3};break-inside:avoid">{rev_card(v, True)}</div>' for k, v in enumerate(REV['reviews']))}</div>
    <div class="center mt-lg reveal">{btn(FIRMY, 'Všech 35 hodnocení na Firmy.cz', 'btn--ghost', ext=True)}</div>
  </div>
</section>
{cta_block('Buďte můj další <em>spokojený</em> klient.', 'Rád pro vás udělám to samé. Stačí zavolat nebo si domluvit nezávazný odhad ceny.')}
'''
    write('reference.html', 'Reference — 4,8 z 35 hodnocení | Tomáš Veigl',
          'Co o realitním makléři Tomáši Veiglovi říkají jeho klienti. Hodnocení 4,8 z 35 recenzí na Firmy.cz.', body, 'reference.html')

# ================================================================== BLOG
def build_blog():
    first, rest = POSTS[0], POSTS[1:]
    feat = f'''<a href="@/blog/{first['slug']}.html" class="split post reveal" style="gap:var(--gap-lg)">
      <div class="post-media" style="aspect-ratio:4/3"><img src="@/{first['file']}" alt="" loading="eager"></div>
      <div><time datetime="{first['date']}">{czdate(first['date'])} · Nejnovější</time><h3 style="font-size:clamp(2rem,3.6vw,3.4rem);margin:.6rem 0 1rem">{esc(first['title'])}</h3><p style="-webkit-line-clamp:5">{esc(first['excerpt'])}</p><span class="link mt-md" style="display:inline-flex">Číst článek {ARR}</span></div></a>'''
    grid = ''.join(post_card(p, '@/', k) for k, p in enumerate(rest))
    body = f'''
<section class="phero">
  {ripples()}
  <div class="container">
    <nav class="crumbs"><a href="@/index.html">Domů</a><span>Blog</span></nav>
    <p class="label fade-up" style="--d:.1s">Blog</p>
    <h1 class="words" style="max-width:12ch">{words('Novinky ze\n_světa realit_')[0]}</h1>
    <p class="lead fade-up" style="--d:.8s">Daně, nájmy, legislativa i zamyšlení z praxe. Píšu srozumitelně — tak, jak bych to vysvětloval u vás v kuchyni.</p>
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
    write('blog.html', 'Blog — novinky ze světa realit | Tomáš Veigl',
          'Články realitního makléře Tomáše Veigla: daň z prodeje nemovitosti, zvyšování nájmu, stavební dokumentace, PENB a další.', body, 'blog.html')
    for k, p in enumerate(POSTS):
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
<figure class="article-cover clip-reveal"><img src="@/{p.get('file','')}" alt="" fetchpriority="high"></figure>
<section class="section" style="padding-top:var(--gap-lg)">
  <div class="narrow prose">{prose(p['body'], 'h2')}</div>
  <div class="narrow mt-xl" style="border-top:1px solid var(--line);padding-top:var(--gap-md)">
    <div class="sig"><img src="@/img/site/portrait.webp" alt="" style="background:var(--accent)"><span><b>Máte k tématu otázku?</b><small>Zavolejte mi na <a class="link-u" href="{TEL_H}">{TEL}</a> — rád poradím.</small></span></div>
  </div>
</section>
<section class="section bg-alt">
  <div class="container">
    <div class="sec-head"><div><p class="label reveal">Blog</p><h2 class="reveal">Další <em>články</em></h2></div><a href="@/blog.html" class="link reveal">Všechny články {ARR}</a></div>
    <div class="grid-list">{''.join(post_card(q, '@/', i) for i, q in enumerate(rel))}</div>
  </div>
</section>
'''
        write(f'blog/{p["slug"]}.html', f'{p["title"]} | Tomáš Veigl', p['excerpt'][:155], body, 'blog.html', 'dark', p.get('file', ''))

# ================================================================== ODHAD
def build_estimate():
    h1, _ = words('Kolik má váš domov\n_hodnotu_?')
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
      <p class="lead-quote reveal">Umění nastavit cenu tak, abyste za prodej dostali maximum, je ve zkušenostech. Online kalkulačka vám dá číslo. Já vám dám cenu.</p>
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
      <p class="form-ok">Děkuji! Ozvu se vám do 24 hodin. — Tomáš</p>
    </div>
    <aside class="dside">
      <div class="agent-card">
        {ripples()}
        <div class="who"><img src="@/img/site/portrait.webp" alt=""><span><b>Raději osobně?</b><small>Zavolejte, nebo si vyberte termín</small></span></div>
        <a class="tel link-u" href="{TEL_H}">{TEL}</a>
        <a class="mail link-u" href="mailto:{MAIL}">{MAIL}</a>
        {btn(CAL, 'Online schůzka', 'btn--light', ext=True)}
      </div>
      <div class="prose" style="font-size:.95rem;color:var(--muted)">
        <p>Nikdy nenajdete dvě stejné nemovitosti. Často působí podobně, ale liší se v hromadě detailů.</p>
        <p>Díky zkušenostem vím, na co se zaměřit, jak vyzdvihnout výhody a jak poctivě prezentovat nedostatky. Proto se mi daří prodávat za tu nejvýhodnější cenu.</p>
      </div>
    </aside>
  </div>
</section>
'''
    write('odhad-ceny.html', 'Odhad ceny nemovitosti zdarma | Tomáš Veigl',
          'Nezávazný odhad ceny domu, bytu nebo pozemku od zkušeného makléře. Hradec Králové, Pardubice, Kutná Hora, Kolín.', body, 'odhad-ceny.html')

# ================================================================== KONTAKT
def build_contact():
    h1, _ = words('Ozvěte se.\n_Slyším_ vás.')
    q = 'https://www.google.com/maps?q=' + 'T%C5%99%C3%ADda+Edvarda+Bene%C5%A1e+1526%2F78%2C+Hradec+Kr%C3%A1lov%C3%A9' + '&output=embed'
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
      <small class="reveal" style="margin-top:0">Telefon</small><a class="cb reveal" href="{TEL_H}">{TEL}</a>
      <small class="reveal">E-mail</small><a class="cb reveal" href="mailto:{MAIL}" style="font-size:clamp(1.8rem,4vw,3.6rem)">{MAIL}</a>
      <small class="reveal">Kancelář</small><p class="reveal" style="font-size:1.15rem">{ADDR}</p>
      <div class="row mt-lg reveal">{btn(CAL, 'Online schůzka', '', True, ext=True)}{btn('@/odhad-ceny.html', 'Odhad ceny', 'btn--ghost')}</div>
      <div class="mt-xl">
        <div class="person reveal"><img src="@/img/site/portrait.webp" alt=""><span><b>Mgr. Tomáš Veigl</b><br><small class="muted">Realitní makléř · {TEL} · {MAIL}</small></span></div>
        <div class="person reveal"><span style="width:58px;height:58px;border-radius:50%;background:var(--bg-alt);display:grid;place-items:center;font-family:var(--font-display);font-size:1.5rem;flex:none">RV</span><span><b>Radka Veiglová</b><br><small class="muted">Asistentka · <a class="link-u" href="tel:+420737143908">+420 737 143 908</a> · <a class="link-u" href="mailto:radka@tomasveigl.cz">radka@tomasveigl.cz</a></small></span></div>
        <div class="row reveal mt-md" style="gap:1.4rem"><a class="link" href="https://www.facebook.com/realityveigl" target="_blank" rel="noopener">Facebook</a><a class="link" href="https://www.instagram.com/realitak_s_kochleary" target="_blank" rel="noopener">Instagram</a><a class="link" href="https://www.linkedin.com/in/mgr-tom%C3%A1%C5%A1-veigl/" target="_blank" rel="noopener">LinkedIn</a></div>
      </div>
    </div>
    <div>
      <div class="map clip-reveal"><iframe src="{q}" loading="lazy" title="Mapa — kancelář Hradec Králové" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
      <form class="form mt-lg reveal" data-demo>
        <div class="field"><label for="cj">Jméno</label><input id="cj" autocomplete="name" required></div>
        <div class="field"><label for="ct">Telefon</label><input id="ct" type="tel" autocomplete="tel" required></div>
        <div class="field full"><label for="cz">Zpráva</label><textarea id="cz" placeholder="Co plánujete? Prodej, pronájem, koupě…"></textarea></div>
        <div class="full row" style="justify-content:space-between"><p class="form-note">Ozvu se obvykle do několika hodin.</p><button type="submit" class="btn">Odeslat <span class="arr">{ARR}</span></button></div>
      </form>
      <p class="form-ok">Děkuji za zprávu, brzy se vám ozvu. — Tomáš</p>
    </div>
  </div>
</section>
<section class="section dark" style="padding-block:var(--gap-xl)">
  <div class="container row" style="justify-content:space-between;gap:2rem">
    <p class="reveal" style="font-family:var(--font-display);font-size:clamp(1.8rem,3.4vw,3rem);line-height:1.15;max-width:24ch">Slyším díky technice, <em style="color:#73C7D2">rozumím díky srdci</em>.</p>
    <div class="reveal" style="color:#73C7D2;width:min(420px,100%)">{wave(60, 17, True)}</div>
  </div>
</section>
'''
    write('kontakt.html', 'Kontakt — Tomáš Veigl, realitní makléř Hradec Králové',
          f'Zavolejte {TEL}, napište na {MAIL} nebo si domluvte online schůzku. Kancelář: {ADDR}.', body, 'kontakt.html')

# ================================================================== 404
def build_404():
    body = f'''<section class="phero" style="min-height:80svh">{ripples()}<div class="container"><p class="label">404</p><h1>Tady je <em>ticho</em>.</h1><p class="lead mt-md">Tahle stránka neexistuje. Ale já vás slyším — zkuste to přes úvodní stránku.</p><div class="mt-lg">{btn('@/index.html', 'Zpět domů')}</div></div></section>'''
    write('404.html', 'Stránka nenalezena | Tomáš Veigl', 'Stránka nenalezena.', body)

if __name__ == '__main__':
    build_home(); build_story(); build_process(); build_listing(); build_details()
    build_services(); build_reference(); build_blog(); build_estimate(); build_contact(); build_404()
    print(f'{len(PAGES)} pages built')
