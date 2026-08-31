// 404 wayfinding. Almost every miss on this site is one year away from being
// right — /2019/keynote/, /2025-programme, or a year that never had an edition —
// so the page reads the address actually requested and names the edition it
// points at. Progressive enhancement: the static "Where to go instead" list is
// the route out when this does not run, and this only ever ADDS a suggestion.
(function () {
  var dataEl = document.getElementById('notfound-data');
  var hint = document.getElementById('notfound-hint');
  if (!dataEl || !hint) return;

  var data;
  try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var base = data.base || '';

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function link(href, text, cls) {
    var a = el('a', cls, text);
    a.href = base + href;
    return a;
  }

  // ── The address asked for ──────────────────────────────────────────────
  // textContent, never innerHTML: this string arrives from the URL bar, and is
  // capped so a pathological path cannot stretch the layout.
  var path = location.pathname + location.search;
  var asked = document.getElementById('notfound-asked');
  var askedPath = document.getElementById('notfound-asked-path');
  // Nothing to report when the page is opened at its own address rather than
  // served in place of a miss.
  if (asked && askedPath && path && path !== base + '/404.html') {
    askedPath.textContent = path.length > 120 ? path.slice(0, 119) + '…' : path;
    asked.hidden = false;
  }

  var probe = path.toLowerCase();
  try { probe = decodeURIComponent(probe); } catch (e) { /* malformed %-escape */ }

  // ── What the address seems to name ─────────────────────────────────────
  // Canonical page keys come from _data/page_labels.yml; the aliases are shapes
  // seen in the wild — the previous Oxford site used <year>-<slug> paths, and
  // the migration renamed accommodation-and-transportation to /local/ (the same
  // rename tools/verify_fidelity.py carries as SLUG_ALIAS).
  var labels = data.labels || [];
  var needles = [];
  labels.forEach(function (pg) { needles.push([pg.key, pg.key]); });
  var ALIAS = {
    'accommodation-and-transportation': 'local',
    'accommodation': 'local',
    'transportation': 'local',
    'travel': 'local',
    'cfp': 'call-for-papers',
    'call-for-paper': 'call-for-papers',
    'papers': 'call-for-papers',
    'program': 'programme',
    'schedule': 'programme',
    'proceeding': 'proceedings'
  };
  Object.keys(ALIAS).forEach(function (k) { needles.push([k, ALIAS[k]]); });
  // Longest needle first, so "call-for-papers" is never mistaken for "papers".
  needles.sort(function (a, b) { return b[0].length - a[0].length; });

  var key = null;
  for (var i = 0; i < needles.length; i++) {
    if (probe.indexOf(needles[i][0]) !== -1) { key = needles[i][1]; break; }
  }
  function labelFor(k) {
    for (var j = 0; j < labels.length; j++) if (labels[j].key === k) return labels[j].label;
    return k;
  }

  var ym = probe.match(/(?:^|\D)(20\d{2})(?:\D|$)/);
  var year = ym ? parseInt(ym[1], 10) : null;
  var editions = data.editions || [];
  var edition = null, oldest = null;
  editions.forEach(function (e) {
    if (e.year === year) edition = e;
    if (oldest === null || e.year < oldest) oldest = e.year;
  });

  // ── The suggestion ────────────────────────────────────────────────────
  function label(text) { hint.appendChild(el('p', 'notfound-hint-label', text)); }

  // Repeats the markup of the list below (and of /previous/), so a suggestion
  // and a listed edition look like the same kind of thing.
  function editionHead(href, title, meta) {
    var head = el('div', 'edition-head');
    head.appendChild(link(href, title, 'edition-year'));
    if (meta) head.appendChild(el('span', 'edition-meta', meta));
    hint.appendChild(head);
  }
  function editionLinks(e) {
    if (!e.pages || !e.pages.length) return;
    var ul = el('ul', 'edition-links');
    var prefix = e.year === data.current ? '/' : '/' + e.year + '/';
    labels.forEach(function (pg) {
      if (e.pages.indexOf(pg.key) === -1) return;
      var li = el('li');
      li.appendChild(link(prefix + pg.key + '/', pg.label));
      ul.appendChild(li);
    });
    hint.appendChild(ul);
  }

  if (edition) {
    var home = edition.year === data.current ? '/' : '/' + edition.year + '/';
    var has = key && edition.pages && edition.pages.indexOf(key) !== -1;
    var meta = [
      edition.ordinal ? edition.ordinal + ' International ' + (edition.kind || 'Conference') : null,
      edition.city, edition.dates
    ].filter(Boolean).join(' · ');

    label('Did you mean…');
    if (has) {
      editionHead(home + key + '/', 'DLfM ' + edition.year + ' · ' + labelFor(key), meta);
    } else {
      editionHead(home, 'DLfM ' + edition.year, meta);
      if (key) {
        // Said plainly rather than silently redirected: the early editions
        // genuinely have no programme page, and pretending otherwise wastes
        // another click.
        hint.appendChild(el('p', 'notfound-hint-note',
          'That edition has no ' + labelFor(key) + ' page on this site.'));
      }
    }
    editionLinks(edition);
  } else if (year !== null && year > data.current) {
    label('Not yet');
    hint.appendChild(el('p', 'notfound-hint-note',
      'DLfM ' + year + ' has not been announced. DLfM ' + data.current + ' is the current edition.'));
  } else if (year !== null) {
    label('No such edition');
    hint.appendChild(el('p', 'notfound-hint-note',
      'There was no DLfM ' + year + ' — the first edition was in ' + oldest + '.'));
  } else if (key) {
    var cur = null;
    editions.forEach(function (e) { if (e.year === data.current) cur = e; });
    if (cur && cur.pages && cur.pages.indexOf(key) !== -1) {
      label('Did you mean…');
      editionHead('/' + key + '/', 'DLfM ' + data.current + ' · ' + labelFor(key),
        [cur.city, cur.dates].filter(Boolean).join(' · '));
    } else {
      return;                      // nothing worth saying; keep the card hidden
    }
  } else {
    return;
  }

  hint.hidden = false;
})();
