# -*- coding: utf-8 -*-
"""
Content data — System Design Vault and DSA Lab programs.

Static, curated content (no DB dependency) so the modules render instantly
and degrade gracefully if the database is empty.
"""

# ── System Design Vault ────────────────────────────────────────────
SYSTEM_DESIGN_VAULT = [
    {
        "title": "Distributed Caching",
        "tag": "#distributed-caching",
        "blurb": "Put a cache in front of hot reads to cut latency and DB load.",
        "scenario": "Your read-heavy service saturates the database during spikes.",
        "blueprint": [
            "Pick a cache tier (Redis / Memcached) sized to working set.",
            "Cache-aside (lazy): read → miss → load DB → write cache with TTL.",
            "Handle stampede: single-flight / request coalescing on miss.",
            "Invalidation contract: set TTL or explicit eviction on write.",
        ],
        "questions": [
            "What happens when the cache node becomes the new single point of failure?",
            "How do you keep cache and DB eventually consistent?",
        ],
    },
    {
        "title": "Concurrency & Locking",
        "tag": "#concurrency",
        "blurb": "Reason about race conditions before they become outages.",
        "scenario": "Two writes to the same row / counter race and lose an update.",
        "blueprint": [
            "Identify the critical section and the data it touches.",
            "Prefer atomic operations (INCR, CAS) over read-modify-write.",
            "Use optimistic locking (version column) for low-contention paths.",
            "Escalate to pessimistic locks or queues only when contention is real.",
        ],
        "questions": [
            "What is the difference between optimistic and pessimistic locking?",
            "When would a distributed lock still not save you?",
        ],
    },
    {
        "title": "Database Indexing",
        "tag": "#database-indexing",
        "blurb": "Indexes buy query speed at the cost of write amplification.",
        "scenario": "Queries are doing full table scans on a growing table.",
        "blueprint": [
            "Find slow queries (EXPLAIN) before adding indexes blindly.",
            "Index the columns used in WHERE / JOIN / ORDER BY.",
            "Composite indexes: leftmost-prefix ordering matters.",
            "Watch out: covering index vs extra write cost on every INSERT.",
        ],
        "questions": [
            "Why does a composite index order matter?",
            "What is a covering index?",
        ],
    },
    {
        "title": "Rate Limiting",
        "tag": "#rate-limiting",
        "blurb": "Protect shared services from bursts and abuse.",
        "scenario": "A rogue client floods the API and crowds out everyone else.",
        "blueprint": [
            "Choose an algorithm: token bucket, fixed window, sliding window.",
            "Define limits per key (IP, user, API key).",
            "Return 429 + Retry-After on over-limit.",
            "In a fleet, move counters to a shared store (Redis) to stay fair.",
        ],
        "questions": [
            "Token bucket vs fixed window — when is each preferable?",
            "How do you rate-limit correctly across multiple app instances?",
        ],
    },
    {
        "title": "Scaling Reads",
        "tag": "#scaling",
        "blurb": "Handling more read traffic without breaking writes.",
        "scenario": "Reads outgrow a single primary database.",
        "blueprint": [
            "Add read replicas and route read-only traffic to them.",
            "Accept replication lag — decide which queries may go stale.",
            "Move session/cache reads off the primary entirely.",
            "Re-evaluate: sometimes a cache fixes it without replica complexity.",
        ],
        "questions": [
            "What is replication lag and when does it bite?",
            "How do you split reads and writes in code?",
        ],
    },
    {
        "title": "Async & Queues",
        "tag": "#asynchronous",
        "blurb": "Decouple slow work from the request path.",
        "scenario": "A request does a 5s side effect and the client waits.",
        "blueprint": [
            "Identify non-critical work: email, notifications, image resize.",
            "Push a job to a queue and return 202 immediately.",
            "Worker consumes the job; report status via polling or push.",
            "Plan for retries, dead-letter queues, and idempotency.",
        ],
        "questions": [
            "How do you guarantee a queue job runs exactly once?",
            "What is a dead-letter queue for?",
        ],
    },
]

