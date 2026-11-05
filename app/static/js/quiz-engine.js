/**
 * Placement Portal — Quiz Engine Modernization
 * ============================================
 * Adds the "high-velocity developer platform" layer to the existing quiz
 * flows (timed mock test `take.html` and full-length palette `quiz.html`):
 *
 *   1. Keyboard-first navigation (Vim-style)
 *      - J / K  or  ↓ / ↑  → move between questions
 *      - 1–4              → select option A/B/C/D in the focused question
 *      - Enter             → confirm / advance to next question (palette mode)
 *      - Ctrl/Cmd + Enter  → submit the quiz
 *      - Space             → flag the current question (bookmark via POST)
 *      - /                 → open the global command palette (handled by
 *                            palette.js; this module only avoids swallowing it)
 *
 *   2. State persistence & resilience
 *      - Selected answers are persisted to localStorage on every change and
 *        restored on load, so a refresh or network drop never wipes progress.
 *      - The state is keyed per attempt (category + question set) so a stale
 *        attempt can never leak into a newer quiz.
 *
 *   3. Inspectable, non-intrusive
 *      - The module hooks into the existing DOM and globals (`navigate`,
 *        `confirmSubmit`) instead of replacing them.
 */
(function () {
  "use strict";

  var form = document.getElementById("quizForm");
  if (!form) return;

  var STORE_KEY = "pp_quiz_session";
  // Palette flow has .question-wrapper cards; the mock test uses .question-card.
  var isPalette = !!document.querySelector("#quizForm .question-wrapper");

  /* ------------------------------------------------------------------ *
   *  localStorage persistence
   * ------------------------------------------------------------------ */

  function keyFor() {
    var cat = form.dataset.quizKey || "generic";
    var names = [];
    var radios = form.querySelectorAll('input[type="radio"]');
    for (var i = 0; i < radios.length; i++) {
      var n = radios[i].getAttribute("name") || "";
      if (names.indexOf(n) === -1) names.push(n);
    }
    return "quiz:" + cat + ":" + names.length + ":" + names.sort().join(",");
  }

  var activeKey = keyFor();
  var state = {};

  function persist() {
    try {
      var store = {};
      var raw = localStorage.getItem(STORE_KEY);
      if (raw) store = JSON.parse(raw) || {};
      // Grow a bounded store: keep at most 8 recent attempt states.
      var keys = Object.keys(store);
      if (keys.length >= 8 && store[activeKey] === undefined) {
        delete store[keys[0]];
      }
      store[activeKey] = state;
      localStorage.setItem(STORE_KEY, JSON.stringify(store));
    } catch (e) {
      /* storage unavailable / quota — degrade gracefully */
    }
  }

  function restore() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      if (!raw) return;
      var store = JSON.parse(raw);
      state = store[activeKey] || {};
    } catch (e) {
      state = {};
    }

    var radios = form.querySelectorAll('input[type="radio"]');
    for (var i = 0; i < radios.length; i++) {
      var el = radios[i];
      var name = el.getAttribute("name");
      if (state[name] && el.value === state[name]) el.checked = true;
    }
  }

  /* ------------------------------------------------------------------ *
   *  Mock-test answer counter
   * ------------------------------------------------------------------ */

  function updateCount() {
    var el = document.getElementById("answerCount");
    if (!el) return;
    var checked = form.querySelectorAll('input[type="radio"]:checked').length;
    var total = form.querySelectorAll('input[type="radio"]').length;
    el.textContent = "Answered " + checked + " / " + total;
    var btn = form.querySelector('button[type="submit"]');
    if (btn)
      btn.classList.toggle("all-answered", checked > 0 && checked === total);
  }

  /* ------------------------------------------------------------------ *
   *  Capture saves (one listener for both modes)
   * ------------------------------------------------------------------ */

  form.addEventListener("change", function (e) {
    if (e.target.type !== "radio") return;
    state[e.target.getAttribute("name")] = e.target.value;
    persist();
    updateCount();
  });

  /* ------------------------------------------------------------------ *
   *  Keyboard model
   * ------------------------------------------------------------------ */

  function visibleQuestionCards() {
    if (isPalette) {
      return Array.prototype.slice
        .call(document.querySelectorAll("#quizForm .question-wrapper"))
        .filter(function (w) {
          return w.style.display !== "none";
        });
    }
    return Array.prototype.slice.call(
      document.querySelectorAll("#quizForm .question-card"),
    );
  }

  function radioGroupOf(el) {
    var name = el.getAttribute("name");
    return form.querySelectorAll('input[type="radio"][name="' + name + '"]');
  }

  function currentGroup() {
    var q = visibleQuestionCards();
    if (!q.length) return null;
    var radios = q[0].querySelectorAll('input[type="radio"]');
    return radios.length ? radios : null;
  }

  function currentQuestionIndex() {
    var cards = document.querySelectorAll("#quizForm .question-wrapper");
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].style.display !== "none") return i;
    }
    return -1;
  }

  function advancePalette(dir) {
    if (typeof window.navigate === "function") window.navigate(dir);
  }

  function moveMockFocus(dir) {
    var cards = document.querySelectorAll("#quizForm .question-card");
    var idx = -1;
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].contains(document.activeElement)) {
        idx = i;
        break;
      }
    }
    var start = idx < 0 ? 0 : idx;
    var next = Math.max(0, Math.min(cards.length - 1, start + dir));
    var radios = cards[next].querySelectorAll('input[type="radio"]');
    if (radios.length) radios[0].focus();
    if (document.body.scrollTop > 0) {
      cards[next].scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  function submitQuiz() {
    if (typeof window.confirmSubmit === "function" && !window.confirmSubmit())
      return;
    form.submit();
  }

  /* ------------------------------------------------------------------ *
   *  Inline bookmark / flagging (Space)
   * ------------------------------------------------------------------ */

  function toggleFlagOnCurrent() {
    var radio = null;
    var a = document.activeElement;
    if (a && a.type === "radio") radio = a;
    if (!radio) {
      var grp = currentGroup();
      if (grp && grp.length) radio = grp[0];
    }
    if (!radio) return;
    var name = radio.getAttribute("name") || "";
    var m = name.match(/question_(\d+)/);
    if (!m) return;
    var qid = m[1];
    var csrf = document.querySelector('meta[name="csrf-token"]');
    var token = csrf ? csrf.getAttribute("content") : "";

    fetch("/quiz/bookmark/" + qid, {
      method: "POST",
      headers: {
        "X-CSRFToken": token,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "csrf_token=" + encodeURIComponent(token),
      credentials: "same-origin",
    })
      .then(function (res) {
        if (res.ok || res.redirected) {
          if (window.QuizSounds) QuizSounds.bookmark();
          pulseFlag(radio);
        }
      })
      .catch(function () {});
  }

  function pulseFlag(radio) {
    var card = radio.closest(".question-card, .question-wrapper");
    if (!card) return;
    card.classList.remove("flag-pulse");
    void card.offsetWidth;
    card.classList.add("flag-pulse");
    setTimeout(function () {
      card.classList.remove("flag-pulse");
    }, 700);
  }

  /* ------------------------------------------------------------------ *
   *  keydown handler
   * ------------------------------------------------------------------ */

  document.addEventListener("keydown", function (e) {
    var t = e.target;

    // Never hijack typing inside text fields.
    if (
      t &&
      (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)
    ) {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        submitQuiz();
      }
      return;
    }

    var k = e.key.toLowerCase();

    // Ctrl/Cmd + Enter → submit.
    if (k === "enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      submitQuiz();
      return;
    }

    // J/K or ↓/↑ → move between questions.
    if (e.key === "j" || e.key === "ArrowDown") {
      e.preventDefault();
      if (isPalette) advancePalette(1);
      else moveMockFocus(1);
      return;
    }
    if (e.key === "k" || e.key === "ArrowUp") {
      e.preventDefault();
      if (isPalette) advancePalette(-1);
      else moveMockFocus(-1);
      return;
    }

    // 1–4 → select option in the focused / current group.
    if (["1", "2", "3", "4"].indexOf(e.key) !== -1) {
      var group = t && t.type === "radio" ? radioGroupOf(t) : currentGroup();
      if (group && group.length >= parseInt(e.key, 10)) {
        e.preventDefault();
        var radio = group[parseInt(e.key, 10) - 1];
        radio.checked = true;
        radio.dispatchEvent(new Event("change", { bubbles: true }));
        if (window.QuizSounds) QuizSounds.select();
      }
      return;
    }

    // Enter → advance in palette mode.
    if (k === "enter" && isPalette) {
      e.preventDefault();
      advancePalette(1);
      return;
    }

    // Space → flag current question.
    if (e.key === " ") {
      e.preventDefault();
      toggleFlagOnCurrent();
      return;
    }
  });

  /* ------------------------------------------------------------------ *
   *  Init
   * ------------------------------------------------------------------ */

  restore();
  updateCount();
})();
