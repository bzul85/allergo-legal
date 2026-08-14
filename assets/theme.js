// AllerGo legal pages — light/dark toggle.
// The stored choice wins; with no choice the OS setting applies.
(function () {
  var KEY = 'allergo-theme';
  var root = document.documentElement;

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function resolved() {
    var choice = root.getAttribute('data-theme');
    if (choice === 'dark' || choice === 'light') return choice;
    return systemPrefersDark() ? 'dark' : 'light';
  }

  function label(btn) {
    var next = resolved() === 'dark' ? 'light' : 'dark';
    var pl = document.documentElement.lang === 'pl';
    btn.setAttribute('aria-label', pl
      ? (next === 'dark' ? 'Włącz tryb ciemny' : 'Włącz tryb jasny')
      : (next === 'dark' ? 'Switch to dark mode' : 'Switch to light mode'));
    btn.setAttribute('title', btn.getAttribute('aria-label'));
  }

  function init() {
    var btn = document.querySelector('.theme-toggle');
    if (!btn) return;
    label(btn);

    btn.addEventListener('click', function () {
      var next = resolved() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
      label(btn);
    });

    // Follow the OS while the user has made no explicit choice.
    if (window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      var onChange = function () { if (!stored()) label(btn); };
      if (mq.addEventListener) mq.addEventListener('change', onChange);
      else if (mq.addListener) mq.addListener(onChange);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
