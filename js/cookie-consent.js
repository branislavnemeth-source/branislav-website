/* =============================================
   BranislavIT — Cookie consent (GDPR + AdSense)
   - Banner s "Iba nevyhnutné" / "Súhlasím so všetkými"
   - AdSense + Analytics sa načítajú IBA po súhlase
   - localStorage kľúč: bw-cookie-consent
   ============================================= */
(function () {
  var KEY = 'bw-cookie-consent';
  var ADSENSE_CLIENT = 'ca-pub-4124785228904294';

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function getConsent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadAdSense() {
    if (window.__bwAdsLoaded) return;
    window.__bwAdsLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADSENSE_CLIENT;
    document.head.appendChild(s);
    // Spusti všetky <ins.adsbygoogle> bloky, ak existujú
    s.onload = function () {
      try {
        document.querySelectorAll('ins.adsbygoogle').forEach(function () {
          (window.adsbygoogle = window.adsbygoogle || []).push({});
        });
      } catch (e) {}
    };
  }

  function showBanner() {
    var b = $('#cookie-banner');
    if (b) b.hidden = false;
  }
  function hideBanner() {
    var b = $('#cookie-banner');
    if (b) b.hidden = true;
  }

  function init() {
    var consent = getConsent();
    if (consent === 'accept') {
      loadAdSense();
    } else if (!consent) {
      setTimeout(showBanner, 600);
    }

    document.querySelectorAll('[data-cookie]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        var v = e.currentTarget.getAttribute('data-cookie');
        setConsent(v);
        hideBanner();
        if (v === 'accept') loadAdSense();
      });
    });
  }

  // Tlačidlo "Nastavenia cookies" v päte
  window.openCookieSettings = function () {
    try { localStorage.removeItem(KEY); } catch (e) {}
    showBanner();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
