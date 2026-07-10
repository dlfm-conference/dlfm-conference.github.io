// Progressive-enhancement navigation: mobile menu + "Previous events" dropdown.
// The site is fully navigable without JS; this only improves the experience.
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  document.querySelectorAll('.dropdown-caret').forEach(function (btn) {
    var menu = document.getElementById(btn.getAttribute('aria-controls'));
    if (!menu) return;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = menu.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });

  // On pages with a {:toc} jump bar, add a "back to top" arrow to each main
  // heading (matching the programme page), and let sections rendered outside the
  // Markdown opt into the bar via `data-jump="Label"`. Enhancement only.
  var toc = document.getElementById('markdown-toc');
  function addTopArrow(h) {
    var a = document.createElement('a');
    a.className = 'to-top';
    a.href = '#markdown-toc';
    a.title = 'Back to top';
    a.setAttribute('aria-label', 'Back to top');
    a.textContent = '↑';
    h.appendChild(a);
  }
  if (toc) {
    document.querySelectorAll('.prose h2[id]').forEach(addTopArrow);
    document.querySelectorAll('[data-jump][id]').forEach(function (sec) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + sec.id;
      a.textContent = sec.getAttribute('data-jump');
      li.appendChild(a);
      toc.appendChild(li);
      var h = sec.querySelector('h2');
      if (h) addTopArrow(h);
    });
  }

  document.addEventListener('click', function (e) {
    var inHeader = e.target.closest('.site-header');
    // close open submenu dropdowns on any outside click
    document.querySelectorAll('.dropdown.open').forEach(function (m) {
      if (inHeader && m.contains(e.target)) return;
      m.classList.remove('open');
      var b = document.querySelector('[aria-controls="' + m.id + '"]');
      if (b) b.setAttribute('aria-expanded', 'false');
    });
    // close the mobile menu when tapping outside the header (e.g. in content)
    if (nav && nav.classList.contains('open') && !inHeader) {
      nav.classList.remove('open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();
