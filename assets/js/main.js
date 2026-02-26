// AI Tech Daily — main.js

(function() {
  'use strict';

  // --- Mobile Navigation Toggle ---
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function() {
      var isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // --- Perspective Section Color Coding ---
  // Detects emoji in H3 headings rendered from generate-news Markdown
  // and wraps each perspective section with a colored container.
  // Markdown structure: ### <emoji> <perspective name>
  var perspectiveMap = {
    '\u26A1': 'breaking',   // ⚡
    '\uD83D\uDCBB': 'developer', // 💻
    '\uD83D\uDCCA': 'business',  // 📊
    '\uD83D\uDCD6': 'beginner',  // 📖
    '\uD83D\uDCA1': 'ideas'      // 💡
  };

  var articleBody = document.querySelector('.article-body');
  if (!articleBody) return;

  var headings = articleBody.querySelectorAll('h3');
  var MAX_SIBLINGS = 100; // safety limit

  headings.forEach(function(h3) {
    var text = h3.textContent || '';

    for (var emoji in perspectiveMap) {
      if (text.indexOf(emoji) === -1) continue;

      var type = perspectiveMap[emoji];
      h3.setAttribute('data-perspective', type);

      // Wrap h3 + following content until next h2/h3/hr
      var wrapper = document.createElement('div');
      wrapper.className = 'perspective-section perspective-' + type;

      h3.parentNode.insertBefore(wrapper, h3);
      wrapper.appendChild(h3);

      var count = 0;
      var next = wrapper.nextSibling;
      while (next && count < MAX_SIBLINGS) {
        count++;
        var sibling = next.nextSibling;
        if (next.nodeType === 1) {
          var tag = next.tagName;
          if (tag === 'H2' || tag === 'H3' || tag === 'HR') break;
        }
        wrapper.appendChild(next);
        next = sibling;
      }
      break;
    }
  });
  // --- AdSense Initialization ---
  var adSlots = document.querySelectorAll('.adsbygoogle');
  if (adSlots.length > 0 && typeof window.adsbygoogle !== 'undefined') {
    adSlots.forEach(function() {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    });
  }
})();
