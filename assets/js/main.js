/* Tomáš Veigl — native scroll, IntersectionObserver, no rAF loops at rest */
(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const scrollTimeline = CSS.supports('animation-timeline: scroll()');

  /* nav state */
  const nav = $('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', scrollY > 40);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  /* progress fallback (only when CSS scroll timelines are missing) */
  const bar = $('.scroll-progress');
  if (bar && !scrollTimeline) {
    let ticking = false;
    addEventListener('scroll', () => {
      if (ticking) return; ticking = true;
      requestAnimationFrame(() => {
        const max = document.documentElement.scrollHeight - innerHeight;
        bar.style.transform = `scaleX(${max > 0 ? scrollY / max : 0})`;
        ticking = false;
      });
    }, { passive: true });
  }

  /* mobile menu */
  const toggle = $('.nav-toggle'), menu = $('.nav-menu');
  if (toggle && menu) {
    const set = (open) => {
      menu.classList.toggle('open', open); toggle.classList.toggle('open', open);
      document.body.classList.toggle('menu-open', open);
      toggle.setAttribute('aria-expanded', open);
      document.documentElement.style.overflow = open ? 'hidden' : '';
    };
    toggle.addEventListener('click', () => set(!menu.classList.contains('open')));
    $$('a', menu).forEach(a => a.addEventListener('click', () => set(false)));
    addEventListener('keydown', e => e.key === 'Escape' && set(false));
  }

  /* reveals */
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('.reveal, .wave-divider').forEach(el => io.observe(el));
  // clip-path hides the target, so watch its sliver with threshold 0
  const clipIO = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); clipIO.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0 });
  $$('.clip-reveal').forEach(el => clipIO.observe(el));
  if (!CSS.supports('animation-timeline: view()')) $$('.hear').forEach(el => io.observe(el));

  /* pause live waveforms when offscreen */
  const wio = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle('paused', !e.isIntersecting)));
  $$('.wave.live').forEach(w => wio.observe(w));

  /* counters */
  const cio = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      const el = e.target, target = parseFloat(el.dataset.count), dec = (el.dataset.count.split(/[.,]/)[1] || '').length;
      if (reduce) { el.textContent = target.toFixed(dec).replace('.', ','); return; }
      const t0 = performance.now(), dur = 1800;
      const step = (t) => {
        const p = Math.min(1, (t - t0) / dur), v = target * (1 - Math.pow(1 - p, 4));
        el.textContent = v.toFixed(dec).replace('.', ',');
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(el => cio.observe(el));

  /* service rows — image follows cursor (only while hovering) */
  const preview = $('.srow-preview');
  if (preview && matchMedia('(hover: hover)').matches) {
    let x = 0, y = 0, raf = 0;
    const paint = () => { preview.style.transform = `translate(${x + 28}px, ${y - 105}px)`; raf = 0; };
    $$('.srow[data-img]').forEach(row => {
      row.addEventListener('mouseenter', () => { preview.style.backgroundImage = `url(${row.dataset.img})`; preview.classList.add('on'); });
      row.addEventListener('mouseleave', () => preview.classList.remove('on'));
      row.addEventListener('mousemove', e => { x = e.clientX; y = e.clientY; if (!raf) raf = requestAnimationFrame(paint); });
    });
  }

  /* magnetic buttons */
  if (matchMedia('(hover: hover)').matches && !reduce) {
    $$('.btn-magnetic').forEach(btn => {
      btn.addEventListener('mousemove', e => {
        const r = btn.getBoundingClientRect();
        btn.style.transition = 'transform .15s linear';
        btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.18}px, ${(e.clientY - r.top - r.height / 2) * 0.25}px)`;
      });
      btn.addEventListener('mouseleave', () => { btn.style.transition = ''; btn.style.transform = ''; });
    });
  }

  /* horizontal rails */
  $$('[data-rail]').forEach(wrap => {
    const rail = $('.rail', wrap.closest('section') || document);
    if (!rail) return;
    $$('button', wrap).forEach(b => b.addEventListener('click', () => {
      const card = rail.firstElementChild; const w = card ? card.getBoundingClientRect().width + 20 : 400;
      rail.scrollBy({ left: (b.dataset.dir === 'prev' ? -1 : 1) * w, behavior: reduce ? 'auto' : 'smooth' });
    }));
  });

  /* listing filters */
  const grid = $('[data-grid]');
  if (grid) {
    const cards = $$('.card', grid), empty = $('.empty-note');
    let status = 'all', type = 'all';
    const apply = () => {
      let n = 0;
      cards.forEach(c => {
        const ok = (status === 'all' || c.dataset.status === status) && (type === 'all' || c.dataset.type.includes(type));
        c.classList.toggle('is-hidden', !ok); if (ok) n++;
      });
      if (empty) empty.style.display = n ? 'none' : 'block';
    };
    $$('[data-status-filter]').forEach(ch => ch.addEventListener('click', () => {
      $$('[data-status-filter]').forEach(x => x.classList.toggle('on', x === ch));
      status = ch.dataset.statusFilter; apply();
    }));
    const sel = $('[data-type-filter]');
    if (sel) sel.addEventListener('change', () => { type = sel.value; apply(); });
    const pre = new URLSearchParams(location.search).get('stav');
    if (pre) { const ch = $(`[data-status-filter="${pre}"]`); if (ch) ch.click(); }
  }

  /* lightbox */
  const lb = $('.lb');
  if (lb) {
    const img = $('img', lb), cnt = $('.c', lb);
    let list = [], i = 0;
    const show = () => { img.src = list[i]; cnt.textContent = `${i + 1} / ${list.length}`; };
    const close = () => { lb.classList.remove('open'); document.documentElement.style.overflow = ''; };
    $$('[data-lb]').forEach(g => {
      const links = $$('a', g);
      links.forEach((a, k) => a.addEventListener('click', e => {
        e.preventDefault(); list = links.map(l => l.getAttribute('href')); i = k; show();
        lb.classList.add('open'); document.documentElement.style.overflow = 'hidden';
      }));
    });
    $('.x', lb).addEventListener('click', close);
    $('.p', lb).addEventListener('click', () => { i = (i - 1 + list.length) % list.length; show(); });
    $('.n', lb).addEventListener('click', () => { i = (i + 1) % list.length; show(); });
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    addEventListener('keydown', e => {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') $('.p', lb).click();
      if (e.key === 'ArrowRight') $('.n', lb).click();
    });
  }

  /* jak pracuji — live step counter */
  const counter = $('[data-step-counter]');
  if (counter) {
    const steps = $$('.step'), phase = $('[data-step-phase]'), dots = $$('.phase-dots i');
    const sio = new IntersectionObserver(es => {
      es.forEach(e => {
        if (!e.isIntersecting) return;
        const k = steps.indexOf(e.target);
        counter.firstChild.textContent = String(k + 1).padStart(2, '0');
        if (phase) phase.textContent = e.target.dataset.phase;
        dots.forEach((d, j) => { d.classList.toggle('on', j <= k); d.classList.toggle('cur', j === k); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    steps.forEach(s => sio.observe(s));
  }

  /* prefill contact message from a listing */
  const want = new URLSearchParams(location.search).get('nemovitost'), msg = $('#cz');
  if (want && msg) msg.value = `Dobrý den, mám zájem o prohlídku: ${want}.`;

  /* demo forms (design proposal — no backend) */
  $$('form[data-demo]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault(); f.classList.add('sent');
    const b = $('button[type=submit]', f); if (b) { b.disabled = true; b.firstChild.textContent = 'Odesláno '; }
  }));
})();
