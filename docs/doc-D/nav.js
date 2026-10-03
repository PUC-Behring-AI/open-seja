// nav.js — progressive enhancement for the per-volume sidebar (.volume-toc).
// The sidebar works as plain anchor links with JS disabled; this script adds
// (1) scroll-spy that marks the section currently in view, and (2) a mobile
// toggle button to collapse/expand the sidebar. Both are strictly additive:
// with JS off the sidebar renders expanded and no dead control appears.
(function () {
  "use strict";

  var ACTIVE_CLASS = "is-active";
  var COLLAPSE_CLASS = "is-collapsed";
  var TOGGLE_CLASS = "volume-toc-toggle";
  var TOC_ID = "volume-toc";

  // Scroll-spy: highlight the sidebar link for the section near the top of the
  // viewport. Only volume-scoped chapter pages have nested `#section` links;
  // volume index pages have none, so we no-op cleanly there.
  function initScrollSpy(toc) {
    var sectionLinks = toc.querySelectorAll('a[href^="#"]');
    if (!sectionLinks.length) return;
    if (!("IntersectionObserver" in window)) return;

    var linkBySection = {};
    var observed = [];
    sectionLinks.forEach(function (link) {
      var href = link.getAttribute("href");
      if (!href || href.charAt(0) !== "#" || href.length < 2) return;
      var id = decodeURIComponent(href.substring(1));
      var section = document.getElementById(id);
      if (section) {
        linkBySection[id] = link;
        observed.push(section);
      }
    });

    if (!observed.length) return;

    function setActive(link) {
      sectionLinks.forEach(function (other) {
        other.classList.remove(ACTIVE_CLASS);
        other.removeAttribute("aria-current");
      });
      if (link) {
        link.classList.add(ACTIVE_CLASS);
        link.setAttribute("aria-current", "true");
      }
    }

    // Track visibility ratios so we can pick a single "current" section: the
    // topmost one intersecting the top band of the viewport.
    var visible = {};

    function pickCurrent() {
      var current = null;
      var bestTop = Infinity;
      observed.forEach(function (section) {
        if (!visible[section.id]) return;
        var top = section.getBoundingClientRect().top;
        if (top < bestTop) {
          bestTop = top;
          current = section;
        }
      });
      if (current) setActive(linkBySection[current.id]);
    }

    // rootMargin pulls the observation band to the top of the viewport so the
    // section "in view" is the one the reader is currently reading, not one
    // just entering at the bottom.
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          visible[entry.target.id] = entry.isIntersecting;
        });
        pickCurrent();
      },
      { rootMargin: "0px 0px -70% 0px", threshold: 0 }
    );

    observed.forEach(function (section) {
      observer.observe(section);
    });
  }

  // Mobile toggle: create a button that collapses/expands the sidebar. CSS
  // hides the button above 60rem, so it only appears on narrow viewports. The
  // button is created here (never in the no-JS markup) so no dead control shows
  // when JS is disabled.
  function initToggle(toc) {
    if (!toc.id) toc.id = TOC_ID;

    var button = document.createElement("button");
    button.type = "button";
    button.className = TOGGLE_CLASS;
    button.setAttribute("aria-controls", toc.id);
    button.setAttribute("aria-expanded", "true");
    button.textContent = "Contents";

    function setExpanded(expanded) {
      button.setAttribute("aria-expanded", expanded ? "true" : "false");
      toc.classList.toggle(COLLAPSE_CLASS, !expanded);
    }

    button.addEventListener("click", function () {
      var expanded = button.getAttribute("aria-expanded") === "true";
      setExpanded(!expanded);
    });

    // Insert the button just before the sidebar so it reads first in source
    // order on narrow viewports.
    toc.parentNode.insertBefore(button, toc);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toc = document.querySelector(".volume-toc");
    if (!toc) return; // pages without a sidebar: nothing to enhance
    initScrollSpy(toc);
    initToggle(toc);
  });
})();
