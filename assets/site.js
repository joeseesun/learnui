/* Learn UI Name · 界面叫啥 — site chrome JS */
(function () {
  "use strict";

  /* ---------- service worker (PWA) ---------- */
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {});
    });
  }

  /* ---------- language mode ---------- */
  var MODE_KEY = "ntui-lang-mode";
  // 首次访问（无本地偏好）按浏览器语言决定：中文环境 → 纯中文，其他 → 纯英文。
  // 与 <head> 内联探测脚本保持一致；用户手动切换后才写 localStorage。
  function detectMode() {
    var langs = navigator.languages || [navigator.language || ""];
    for (var i = 0; i < langs.length; i++) {
      if (/^zh/i.test(langs[i])) return "zh";
    }
    return "en";
  }
  function mode() {
    try { return localStorage.getItem(MODE_KEY) || detectMode(); } catch (e) { return detectMode(); }
  }
  function applyMode(m) {
    document.documentElement.setAttribute("data-lang-mode", m);
    document.querySelectorAll(".ls-btn").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-mode") === m);
    });
    var input = document.getElementById("search") || document.getElementById("style-search");
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

  /* ---------- keyboard: / or ⌘K focuses search, Esc clears ---------- */
  document.addEventListener("keydown", function (ev) {
    var tag = (ev.target.tagName || "").toLowerCase();
    var typing = tag === "input" || tag === "textarea" || ev.target.isContentEditable;
    if ((ev.key === "/" && !typing) || ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k")) {
      var inp = document.getElementById("search") || document.getElementById("style-search") || document.getElementById("table-search");
      if (inp) { ev.preventDefault(); inp.focus(); inp.select(); }
    }
    if (ev.key === "Escape" && typing) {
      var active = document.activeElement;
      if (active && (active.id === "search" || active.id === "style-search" || active.id === "table-search")) {
        if (active.value) { active.value = ""; active.dispatchEvent(new Event("input")); }
        active.blur();
      }
    }
  });

  function debounce(fn, ms) {
    var t = null;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, ms);
    };
  }

  function syncURL(params) {
    if (!history.replaceState) return;
    var url = new URL(location.href);
    Object.keys(params).forEach(function (k) {
      if (params[k]) url.searchParams.set(k, params[k]);
      else url.searchParams.delete(k);
    });
    history.replaceState(null, "", url);
  }

  function highlightEl(el, q) {
    if (!el) return;
    if (!el.hasAttribute("data-orig")) el.setAttribute("data-orig", el.innerHTML);
    else el.innerHTML = el.getAttribute("data-orig");
    if (!q) return;
    var txt = el.textContent;
    var i = txt.toLowerCase().indexOf(q);
    if (i === -1) return;
    var before = txt.slice(0, i), hit = txt.slice(i, i + q.length), after = txt.slice(i + q.length);
    el.textContent = "";
    el.appendChild(document.createTextNode(before));
    var mark = document.createElement("mark");
    mark.textContent = hit;
    el.appendChild(mark);
    el.appendChild(document.createTextNode(after));
  }

  /* ---------- homepage search / tabs / surprise ---------- */
  var indexEl = document.getElementById("search-index");
  if (indexEl) {
    var INDEX = JSON.parse(indexEl.textContent);
    var bySlug = {};
    INDEX.forEach(function (it) { bySlug[it.slug] = it; });
    var cards = Array.prototype.slice.call(document.querySelectorAll(".card[data-platform]"));
    var searchInput = document.getElementById("search");
    var noResult = document.getElementById("no-result");
    var countNote = document.getElementById("count-note");
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
      if (has(item.symbol)) s += 30;
      if (has(item.tagline)) s += 20;
      if (has(item.tagline_zh)) s += 18;
      return s;
    }

    function matchReason(item, q) {
      function has(str) { return str && str.toLowerCase().indexOf(q) !== -1; }
      if (has(item.name) || has(item.name_zh)) return "";
      var pools = [["aka", item.aka], ["aka", item.aka_zh], ["fuzzy", item.fuzzy], ["fuzzy", item.fuzzy_zh]];
      for (var p = 0; p < pools.length; p++) {
        var arr = pools[p][1] || [];
        for (var i = 0; i < arr.length; i++) {
          if (has(arr[i])) return pools[p][0] + ": “" + arr[i] + "”";
        }
      }
      if (has(item.symbol)) return "symbol: " + item.symbol;
      return "";
    }

    function apply() {
      var q = state.q.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var slug = card.getAttribute("data-slug") || card.getAttribute("href").split("/").filter(Boolean).pop();
        var item = bySlug[slug];
        var ok = state.platform === "all" || card.getAttribute("data-platform") === state.platform;
        if (ok && q) ok = score(item, q) > 0;
        card.style.display = ok ? "" : "none";

        // highlight + match reason
        highlightEl(card.querySelector(".card-name .lang-en"), q && ok ? q : "");
        highlightEl(card.querySelector(".card-name-zh"), q && ok ? q : "");
        highlightEl(card.querySelector(".card-symbol"), q && ok ? q : "");
        card.querySelectorAll(".card-tag").forEach(function (el) { highlightEl(el, q && ok ? q : ""); });
        var mEl = card.querySelector(".card-match");
        if (ok && q) {
          var reason = matchReason(item, q);
          if (reason) {
            if (!mEl) {
              mEl = document.createElement("p");
              mEl.className = "card-match";
              card.querySelector(".card-meta").appendChild(mEl);
            }
            mEl.textContent = reason;
            mEl.hidden = false;
          } else if (mEl) { mEl.hidden = true; }
        } else if (mEl) { mEl.hidden = true; }

        if (ok) visible++;
      });
      if (noResult) noResult.hidden = visible !== 0;
      if (countNote) {
        countNote.querySelectorAll("[data-tpl]").forEach(function (el) {
          el.textContent = el.getAttribute("data-tpl").replace("{n}", q ? visible + " / " + INDEX.length : visible);
        });
      }
    }

    var applyDebounced = debounce(apply, 80);
    var syncDebounced = debounce(function () {
      syncURL({ q: state.q.trim() || null, platform: state.platform === "all" ? null : state.platform });
    }, 200);

    if (searchInput) {
      searchInput.addEventListener("input", function () {
        state.q = searchInput.value;
        applyDebounced();
        syncDebounced();
      });
    }
    tabBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        tabBtns.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        state.platform = btn.getAttribute("data-filter");
        apply();
        syncDebounced();
      });
    });
    // deep links ?platform=web&q=...
    var params = new URLSearchParams(location.search);
    var qp = params.get("platform");
    if (qp === "web" || qp === "macos") {
      state.platform = qp;
      tabBtns.forEach(function (b) { b.classList.toggle("active", b.getAttribute("data-filter") === qp); });
    }
    var qq = params.get("q");
    if (qq && searchInput) {
      searchInput.value = qq;
      state.q = qq;
    }
    if (qp || qq) apply();

    // no-result example chips
    document.querySelectorAll(".no-result-examples button[data-q]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (!searchInput) return;
        searchInput.value = btn.getAttribute("data-q");
        state.q = searchInput.value;
        apply();
        syncDebounced();
        searchInput.focus();
      });
    });

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

  /* ---------- styles atlas search ---------- */
  var styleInput = document.getElementById("style-search");
  if (styleInput) {
    var sCards = Array.prototype.slice.call(document.querySelectorAll(".style-card"));
    var sNoResult = document.getElementById("style-no-result");
    var sCount = document.getElementById("style-count");
    var sApply = function () {
      var q = styleInput.value.trim().toLowerCase();
      var n = 0;
      sCards.forEach(function (c) {
        var ok = !q || (c.getAttribute("data-search") || "").indexOf(q) !== -1;
        c.style.display = ok ? "" : "none";
        if (ok) n++;
      });
      if (sNoResult) sNoResult.hidden = n !== 0;
      if (sCount) {
        sCount.querySelectorAll("[data-tpl]").forEach(function (el) {
          el.textContent = el.getAttribute("data-tpl").replace("{n}", q ? n + " / " + sCards.length : n);
        });
      }
    };
    var sApplyD = debounce(sApply, 80);
    var sSyncD = debounce(function () {
      syncURL({ q: styleInput.value.trim() || null });
    }, 200);
    styleInput.addEventListener("input", function () { sApplyD(); sSyncD(); });
    var sq = new URLSearchParams(location.search).get("q");
    if (sq) { styleInput.value = sq; sApply(); }
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
    tableInput.addEventListener("input", debounce(function () {
      var q = tableInput.value.trim().toLowerCase();
      var n = 0;
      rows.forEach(function (r) {
        var ok = !q || r.getAttribute("data-search").indexOf(q) !== -1;
        r.style.display = ok ? "" : "none";
        if (ok) n++;
      });
      if (cnt) cnt.textContent = cnt.getAttribute("data-tpl").replace("{n}", n).replace("{total}", rows.length);
      if (cntZh) cntZh.textContent = cntZh.getAttribute("data-tpl").replace("{n}", n).replace("{total}", rows.length);
    }, 80));
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
