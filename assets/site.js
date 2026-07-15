/* name that ui? · 界面叫啥 — site chrome JS */
(function () {
  "use strict";

  /* ---------- language mode ---------- */
  var MODE_KEY = "ntui-lang-mode";
  function mode() {
    try { return localStorage.getItem(MODE_KEY) || "bilingual"; } catch (e) { return "bilingual"; }
  }
  function applyMode(m) {
    document.documentElement.setAttribute("data-lang-mode", m);
    document.querySelectorAll(".ls-btn").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-mode") === m);
    });
    var input = document.getElementById("search");
    if (input) {
      var ph = m === "en" ? input.getAttribute("data-ph-en")
        : m === "zh" ? input.getAttribute("data-ph-zh")
        : input.getAttribute("data-ph-zh") + " / " + input.getAttribute("data-ph-en");
      input.setAttribute("placeholder", ph);
    }
  }
  document.querySelectorAll(".ls-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      var m = b.getAttribute("data-mode");
      try { localStorage.setItem(MODE_KEY, m); } catch (e) {}
      applyMode(m);
    });
  });
  applyMode(mode());

  /* ---------- homepage search / tabs / surprise ---------- */
  var indexEl = document.getElementById("search-index");
  if (indexEl) {
    var INDEX = JSON.parse(indexEl.textContent);
    var bySlug = {};
    INDEX.forEach(function (it) { bySlug[it.slug] = it; });
    var cards = Array.prototype.slice.call(document.querySelectorAll(".card[data-platform]"));
    var searchInput = document.getElementById("search");
    var noResult = document.getElementById("no-result");
    var tabBtns = Array.prototype.slice.call(document.querySelectorAll(".tab[data-filter]"));
    var state = { q: "", platform: "all" };

    function score(item, q) {
      var s = 0;
      function has(str) { return str && str.toLowerCase().indexOf(q) !== -1; }
      if (has(item.name)) s += 100;
      if (has(item.name_zh)) s += 95;
      (item.aka || []).forEach(function (a) { if (has(a)) s += 60; });
      (item.aka_zh || []).forEach(function (a) { if (has(a)) s += 55; });
      (item.fuzzy || []).forEach(function (f) { if (has(f)) s += 40; });
      (item.fuzzy_zh || []).forEach(function (f) { if (has(f)) s += 38; });
      if (has(item.tagline)) s += 20;
      if (has(item.tagline_zh)) s += 18;
      return s;
    }

    function apply() {
      var q = state.q.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var slug = card.getAttribute("href").split("/").filter(Boolean).pop();
        var item = bySlug[slug];
        var ok = state.platform === "all" || card.getAttribute("data-platform") === state.platform;
        if (ok && q) ok = score(item, q) > 0;
        card.style.display = ok ? "" : "none";
        if (ok) visible++;
      });
      if (noResult) noResult.hidden = visible !== 0;
    }

    if (searchInput) {
      searchInput.addEventListener("input", function () { state.q = searchInput.value; apply(); });
    }
    tabBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        tabBtns.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        state.platform = btn.getAttribute("data-filter");
        apply();
      });
    });
    // deep link ?platform=web
    var qp = new URLSearchParams(location.search).get("platform");
    if (qp === "web" || qp === "macos") {
      state.platform = qp;
      tabBtns.forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-filter") === qp); });
      apply();
    }

    var surprise = document.getElementById("surprise");
    if (surprise) {
      surprise.addEventListener("click", function () {
        var pool = INDEX.filter(function (it) {
          return state.platform === "all" || it.platform === state.platform;
        });
        var pick = pool[Math.floor(Math.random() * pool.length)];
        if (pick) location.href = pick.url;
      });
    }
  }

  /* ---------- copy buttons ---------- */
  function flash(btn, done) {
    var en = btn.querySelector(".lang-en");
    var zh = btn.querySelector(".lang-zh");
    var oEn = en ? en.textContent : btn.textContent;
    var oZh = zh ? zh.textContent : "";
    btn.classList.add("done");
    if (en) en.textContent = btn.getAttribute("data-done-en") || "Copied";
    if (zh) zh.textContent = btn.getAttribute("data-done-zh") || "已复制";
    if (!en && !zh) btn.textContent = btn.getAttribute("data-done-en") || "Copied";
    setTimeout(function () {
      btn.classList.remove("done");
      if (en) en.textContent = oEn;
      if (zh) zh.textContent = oZh;
    }, 1600);
  }
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = document.getElementById(btn.getAttribute("data-copy"));
      if (!target) return;
      navigator.clipboard.writeText(target.textContent).then(function () { flash(btn); }, function () {});
    });
  });
  var copyMd = document.getElementById("copy-md");
  if (copyMd) {
    copyMd.addEventListener("click", function () {
      var tpl = document.getElementById("md-source");
      if (!tpl) return;
      navigator.clipboard.writeText(tpl.innerHTML).then(function () { flash(copyMd); }, function () {});
    });
  }

  /* ---------- translate table filter ---------- */
  var tableInput = document.getElementById("table-search");
  if (tableInput) {
    var rows = Array.prototype.slice.call(document.querySelectorAll("#translate-table tbody tr"));
    var cnt = document.getElementById("table-count");
    var cntZh = document.getElementById("table-count-zh");
    tableInput.addEventListener("input", function () {
      var q = tableInput.value.trim().toLowerCase();
      var n = 0;
      rows.forEach(function (r) {
        var ok = !q || r.getAttribute("data-search").indexOf(q) !== -1;
        r.style.display = ok ? "" : "none";
        if (ok) n++;
      });
      if (cnt) cnt.textContent = cnt.getAttribute("data-tpl").replace("{n}", n).replace("{total}", rows.length);
      if (cntZh) cntZh.textContent = cntZh.getAttribute("data-tpl").replace("{n}", n).replace("{total}", rows.length);
    });
  }

  /* ---------- double-press a word: plain-English definition ---------- */
  var pop = document.getElementById("def-pop");
  var popWord = document.getElementById("def-word");
  var popBody = document.getElementById("def-body");
  var popSrc = document.getElementById("def-src");
  var hideTimer = null;

  function hidePop() { if (pop) pop.hidden = true; }
  function selectedWord() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed) return "";
    var txt = sel.toString().trim();
    var m = txt.match(/[A-Za-z][A-Za-z\-']*/);
    return m ? m[0].toLowerCase() : "";
  }
  document.addEventListener("dblclick", function (ev) {
    if (!pop) return;
    var w = selectedWord();
    if (!w || w.length < 2) { hidePop(); return; }
    popWord.textContent = w;
    popBody.textContent = "Looking up… / 查询中……";
    popSrc.textContent = "plain-English definition";
    pop.hidden = false;
    var x = Math.min(ev.clientX + 12, window.innerWidth - 340);
    var y = Math.min(ev.clientY + 14, window.innerHeight - 160);
    pop.style.left = Math.max(8, x) + "px";
    pop.style.top = Math.max(8, y) + "px";
    clearTimeout(hideTimer);
    fetch("https://api.dictionaryapi.dev/api/v2/entries/en/" + encodeURIComponent(w))
      .then(function (r) { if (!r.ok) throw new Error("nf"); return r.json(); })
      .then(function (data) {
        var meanings = data[0] && data[0].meanings || [];
        var out = [];
        for (var i = 0; i < meanings.length && out.length < 2; i++) {
          var d = meanings[i].definitions && meanings[i].definitions[0];
          if (d) out.push("(" + meanings[i].partOfSpeech + ") " + d.definition);
        }
        popBody.textContent = out.length ? out.join("\n") : "No definition found. / 未找到释义。";
      })
      .catch(function () {
        popBody.textContent = "No definition found. / 未找到释义（网络不可用）。";
      });
    hideTimer = setTimeout(hidePop, 9000);
  });
  document.addEventListener("click", function (ev) {
    if (pop && !pop.hidden && !pop.contains(ev.target)) hidePop();
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") hidePop();
  });
})();
