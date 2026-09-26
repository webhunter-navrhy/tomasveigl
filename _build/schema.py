"""Content schema for the admin — every editable text, image and list on the site.

Each page groups sections; each section holds fields:
  F(key, label, kind, default, hint)          kinds: text | md | textarea | image | url
  L(key, label, item_fields, default, title)  repeatable list (item_fields = [(name, label, kind)])
md: *kurzíva v barvě*, **tučně**, ~tlumeně~, nový řádek = zalomení
textarea: odstavce oddělené prázdným řádkem, uvnitř funguje totéž co md
"""

def F(key, label, kind='text', default='', hint=''):
    return {'key': key, 'label': label, 'kind': kind, 'default': default, 'hint': hint}

def L(key, label, fields, default, title='title', hint=''):
    return {'key': key, 'label': label, 'kind': 'list', 'fields': [{'name': n, 'label': l, 'kind': k} for n, l, k in fields],
            'default': default, 'title': title, 'hint': hint}

MD = 'Slovo v *hvězdičkách* se zvýrazní kurzívou v barvě, **dvě hvězdičky** = tučně.'
H1 = 'Nový řádek nadpisu = Enter. Slovo v *hvězdičkách* se zvýrazní.'

SCHEMA = [
 {'id': 'general', 'title': 'Kontakty a firma', 'icon': 'contact', 'sections': [
  {'title': 'Kontaktní údaje', 'fields': [
    F('contact.phone', 'Telefon', default='+420 737 132 041'),
    F('contact.email', 'E-mail', default='reality@tomasveigl.cz'),
    F('contact.address', 'Adresa kanceláře', default='Třída Edvarda Beneše 1526/78, Hradec Králové'),
    F('contact.ic', 'IČ', default='684 56 255'),
    F('contact.calendar', 'Odkaz na online schůzku (Google kalendář)', 'url', 'https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2FVFpnfyA8WAejvXm4w3nQwt5CBjg56ZaEEC5JL69R0093WGU7qkEl2kyTliHDKM-0qVM6m2pB'),
  ]},
  {'title': 'Asistentka', 'fields': [
    F('contact.assistant_name', 'Jméno', default='Radka Veiglová'),
    F('contact.assistant_role', 'Role', default='Asistentka'),
    F('contact.assistant_phone', 'Telefon', default='+420 737 143 908'),
    F('contact.assistant_email', 'E-mail', default='radka@tomasveigl.cz'),
  ]},
  {'title': 'Sociální sítě a odkazy', 'fields': [
    F('contact.facebook', 'Facebook', 'url', 'https://www.facebook.com/realityveigl'),
    F('contact.instagram', 'Instagram', 'url', 'https://www.instagram.com/realitak_s_kochleary'),
    F('contact.linkedin', 'LinkedIn', 'url', 'https://www.linkedin.com/in/mgr-tom%C3%A1%C5%A1-veigl/'),
    F('contact.reality11', 'Reality 11', 'url', 'https://www.reality11.cz/'),
    F('contact.najem', 'Pronájem s radostí (web)', 'url', 'https://najemsradosti.cz/'),
    F('contact.vykup', 'Klidné řešení — výkup (web)', 'url', 'https://klidnereseni.cz/'),
  ]},
  {'title': 'Hodnocení', 'fields': [
    F('rating.value', 'Průměrné hodnocení', default='4,8', hint='Zobrazuje se v horní liště, na úvodu i v referencích.'),
    F('rating.count', 'Počet hodnocení', default='35'),
    F('rating.source', 'Zdroj hodnocení', default='Firmy.cz'),
    F('rating.url', 'Odkaz na všechna hodnocení', 'url', 'https://www.firmy.cz/detail/13326397-tomasveigl-cz-slysim-vas-domov-hradec-kralove-novy-hradec-kralove.html'),
  ]},
  {'title': 'Horní lišta a patička', 'fields': [
    L('topbar.items', 'Texty v horní liště', [('title', 'Text', 'text')],
      [{'title': 'Zlatý člen Realitní komory ČR'}, {'title': 'Realiťák roku 2023 · 2. místo, okres HK'}]),
    F('footer.text', 'Text v patičce', 'textarea', 'Realitní makléř z Hradce Králové. Slyším díky technice, rozumím díky srdci.'),
    F('footer.giant', 'Velký nápis v patičce', default='Slyším váš domov'),
    F('footer.legal', 'Právní řádek', default='Mgr. Tomáš Veigl · Powered by REALITY 11 · Fyzická osoba zapsaná v živnostenském rejstříku'),
    L('footer.docs', 'Dokumenty v patičce', [('title', 'Název', 'text'), ('url', 'Odkaz (PDF)', 'url')], [
      {'title': 'GDPR', 'url': 'https://www.tomasveigl.cz/wp-content/uploads/2025/05/informace_o_ochrane_osobnich_udaju_-_gdpr.pdf'},
      {'title': 'Reklamační řád', 'url': 'https://www.tomasveigl.cz/wp-content/uploads/2025/05/reklamacni_rad.pdf'},
      {'title': 'Oznamovací systém', 'url': 'https://www.tomasveigl.cz/wp-content/uploads/2025/05/informace_o_vnitrnim_oznamovacim_systemu.pdf'},
      {'title': 'Vnitřní zásady', 'url': 'https://www.tomasveigl.cz/wp-content/uploads/2025/05/system_vnitrnich_zasad.pdf'}]),
  ]},
  {'title': 'Výzva k odhadu ceny (tmavý blok dole na stránkách)', 'fields': [
    F('cta.label', 'Štítek', default='Odhad ceny zdarma'),
    F('cta.title', 'Nadpis', 'md', 'Kolik má váš domov *hodnotu*?', MD),
    F('cta.text', 'Text', 'md', 'Nezávazně a zdarma. Přijedu, poslechnu si, co od prodeje čekáte, a řeknu vám reálnou cenu — ne číslo z kalkulačky.'),
    F('cta.btn', 'Tlačítko', default='Chci odhad ceny'),
  ]},
  {'title': 'Partneři („Bezpečný obchod“)', 'fields': [
    F('partners.label', 'Štítek', default='Bezpečný obchod'),
    F('partners.title', 'Nadpis', 'md', 'Za každým obchodem stojí *ověření* partneři', MD),
    F('partners.lead', 'Text', 'md', 'Smlouvy připravuje ABES nebo advokátní kancelář Rezek – Petráš, peníze putují přes úschovu UniCredit Bank a vaši nemovitost uvidí lidé na největších realitních portálech.'),
    L('partners.items', 'Partneři', [('title', 'Název', 'text'), ('image', 'Logo', 'image'), ('caption', 'Popisek', 'text'), ('url', 'Odkaz', 'url')], [
      {'title': 'Reality 11', 'image': 'img/site/r11-dark.png', 'caption': 'Realitní síť', 'url': 'https://www.reality11.cz/'},
      {'title': 'Realitní komora ČR', 'image': 'img/partners/rkcr.png', 'caption': 'Zlatý člen', 'url': ''},
      {'title': 'ABES', 'image': 'img/partners/abes.png', 'caption': 'Právní servis', 'url': ''},
      {'title': 'Rezek – Petráš', 'image': 'img/partners/rezek.png', 'caption': 'Advokátní kancelář', 'url': ''},
      {'title': 'UniCredit Bank', 'image': 'img/partners/unicredit.png', 'caption': 'Úschova peněz', 'url': 'https://www.unicreditbank.cz/'},
      {'title': 'Sreality', 'image': 'img/partners/sreality.png', 'caption': 'Inzerce', 'url': 'https://www.sreality.cz/'},
      {'title': 'Reality iDNES', 'image': 'img/partners/idnes.png', 'caption': 'Inzerce', 'url': 'https://reality.idnes.cz/'},
      {'title': 'České reality', 'image': 'img/partners/ceskereality.png', 'caption': 'Inzerce', 'url': 'https://www.ceskereality.cz/'}]),
  ]},
 ]},

 {'id': 'home', 'title': 'Úvodní stránka', 'icon': 'home', 'sections': [
  {'title': 'Vyhledávače (SEO)', 'fields': [
    F('home.seo_title', 'Titulek stránky', default='Tomáš Veigl — realitní makléř, Hradec Králové | Slyším váš domov'),
    F('home.seo_desc', 'Popis pro Google', 'textarea', 'Realitní makléř Mgr. Tomáš Veigl — prodej, pronájem a výkup nemovitostí v Hradci Králové, Pardubicích, Kutné Hoře a Kolíně. 200+ prodaných nemovitostí, hodnocení 4,8.'),
  ]},
  {'title': 'Úvod (první obrazovka)', 'fields': [
    F('home.hero_label', 'Štítek nad nadpisem', default='Realitní makléř · Hradec Králové'),
    F('home.hero_title', 'Hlavní nadpis', 'md', 'Slyším\n*váš* domov.', H1),
    F('home.hero_sub', 'Text pod nadpisem', 'md', 'Jsem Tomáš Veigl. Prodávám a pronajímám domy, byty i chalupy ve východních Čechách. Díky kochleárnímu implantátu jsem se znovu naučil slyšet — a hlavně **naslouchat**. Vám i vašemu domovu.', MD),
    F('home.hero_cta', 'Hlavní tlačítko', default='Odhad ceny zdarma'),
    F('home.hero_link', 'Odkaz vedle tlačítka', default='Nemovitosti v nabídce'),
    F('home.hero_image', 'Portrét (PNG bez pozadí)', 'image', 'img/site/portrait.webp', 'Nejlépe fotka s průhledným pozadím.'),
    F('home.hero_tag_title', 'Plovoucí štítek — tučně', default='200+ prodaných'),
    F('home.hero_tag_text', 'Plovoucí štítek — text', default='nemovitostí za 10 let'),
    L('home.marquee', 'Běžící pás pod úvodem', [('title', 'Slovo', 'text')],
      [{'title': w} for w in ['Hradec Králové', 'Pardubice', 'Kutná Hora', 'Kolín', 'Praha-východ', 'Prodej', 'Pronájem a správa', 'Výkup', 'Odhad ceny zdarma']]),
  ]},
  {'title': 'Rozcestník „S čím přicházíte?“', 'fields': [
    F('home.intents_label', 'Štítek', default='S čím přicházíte?'),
    L('home.intents', 'Položky', [('title', 'Název', 'text'), ('text', 'Popis', 'text'), ('link', 'Odkaz', 'url')], [
      {'title': 'Chci prodat', 'text': 'Odhad ceny zdarma a prodej za nejvyšší možnou cenu.', 'link': 'odhad-ceny.html'},
      {'title': 'Chci pronajmout', 'text': 'Pronájem s radostí — garance nájmu až 600 000 Kč.', 'link': 'sluzby.html#pronajem'},
      {'title': 'Hledám bydlení', 'text': 'Domy, byty, chalupy a novostavby v nabídce.', 'link': 'nemovitosti.html'},
      {'title': 'Potřebuji to rychle', 'text': 'Rozvod, dluhy, dědictví? Výkup nebo chytrý prodej.', 'link': 'sluzby.html#vykup'}]),
  ]},
  {'title': 'Co ode mě čekat', 'fields': [
    F('home.statement_label', 'Štítek', default='Co ode mě čekat'),
    F('home.statement', 'Velký text', 'md', 'Cílím na *nejvyšší možnou cenu*, ne na nejrychlejší podpis. ~Co si domluvíme, to platí.~ Ozvu se, když to slíbím. A protože vím přesně, co zařídit, ~nestřílím naslepo~ — šetřím váš čas i nervy.', MD + ' ~Vlnovky~ = šedě ztlumený text.'),
    L('home.pillars', 'Tři pilíře', [('title', 'Nadpis', 'text'), ('text', 'Text', 'text')], [
      {'title': 'Lepší cena', 'text': 'Vždy cílím na nejvyšší možnou cenu, i když to chce špičkovou přípravu a pořádnou porci času.'},
      {'title': 'Spolehlivost', 'text': 'Ozývám se, jak jsem slíbil, plním, co očekáváte — a vždy jednám ve vašem zájmu.'},
      {'title': 'Úspora času', 'text': 'Vím, co a jak zařídit, aby prodej proběhl bezpečně a s požadovaným výsledkem.'}]),
    F('home.sig_name', 'Podpis — jméno', default='Mgr. Tomáš Veigl'),
    F('home.sig_role', 'Podpis — role', default='Realitní makléř · Powered by reality11 · zlatý člen RK ČR'),
  ]},
  {'title': 'Hlavní nemovitost (velká fotka)', 'fields': [
    F('home.feature_slug', 'Která nemovitost', 'listing', 'rodinny-dum-4kk-vinary-u-noveho-bydzova', 'Vyberte nemovitost, která se ukáže přes celou šířku.'),
    F('home.feature_image', 'Fotka na pozadí', 'image', 'img/nem/rodinny-dum-4kk-vinary-u/f05.webp'),
    F('home.feature_label', 'Štítek', default='Právě připravujeme'),
    F('home.feature_title', 'Nadpis', 'md', 'Dům, kam se *budete těšit* celý týden.', MD),
    F('home.feature_text', 'Krátký popis v kartě', 'textarea', 'Kompletně zrekonstruovaný interiér, tepelné čerpadlo, podlahové topení a zahrada, kde nemusíte počítat každý metr.'),
    F('home.feature_btn', 'Tlačítko', default='Prohlédnout dům'),
  ]},
  {'title': 'Aktuální nabídka', 'fields': [
    F('home.offers_label', 'Štítek', default='Aktuální nabídka'),
    F('home.offers_title', 'Nadpis', 'md', 'Domovy, které *hledají* nové lidi', MD + ' Které nemovitosti se zde ukážou, nastavíte u nemovitosti přepínačem „Na úvodní stránce“.'),
    F('home.sold_text', 'Text nad pásem prodaných', default='{n} domovů na tomhle webu už má nové majitele nebo nájemníky.', hint='{n} se nahradí skutečným počtem prodaných a pronajatých.'),
    F('home.sold_link', 'Odkaz u prodaných', default='Prodané a pronajaté'),
  ]},
  {'title': 'Můj příběh (tmavá sekce)', 'fields': [
    F('home.story_label', 'Štítek', default='Můj příběh'),
    F('home.story_title', 'Nadpis', 'md', 'Proč umím *naslouchat* lépe než ostatní?', MD),
    F('home.story_image', 'Fotka', 'image', 'img/site/telefon.webp'),
    F('home.story_caption', 'Popisek fotky', default='Hradec Králové, můj domov'),
    L('home.story_lines', 'Věty, které se „vyjasňují“', [('title', 'Velká věta', 'md'), ('text', 'Menší text pod ní', 'textarea')], [
      {'title': 'Kariéru v realitách jsem začal s horším sluchem. Svět ale časem *utichal* čím dál víc.', 'text': 'Vyvinula se u mě těžká percepční ztráta sluchu. Pro makléře, pro kterého je komunikace vším, to bylo jako prodávat se zavázanýma očima.'},
      {'title': 'Pak přišel *kochleární implantát*. A s ním se vrátil zvuk.', 'text': 'Implantát obchází poškozené části ucha a posílá signál přímo do sluchového nervu. Vrátil mi sluch — a mnohem víc než jen to.'},
      {'title': 'Kdo jednou ztratil sluch, začne *doopravdy naslouchat*.', 'text': 'Nejen ušima, ale hlavně srdcem. Proto slyším i to, co klienti neříkají nahlas: obavy, přání a to, co pro ně domov znamená.'}]),
    L('home.stats', 'Čísla', [('num', 'Číslo', 'text'), ('suffix', 'Přípona (+, let, ★…)', 'text'), ('text', 'Popisek', 'text')], [
      {'num': '200', 'suffix': '+', 'text': 'prodaných a pronajatých nemovitostí'},
      {'num': '10', 'suffix': 'let', 'text': 'zkušeností v realitách'},
      {'num': '4,8', 'suffix': '★', 'text': 'průměrné hodnocení z 35 recenzí'},
      {'num': '2', 'suffix': '. místo', 'text': 'Realiťák roku 2023, okres Hradec Králové'}], title='num'),
  ]},
  {'title': 'Služby', 'fields': [
    F('home.services_label', 'Štítek', default='Služby'),
    F('home.services_title', 'Nadpis', 'md', 'S čím vám *pomůžu*', MD),
    F('home.services_lead', 'Text', 'md', 'Prodej je jen začátek. Postarám se i o pronájem, výkup nebo stavbu nového domu — vždycky s jedním člověkem na telefonu.'),
    L('home.services', 'Služby', [('title', 'Název', 'text'), ('text', 'Popis', 'text'), ('link', 'Odkaz', 'url'), ('image', 'Obrázek (při najetí myší)', 'image')], [
      {'title': 'Prodej nemovitosti', 'text': 'Od úvodní schůzky přes profi fotky, video, dron a 3D scan až po předání klíčů a přepis energií. 21 kroků, nic nechybí.', 'link': 'jak-pracuji.html', 'image': 'img/site/street.webp'},
      {'title': 'Pronájem a správa', 'text': 'Pronájem s radostí: opravy 24/7, garance nájmu až 600 000 Kč a právní asistence po celé republice.', 'link': 'sluzby.html#pronajem', 'image': 'img/site/najem.webp'},
      {'title': 'Výkup nemovitosti', 'text': 'Klidné řešení pro rozvod, dluhy nebo dědictví. Rychle, férově a bez zbytečného čekání.', 'link': 'sluzby.html#vykup', 'image': 'img/site/klidne.webp'},
      {'title': 'Novostavby na klíč', 'text': 'Nízkoenergetické domy PURLIVE v Hradci, Pardubicích, Kolíně i Kutné Hoře — od 1,3 mil. Kč.', 'link': 'sluzby.html#novostavby', 'image': 'img/nem/novostavbakolin/f00.webp'},
      {'title': 'Odhad ceny zdarma', 'text': 'Zkušenost, ne kalkulačka. Řeknu vám, za kolik se vaše nemovitost reálně prodá — a proč.', 'link': 'odhad-ceny.html', 'image': 'img/site/dron1.webp'}]),
  ]},
  {'title': 'Reference', 'fields': [
    F('home.reviews_label', 'Štítek', default='Reference'),
    F('home.quote', 'Velká citace', 'md', 'Hledáte makléře, kterému na klientech *opravdu záleží*? Pan Veigl je ta nejlepší volba.', MD),
    F('home.quote_name', 'Autor citace', default='Aneta Lišková'),
    F('home.quote_meta', 'Zdroj a datum', default='Firmy.cz · 07.05.2026'),
  ]},
  {'title': 'Kde působím', 'fields': [
    F('home.regions_label', 'Štítek', default='Kde působím'),
    F('home.regions_title', 'Nadpis', 'md', 'Znám to tu *jako své boty*', MD),
    F('home.regions_lead', 'Text', 'md', 'Mám přehled o vývoji cen ve východních Čechách a díky zkušenostem vím, jak vám tady zajistit nejvýhodnější prodej. Ale klidně přijedu kamkoli v Česku.'),
    L('home.regions', 'Oblasti', [('title', 'Oblast', 'text'), ('text', 'Města', 'text')], [
      {'title': 'Královéhradecko', 'text': 'HK · Nový Bydžov · Rychnov'}, {'title': 'Pardubicko', 'text': 'Pardubice · Přelouč · Chrudim'},
      {'title': 'Kutnohorsko', 'text': 'Kutná Hora · Čáslav'}, {'title': 'Kolínsko', 'text': 'Kolín · Velim'}, {'title': 'Praha-východ', 'text': 'a celá ČR'}]),
  ]},
  {'title': 'Blog na úvodní stránce', 'fields': [
    F('home.blog_label', 'Štítek', default='Blog'),
    F('home.blog_title', 'Nadpis', 'md', 'Novinky ze *světa realit*', MD),
  ]},
 ]},

 {'id': 'story', 'title': 'Můj příběh', 'icon': 'user', 'sections': [
  {'title': 'Vyhledávače (SEO)', 'fields': [
    F('story.seo_title', 'Titulek stránky', default='Můj příběh — Tomáš Veigl | Slyším váš domov'),
    F('story.seo_desc', 'Popis pro Google', 'textarea', 'Realitní makléř s kochleárním implantátem. Příběh Tomáše Veigla o tom, proč umí naslouchat lépe než ostatní.'),
  ]},
  {'title': 'Úvod', 'fields': [
    F('story.hero_title', 'Nadpis', 'md', 'Slyším díky technice.\n*Rozumím* díky srdci.', H1),
    F('story.hero_lead', 'Text', 'md', 'Realitní makléř, ale také veselý člověk, manžel a táta. A člověk, který ví, jaké to je, když svět zničehonic ztichne.'),
    F('story.hero_image', 'Fotka', 'image', 'img/site/whatsapp1.webp'),
  ]},
  {'title': 'Proč umím naslouchat (tmavá sekce)', 'fields': [
    F('story.dark_label', 'Štítek', default='Proč umím naslouchat'),
    F('story.dark_title', 'Nadpis', 'md', 'Od *ticha* ke každému slovu.', MD),
    F('story.dark_lead', 'Text', 'md', 'Scrollujte pomalu. Tak nějak to znělo, když se mi sluch vracel.'),
    L('story.lines', 'Věty, které se „vyjasňují“', [('title', 'Velká věta', 'md'), ('text', 'Menší text', 'textarea')], [
      {'title': 'Svou kariéru v realitách jsem začal s horším sluchem. V průběhu let se ale vyvinula *těžká percepční ztráta* sluchu.', 'text': 'Neuvěřitelně mi to ztížilo práci. Pro realitního makléře je komunikace vším — musím rozumět klientům, jednat jejich jménem a vysvětlit každý důležitý detail o nemovitosti. Ztráta sluchu mi bránila poskytovat služby, na které jsem byl zvyklý.'},
      {'title': 'Rozhodl jsem se pro operaci *kochleárního implantátu*. Změnila mi život.', 'text': 'Kochleární implantát obchází poškozené části ucha a posílá elektrické signály přímo do sluchového nervu. Implantát mi vrátil sluch — a nejen to.'},
      {'title': 'Protože vím, jaké je o sluch přijít, *vnímám víc*. Okolí, lidi i to, co mi klienti opravdu říkají.', 'text': 'Díky kochleární technologii mohu znovu naplno komunikovat. Implantát vrátil mou kariéru na správnou cestu — a mně dal schopnost pozorně naslouchat přesně tomu, co moji klienti chtějí.'}]),
    L('story.timeline', 'Časová osa', [('title', 'Rok / etapa', 'text'), ('text', 'Popis', 'text')], [
      {'title': 'Začátky', 'text': 'První obchody v realitách — už tehdy s horším sluchem.'},
      {'title': 'Ticho', 'text': 'Těžká percepční ztráta sluchu. Každý telefonát je boj.'},
      {'title': 'Implantát', 'text': 'Operace, která mi vrátila zvuk — i chuť do práce.'},
      {'title': '2023', 'text': '2. místo v soutěži Realiťák roku, okres Hradec Králové.'},
      {'title': '2024', 'text': '3. místo v soutěži Realiťák roku, okres Hradec Králové.'}]),
  ]},
  {'title': 'Kdo jsem (rodina)', 'fields': [
    F('story.family_label', 'Štítek', default='Kdo jsem'),
    F('story.family_title', 'Nadpis', 'md', 'Realitní makléř, ale také *veselý člověk*, manžel a táta', MD),
    F('story.family_image', 'Fotka', 'image', 'img/site/rodina.webp'),
    F('story.family_text', 'Text', 'textarea', 'Nejen prací živ je člověk. Kromě toho, že jsem realiťák, jsem hlavně člověk z masa a kostí. Volný čas se snažím co nejvíc trávit s rodinou.\n\nS dcerou Natálkou jezdíme na kole a koloběžce a lyžujeme. Doma máme dva psy — Coru (maďarský ohař) a Kyru (německý ohař), se kterými trávíme čas na louce nebo na procházkách v lese.\n\nV práci mi pomáhá manželka **Radka Veiglová** jako asistentka. Takže když voláte nám, voláte vlastně rodinné firmě.', 'Odstavce oddělte prázdným řádkem.'),
    F('story.family_quote', 'Závěrečná věta', 'md', 'Nuda? Tak to u nás *absolutně* nehledejte.'),
  ]},
  {'title': 'Ocenění a vzdělávání', 'fields': [
    F('story.awards_label', 'Štítek', default='Ocenění a vzdělávání'),
    F('story.awards_title', 'Nadpis', 'md', 'Proč se účastním *Realiťáka roku*?', MD),
    F('story.awards_image', 'Obrázek', 'image', 'img/site/certifikaty.webp'),
    F('story.awards_text', 'Text', 'textarea', 'Věřím, že kvalitní práce si zaslouží být vidět. Soutěž mě motivuje se neustále zlepšovat a posouvat dál — a je úzce propojená se vzděláváním. Mám díky ní přístup k aktuálním trendům, novinkám v legislativě a zkušenostem od špiček v oboru.\n\nV pravidelných rozhovorech Realiťáka roku můžete nahlédnout do mého přístupu k realitám: co mě motivuje, jak pracuji s klienty a proč mě tahle práce opravdu baví.'),
    L('story.badges', 'Odznaky', [('title', 'Velký text', 'text'), ('text', 'Popisek', 'textarea')], [
      {'title': '2.', 'text': 'místo · Realiťák roku 2023\nokres Hradec Králové'},
      {'title': '3.', 'text': 'místo · Realiťák roku 2024\nokres Hradec Králové'},
      {'title': 'Zlatý', 'text': 'člen Realitní komory\nČeské republiky'}]),
  ]},
  {'title': 'Výzva na konci stránky', 'fields': [
    F('story.cta_title', 'Nadpis', 'md', 'Pojďme si *promluvit*.', MD),
    F('story.cta_text', 'Text', 'md', 'Rád si vyslechnu, co plánujete. Osobně u vás, v kanceláři v Hradci Králové nebo online — jak je vám to příjemnější.'),
  ]},
 ]},

 {'id': 'process', 'title': 'Jak pracuji', 'icon': 'steps', 'sections': [
  {'title': 'Vyhledávače (SEO)', 'fields': [
    F('process.seo_title', 'Titulek stránky', default='Jak pracuji — 21 kroků k prodanému domovu | Tomáš Veigl'),
    F('process.seo_desc', 'Popis pro Google', 'textarea', 'Od úvodní schůzky přes vizualizace, dron, 3D scan a portály až po předání a přepis energií. Kompletní servis realitního makléře Tomáše Veigla.'),
  ]},
  {'title': 'Úvod', 'fields': [
    F('process.hero_title', 'Nadpis', 'md', '{n} kroků\nk *prodanému* domovu', H1 + ' {n} = počet kroků.'),
    F('process.hero_lead', 'Text', 'md', 'Prodej nemovitosti není inzerát a čekání. Je to řemeslo. Tady je všechno, co pro vás udělám — od první kávy u vás v kuchyni až po přepis energií.'),
    F('process.aside_btn', 'Tlačítko vedle kroků', default='Chci začít krokem 1'),
  ]},
  {'title': 'Kroky', 'fields': [
    L('process.steps', 'Kroky prodeje', [('phase', 'Fáze (nadpis skupiny)', 'text'), ('title', 'Název kroku', 'text'), ('text', 'Popis', 'textarea'), ('image', 'Obrázek (nepovinný)', 'image'), ('contain', 'Obrázek celý (logo, dokument)', 'bool')], [], hint='Kroky se automaticky číslují. Stejná fáze za sebou = jedna skupina.'),
  ]},
  {'title': 'Výzva na konci stránky', 'fields': [
    F('process.cta_title', 'Nadpis', 'md', 'Začneme *krokem jedna*?', MD),
    F('process.cta_text', 'Text', 'md', 'Úvodní schůzka je nezávazná. Přijedu, prohlédnu si nemovitost a řeknu vám, jak bych ji prodával — a za kolik.'),
  ]},
 ]},

 {'id': 'listing', 'title': 'Stránka Nemovitosti', 'icon': 'grid', 'sections': [
  {'title': 'Vyhledávače (SEO)', 'fields': [
    F('listing.seo_title', 'Titulek stránky', default='Nemovitosti v nabídce — Tomáš Veigl, realitní makléř'),
    F('listing.seo_desc', 'Popis pro Google', 'textarea', 'Aktuální nabídka domů, bytů, chalup a novostaveb ve východních Čechách i reference prodaných a pronajatých nemovitostí.'),
  ]},
  {'title': 'Úvod a texty', 'fields': [
    F('listing.hero_title', 'Nadpis', 'md', 'Domy, byty a chalupy,\nkteré *hledají* nové lidi', H1),
    F('listing.hero_lead', 'Text', 'md', 'Aktuální nabídka i to, co už má nové majitele. Každá nemovitost dostala vlastní prezentaci, fotky, půdorysy a péči.'),
    F('listing.empty', 'Text, když filtr nic nenajde', 'md', 'V této kombinaci teď nic nemám. Ale ozvěte se — často vím o nemovitostech dřív, než jdou na portály.'),
    F('listing.cta_title', 'Výzva dole — nadpis', 'md', 'Hledáte, co *tu není*?', MD),
    F('listing.cta_text', 'Výzva dole — text', 'md', 'Řekněte mi, co hledáte. Často vím o nemovitostech dřív, než se objeví na portálech — a rád vám dám vědět jako prvnímu.'),
  ]},
  {'title': 'Karta „Tady je místo pro vaši nemovitost“', 'fields': [
    F('listing.card_label', 'Štítek', default='Prodáváte?'),
    F('listing.card_title', 'Nadpis', 'md', 'Tady je místo pro *vaši* nemovitost.', MD),
    F('listing.card_btn', 'Odkaz', default='Odhad ceny zdarma'),
  ]},
  {'title': 'Detail nemovitosti', 'fields': [
    F('detail.agent_sub', 'Text pod jménem makléře', default='Váš makléř pro tuto nemovitost'),
    F('detail.btn', 'Tlačítko', default='Domluvit prohlídku'),
    F('detail.viz_note', 'Poznámka k vizualizacím', default='Ilustrativní vizualizace možného budoucího řešení.'),
  ]},
 ]},

 {'id': 'services', 'title': 'Služby', 'icon': 'briefcase', 'sections': [
  {'title': 'Vyhledávače (SEO)', 'fields': [
    F('services.seo_title', 'Titulek stránky', default='Služby — prodej, pronájem, výkup a novostavby | Tomáš Veigl'),
    F('services.seo_desc', 'Popis pro Google', 'textarea', 'Prodej nemovitostí v 21 krocích, Pronájem s radostí s garancemi až 600 000 Kč, výkup Klidné řešení a novostavby PURLIVE.'),
  ]},
  {'title': 'Úvod', 'fields': [
    F('services.hero_title', 'Nadpis', 'md', 'Prodej, pronájem, výkup.\n*Klidně* a férově.', H1),
  ]},
  {'title': '01 — Prodej', 'fields': [
    F('services.sale_title', 'Nadpis', 'md', 'Prodám váš dům za *nejvyšší možnou* cenu', MD),
    F('services.sale_image', 'Fotka', 'image', 'img/site/dron2.webp'),
    F('services.sale_text', 'Text', 'textarea', 'Nestačí vyfotit pokoje a dát inzerát na portál. Každá nemovitost ode mě dostane strategii, profesionální fotky, video, dron, 3D scan, vizualizace, půdorysy, vlastní web, tištěný katalog i plachtu na plot.\n\nInzeráty TOPuji 2–3× týdně, smlouvy připravuje ABES nebo AK Rezek – Petráš a peníze putují přes úschovu UniCredit Bank. Po předání s vámi jdu přepsat i energie.'),
    L('services.sale_points', 'Body', [('title', 'Text', 'text'), ('text', 'Štítek', 'text')], [
      {'title': 'Profi fotky, video a dron', 'text': 'Prezentace'}, {'title': '3D scan a vizualizace', 'text': 'Prezentace'},
      {'title': 'Portály, sítě, plachty', 'text': 'Marketing'}, {'title': 'Právní servis a úschova', 'text': 'Bezpečnost'}]),
  ]},
  {'title': '02 — Pronájem s radostí', 'fields': [
    F('services.rent_title', 'Nadpis', 'md', 'My se staráme, *vy si užíváte* života', MD),
    F('services.rent_text', 'Text', 'md', 'Pronájem bez nočních telefonátů a strachu z neplatiče. Najdu spolehlivého nájemníka, postarám se o správu a vy máte garance, které běžný pronájem nenabízí.'),
    F('services.rent_image', 'Fotka', 'image', 'img/site/najem.webp'),
    L('services.guarantees', 'Garance', [('title', 'Částka / hodnota', 'text'), ('text', 'Popis', 'text')], [
      {'title': '600 000 Kč', 'text': 'zaplacení nájmu za nájemníka při nemoci nebo ztrátě zaměstnání'},
      {'title': '250 000 Kč', 'text': 'proplacení škod způsobených nájemníkem'},
      {'title': '100 000 Kč', 'text': 'proplacení dluhu při sporu s nájemcem kvůli nezaplacenému nájmu'},
      {'title': '24/7', 'text': 'opravy závad a havárií i právní asistence — po celé ČR'}]),
  ]},
  {'title': '03 — Výkup', 'fields': [
    F('services.buy_title', 'Nadpis', 'md', 'Výkup, když *čas* hraje roli', MD),
    F('services.buy_image', 'Fotka', 'image', 'img/site/klidne.webp'),
    F('services.buy_text', 'Text', 'textarea', 'Rozvod, dluhy, dědictví nebo nutnost rychle se stěhovat. Jsou situace, kdy je potřeba jednat opravdu rychle — a tehdy nabízím výkup nemovitosti.\n\nPovažuji ho za krajní, ale férové řešení. Nejdřív vám ale vysvětlím možnosti a pomůžu najít další postup. **Ne vždy je potřeba výkup. Někdy stačí dobře nastavený prodej.**'),
  ]},
  {'title': '04 — Novostavby', 'fields': [
    F('services.new_title', 'Nadpis', 'md', 'Nový dům *bez starostí* se stavbou', MD),
    F('services.new_text', 'Text', 'md', 'Nízkoenergetické dřevostavby systému PURLIVE ve stavu k dokončení. Ceny včetně 12% DPH.', 'Zobrazí se všechny nemovitosti typu Novostavba.'),
  ]},
 ]},

 {'id': 'reference', 'title': 'Stránka Reference', 'icon': 'star', 'sections': [
  {'title': 'Texty', 'fields': [
    F('reference.seo_title', 'Titulek stránky', default='Reference — {rating} z {count} hodnocení | Tomáš Veigl'),
    F('reference.seo_desc', 'Popis pro Google', 'textarea', 'Co o realitním makléři Tomáši Veiglovi říkají jeho klienti. Hodnocení {rating} z {count} recenzí na Firmy.cz.'),
    F('reference.hero_title', 'Nadpis', 'md', 'Co o mně *říkají* klienti', H1),
    F('reference.hero_lead', 'Text', 'md', 'Skutečná hodnocení z Firmy.cz — včetně mých odpovědí. Protože naslouchat znamená i odpovědět.'),
    F('reference.cta_title', 'Výzva dole — nadpis', 'md', 'Buďte můj další *spokojený* klient.', MD),
    F('reference.cta_text', 'Výzva dole — text', 'md', 'Rád pro vás udělám to samé. Stačí zavolat nebo si domluvit nezávazný odhad ceny.'),
  ]},
 ]},

 {'id': 'blogpage', 'title': 'Stránka Blog', 'icon': 'pen', 'sections': [
  {'title': 'Texty', 'fields': [
    F('blog.seo_title', 'Titulek stránky', default='Blog — novinky ze světa realit | Tomáš Veigl'),
    F('blog.seo_desc', 'Popis pro Google', 'textarea', 'Články realitního makléře Tomáše Veigla: daň z prodeje nemovitosti, zvyšování nájmu, stavební dokumentace, PENB a další.'),
    F('blog.hero_title', 'Nadpis', 'md', 'Novinky ze\n*světa realit*', H1),
    F('blog.hero_lead', 'Text', 'md', 'Daně, nájmy, legislativa i zamyšlení z praxe. Píšu srozumitelně — tak, jak bych to vysvětloval u vás v kuchyni.'),
    F('blog.question', 'Text pod článkem', default='Máte k tématu otázku?'),
  ]},
 ]},

 {'id': 'estimate', 'title': 'Odhad ceny', 'icon': 'calc', 'sections': [
  {'title': 'Texty', 'fields': [
    F('estimate.seo_title', 'Titulek stránky', default='Odhad ceny nemovitosti zdarma | Tomáš Veigl'),
    F('estimate.seo_desc', 'Popis pro Google', 'textarea', 'Nezávazný odhad ceny domu, bytu nebo pozemku od zkušeného makléře. Hradec Králové, Pardubice, Kutná Hora, Kolín.'),
    F('estimate.hero_title', 'Nadpis', 'md', 'Kolik má váš domov\n*hodnotu*?', H1),
    F('estimate.quote', 'Citát nad formulářem', 'md', 'Umění nastavit cenu tak, abyste za prodej dostali maximum, je ve zkušenostech. Online kalkulačka vám dá číslo. Já vám dám cenu.'),
    F('estimate.aside', 'Text vedle formuláře', 'textarea', 'Nikdy nenajdete dvě stejné nemovitosti. Často působí podobně, ale liší se v hromadě detailů.\n\nDíky zkušenostem vím, na co se zaměřit, jak vyzdvihnout výhody a jak poctivě prezentovat nedostatky. Proto se mi daří prodávat za tu nejvýhodnější cenu.'),
    F('estimate.thanks', 'Poděkování po odeslání', default='Děkuji! Ozvu se vám do 24 hodin. — Tomáš'),
  ]},
 ]},

 {'id': 'contactpage', 'title': 'Stránka Kontakt', 'icon': 'mail', 'sections': [
  {'title': 'Texty', 'fields': [
    F('contactpage.seo_title', 'Titulek stránky', default='Kontakt — Tomáš Veigl, realitní makléř Hradec Králové'),
    F('contactpage.hero_title', 'Nadpis', 'md', 'Ozvěte se.\n*Slyším* vás.', H1),
    F('contactpage.band', 'Věta v tmavém pruhu', 'md', 'Slyším díky technice, *rozumím díky srdci*.', MD),
    F('contactpage.thanks', 'Poděkování po odeslání', default='Děkuji za zprávu, brzy se vám ozvu. — Tomáš'),
  ]},
 ]},
]

def defaults():
    out = {}
    for page in SCHEMA:
        for sec in page['sections']:
            for f in sec['fields']:
                out[f['key']] = f['default']
    return out
