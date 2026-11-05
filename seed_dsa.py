"""
Seed DSA topics, sample questions, and algorithm visualizer data.
Run: python seed_dsa.py
"""
import json
from app import create_app
from app.extensions import db
from app.models.dsa import DSATopic, DSAQuestion, AlgorithmVisualizer


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ── Topics ─────────────────────────────────────────
        topics_data = [
            ("Arrays", "arrays", "📦", "Master array manipulation, two pointers, and sliding window.", 1),
            ("Strings", "strings", "🔤", "String manipulation, palindromes, and pattern matching.", 2),
            ("Linked Lists", "linked-lists", "🔗", "Singly/doubly linked list operations and cycles.", 3),
            ("Stacks & Queues", "stacks-queues", "📚", "LIFO/FIFO structures and their applications.", 4),
            ("Hash Maps", "hash-maps", "🗺️", "Key-value lookups, frequency counting, and sets.", 5),
            ("Binary Search", "binary-search", "🔍", "Efficient searching in sorted arrays.", 6),
            ("Recursion", "recursion", "🔄", "Recursive thinking, backtracking, and divide & conquer.", 7),
            ("Sorting", "sorting", "📊", "Bubble, merge, quick, and other sorting algorithms.", 8),
            ("Trees", "trees", "🌳", "Binary trees, BST, traversals, and balancing.", 9),
            ("Graphs", "graphs", "🕸️", "BFS, DFS, shortest path, and topological sort.", 10),
            ("Dynamic Programming", "dynamic-programming", "🧠", "Optimal substructure, memoization, and tabulation.", 11),
            ("Greedy", "greedy", "🦊", "Greedy algorithms and interval scheduling.", 12),
        ]
        topic_map = {}
        for name, slug, icon, desc, order in topics_data:
            existing = DSATopic.query.filter_by(slug=slug).first()
            if not existing:
                t = DSATopic(name=name, slug=slug, icon=icon, description=desc, order=order)
                db.session.add(t)
                db.session.flush()
                topic_map[slug] = t
            else:
                topic_map[slug] = existing
        db.session.commit()

        # ── Sample Questions ────────────────────────────────
        questions = [
            # Arrays - Easy
            ("arrays", "easy", "Two Sum",
             "Given an array of integers `nums` and an integer `target`, return indices of the two numbers that add up to `target`.",
             json.dumps([{"input": "[2,7,11,15], 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] = 2 + 7 = 9"}]),
             "Constraints: 2 <= nums.length <= 10^4",
             "def solution(nums, target):\n    # Write your solution here\n    pass",
             "def solution(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        comp = target - n\n        if comp in seen:\n            return [seen[comp], i]\n        seen[n] = i\n    return []",
             json.dumps([{"input": "[2,7,11,15], 9", "expected_output": "[0, 1]"}, {"input": "[3,2,4], 6", "expected_output": "[1, 2]"}, {"input": "[3,3], 6", "expected_output": "[0, 1]"}])),

            ("arrays", "easy", "Best Time to Buy and Sell Stock",
             "Given an array of prices where prices[i] is the price on day i, find the maximum profit from buying and selling once.",
             json.dumps([{"input": "[7,1,5,3,6,4]", "output": "5", "explanation": "Buy on day 1 (price=1), sell on day 4 (price=6), profit=5"}]),
             "Constraints: 1 <= prices.length <= 10^5",
             "def solution(prices):\n    # Write your solution here\n    pass",
             "def solution(prices):\n    min_price = float('inf')\n    max_profit = 0\n    for p in prices:\n        min_price = min(min_price, p)\n        max_profit = max(max_profit, p - min_price)\n    return max_profit",
             json.dumps([{"input": "[7,1,5,3,6,4]", "expected_output": "5"}, {"input": "[7,6,4,3,1]", "expected_output": "0"}])),

            ("arrays", "medium", "Container With Most Water",
             "Given n non-negative integers, find two lines that together with the x-axis form a container that holds the most water.",
             json.dumps([{"input": "[1,8,6,2,5,4,8,3,7]", "output": "49", "explanation": "Lines at index 1 and 8 hold 7*7=49 water"}]),
             "Constraints: n >= 2",
             "def solution(height):\n    # Write your solution here\n    pass",
             "def solution(height):\n    l, r = 0, len(height) - 1\n    best = 0\n    while l < r:\n        area = min(height[l], height[r]) * (r - l)\n        best = max(best, area)\n        if height[l] < height[r]:\n            l += 1\n        else:\n            r -= 1\n    return best",
             json.dumps([{"input": "[1,8,6,2,5,4,8,3,7]", "expected_output": "49"}, {"input": "[1,1]", "expected_output": "1"}])),

            ("arrays", "hard", "Trapping Rain Water",
             "Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.",
             json.dumps([{"input": "[0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"}]),
             "Constraints: n == height.length",
             "def solution(height):\n    # Write your solution here\n    pass",
             "def solution(height):\n    if not height: return 0\n    l, r = 0, len(height) - 1\n    l_max, r_max = height[l], height[r]\n    water = 0\n    while l < r:\n        if l_max < r_max:\n            l += 1\n            l_max = max(l_max, height[l])\n            water += l_max - height[l]\n        else:\n            r -= 1\n            r_max = max(r_max, height[r])\n            water += r_max - height[r]\n    return water",
             json.dumps([{"input": "[0,1,0,2,1,0,1,3,2,1,2,1]", "expected_output": "6"}, {"input": "[4,2,0,3,2,5]", "expected_output": "9"}])),

            # Binary Search - Easy
            ("binary-search", "easy", "Binary Search",
             "Given a sorted array and a target, return the index if found, else -1.",
             json.dumps([{"input": "[-1,0,3,5,9,12], 9", "output": "4"}]),
             "All integers are unique. Array is sorted.",
             "def solution(nums, target):\n    # Write your solution here\n    pass",
             "def solution(nums, target):\n    lo, hi = 0, len(nums) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
             json.dumps([{"input": "[-1,0,3,5,9,12], 9", "expected_output": "4"}, {"input": "[-1,0,3,5,9,12], 2", "expected_output": "-1"}])),

            # Sorting - Easy
            ("sorting", "easy", "Bubble Sort Implementation",
             "Implement bubble sort to sort an array of integers in ascending order.",
             json.dumps([{"input": "[64,34,25,12,22,11,90]", "output": "[11,12,22,25,34,64,90]"}]),
             "Return the sorted array.",
             "def solution(arr):\n    # Implement bubble sort\n    pass",
             "def solution(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
             json.dumps([{"input": "[64,34,25,12,22,11,90]", "expected_output": "[11, 12, 22, 25, 34, 64, 90]"}, {"input": "[5,1,4,2,8]", "expected_output": "[1, 2, 4, 5, 8]"}])),

            # Trees - Medium
            ("trees", "medium", "Invert Binary Tree",
             "Given the root of a binary tree, invert the tree (mirror it).",
             json.dumps([{"input": "[4,2,7,1,3,6,9]", "output": "[4,7,2,9,6,3,1]"}]),
             "Return the root of the inverted tree.",
             "# class TreeNode:\n#     def __init__(self, val=0, left=None, right=None):\n#         self.val = val\n#         self.left = left\n#         self.right = right\ndef solution(root):\n    # Write your solution here\n    pass",
             "def solution(root):\n    if not root:\n        return None\n    root.left, root.right = root.right, root.left\n    solution(root.left)\n    solution(root.right)\n    return root",
             json.dumps([{"input": "[4,2,7,1,3,6,9]", "expected_output": "[4,7,2,9,6,3,1]"}])),

            # Dynamic Programming - Medium
            ("dynamic-programming", "medium", "Climbing Stairs",
             "You are climbing a staircase with n steps. Each time you can climb 1 or 2 steps. How many distinct ways can you reach the top?",
             json.dumps([{"input": "2", "output": "2", "explanation": "1+1 or 2"}, {"input": "3", "output": "3"}]),
             "1 <= n <= 45",
             "def solution(n):\n    # Write your solution here\n    pass",
             "def solution(n):\n    if n <= 2: return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b",
             json.dumps([{"input": "2", "expected_output": "2"}, {"input": "3", "expected_output": "3"}, {"input": "5", "expected_output": "8"}])),

            # Graphs - Medium
            ("graphs", "medium", "Number of Islands",
             "Given an m x n grid of '1' (land) and '0' (water), count the number of islands.",
             json.dumps([{"input": "[[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"1\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"1\",\"1\"]]", "output": "3"}]),
             "Grid is surrounded by water.",
             "def solution(grid):\n    # Write your solution here\n    pass",
             "def solution(grid):\n    if not grid: return 0\n    rows, cols = len(grid), len(grid[0])\n    count = 0\n    def dfs(r, c):\n        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != '1':\n            return\n        grid[r][c] = '0'\n        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1':\n                dfs(r, c)\n                count += 1\n    return count",
             json.dumps([{"input": "[[\"1\",\"1\",\"0\"],[\"0\",\"1\",\"0\"],[\"0\",\"0\",\"1\"]]", "expected_output": "2"}])),
        ]

        for topic_slug, diff, title, desc, examples, constraints, starter, solution, tests in questions:
            t = topic_map.get(topic_slug)
            if not t:
                continue
            existing = DSAQuestion.query.filter_by(title=title, topic_id=t.id).first()
            if not existing:
                q = DSAQuestion(
                    topic_id=t.id, title=title, difficulty=diff,
                    description=desc, examples=examples, constraints=constraints,
                    starter_code=starter, solution_code=solution, test_cases=tests,
                )
                db.session.add(q)
        db.session.commit()

        # ── Algorithm Visualizers ───────────────────────────
        visualizers = [
            ("Bubble Sort", "bubble-sort", "sorting",
             "Repeatedly swap adjacent elements if they're in wrong order.",
             json.dumps([
                 {"array": [64, 34, 25, 12, 22, 11, 90], "highlight": [], "swapped": [], "sorted": [], "pass": 0, "label": "Initial array"},
                 {"array": [34, 25, 12, 22, 11, 64, 90], "highlight": [0, 1], "swapped": [0, 1], "sorted": [], "pass": 1, "label": "Compare & swap 64,34"},
                 {"array": [25, 12, 22, 11, 34, 64, 90], "highlight": [1, 2], "swapped": [1, 2], "sorted": [6], "pass": 1, "label": "Bubble 64 right"},
                 {"array": [12, 22, 11, 25, 34, 64, 90], "highlight": [2, 3], "swapped": [2, 3], "sorted": [5, 6], "pass": 1, "label": "64 in position"},
                 {"array": [12, 11, 22, 25, 34, 64, 90], "highlight": [0, 1], "swapped": [0, 1], "sorted": [5, 6], "pass": 2, "label": "Pass 2: fix start"},
                 {"array": [11, 12, 22, 25, 34, 64, 90], "highlight": [], "swapped": [], "sorted": [0, 1, 2, 3, 4, 5, 6], "pass": 3, "label": "✅ Sorted!"},
             ]),
             json.dumps([
                 {"code": "def bubble_sort(arr):", "line": 0},
                 {"code": "    n = len(arr)", "line": 1},
                 {"code": "    for i in range(n):", "line": 2},
                 {"code": "        for j in range(0, n-i-1):", "line": 3},
                 {"code": "            if arr[j] > arr[j+1]:", "line": 4},
                 {"code": "                arr[j], arr[j+1] = arr[j+1], arr[j]", "line": 5},
                 {"code": "    return arr", "line": 6},
             ]),
             "O(n²)", "O(n²)", "O(1)"),

            ("Selection Sort", "selection-sort", "sorting",
             "Find the minimum element and place it at the beginning repeatedly.",
             json.dumps([
                 {"array": [29, 10, 14, 37, 13], "highlight": [], "swapped": [], "sorted": [], "pass": 0, "label": "Initial array"},
                 {"array": [10, 29, 14, 37, 13], "highlight": [0, 1], "swapped": [0, 1], "sorted": [0], "pass": 1, "label": "Found min=10, swap"},
                 {"array": [10, 13, 14, 37, 29], "highlight": [1, 4], "swapped": [1, 4], "sorted": [0, 1], "pass": 2, "label": "Found min=13, swap"},
                 {"array": [10, 13, 14, 37, 29], "highlight": [2, 2], "swapped": [], "sorted": [0, 1, 2], "pass": 3, "label": "14 already in place"},
                 {"array": [10, 13, 14, 29, 37], "highlight": [3, 4], "swapped": [3, 4], "sorted": [0, 1, 2, 3, 4], "pass": 4, "label": "✅ Sorted!"},
             ]),
             json.dumps([
                 {"code": "def selection_sort(arr):", "line": 0},
                 {"code": "    n = len(arr)", "line": 1},
                 {"code": "    for i in range(n):", "line": 2},
                 {"code": "        min_idx = i", "line": 3},
                 {"code": "        for j in range(i+1, n):", "line": 4},
                 {"code": "            if arr[j] < arr[min_idx]:", "line": 5},
                 {"code": "                min_idx = j", "line": 6},
                 {"code": "        arr[i], arr[min_idx] = arr[min_idx], arr[i]", "line": 7},
                 {"code": "    return arr", "line": 8},
             ]),
             "O(n²)", "O(n²)", "O(1)"),

            ("Binary Search", "binary-search", "searching",
             "Efficiently find a target in a sorted array by halving the search space.",
             json.dumps([
                 {"array": [2, 5, 8, 12, 16, 23, 38, 56, 72, 91], "low": 0, "high": 9, "mid": 4, "target": 23, "label": "Initial: search 23 in [0..9]"},
                 {"array": [2, 5, 8, 12, 16, 23, 38, 56, 72, 91], "low": 5, "high": 9, "mid": 7, "target": 23, "label": "16 < 23, search right half"},
                 {"array": [2, 5, 8, 12, 16, 23, 38, 56, 72, 91], "low": 5, "high": 6, "mid": 5, "target": 23, "label": "56 > 23, search left half"},
                 {"array": [2, 5, 8, 12, 16, 23, 38, 56, 72, 91], "low": 5, "high": 5, "mid": 5, "target": 23, "label": "Found at index 5! ✅"},
             ]),
             json.dumps([
                 {"code": "def binary_search(arr, target):", "line": 0},
                 {"code": "    lo, hi = 0, len(arr) - 1", "line": 1},
                 {"code": "    while lo <= hi:", "line": 2},
                 {"code": "        mid = (lo + hi) // 2", "line": 3},
                 {"code": "        if arr[mid] == target:", "line": 4},
                 {"code": "            return mid", "line": 5},
                 {"code": "        elif arr[mid] < target:", "line": 6},
                 {"code": "            lo = mid + 1", "line": 7},
                 {"code": "        else:", "line": 8},
                 {"code": "            hi = mid - 1", "line": 9},
                 {"code": "    return -1", "line": 10},
             ]),
             "O(log n)", "O(log n)", "O(1)"),

            ("Linear Search", "linear-search", "searching",
             "Check each element one by one until the target is found.",
             json.dumps([
                 {"array": [4, 2, 7, 1, 9, 3], "highlight": [0], "target": 7, "label": "Check index 0: 4 ≠ 7"},
                 {"array": [4, 2, 7, 1, 9, 3], "highlight": [1], "target": 7, "label": "Check index 1: 2 ≠ 7"},
                 {"array": [4, 2, 7, 1, 9, 3], "highlight": [2], "target": 7, "found": True, "label": "Check index 2: 7 = 7 ✅ Found!"},
             ]),
             json.dumps([
                 {"code": "def linear_search(arr, target):", "line": 0},
                 {"code": "    for i in range(len(arr)):", "line": 1},
                 {"code": "        if arr[i] == target:", "line": 2},
                 {"code": "            return i", "line": 3},
                 {"code": "    return -1", "line": 4},
             ]),
             "O(n)", "O(n)", "O(1)"),
        ]

        for name, slug, cat, desc, steps, code, bt, wt, sp in visualizers:
            existing = AlgorithmVisualizer.query.filter_by(slug=slug).first()
            if not existing:
                v = AlgorithmVisualizer(
                    name=name, slug=slug, category=cat,
                    description=desc, steps_json=steps, code_json=code,
                    best_time=bt, worst_time=wt, space=sp,
                )
                db.session.add(v)
        db.session.commit()
        print("✅ DSA seed data loaded!")


if __name__ == "__main__":
    seed()