# ── DSA Labs (university practical programs) ────────────────────────
DSA_LABS = [
    {
        "slug": "sorting",
        "name": "Sorting Implementations",
        "program": "Implement selection, bubble, insertion, merge, and quick sort; verify O(n²) vs O(n log n).",
        "topic_slug": "sorting",
        "complexity_tags": ["O(n²)", "O(n log n)", "in-place"],
        "steps": ["bubble", "insertion", "merge", "quick"],
        "tabs": {
            "bubble": {
                "title": "Bubble Sort",
                "desc": "Swap adjacent out-of-order pairs until the array is sorted. O(n²) worst case.",
                "code": "def bubble_sort(a):\n    n = len(a)\n    for i in range(n):\n        swapped = False\n        for j in range(0, n - i - 1):\n            if a[j] > a[j + 1]:\n                a[j], a[j + 1] = a[j + 1], a[j]\n                swapped = True\n        if not swapped:\n            break\n    return a",
            },
            "insertion": {
                "title": "Insertion Sort",
                "desc": "Build the sorted part one element at a time by inserting into place. Fast on near-sorted input.",
                "code": "def insertion_sort(a):\n    for i in range(1, len(a)):\n        key = a[i]\n        j = i - 1\n        while j >= 0 and a[j] > key:\n            a[j + 1] = a[j]\n            j -= 1\n        a[j + 1] = key\n    return a",
            },
            "merge": {
                "title": "Merge Sort",
                "desc": "Divide, recursively sort, then merge two halves. Stable, O(n log n), O(n) space.",
                "code": "def merge_sort(a):\n    if len(a) <= 1:\n        return a\n    mid = len(a) // 2\n    left = merge_sort(a[:mid])\n    right = merge_sort(a[mid:])\n    return merge(left, right)\n\ndef merge(l, r):\n    out, i, j = [], 0, 0\n    while i < len(l) and j < len(r):\n        if l[i] <= r[j]:\n            out.append(l[i]); i += 1\n        else:\n            out.append(r[j]); j += 1\n    out.extend(l[i:]); out.extend(r[j:])\n    return out",
            },
            "quick": {
                "title": "Quick Sort",
                "desc": "Partition around a pivot, recurse. O(n log n) average, O(n²) worst.",
                "code": "def quick_sort(a):\n    if len(a) <= 1:\n        return a\n    pivot = a[len(a) // 2]\n    lo = [x for x in a if x < pivot]\n    eq = [x for x in a if x == pivot]\n    hi = [x for x in a if x > pivot]\n    return quick_sort(lo) + eq + quick_sort(hi)",
            },
        },
    },
    {
        "slug": "searching",
        "name": "Searching",
        "program": "Linear vs binary search on sorted data; verify O(n) vs O(log n).",
        "topic_slug": "searching",
        "complexity_tags": ["O(log n)", "sorted"],
        "steps": ["binary"],
        "tabs": {
            "binary": {
                "title": "Binary Search",
                "desc": "Repeatedly halve the search space. Requires sorted input. O(log n).",
                "code": "def binary_search(a, target):\n    lo, hi = 0, len(a) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if a[mid] == target:\n            return mid\n        elif a[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
            },
        },
    },
    {
        "slug": "trees",
        "name": "Tree Traversals",
        "program": "Preorder, inorder, postorder, and level-order traversals of a binary tree.",
        "topic_slug": "trees",
        "complexity_tags": ["O(n)", "recursion"],
        "steps": ["inorder", "dfs_depth"],
        "tabs": {
            "inorder": {
                "title": "Inorder",
                "desc": "Left → root → right. On a BST, yields sorted order.",
                "code": "class Node:\n    def __init__(self, val):\n        self.val = val\n        self.left = None\n        self.right = None\n\ndef inorder(root):\n    if not root:\n        return []\n    return inorder(root.left) + [root.val] + inorder(root.right)",
            },
            "dfs_depth": {
                "title": "Depth-First (stack)",
                "desc": "Iterative DFS with an explicit stack.",
                "code": "def dfs_iterative(root):\n    if not root:\n        return []\n    stack, out = [root], []\n    while stack:\n        node = stack.pop()\n        out.append(node.val)\n        if node.right:\n            stack.append(node.right)\n        if node.left:\n            stack.append(node.left)\n    return out",
            },
        },
    },
    {
        "slug": "graphs",
        "name": "Graph Algorithms",
        "program": "BFS/DFS traversal and shortest path (Dijkstra) on weighted graphs.",
        "topic_slug": "graphs",
        "complexity_tags": ["O(V+E)", "shortest-path"],
        "steps": ["bfs", "dijkstra"],
        "tabs": {
            "bfs": {
                "title": "BFS (level order)",
                "desc": "Visit in order of distance from source. O(V+E).",
                "code": "from collections import deque\n\ndef bfs(graph, start):\n    seen = {start}\n    q = deque([start])\n    order = []\n    while q:\n        node = q.popleft()\n        order.append(node)\n        for nxt in graph.get(node, []):\n            if nxt not in seen:\n                seen.add(nxt)\n                q.append(nxt)\n    return order",
            },
            "dijkstra": {
                "title": "Dijkstra",
                "desc": "Shortest paths from a source on non-negative weights. O(E log V) with a heap.",
                "code": "import heapq\n\ndef dijkstra(graph, start):\n    dist = {v: float('inf') for v in graph}\n    dist[start] = 0\n    pq = [(0, start)]\n    while pq:\n        d, u = heapq.heappop(pq)\n        if d > dist[u]:\n            continue\n        for v, w in graph[u]:\n            nd = d + w\n            if nd < dist[v]:\n                dist[v] = nd\n                heapq.heappush(pq, (nd, v))\n    return dist",
            },
        },
    },
]
