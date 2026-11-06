/**
 * Placement Portal — Global Command Palette ("/" search)
 * ======================================================
 * A keyboard-first, Vim-style module switcher. Press "/" anywhere to open it,
 * type to filter, use ↑/↓ to move and Enter to navigate. Built as a minimal
 * standalone layer — it reads its command list from a global injected by
 * base.html (window.PORTAL_COMMANDS) so route URLs always stay in sync with
 * the server.
 */
(function () {
  "use strict";

  var commands = (window.PORTAL_COMMANDS || []).filter(function (c) {
    return c && c.label && c.href;
  });

  var palette = document.getElementById("cmdPalette");
  var input = document.getElementById("cmdInput");
  var list = document.getElementById("cmdList");
  if (!palette || !input || !list) return;

  var currentHighlight = 0;
  var filtered = [];

  function isOpen() {
    return !palette.hidden;
  }

  function open() {
    filtered = commands.slice();
    currentHighlight = 0;
    palette.hidden = false;
    render();
    input.value = "";
    input.focus();
    document.body.classList.add("cmd-palette-open");
  }

  function close() {
    palette.hidden = true;
    document.body.classList.remove("cmd-palette-open");
  }

  function toggle() {
    isOpen() ? close() : open();
  }

  function render() {
    list.innerHTML = "";
    filtered.forEach(function (cmd, i) {
      var li = document.createElement("li");
      li.className = "cmd-item" + (i === currentHighlight ? " active" : "");
      li.dataset.index = String(i);

      var kbd = document.createElement("span");
      kbd.className = "cmd-key";
      kbd.textContent = cmd.key || (i + 1);

      var label = document.createElement("span");
      label.className = "cmd-label";
      label.textContent = cmd.label;

      var desc = document.createElement("span");
      desc.className = "cmd-desc";
      desc.textContent = cmd.desc || "";

      li.appendChild(kbd);
      li.appendChild(label);
      li.appendChild(desc);
      li.addEventListener("mousemove", function () {
        setHighlight(parseInt(li.dataset.index, 10));
      });
      li.addEventListener("click", function () {
        goTo(filtered[parseInt(li.dataset.index, 10)]);
      });
      list.appendChild(li);
    });
    if (!filtered.length) {
      var empty = document.createElement("li");
      empty.className = "cmd-empty";
      empty.textContent = "No modules match. Try 'practice', 'analytics', 'dsa'…";
      list.appendChild(empty);
    }
  }

  function setHighlight(i) {
    currentHighlight = i;
    var items = list.querySelectorAll(".cmd-item");
    for (var n = 0; n < items.length; n++) {
      items[n].classList.toggle("active", n === i);
    }
    var active = items[currentHighlight];
    if (active && typeof active.scrollIntoView === "function") {
      active.scrollIntoView({ block: "nearest" });
    }
  }

  function goTo(cmd) {
    if (!cmd) return;
    close();
    if (cmd.href) window.location.href = cmd.href;
  }

  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase();
    if (!q) {
      filtered = commands.slice();
    } else {
      filtered = commands.filter(function (c) {
        return (c.label + " " + (c.desc || "")).toLowerCase().indexOf(q) !== -1;
      });
    }
    currentHighlight = 0;
    render();
  });

  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight(Math.min(filtered.length - 1, currentHighlight + 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight(Math.max(0, currentHighlight - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      goTo(filtered[currentHighlight]);
    } else if (e.key === "Escape") {
      e.preventDefault();
      close();
    }
  });

  palette.addEventListener("click", function (e) {
    if (e.target === palette) close();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen()) close();
    if (e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey && !isOpen()) {
      var t = e.target;
      var typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA");
      if (!typing) {
        e.preventDefault();
        open();
      }
    }
  });

  window.PortalPalette = { toggle: toggle, open: open, close: close };
})();
