/* Learn UI Name · 界面叫啥 — quiz engine */
(function () {
  "use strict";
  var DATA = window.QUIZ_DATA;
  if (!DATA || !document.getElementById("quiz-card")) return;

  var ITEMS = DATA.items;
  var I18N = DATA.i18n;
  var STORE_KEY = "ntui-quiz-v1";
  var MASTER_STREAK = 2;      // consecutive correct answers to master an item
  var REVIEW_RATIO = 0.15;    // chance to pull a mastered item back for review
  var RECENT = 4;             // don't repeat the last N answers

  var bySlug = {};
  ITEMS.forEach(function (it) { bySlug[it.s] = it; });

  /* ---------- persistent mastery store ---------- */
  var store = {};
  try { store = JSON.parse(localStorage.getItem(STORE_KEY) || "{}") || {}; } catch (e) { store = {}; }
  function save() { try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e) {} }
  function st(slug) {
    return store[slug] || { s: 0, m: 0, ok: 0, seen: 0, last: 0 };
  }

  /* ---------- state ---------- */
  var mode = "mixed";                    // components | styles | mixed
  var session = { n: 0, ok: 0, streak: 0 };
  var recent = [];
  var cur = null;                        // { item, dir, choices:[slug], answered, correctSlug }
  var els = {
    q: document.getElementById("quiz-q"),
    stage: document.getElementById("quiz-stage"),
    choices: document.getElementById("quiz-choices"),
    fb: document.getElementById("quiz-fb"),
    link: document.getElementById("quiz-link"),
    next: document.getElementById("quiz-next"),
    sess: document.getElementById("q-session"),
    streak: document.getElementById("q-streak"),
    mfill: document.getElementById("q-mastery-fill"),
    mn: document.getElementById("q-mastery-n"),
    reset: document.getElementById("q-reset")
  };

  /* ---------- i18n helpers ---------- */
  function langMode() {
    var m = document.documentElement.getAttribute("data-lang-mode");
    return m === "en" || m === "zh" ? m : "bilingual";
  }
  function tr(key) {
    var pair = I18N[key] || [key, ""];
    var m = langMode();
    if (m === "en") return pair[0];
    if (m === "zh") return pair[1] || pair[0];
    return pair[1] ? pair[0] + " · " + pair[1] : pair[0];
  }
  function itemLabel(it) {
    var m = langMode();
    if (m === "en") return it.en;
    if (m === "zh") return it.zh;
    return it.en + '<span class="qchoice-zh">' + it.zh + "</span>";
  }

  /* ---------- pool & picking ---------- */
  function inMode(it) {
    if (mode === "components") return it.k === "c";
    if (mode === "styles") return it.k === "s";
    return true;
  }
  function pool() { return ITEMS.filter(inMode); }
  function masteredIn(p) { return p.filter(function (it) { return st(it.s).m; }).length; }

  function pickItem() {
    var p = pool();
    var un = p.filter(function (it) { return !st(it.s).m; });
    var mastered = p.filter(function (it) { return st(it.s).m; });
    var use;
    if (un.length && (Math.random() >= REVIEW_RATIO || !mastered.length)) {
      use = un;
    } else if (mastered.length) {
      use = mastered.slice().sort(function (a, b) { return st(a.s).last - st(b.s).last; });
      use = use.slice(0, Math.max(4, Math.ceil(use.length / 3))); // oldest third
    } else {
      use = p;
    }
    var cand = use.filter(function (it) { return recent.indexOf(it.s) < 0; });
    if (!cand.length) cand = use;
    var unseen = cand.filter(function (it) { return !st(it.s).seen; });
    var from = unseen.length ? unseen : cand;
    return from[Math.floor(Math.random() * from.length)];
  }

  function pickDistractors(item) {
    var same = ITEMS.filter(function (it) { return it.k === item.k && it.s !== item.s; });
    // shuffle
    for (var i = same.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = same[i]; same[i] = same[j]; same[j] = tmp;
    }
    return same.slice(0, 3).map(function (it) { return it.s; });
  }

  /* ---------- rendering ---------- */
  function specIframe(slug) {
    var f = document.createElement("iframe");
    f.src = "/specimen/" + slug + "/";
    // 同源可信内容：allow-same-origin 让 @font-face 等同源资源可加载；
    // 仍禁 top navigation / 弹窗 / 表单。
    f.setAttribute("sandbox", "allow-scripts allow-same-origin");
    f.setAttribute("loading", "lazy");
    f.setAttribute("scrolling", "no");
    f.title = "specimen";
    return f;
  }

  function renderQuestion() {
    var item = cur.item;
    els.stage.innerHTML = "";
    els.choices.innerHTML = "";
    els.fb.textContent = "";
    els.fb.className = "quiz-fb";
    els.link.hidden = true;
    els.next.hidden = true;

    if (cur.dir === "specimen") {
      // show the specimen, choose its name
      els.q.innerHTML = tr("quizWhatIs");
      var stage = document.createElement("div");
      stage.className = "quiz-stage-single";
      stage.appendChild(specIframe(item.s));
      els.stage.appendChild(stage);
      cur.choices.forEach(function (slug, i) {
        var it = bySlug[slug];
        var b = document.createElement("button");
        b.type = "button";
        b.className = "qchoice";
        b.innerHTML = '<span class="qnum">' + (i + 1) + "</span>" + itemLabel(it);
        b.addEventListener("click", function () { answer(slug, b); });
        els.choices.appendChild(b);
      });
      els.choices.className = "quiz-choices qgrid-names";
    } else {
      // show the name, choose its specimen
      els.q.innerHTML = tr("quizWhichIs") + ' <b class="quiz-q-name">' + itemLabel(item) + "</b>";
      cur.choices.forEach(function (slug, i) {
        var cell = document.createElement("button");
        cell.type = "button";
        cell.className = "qcell";
        cell.setAttribute("aria-label", "choice " + (i + 1));
        var inner = document.createElement("span");
        inner.className = "qcell-frame";
        inner.appendChild(specIframe(slug));
        cell.appendChild(inner);
        var num = document.createElement("span");
        num.className = "qnum qnum-cell";
        num.textContent = i + 1;
        cell.appendChild(num);
        cell.addEventListener("click", function () { answer(slug, cell); });
        els.choices.appendChild(cell);
      });
      els.choices.className = "quiz-choices qgrid-cells";
    }
  }

  function renderStats() {
    els.sess.textContent = session.ok + "/" + session.n;
    els.streak.textContent = session.streak;
    var p = pool();
    var m = masteredIn(p);
    els.mn.textContent = m + "/" + p.length;
    els.mfill.style.width = p.length ? (m / p.length * 100) + "%" : "0%";
  }

  function renderStatic() {
    els.next.textContent = tr("quizNext") + " ⏎";
  }

  /* ---------- answering ---------- */
  function answer(slug, btn) {
    if (cur.answered) return;
    cur.answered = true;
    var item = cur.item;
    var right = slug === item.s;
    var s = st(item.s);
    session.n++;
    if (right) {
      session.ok++;
      session.streak++;
      s.s++;
      s.ok++;
      if (s.s >= MASTER_STREAK) s.m = 1;
    } else {
      session.streak = 0;
      s.s = 0;
      s.m = 0;
    }
    s.seen++;
    s.last = Date.now();
    store[item.s] = s;
    save();

    // paint choices
    Array.prototype.forEach.call(els.choices.children, function (el) {
      var elSlug = cur.choices[Array.prototype.indexOf.call(els.choices.children, el)];
      if (elSlug === item.s) el.classList.add("is-correct");
      else if (el === btn) el.classList.add("is-wrong");
      else el.classList.add("is-dim");
      el.disabled = true;
    });

    var allDone = masteredIn(pool()) === pool().length;
    if (right) {
      els.fb.innerHTML = '<span class="fb-ok">' + tr("quizCorrect") + "</span>" +
        (allDone ? ' <span class="fb-done">' + tr("quizAllDone") + "</span>" : "");
    } else {
      els.fb.innerHTML = '<span class="fb-no">' + tr("quizWrong") + "</span> " +
        tr("quizAnswerWas") + ' <b>' + itemLabel(item) + "</b>";
    }
    els.link.textContent = tr("quizViewEntry") + " →";
    els.link.href = item.u;
    els.link.hidden = false;
    els.next.hidden = false;
    els.next.focus();
    renderStats();
  }

  function next() {
    var item = pickItem();
    recent.push(item.s);
    if (recent.length > RECENT) recent.shift();
    var choices = pickDistractors(item);
    choices.push(item.s);
    // shuffle
    for (var i = choices.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = choices[i]; choices[i] = choices[j]; choices[j] = tmp;
    }
    cur = { item: item, dir: Math.random() < 0.5 ? "specimen" : "name", choices: choices, answered: false };
    renderQuestion();
    renderStats();
  }

  /* ---------- events ---------- */
  document.querySelectorAll(".qmode").forEach(function (b) {
    b.addEventListener("click", function () {
      mode = b.getAttribute("data-qmode");
      document.querySelectorAll(".qmode").forEach(function (x) {
        x.classList.toggle("active", x === b);
      });
      next();
    });
  });

  els.next.addEventListener("click", next);

  els.reset.addEventListener("click", function () {
    pool().forEach(function (it) { delete store[it.s]; });
    save();
    session = { n: 0, ok: 0, streak: 0 };
    recent = [];
    next();
  });

  document.addEventListener("keydown", function (ev) {
    var tag = (ev.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea") return;
    if (cur && !cur.answered && ev.key >= "1" && ev.key <= "4") {
      var idx = parseInt(ev.key, 10) - 1;
      var el = els.choices.children[idx];
      if (el) el.click();
    } else if (cur && cur.answered && ev.key === "Enter") {
      ev.preventDefault();
      next();
    }
  });

  // re-render current question when the site language mode flips
  new MutationObserver(function () {
    if (cur) { renderQuestion(); renderStats(); renderStatic(); }
  }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-lang-mode"] });

  renderStatic();
  next();
})();
