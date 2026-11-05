/**
 * Placement Portal — Duel Room client
 * ====================================
 * Countdown timer, keyboard-first navigation (J/K, 1–4), and localStorage
 * persistence so a refresh never wipes your duel progress.
 */
(function () {
  "use strict";

  var room = window.DUEL_ROOM || {};
  var cards = Array.prototype.slice.call(document.querySelectorAll(".duel-qcard"));
  var qTabs = Array.prototype.slice.call(document.querySelectorAll(".duel-q"));
  var timerEl = document.getElementById("duelTimer");
  var statusEl = document.getElementById("duelStatus");
  var finishedBox = document.getElementById("duelFinished");
  var submitBtn = document.getElementById("duelSubmitBtn");
  var scoreBtn = document.getElementById("duelScoreBtn");
  if (!cards.length) return;

  var STORE_KEY = "pp_duel_" + room.code;
  var state = loadState();
  var currentIdx = state.currentIdx != null ? state.currentIdx : 0;

  function loadState() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      if (raw) return JSON.parse(raw) || {};
    } catch (e) {}
    return { answers: {}, flags: [], startedAt: Date.now(), remaining: null, currentIdx: 0 };
  }

  function persist() {
    state.currentIdx = currentIdx;
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  /* ---------- Timer ---------- */

  var totalMs = room.duration_min * 60 * 1000;
  var remaining = state.remaining != null ? state.remaining : totalMs;

  function tick() {
    if (room.status !== "active") {
      if (timerEl) timerEl.textContent = "--:--";
      if (statusEl) statusEl.textContent = "waiting for opponent";
      return;
    }
    var elapsed = Date.now() - state.startedAt;
    remaining = Math.max(0, totalMs - elapsed);
    if (timerEl) {
      var s = Math.ceil(remaining / 1000);
      var m = Math.floor(s / 60);
      s = s % 60;
      timerEl.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
      if (remaining <= 30000 && remaining > 0) {
        timerEl.style.color = "#e63946";
        if (window.QuizSounds && s % 5 === 0) QuizSounds.timerWarning();
      }
    }
    if (remaining <= 0) {
      finish();
      return;
    }
    persist();
  }

  /* ---------- View switching ---------- */

  function show(idx) {
    currentIdx = Math.max(0, Math.min(cards.length - 1, idx));
    cards.forEach(function (c, i) { c.style.display = i === currentIdx ? "block" : "none"; });
    qTabs.forEach(function (t, i) {
      t.style.background = i === currentIdx ? "#111111" : "#fbf9f5";
      t.style.color = i === currentIdx ? "#fbf9f5" : "#111";
    });
    persist();
  }

  function saveAnswer(idx) {
    var card = cards[idx];
    if (!card) return;
    var ta = card.querySelector(".duel-answer");
    if (ta) {
      state.answers[ta.getAttribute("data-qid")] = ta.value;
      persist();
    }
  }

  function restoreAnswers() {
    cards.forEach(function (card, idx) {
      var ta = card.querySelector(".duel-answer");
      if (ta) {
        var qid = ta.getAttribute("data-qid");
        if (state.answers[qid] != null) ta.value = state.answers[qid];
        ta.addEventListener("input", function () { saveAnswer(idx); });
      }
      var btn = qTabs[idx];
      if (btn) btn.addEventListener("click", function () { show(idx); });
    });
  }

  /* ---------- Keyboard ---------- */

  document.addEventListener("keydown", function (e) {
    if (finishedBox && finishedBox.style.display !== "none") {
      if (e.key === "Enter") { e.preventDefault(); showScore(); }
      return;
    }
    var t = e.target;
    if (t && (t.tagName === "TEXTAREA" || t.tagName === "INPUT" || t.isContentEditable)) {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); submit(); }
      return;
    }
    var k = e.key.toLowerCase();
    if (k === "enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); submit(); return; }
    if (e.key === "j" || e.key === "ArrowDown") { e.preventDefault(); show(currentIdx + 1); return; }
    if (e.key === "k" || e.key === "ArrowUp") { e.preventDefault(); show(currentIdx - 1); return; }
    if (["1", "2", "3", "4"].indexOf(e.key) !== -1) {
      // focus the answer box (placeholder for option select in a duel)
      var card = cards[currentIdx];
      if (card) {
        var ta = card.querySelector(".duel-answer");
        if (ta) { e.preventDefault(); ta.focus(); if (window.QuizSounds) QuizSounds.select(); }
      }
      return;
    }
    if (e.key === "Enter") { e.preventDefault(); show(currentIdx + 1); return; }
  });

  /* ---------- Submit / score ---------- */

  function submit() {
    saveAnswer(currentIdx);
    finish(true);
  }

  function finish(manual) {
    if (finishedBox && finishedBox.style.display === "none") {
      finishedBox.style.display = "block";
      if (statusEl) statusEl.textContent = "finished";
      cards.forEach(function (c) { c.style.display = "none"; });
      if (manual && window.QuizSounds) QuizSounds.fanfare();
    }
    persist();
  }

  function showScore() {
    var answered = Object.keys(state.answers).filter(function (k) {
      return (state.answers[k] || "").trim().length > 0;
    }).length;
    var pct = Math.round((answered / cards.length) * 100);
    var msg = "You filled in " + answered + " of " + cards.length + " questions (" + pct + "%).\n\n";
    msg += "In a live duel, your opponent's answers are compared on the same set.\n";
    msg += "Review your answers for completeness before the real round.";

    if (finishedBox) {
      finishedBox.innerHTML = "";
      var title = document.createElement("div");
      title.style.fontFamily = "'Fraunces', serif";
      title.style.fontWeight = "900";
      title.style.fontSize = "1.8rem";
      title.style.color = "#111";
      title.style.textAlign = "center";
      title.textContent = "Duel summary";
      var text = document.createElement("p");
      text.style.textAlign = "center";
      text.style.fontSize = ".9rem";
      text.style.color = "var(--text-light)";
      text.style.margin = ".8rem 0";
      text.style.whiteSpace = "pre-line";
      text.textContent = msg;
      var big = document.createElement("div");
      big.style.textAlign = "center";
      big.style.fontFamily = "'JetBrains Mono', monospace";
      big.style.fontWeight = "700";
      big.style.fontSize = "2.4rem";
      big.style.color = pct >= 70 ? "#2bb673" : "#e63946";
      big.textContent = pct + "%";
      finishedBox.appendChild(big);
      finishedBox.appendChild(title);
      finishedBox.appendChild(text);
    }
  }

  if (submitBtn) submitBtn.addEventListener("click", submit);
  if (scoreBtn) scoreBtn.addEventListener("click", showScore);

  /* ---------- Init ---------- */

  restoreAnswers();
  show(currentIdx);
  if (room.status === "active") setInterval(tick, 500);
  else if (timerEl) tick();
})();
