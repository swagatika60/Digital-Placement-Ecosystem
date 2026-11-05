/**
 * Placement Portal — ScopeSentry client analyzer
 * ===============================================
 * Runs the same rule-based risk scan locally so the user sees findings
 * instantly, then posts to /scope-sentry/analyze to persist the audit.
 */
(function () {
  "use strict";

  var textEl = document.getElementById("sentryText");
  var runBtn = document.getElementById("sentryRun");
  var scoreEl = document.getElementById("sentryScore");
  var barEl = document.getElementById("sentryBar");
  var findingsEl = document.getElementById("sentryFindings");
  if (!textEl || !runBtn) return;

  // ── Resume upload session ──────────────────────────────────────
  var dropZone = document.getElementById("sentryDrop");
  var fileInput = document.getElementById("sentryFile");
  var uploadStatus = document.getElementById("sentryUploadStatus");

  function setUploadStatus(msg, ok) {
    if (!uploadStatus) return;
    uploadStatus.textContent = msg || "";
    uploadStatus.style.color = ok ? "#2bb673" : "#e63946";
  }

  function handleFile(file) {
    if (!file) return;
    if (
      !file.name ||
      (!/\.pdf$/i.test(file.name) && !/\.(txt|md)$/i.test(file.name))
    ) {
      setUploadStatus("Please choose a PDF, TXT, or Markdown file.");
      return;
    }
    var csrf = document.querySelector('meta[name="csrf-token"]');
    var form = new FormData();
    form.append("resume", file);
    setUploadStatus("Reading " + file.name + "…");
    fetch("/scope-sentry/upload", {
      method: "POST",
      headers: { "X-CSRFToken": csrf ? csrf.getAttribute("content") : "" },
      body: form,
      credentials: "same-origin",
    })
      .then(function (r) {
        return r.json().then(function (data) {
          if (!r.ok) throw new Error(data.error || "Upload failed.");
          return data;
        });
      })
      .then(function (data) {
        render(data);
        setUploadStatus(
          "Analyzed " + file.name + " → score " + data.score,
          true,
        );
        if (textEl) textEl.value = ""; // clear paste field; focus on file result
      })
      .catch(function (err) {
        console.error("[scope-sentry] upload failed:", err);
        setUploadStatus(err.message || "Could not upload that file.");
      });
  }

  if (dropZone && fileInput) {
    dropZone.addEventListener("click", function () {
      fileInput.click();
    });
    fileInput.addEventListener("change", function () {
      handleFile(fileInput.files && fileInput.files[0]);
    });
    ["dragover", "dragenter"].forEach(function (ev) {
      dropZone.addEventListener(ev, function (e) {
        e.preventDefault();
        dropZone.style.background = "#f4f0ea";
      });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      dropZone.addEventListener(ev, function (e) {
        e.preventDefault();
        dropZone.style.background = "#fffdf8";
      });
    });
    dropZone.addEventListener("drop", function (e) {
      e.preventDefault();
      var file =
        e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) handleFile(file);
    });
  }

  var source = "resume";
  document.querySelectorAll(".src-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      source = btn.getAttribute("data-src");
      document.querySelectorAll(".src-toggle").forEach(function (b) {
        b.style.background = "#fbf9f5";
        b.style.color = "#111";
      });
      btn.style.background = "#111111";
      btn.style.color = "#fbf9f5";
    });
  });

  function analyze(text, src) {
    var lower = text.toLowerCase();
    var findings = [];
    var score = 100;

    function add(severity, title, note) {
      findings.push({ severity: severity, title: title, note: note });
    }

    var metricWords = [
      "improved",
      "increased",
      "reduced",
      "boosted",
      "optimized",
      "enhanced",
    ];
    var hasMetric = metricWords.some(function (w) {
      return lower.indexOf(w) !== -1;
    });
    var hasNumber = /\d/.test(text);

    if (hasMetric && !hasNumber) {
      score -= 20;
      add(
        "high",
        "Improvement claims lack numbers",
        "You say 'improved X' without a metric. Add a baseline → result figure (e.g. 'cut latency 40%').",
      );
    }
    if (!hasMetric && !hasNumber) {
      score -= 15;
      add(
        "medium",
        "No measurable outcomes",
        "No quantified impact anywhere. Recruiters scan for numbers first.",
      );
    }

    var depthTerms = [
      "architecture",
      "schema",
      "api",
      "database",
      "caching",
      "asynchronous",
      "concurrency",
      "load",
      "latency",
      "throughput",
      "algorithm",
      "complexity",
      "distributed",
      "scaling",
    ];
    var foundDepth = depthTerms.filter(function (w) {
      return lower.indexOf(w) !== -1;
    });
    if (!foundDepth.length) {
      score -= 18;
      add(
        "high",
        "No technical surface",
        "None of the expected depth signals appear. Name the stack pieces you actually touched: schema, API, caching, async, complexity.",
      );
    } else if (foundDepth.length < 2) {
      score -= 10;
      add(
        "medium",
        "Thin technical depth",
        "Only " +
          foundDepth.length +
          " technical signal(s): " +
          foundDepth.join(", ") +
          ". Add one or two more concrete implementation details.",
      );
    }

    var filler = [
      "passionate",
      "highly motivated",
      "hardworking",
      "team player",
      "go-getter",
    ];
    if (
      filler.some(function (w) {
        return lower.indexOf(w) !== -1;
      })
    ) {
      score -= 8;
      add(
        "low",
        "Buzzy filler",
        "Generic trait words (passionate, team player…) read as filler. Replace them with a concrete thing you built.",
      );
    }

    if (src === "readme") {
      if (
        lower.indexOf("setup") === -1 &&
        lower.indexOf("install") === -1 &&
        lower.indexOf("getting started") === -1
      ) {
        score -= 10;
        add(
          "medium",
          "Missing setup instructions",
          "A good README is runnable. Add a Setup/Install section so a reviewer can run the project in minutes.",
        );
      }
      if (
        lower.indexOf("api") !== -1 &&
        lower.indexOf("authentication") === -1 &&
        lower.indexOf("auth") === -1
      ) {
        score -= 6;
        add(
          "low",
          "Auth unspecified",
          "You mention an API but not authentication. Even a half-line on how requests are authorized matters.",
        );
      }
    }

    score = Math.max(0, Math.min(100, score));
    var rank = { high: 0, medium: 1, low: 2 };
    findings.sort(function (a, b) {
      return rank[a.severity] - rank[b.severity];
    });
    return { score: score, findings: findings };
  }

  function render(result) {
    if (scoreEl) scoreEl.textContent = result.score;
    var pct = result.score;
    if (barEl) barEl.style.width = pct + "%";
    if (!findingsEl) return;

    findingsEl.innerHTML = "";
    if (!result.findings.length) {
      var ok = document.createElement("p");
      ok.style.fontFamily = "'JetBrains Mono', monospace";
      ok.style.fontSize = ".8rem";
      ok.style.color = "#2bb673";
      ok.textContent = "No red flags. This scans clean — ship it.";
      findingsEl.appendChild(ok);
      return;
    }
    var colors = { high: "#e63946", medium: "#f59e0b", low: "#457b9d" };
    result.findings.forEach(function (f) {
      var row = document.createElement("div");
      row.style.display = "flex";
      row.style.gap = ".7rem";
      row.style.alignItems = "flex-start";
      row.style.borderLeft = "3px solid " + colors[f.severity];
      row.style.paddingLeft = ".7rem";

      var sev = document.createElement("span");
      sev.style.fontFamily = "'JetBrains Mono', monospace";
      sev.style.fontSize = ".7rem";
      sev.style.fontWeight = "700";
      sev.style.textTransform = "uppercase";
      sev.style.color = colors[f.severity];
      sev.textContent = f.severity;

      var body = document.createElement("div");
      var title = document.createElement("div");
      title.style.fontWeight = "700";
      title.style.fontSize = ".88rem";
      title.style.color = "#111";
      title.textContent = f.title;
      var note = document.createElement("div");
      note.style.fontSize = ".82rem";
      note.style.color = "var(--text-light)";
      note.style.lineHeight = "1.5";
      note.textContent = f.note;
      body.appendChild(title);
      body.appendChild(note);

      row.appendChild(sev);
      row.appendChild(body);
      findingsEl.appendChild(row);
    });
  }

  runBtn.addEventListener("click", function () {
    var text = textEl.value || "";
    if (text.trim().length < 10) {
      if (findingsEl) findingsEl.innerHTML = "";
      if (scoreEl) scoreEl.textContent = "—";
      if (barEl) barEl.style.width = "0";
      var msg = document.createElement("p");
      msg.style.fontFamily = "'JetBrains Mono', monospace";
      msg.style.fontSize = ".8rem";
      msg.style.color = "#e63946";
      msg.textContent = "Paste at least a few bullet points first.";
      findingsEl.appendChild(msg);
      return;
    }
    var result = analyze(text, source);
    render(result);

    var csrf = document.querySelector('meta[name="csrf-token"]');
    fetch("/scope-sentry/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf ? csrf.getAttribute("content") : "",
      },
      body: JSON.stringify({ source: source, text: text }),
      credentials: "same-origin",
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (saved) {
        if (
          saved &&
          typeof saved.score === "number" &&
          saved.score !== result.score
        ) {
          // Server computed slightly differently (same rules, so usually equal).
          render(saved);
        }
      })
      .catch(function () {
        /* offline / POST blocked — local result already shown */
      });
  });
})();
