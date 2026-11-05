/**
 * Placement Portal — DSA Lab Step-through Visualizer
 * ===================================================
 * A minimal, dependency-free canvas renderer. It computes the full sequence of
 * "snapshots" for the selected algorithm up front, then plays them back with
 * the speed slider, step button, or play button. This keeps the animation loop
 * trivial and deterministic.
 *
 * Supported shapes:
 *   - array algorithms (bubble / insertion / merge / quick / binary search)
 *   - graph traversals (BFS / Dijkstra)
 */
(function () {
  "use strict";

  var cfg = window.LAB_CONFIG || {};
  var tabs = cfg.tabs || {};
  var canvas = document.getElementById("algoCanvas");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");

  var codeEl = document.getElementById("algoCode");
  var descEl = document.getElementById("algoDesc");
  var statusEl = document.getElementById("vizStatus");
  var playBtn = document.getElementById("playBtn");
  var stepBtn = document.getElementById("stepBtn");
  var resetBtn = document.getElementById("resetBtn");
  var speedRange = document.getElementById("speedRange");

  var frames = [];
  var frameIndex = 0;
  var playing = false;
  var playTimer = null;

  /* ---------------------------------------------------------------- *
   *  Frame builders
   * ---------------------------------------------------------------- */

  function buildArrayFrames(algo) {
    var input = [42, 17, 33, 8, 51, 25, 64, 11, 29, 47, 5, 38];
    var arr = input.slice();
    var out = [];
    var mark = { compare: [-1, -1], swap: [-1, -1], sorted: [] };

    function push(extra) {
      out.push({ arr: arr.slice(), mark: Object.assign({}, mark, extra || {}) });
    }
    push();

    if (algo === "bubble") {
      var n = arr.length;
      for (var i = 0; i < n - 1; i++) {
        var swapped = false;
        for (var j = 0; j < n - i - 1; j++) {
          mark.compare = [j, j + 1];
          push();
          if (arr[j] > arr[j + 1]) {
            var t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t;
            mark.swap = [j, j + 1];
            push({ compare: [-1, -1] });
            mark.swap = [-1, -1];
            swapped = true;
          }
          mark.compare = [-1, -1];
        }
        mark.sorted.unshift(n - i - 1);
        push();
        if (!swapped) break;
      }
      for (var s = 0; s < n; s++) {
        if (mark.sorted.indexOf(s) === -1) mark.sorted.push(s);
      }
      push();
    } else if (algo === "insertion") {
      for (var i2 = 1; i2 < arr.length; i2++) {
        var key = arr[i2];
        var j2 = i2 - 1;
        while (j2 >= 0 && arr[j2] > key) {
          mark.compare = [j2, j2 + 1];
          push();
          arr[j2 + 1] = arr[j2];
          mark.swap = [j2, j2 + 1];
          push({ compare: [-1, -1] });
          mark.swap = [-1, -1];
          j2--;
        }
        arr[j2 + 1] = key;
        mark.compare = [j2 + 1, i2];
        push();
        mark.compare = [-1, -1];
      }
      mark.sorted = arr.map(function (_, i) { return i; });
      push();
    } else if (algo === "merge") {
      // Bottom-up merge sort with explicit snapshotting.
      var width = 1;
      var tmp = arr.slice();
      while (width < arr.length) {
        for (var lo = 0; lo < arr.length; lo += 2 * width) {
          var mid = Math.min(lo + width, arr.length);
          var hi = Math.min(lo + 2 * width, arr.length);
          var i3 = lo, j3 = mid, k = lo;
          while (i3 < mid && j3 < hi) {
            mark.compare = [i3, j3];
            push();
            if (arr[i3] <= arr[j3]) tmp[k++] = arr[i3++];
            else tmp[k++] = arr[j3++];
          }
          while (i3 < mid) tmp[k++] = arr[i3++];
          while (j3 < hi) tmp[k++] = arr[j3++];
          for (var c = lo; c < hi; c++) arr[c] = tmp[c];
          mark.swap = [lo, hi - 1];
          push({ compare: [-1, -1] });
          mark.swap = [-1, -1];
        }
        width *= 2;
      }
      mark.sorted = arr.map(function (_, i) { return i; });
      push();
    } else if (algo === "quick") {
      (function quickSort(lo, hi) {
        if (lo >= hi) return;
        var pivot = arr[hi];
        var store = lo;
        for (var i4 = lo; i4 < hi; i4++) {
          mark.compare = [i4, hi];
          push();
          if (arr[i4] < pivot) {
            if (store !== i4) {
              var t2 = arr[store]; arr[store] = arr[i4]; arr[i4] = t2;
              mark.swap = [store, i4];
              push({ compare: [-1, -1] });
              mark.swap = [-1, -1];
            }
            store++;
          }
        }
        if (store !== hi) {
          var t3 = arr[store]; arr[store] = arr[hi]; arr[hi] = t3;
          mark.swap = [store, hi];
          push({ compare: [-1, -1] });
          mark.swap = [-1, -1];
        }
        mark.sorted.push(store);
        push();
        quickSort(lo, store - 1);
        quickSort(store + 1, hi);
      })(0, arr.length - 1);
      mark.sorted = arr.map(function (_, i) { return i; });
      push();
    } else if (algo === "binary") {
      var sorted = arr.slice().sort(function (a, b) { return a - b; });
      arr = sorted;
      var target = 29;
      var lo2 = 0, hi2 = sorted.length - 1;
      push({ range: [lo2, hi2] });
      while (lo2 <= hi2) {
        var mid2 = (lo2 + hi2) >> 1;
        mark.compare = [mid2, mid2];
        push({ range: [lo2, hi2] });
        if (sorted[mid2] === target) {
          mark.sorted = [mid2];
          push({ found: mid2, range: [mid2, mid2] });
          return out;
        } else if (sorted[mid2] < target) {
          lo2 = mid2 + 1;
        } else {
          hi2 = mid2 - 1;
        }
        push({ range: [lo2, hi2] });
      }
      push({ range: [lo2, hi2], none: true });
    }
    return out;
  }

  function buildGraphFrames(algo) {
    var nodes = [
      { id: "A", x: 90, y: 150 }, { id: "B", x: 200, y: 70 },
      { id: "C", x: 210, y: 230 }, { id: "D", x: 330, y: 150 },
      { id: "E", x: 450, y: 70 }, { id: "F", x: 460, y: 230 },
      { id: "G", x: 590, y: 150 },
    ];
    var edges = [
      { u: "A", v: "B", w: 4 }, { u: "A", v: "C", w: 2 },
      { u: "B", v: "D", w: 5 }, { u: "C", v: "D", w: 1 },
      { u: "B", v: "E", w: 3 }, { u: "D", v: "F", w: 6 },
      { u: "C", v: "F", w: 8 }, { u: "E", v: "G", w: 2 },
      { u: "F", v: "G", w: 4 },
    ];
    var adj = {};
    nodes.forEach(function (n) { adj[n.id] = []; });
    edges.forEach(function (e) { adj[e.u].push({ v: e.v, w: e.w }); adj[e.v].push({ v: e.u, w: e.w }); });

    var out = [];
    var mark = { visited: [], frontier: [], current: null, path: [], dist: {} };

    function push() {
      out.push({ nodes: nodes, edges: edges, mark: JSON.parse(JSON.stringify(mark)) });
    }

    if (algo === "bfs") {
      var queue = ["A"];
      mark.frontier = ["A"];
      push();
      while (queue.length) {
        var u = queue.shift();
        mark.current = u;
        mark.frontier = queue.slice();
        mark.visited.push(u);
        push();
        adj[u].forEach(function (edge) {
          if (mark.visited.indexOf(edge.v) === -1 && mark.frontier.indexOf(edge.v) === -1) {
            queue.push(edge.v);
            mark.frontier = queue.slice();
            push();
          }
        });
      }
      mark.current = null; mark.frontier = [];
      push();
    } else if (algo === "dijkstra") {
      var start = "A";
      var dist = {};
      nodes.forEach(function (n) { dist[n.id] = Infinity; });
      dist[start] = 0;
      var settled = [];
      var pq = [{ id: start, d: 0 }];

      function popMin() {
        var best = 0;
        for (var i = 1; i < pq.length; i++) if (pq[i].d < pq[best].d) best = i;
        return pq.splice(best, 1)[0];
      }

      push();
      while (pq.length) {
        var cur = popMin();
        if (settled.indexOf(cur.id) !== -1) continue;
        settled.push(cur.id);
        mark.current = cur.id;
        mark.dist = Object.assign({}, dist);
        push();
        adj[cur.id].forEach(function (edge) {
          var nd = dist[cur.id] + edge.w;
          if (nd < dist[edge.v]) {
            dist[edge.v] = nd;
            pq.push({ id: edge.v, d: nd });
            mark.dist = Object.assign({}, dist);
            mark.path = settled.concat([cur.id]);
            push();
          }
        });
      }
      mark.current = null; mark.dist = dist;
      push();
    }
    return out;
  }

  /* ---------------------------------------------------------------- *
   *  Rendering
   * ---------------------------------------------------------------- */

  function drawArrayFrame(frame) {
    var W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    var n = frame.arr.length;
    var gap = 6;
    var bw = (W - gap * (n + 1)) / n;
    var base = H - 40;

    frame.arr.forEach(function (v, i) {
      var h = (v / 64) * (H - 90);
      var x = gap + i * (bw + gap);
      var y = base - h;

      var fill = "#f4f0ea";
      if (frame.mark.compare.indexOf(i) !== -1) fill = "#e63946";
      if (frame.mark.swap.indexOf(i) !== -1) fill = "#457b9d";
      if (frame.mark.sorted.indexOf(i) !== -1) fill = "#dbe7ee";
      if (frame.mark.found === i) fill = "#2bb673";

      ctx.fillStyle = "#111111";
      ctx.fillRect(x - 2, y - 2, bw + 4, h + 4);
      ctx.fillStyle = fill;
      ctx.fillRect(x, y, bw, h);

      ctx.fillStyle = "#111111";
      ctx.font = "600 11px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText(v, x + bw / 2, y - 8);
    });

    if (frame.mark.range) {
      var lo = frame.mark.range[0], hi = frame.mark.range[1];
      if (lo <= hi) {
        var x0 = gap + lo * (bw + gap) - 4;
        var w0 = (hi - lo + 1) * (bw + gap) - gap + 8;
        ctx.strokeStyle = "#e63946";
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 3]);
        ctx.strokeRect(x0, 18, w0, base - 18);
        ctx.setLineDash([]);
      }
    }
    if (frame.mark.none) {
      ctx.fillStyle = "#111111";
      ctx.font = "700 14px 'JetBrains Mono', monospace";
      ctx.fillText("target not found", W / 2, H - 12);
    }
  }

  function drawGraphFrame(frame) {
    var W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    frame.edges.forEach(function (e) {
      var u = frame.nodes.filter(function (n) { return n.id === e.u; })[0];
      var v = frame.nodes.filter(function (n) { return n.id === e.v; })[0];
      var active = frame.mark.current &&
        ((frame.mark.path.indexOf(e.u) !== -1 && frame.mark.path.indexOf(e.v) !== -1));
      ctx.beginPath();
      ctx.moveTo(u.x, u.y);
      ctx.lineTo(v.x, v.y);
      ctx.strokeStyle = active ? "#e63946" : "#c9c2b4";
      ctx.lineWidth = active ? 3 : 1.5;
      ctx.stroke();
      ctx.fillStyle = "#111111";
      ctx.font = "600 10px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.fillText(e.w, (u.x + v.x) / 2, (u.y + v.y) / 2 - 6);
    });

    frame.nodes.forEach(function (n) {
      var isVisited = frame.mark.visited.indexOf(n.id) !== -1;
      var isFrontier = frame.mark.frontier.indexOf(n.id) !== -1;
      var isCurrent = frame.mark.current === n.id;
      var fill = "#f4f0ea";
      if (isVisited) fill = "#dbe7ee";
      if (isFrontier) fill = "#457b9d";
      if (isCurrent) fill = "#e63946";

      ctx.beginPath();
      ctx.arc(n.x, n.y, 26, 0, Math.PI * 2);
      ctx.fillStyle = "#111111";
      ctx.fill();
      ctx.beginPath();
      ctx.arc(n.x, n.y, 23, 0, Math.PI * 2);
      ctx.fillStyle = fill;
      ctx.fill();
      ctx.fillStyle = "#111111";
      ctx.font = "700 13px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(n.id, n.x, n.y);
      ctx.textBaseline = "alphabetic";
    });
  }

  function render() {
    var frame = frames[frameIndex] || frames[0];
    if (!frame) return;
    if (frame.nodes) drawGraphFrame(frame);
    else drawArrayFrame(frame);
  }

  /* ---------------------------------------------------------------- *
   *  Controls
   * ---------------------------------------------------------------- */

  function loadAlgo(key) {
    if (playing) stop();
    var tab = tabs[key];
    if (!tab) return;
    if (codeEl) codeEl.textContent = tab.code || "";
    if (descEl) descEl.textContent = tab.desc || "";
    var isGraph = key === "bfs" || key === "dijkstra";
    frames = isGraph ? buildGraphFrames(key) : buildArrayFrames(key);
    frameIndex = 0;
    setStatus("0 / " + frames.length);
    render();
  }

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  function step(forward) {
    if (!frames.length) return;
    frameIndex = Math.max(0, Math.min(frames.length - 1, frameIndex + (forward ? 1 : -1)));
    render();
    setStatus(frameIndex + " / " + frames.length);
  }

  function play() {
    if (playing || !frames.length) return;
    playing = true;
    if (playBtn) playBtn.textContent = "❚❚ Pause";
    var speed = speedRange ? parseInt(speedRange.value, 10) : 4;
    var delay = Math.max(60, 360 - speed * 28);
    playTimer = setInterval(function () {
      if (frameIndex >= frames.length - 1) { stop(); render(); return; }
      step(true);
    }, delay);
  }

  function stop() {
    playing = false;
    if (playTimer) clearInterval(playTimer);
    playTimer = null;
    if (playBtn) playBtn.textContent = "▶ Play";
  }

  function reset() {
    stop();
    frameIndex = 0;
    setStatus("0 / " + frames.length);
    render();
  }

  if (playBtn) playBtn.addEventListener("click", function () { playing ? stop() : play(); });
  if (stepBtn) stepBtn.addEventListener("click", function () { stop(); step(true); });
  if (resetBtn) resetBtn.addEventListener("click", reset);
  if (speedRange && speedRange.addEventListener) {
    speedRange.addEventListener("input", function () { if (playing) { stop(); play(); } });
  }

  document.querySelectorAll(".algo-tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".algo-tab").forEach(function (b) {
        b.style.background = "#fbf9f5";
        b.style.color = "#111";
      });
      btn.style.background = "#111111";
      btn.style.color = "#fbf9f5";
      loadAlgo(btn.getAttribute("data-key"));
    });
  });

  // Init with the first tab.
  var firstKey = Object.keys(tabs)[0];
  if (firstKey) loadAlgo(firstKey);
  if (firstKey) {
    var firstBtn = document.querySelector('.algo-tab[data-key="' + firstKey + '"]');
    if (firstBtn) { firstBtn.style.background = "#111111"; firstBtn.style.color = "#fbf9f5"; }
  }
})();
