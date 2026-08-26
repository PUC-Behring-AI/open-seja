/*
 * SEJA doc-C shared navigation script (Pattern 2b -- see doc-guidelines.md
 * Section G). Co-located, self-contained, vanilla JS. No imports, no CDN, no
 * build step. Load with `defer`:
 *
 *   <!-- JS depth: 1 (volume-level page) -->
 *   <script src="../nav.js" defer></script>
 *
 * PROGRESSIVE ENHANCEMENT: every page must be fully readable and navigable
 * with JavaScript disabled. This script only *adds* convenience (auto-TOC,
 * scrollspy, collapsible groups, Diataxis filtering). It never supplies
 * essential content, and it no-ops silently when its optional containers are
 * absent.
 *
 * ── HTML CONTRACT ──────────────────────────────────────────────────────────
 * Reads:
 *   - The prose column: an element matching `.doc-content` (falls back to
 *     <main>). Its <h2> and <h3> descendants become the table of contents.
 *   - `data-diataxis` attributes on <section> elements inside `.doc-content`
 *     (values: tutorial | howto | reference | explanation). Drive the filter.
 * Requires (optional -- absent → that feature no-ops):
 *   - A navigation container matching `.doc-nav` to receive the generated TOC
 *     and, when applicable, the Diataxis filter controls.
 * Writes:
 *   - Injects a `.doc-nav-title` + `ul.toc` into `.doc-nav`; groups an <h2>
 *     that has <h3> children into `li.doc-nav-group` > `button.doc-nav-toggle`
 *     (`aria-expanded`) + `ul.doc-nav-group-items`.
 *   - Adds/removes `.active` on TOC links (scrollspy).
 *   - Injects `.doc-filter` controls with `button[aria-pressed]` when at least
 *     one `data-diataxis` section exists.
 *   - Adds/removes `.dimmed` on non-matching `.doc-content` <section>s while a
 *     filter is active.
 *   - Assigns `id`s to headings that lack one (slugified, de-duplicated).
 *
 * SECURITY: all dynamic DOM is built with createElement/textContent. Page text
 * is never interpolated into innerHTML, so the XSS surface stays at zero.
 *
 * Entry point: initDocNav(), invoked on DOMContentLoaded (below).
 */

