/* SkyWise AI — Main JS */
document.addEventListener('DOMContentLoaded', () => {

  // ── Navbar scroll ──
  const nb = document.querySelector('.navbar');
  if (nb) window.addEventListener('scroll', () => nb.classList.toggle('scrolled', scrollY > 20));

  // ── Mobile nav ──
  const ham = document.getElementById('ham');
  const navLinks = document.getElementById('nav-links');
  if (ham && navLinks) ham.addEventListener('click', () => navLinks.classList.toggle('open'));

  // ── Fade-up on scroll ──
  const fus = document.querySelectorAll('.fu');
  if (fus.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.1 });
    fus.forEach((el, i) => { el.style.transitionDelay = (i % 6 * 0.07) + 's'; io.observe(el); });
  }

  // ── Django messages auto-dismiss ──
  document.querySelectorAll('.toast').forEach((t, i) => {
    setTimeout(() => {
      t.style.transition = 'opacity .4s,transform .4s';
      t.style.opacity = '0'; t.style.transform = 'translateX(110%)';
      setTimeout(() => t.remove(), 400);
    }, 4000 + i * 200);
  });

  // ── Star rating ──
  document.querySelectorAll('.stars[data-for]').forEach(wrap => {
    const input = document.getElementById(wrap.dataset.for);
    const stars = wrap.querySelectorAll('.star');
    const setActive = n => stars.forEach((s, i) => s.classList.toggle('on', i < n));
    stars.forEach((s, i) => {
      s.addEventListener('click', () => { if (input) input.value = i + 1; setActive(i + 1); });
      s.addEventListener('mouseenter', () => setActive(i + 1));
    });
    wrap.addEventListener('mouseleave', () => setActive(input ? +input.value : 0));
  });

  // ── Count-up animation ──
  document.querySelectorAll('.count-up[data-target]').forEach(el => {
    const target = +el.dataset.target;
    const dur = 1200;
    const io = new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting) return;
      io.disconnect();
      const start = Date.now();
      const tick = () => {
        const p = Math.min((Date.now() - start) / dur, 1);
        el.textContent = Math.round((1 - Math.pow(1 - p, 3)) * target).toLocaleString();
        if (p < 1) requestAnimationFrame(tick);
      };
      tick();
    });
    io.observe(el);
  });

  // ── Tip city rotation ──
  const tipEl = document.getElementById('tip-city');
  if (tipEl) {
    const cities = ['Balikpapan, ID','Jakarta, ID','Tokyo, JP','London, GB','New York, US','Paris, FR','Sydney, AU','Dubai, AE'];
    let idx = 0;
    setInterval(() => {
      tipEl.style.opacity = '0';
      setTimeout(() => { idx = (idx + 1) % cities.length; tipEl.textContent = cities[idx]; tipEl.style.opacity = '1'; }, 300);
    }, 2500);
    tipEl.style.transition = 'opacity .3s';
  }

  // ── Hourly scroll buttons ──
  const hs = document.getElementById('hourly-scroll');
  document.getElementById('h-left')?.addEventListener('click', () => hs?.scrollBy({ left: -200, behavior: 'smooth' }));
  document.getElementById('h-right')?.addEventListener('click', () => hs?.scrollBy({ left: 200, behavior: 'smooth' }));

  // ── Search form loading state ──
  document.querySelector('#search-form')?.addEventListener('submit', function() {
    const btn = this.querySelector('button[type=submit]');
    if (btn) { btn.innerHTML = '<span class="spin"></span> Mencari...'; btn.disabled = true; }
  });

  // ── Dashboard sidebar mobile ──

});

// ── Weather background setter ──
function applyWeatherBg(el, code, isDay) {
  const cls = ['bg-clear','bg-cloudy','bg-rain','bg-storm','bg-snow','bg-fog','bg-night','bg-default'];
  el.classList.remove(...cls);
  if (!code) return el.classList.add('bg-default');
  const c = +code;
  if (!isDay) return el.classList.add('bg-night');
  if (c === 800) el.classList.add('bg-clear');
  else if (c >= 801 && c <= 804) el.classList.add('bg-cloudy');
  else if ((c >= 300 && c <= 321) || (c >= 500 && c <= 531)) el.classList.add('bg-rain');
  else if (c >= 200 && c <= 232) el.classList.add('bg-storm');
  else if (c >= 600 && c <= 622) el.classList.add('bg-snow');
  else if (c >= 700 && c <= 781) el.classList.add('bg-fog');
  else el.classList.add('bg-default');
}

const wBg = document.getElementById('w-bg');
if (wBg) applyWeatherBg(wBg, wBg.dataset.code, wBg.dataset.day !== '0');

// ── Confirm delete ──
function confirmDelete(url, name) {
  if (confirm(`Hapus "${name}"?\nTindakan ini tidak dapat dibatalkan.`)) window.location.href = url;
}

// ── Galeri / highlights modal ──
function openModal(title, desc, emoji, detail) {
  const m = document.getElementById('ph-modal');
  if (!m) return;
  document.getElementById('m-emoji').textContent = emoji || '🌤️';
  document.getElementById('m-title').textContent = title || '';
  document.getElementById('m-desc').textContent = desc || '';
  document.getElementById('m-detail').textContent = detail || '';
  m.style.display = 'flex';
}
function closeModal() {
  const m = document.getElementById('ph-modal');
  if (m) m.style.display = 'none';
}
document.getElementById('ph-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
