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

  // --- Chat Demo (XSS対策済み) ---
  var chatMessages = document.getElementById('chatMessages');
  var chatInput = document.getElementById('chatInput');
  var sendButton = document.getElementById('sendButton');

  var demoResponses = {
    'おすすめ': '今日はカレーはいかがですか？🍛',
    'ai': 'AI（人工知能）は、コンピュータが人間のように考えるプログラムです。',
    'AI': 'AI（人工知能）は、コンピュータが人間のように考えるプログラムです。',
    'default': '興味深いですね！もっと詳しく教えていただけますか？'
  };

  function sendMessage() {
    var userText = chatInput.value.trim();
    if (!userText || !chatMessages) return;

    // ユーザーメッセージ追加（textContentでXSS対策）
    var userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'message user';
    userMsgDiv.textContent = userText;
    chatMessages.appendChild(userMsgDiv);

    // 応答を探す
    var response = demoResponses.default;
    for (var key in demoResponses) {
      if (userText.indexOf(key) !== -1) {
        response = demoResponses[key];
        break;
      }
    }

    // AI応答追加（少し遅延）
    setTimeout(function() {
      var aiMsgDiv = document.createElement('div');
      aiMsgDiv.className = 'message ai';
      aiMsgDiv.textContent = response;
      chatMessages.appendChild(aiMsgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 500);

    chatInput.value = '';
  }

  if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
  }
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  }

  // --- Article Generation Demo (XSS対策済み) ---
  var articleInput = document.getElementById('articleInput');
  var generateButton = document.getElementById('generateButton');
  var articleOutput = document.getElementById('articleOutput');

  var articleTemplates = {
    '仕事': '# 【仕事】で仕事効率化\n\nAIを使って仕事の作業を効率化しましょう。\n例えば、メール作成や議事録の作成に使えます。',
    '学習': '# 【学習】で学習効率アップ\n\n学習にAIを活用する方法をご紹介。\nAIが質問に答えてくれたり、学習計画を立ててくれます。',
    'default': '# 【{{keyword}}】について\n\nAIを使って{{keyword}}について調べてみましょう。'
  };

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
  }

  function generateArticle() {
    var keyword = (articleInput.value && articleInput.value.trim()) || 'AI';
    if (!articleOutput) return;

    // キーワードをサニタイズ
    var safeKeyword = escapeHtml(keyword);

    var template = articleTemplates.default;
    for (var key in articleTemplates) {
      if (keyword.indexOf(key) !== -1) {
        template = articleTemplates[key];
        break;
      }
    }

    // テンプレートを適用
    var markdownText = template.replace(/\{\{keyword\}\}/g, safeKeyword);

    // marked.jsが利用可能な場合のみMarkdownをパース
    if (typeof marked !== 'undefined') {
      articleOutput.innerHTML = marked.parse(markdownText);
    } else {
      // フォールバック: プレーンテキストで表示
      articleOutput.textContent = markdownText;
      console.warn('marked.js not available, using plain text');
    }
  }

  if (generateButton) {
    generateButton.addEventListener('click', generateArticle);
  }
  if (articleInput) {
    articleInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        generateArticle();
      }
    });
  }
})();