(function () {
  'use strict';

  var DIATAXIS_LABELS = {
    tutorial: 'Tutorial',
    howto: 'How-to',
    reference: 'Reference',
    explanation: 'Explanation'
  };

  var prefersReducedMotion = false;
  try {
    prefersReducedMotion =
      window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch (e) {
    prefersReducedMotion = false;
  }

  /* ---------------------------------------------------------------- */
  /* Utilities                                                        */
  /* ---------------------------------------------------------------- */

  function slugify(text) {
    return String(text)
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  // Ensure every heading has a unique id so TOC links resolve.
  function ensureHeadingIds(headings) {
    var used = {};
    // Seed with ids already present on the page.
    var existing = document.querySelectorAll('[id]');
    for (var i = 0; i < existing.length; i++) {
      used[existing[i].id] = true;
    }
    headings.forEach(function (h) {
      if (h.id) {
        used[h.id] = true;
        return;
      }
      var base = slugify(h.textContent) || 'section';
      var id = base;
      var n = 2;
      while (used[id]) {
        id = base + '-' + n;
        n++;
      }
      h.id = id;
      used[id] = true;
    });
  }

  function makeTocLink(heading) {
    var a = document.createElement('a');
    a.className = 'toc-link';
    a.href = '#' + heading.id;
    a.textContent = heading.textContent;
    a.setAttribute('data-target', heading.id);
    return a;
  }

  /* ---------------------------------------------------------------- */
  /* Table of contents                                                */
  /* ---------------------------------------------------------------- */

  // Build a grouped TOC: each <h2> is a top-level entry; its following <h3>s
  // (until the next <h2>) become a collapsible child group.
  function buildToc(nav, content) {
    var headings = Array.prototype.slice.call(
      content.querySelectorAll('h2, h3')
    );
    if (!headings.length) {
      return []; // no headings → nothing to navigate; leave .doc-nav as-is
    }
    ensureHeadingIds(headings);

    var title = document.createElement('p');
    title.className = 'doc-nav-title';
    title.textContent = 'On this page';

    var list = document.createElement('ul');
    list.className = 'toc';

    var links = [];
    var groupSeq = 0;
    var i = 0;

    while (i < headings.length) {
      var h = headings[i];
      if (h.tagName.toLowerCase() === 'h3') {
        // Stray h3 before any h2 → treat as a flat top-level entry.
        var strayItem = document.createElement('li');
        strayItem.className = 'toc-item toc-h3';
        var strayLink = makeTocLink(h);
        strayItem.appendChild(strayLink);
        list.appendChild(strayItem);
        links.push(strayLink);
        i++;
        continue;
      }

      // h2: gather following h3 children.
      var children = [];
      var j = i + 1;
      while (j < headings.length && headings[j].tagName.toLowerCase() === 'h3') {
        children.push(headings[j]);
        j++;
      }

      if (!children.length) {
        var item = document.createElement('li');
        item.className = 'toc-item';
        var link = makeTocLink(h);
        item.appendChild(link);
        list.appendChild(item);
        links.push(link);
      } else {
        groupSeq++;
        var groupId = 'doc-nav-group-' + groupSeq;

        var groupLi = document.createElement('li');
        groupLi.className = 'doc-nav-group';

        var toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'doc-nav-toggle';
        toggle.textContent = h.textContent;
        toggle.setAttribute('aria-expanded', 'true');
        toggle.setAttribute('aria-controls', groupId);

        var groupItems = document.createElement('ul');
        groupItems.className = 'doc-nav-group-items';
        groupItems.id = groupId;

        // Self-link to the h2 section top, then each h3.
        var selfLi = document.createElement('li');
        selfLi.className = 'toc-item';
        var selfLink = makeTocLink(h);
        selfLi.appendChild(selfLink);
        groupItems.appendChild(selfLi);
        links.push(selfLink);

        children.forEach(function (child) {
          var childLi = document.createElement('li');
          childLi.className = 'toc-h3';
          var childLink = makeTocLink(child);
          childLi.appendChild(childLink);
          groupItems.appendChild(childLi);
          links.push(childLink);
        });

        toggle.addEventListener('click', function (items, btn) {
          return function () {
            var expanded = btn.getAttribute('aria-expanded') === 'true';
            btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
            // Express collapsed state on the controlled element itself, not
            // solely via the adjacent-sibling CSS selector, so the group's
            // open/closed state survives DOM refactors and is exposed to AT.
            items.hidden = expanded;
          };
        }(groupItems, toggle));

        groupLi.appendChild(toggle);
        groupLi.appendChild(groupItems);
        list.appendChild(groupLi);
      }
      i = j;
    }

    nav.appendChild(title);
    nav.appendChild(list);

    wireSmoothScroll(links);
    wireScrollSpy(links, headings);

    return links;
  }

  /* ---------------------------------------------------------------- */
  /* Smooth scroll + focus management                                 */
  /* ---------------------------------------------------------------- */

  function wireSmoothScroll(links) {
    links.forEach(function (link) {
      link.addEventListener('click', function (ev) {
        var id = link.getAttribute('data-target');
        var target = id && document.getElementById(id);
        if (!target) {
          return; // let the browser handle a missing target gracefully
        }
        ev.preventDefault();
        target.scrollIntoView({
          behavior: prefersReducedMotion ? 'auto' : 'smooth',
          block: 'start'
        });
        // Move focus to the heading for keyboard/screen-reader users.
        if (!target.hasAttribute('tabindex')) {
          target.setAttribute('tabindex', '-1');
        }
        target.focus({ preventScroll: true });
        // Reflect location without a second jump.
        if (window.history && window.history.replaceState) {
          window.history.replaceState(null, '', '#' + id);
        }
      });
    });
  }

  /* ---------------------------------------------------------------- */
  /* Scrollspy (active-section highlight)                             */
  /* ---------------------------------------------------------------- */

  function wireScrollSpy(links, headings) {
    var linkById = {};
    links.forEach(function (link) {
      var id = link.getAttribute('data-target');
      // First link wins (the self-link) when an id maps to several links.
      if (id && !linkById[id]) {
        linkById[id] = link;
      }
    });

    function setActive(id) {
      links.forEach(function (link) {
        link.classList.toggle('active', link.getAttribute('data-target') === id);
      });
    }

    if (!('IntersectionObserver' in window)) {
      // Graceful fallback: highlight on click only (already wired). No spy.
      return;
    }

    var visible = {};
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            visible[entry.target.id] = true;
          } else {
            delete visible[entry.target.id];
          }
        });
        // Choose the topmost visible heading in document order.
        for (var k = 0; k < headings.length; k++) {
          if (visible[headings[k].id]) {
            setActive(headings[k].id);
            return;
          }
        }
      },
      {
        rootMargin: '0px 0px -70% 0px',
        threshold: 0
      }
    );

    headings.forEach(function (h) {
      observer.observe(h);
    });
  }

  /* ---------------------------------------------------------------- */
  /* Diataxis filter                                                  */
  /* ---------------------------------------------------------------- */

  function buildFilter(nav, content) {
    var sections = Array.prototype.slice.call(
      content.querySelectorAll('section[data-diataxis]')
    );
    if (!sections.length) {
      return; // no typed sections → no filter UI
    }

    // Distinct types, in document order.
    var order = [];
    var seen = {};
    sections.forEach(function (s) {
      var t = s.getAttribute('data-diataxis');
      if (t && !seen[t]) {
        seen[t] = true;
        order.push(t);
      }
    });
    if (order.length < 2) {
      return; // a single type isn't worth a filter
    }

    var wrap = document.createElement('div');
    wrap.className = 'doc-filter';

    var title = document.createElement('p');
    title.className = 'doc-nav-title';
    title.textContent = 'Filter by type';
    wrap.appendChild(title);

    var active = null; // currently selected type, or null for "all"
    var buttons = [];

    function apply() {
      sections.forEach(function (s) {
        var t = s.getAttribute('data-diataxis');
        s.classList.toggle('dimmed', active !== null && t !== active);
      });
      buttons.forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-type') === active ? 'true' : 'false');
      });
    }

    order.forEach(function (type) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.setAttribute('data-type', type);
      btn.setAttribute('aria-pressed', 'false');
      btn.textContent = DIATAXIS_LABELS[type] || type;
      btn.addEventListener('click', function () {
        active = active === type ? null : type; // toggle off returns to "all"
        apply();
      });
      buttons.push(btn);
      wrap.appendChild(btn);
    });

    nav.appendChild(wrap);
  }

  /* ---------------------------------------------------------------- */
  /* Entry point                                                      */
  /* ---------------------------------------------------------------- */

  function initDocNav() {
    var content = document.querySelector('.doc-content') || document.querySelector('main');
    var nav = document.querySelector('.doc-nav');
    if (!content || !nav) {
      return; // nothing to enhance; page stays fully usable without JS
    }
    buildToc(nav, content);
    buildFilter(nav, content);
  }

  // Expose the documented entry point.
  window.initDocNav = initDocNav;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDocNav);
  } else {
    initDocNav();
  }
})();
