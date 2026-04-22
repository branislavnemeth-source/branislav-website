// =============================================
// BRANISLAV.WEBSITE — Main JS
// =============================================

// --- Dark Mode Toggle ---
(function () {
  const html = document.documentElement;
  const stored = null; // no localStorage in sandboxed env
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let theme = prefersDark ? 'dark' : 'light';
  html.setAttribute('data-theme', theme);

  function updateToggleIcon(btn, t) {
    if (!btn) return;
    btn.innerHTML = t === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    btn.setAttribute('aria-label', 'Prepnúť na ' + (t === 'dark' ? 'svetlý' : 'tmavý') + ' režim');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const toggles = document.querySelectorAll('[data-theme-toggle]');
    toggles.forEach(btn => {
      updateToggleIcon(btn, theme);
      btn.addEventListener('click', () => {
        theme = theme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', theme);
        toggles.forEach(b => updateToggleIcon(b, theme));
      });
    });
  });
})();

// --- Sticky Header ---
document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('site-header--scrolled', window.scrollY > 10);
    });
  }

  // --- Hamburger Menu ---
  const hamburger = document.querySelector('.hamburger');
  const navMobile = document.querySelector('.nav-mobile');
  if (hamburger && navMobile) {
    hamburger.addEventListener('click', () => {
      navMobile.classList.toggle('open');
      const isOpen = navMobile.classList.contains('open');
      hamburger.setAttribute('aria-expanded', isOpen);
    });
  }

  // --- Tabs ---
  document.querySelectorAll('.tab-nav').forEach(nav => {
    const btns = nav.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => { b.classList.remove('active', 'active-ai'); });
        panels.forEach(p => p.classList.remove('active'));
        btn.classList.add(btn.dataset.tabType === 'ai' ? 'active-ai' : 'active');
        const target = document.getElementById(btn.dataset.tab);
        if (target) target.classList.add('active');
      });
    });
  });

  // --- Fade-in on scroll ---
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

  // --- Active nav link ---
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .nav-mobile a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      a.classList.add(href && href.includes('ai') ? 'active-ai' : 'active');
    }
  });

  // --- Set current year in footer ---
  const yearEl = document.getElementById('current-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();
});


document.addEventListener('DOMContentLoaded', () => { document.querySelectorAll('.quick-offer, .homepage-offer-card, .support-card').forEach(el => el.classList.add('fade-in')); });
