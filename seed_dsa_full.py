"""
Seed 50+ DSA questions across all topics with company tags and multi-language starter code.
Run: python seed_dsa_full.py
"""
import json
from app import create_app
from app.extensions import db
from app.models.dsa import DSATopic, DSAQuestion


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ── Ensure topics exist ─────────────────────────────
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
            t = DSATopic.query.filter_by(slug=slug).first()
            if not t:
                t = DSATopic(name=name, slug=slug, icon=icon, description=desc, order=order)
                db.session.add(t)
                db.session.flush()
            topic_map[slug] = t
        db.session.commit()

        # ── Helper: build multi-language starter code ────────
        def starters(title, desc):
            """Generate starter code for Python, Java, C, C++, JS."""
            # Extract function signature hint from title
            return json.dumps({
                "python": f"# {title}\n# {desc[:60]}...\n\ndef solution(nums):\n    # Write your solution here\n    pass\n",
                "java": f"// {title}\nimport java.util.*;\n\nclass Solution {{\n    public static int[] solution(int[] nums) {{\n        // Write your solution here\n        return nums;\n    }}\n}}\n",
                "c": f"// {title}\n#include <stdio.h>\n\nvoid solution(int* nums, int n) {{\n    // Write your solution here\n}}\n",
                "cpp": f"// {title}\n#include <vector>\nusing namespace std;\n\nclass Solution {{\npublic:\n    vector<int> solution(vector<int>& nums) {{\n        // Write your solution here\n        return nums;\n    }}\n}};\n",
                "javascript": f"// {title}\n/**\n * @param {{{{number[]}}}} nums\n * @return {{{{number[]}}}}\n */\nfunction solution(nums) {{\n    // Write your solution here\n    return nums;\n}}\n",
            })

        # ── All Questions ───────────────────────────────────
        all_questions = [
            # ═══════════ ARRAYS ═══════════
            ("arrays", "easy", "Two Sum", "Given an array of integers `nums` and an integer `target`, return indices of the two numbers that add up to `target`.", "[2,7,11,15], 9", "[0,1]", "nums[0]+nums[1]=9", "[2,7,11,15], 9", "[0, 1]", "[3,2,4], 6", "[1, 2]", "[3,3], 6", "[0, 1]", "Amazon"),
            ("arrays", "easy", "Best Time to Buy and Sell Stock", "Given prices[], find the maximum profit from one buy and one sell.", "[7,1,5,3,6,4]", "5", "Buy@1, sell@6", "[7,1,5,3,6,4]", "5", "[7,6,4,3,1]", "0", "Amazon"),
            ("arrays", "easy", "Contains Duplicate", "Return true if any value appears at least twice in the array.", "[1,2,3,1]", "true", "", "[1,2,3,4]", "false", "[1,1,1,3,3,4,3,2,4,2]", "true", "Google"),
            ("arrays", "medium", "Container With Most Water", "Find two lines that together with the x-axis form a container holding the most water.", "[1,8,6,2,5,4,8,3,7]", "49", "", "[1,1]", "1", "Microsoft"),
            ("arrays", "medium", "3Sum", "Find all unique triplets in the array which gives the sum of zero.", "[-1,0,1,2,-1,-4]", "[[-1,-1,2],[-1,0,1]]", "", "[0,0,0]", "[[0,0,0]]", "Amazon"),
            ("arrays", "medium", "Product of Array Except Self", "Return an array such that output[i] is the product of all elements except nums[i].", "[1,2,3,4]", "[24,12,8,6]", "", "[-1,1,0,-3,3]", "[0,0,9,0,0]", "Facebook"),
            ("arrays", "hard", "Trapping Rain Water", "Compute how much water it can trap after raining.", "[0,1,0,2,1,0,1,3,2,1,2,1]", "6", "", "[4,2,0,3,2,5]", "9", "Google"),
            ("arrays", "hard", "Maximum Subarray Sum", "Find the contiguous subarray with the largest sum.", "[-2,1,-3,4,-1,2,1,-5,4]", "6", "[4,-1,2,1] = 6", "[1]", "1", "Google"),

            # ═══════════ STRINGS ═══════════
            ("strings", "easy", "Valid Anagram", "Given two strings s and t, return true if t is an anagram of s.", "anagram, nagaram", "true", "", "rat, car", "false", "Amazon"),
            ("strings", "easy", "Reverse String", "Reverse the input string in-place.", "hello", "olleh", "", "Hannah", "hannaH", "Meta"),
            ("strings", "easy", "First Unique Character", "Find the index of the first non-repeating character.", "leetcode", "0", "l is unique", "aabb", "-1", "Google"),
            ("strings", "medium", "Longest Substring Without Repeating", "Find the length of the longest substring without repeating characters.", "abcabcbb", "3", "abc", "bbbbb", "1", "Amazon"),
            ("strings", "medium", "Group Anagrams", "Group strings that are anagrams of each other.", '[eat,tea,tan,ate,nat,bat]', '[[eat,tea,ate],[tan,nat],[bat]]', "", "Microsoft"),
            ("strings", "medium", "Valid Parentheses", "Given a string containing just ()[]{}, determine if input is valid.", "()[]{}", "true", "", "(]", "false", "Amazon"),
            ("strings", "hard", "Minimum Window Substring", "Find the minimum window in s that contains all characters of t.", "ADOBECODEBANC, ABC", "BANC", "", "a, a", "a", "Meta"),

            # ═══════════ LINKED LISTS ═══════════
            ("linked-lists", "easy", "Reverse Linked List", "Reverse a singly linked list.", "1->2->3->4->5", "5->4->3->2->1", "", "", "", "Amazon"),
            ("linked-lists", "easy", "Merge Two Sorted Lists", "Merge two sorted linked lists into one sorted list.", "1->2->4, 1->3->4", "1->1->2->3->4", "", "", "", "Microsoft"),
            ("linked-lists", "medium", "Linked List Cycle", "Detect if a linked list has a cycle.", "3->2->0->-4, pos=1", "true", "", "1->2, pos=0", "true", "Google"),
            ("linked-lists", "medium", "Remove Nth Node From End", "Remove the nth node from the end of the list.", "1->2->3->4->5, n=2", "1->2->3->5", "", "", "", "Amazon"),
            ("linked-lists", "hard", "Merge k Sorted Lists", "Merge k sorted linked lists into one sorted list.", "[1->4->5, 1->3->4, 2->6]", "1->1->2->3->4->5->6", "", "", "", "Google"),

            # ═══════════ STACKS & QUEUES ═══════════
            ("stacks-queues", "easy", "Valid Parentheses", "Check if input string has valid brackets.", "()[]{}", "true", "", "([)]", "false", "Amazon"),
            ("stacks-queues", "easy", "Min Stack", "Design a stack that supports push, pop, top, and retrieving min in O(1).", "push(-2),push(0),push(-3),getMin()", "-3", "", "pop,getMin()", "0", "Amazon"),
            ("stacks-queues", "medium", "Daily Temperatures", "For each day, find how many days until a warmer temperature.", "[73,74,75,71,69,72,76,73]", "[1,1,4,2,1,1,0,0]", "", "Google"),
            ("stacks-queues", "medium", "Evaluate Reverse Polish Notation", "Evaluate arithmetic expression in reverse polish notation.", '[2,1,+,3,*]', "9", "(2+1)*3=9", '[4,13,5,/,+]', "6", "Amazon"),
            ("stacks-queues", "hard", "Largest Rectangle in Histogram", "Find the area of the largest rectangle in the histogram.", "[2,1,5,6,2,3]", "10", "", "[2,4]", "4", "Google"),

            # ═══════════ HASH MAPS ═══════════
            ("hash-maps", "easy", "Two Sum (HashMap)", "Use a hash map for O(n) Two Sum solution.", "[2,7,11,15], 9", "[0,1]", "", "[3,2,4], 6", "[1,2]", "Amazon"),
            ("hash-maps", "easy", "Ransom Note", "Check if magazine can construct ransom note from letters.", "aa, aab", "false", "", "a, b", "false", "Google"),
            ("hash-maps", "medium", "Top K Frequent Elements", "Return the k most frequent elements.", "[1,1,1,2,2,3], k=2", "[1,2]", "", "[1], k=1", "[1]", "Meta"),
            ("hash-maps", "medium", "Longest Consecutive Sequence", "Find the length of the longest consecutive elements sequence.", "[100,4,200,1,3,2]", "4", "1,2,3,4", "[0,3,7,2,5,8,4,6,0,1]", "9", "Google"),
            ("hash-maps", "hard", "Minimum Window Substring (HashMap)", "Find minimum window in s containing all characters of t.", "a, aa", "", "", "aab, b", "ab", "Amazon"),

            # ═══════════ BINARY SEARCH ═══════════
            ("binary-search", "easy", "Binary Search", "Search for a target in a sorted array.", "[-1,0,3,5,9,12], 9", "4", "", "[-1,0,3,5,9,12], 2", "-1", "Amazon"),
            ("binary-search", "easy", "Guess Number Higher or Lower", "Guess number 1-n, higher/lower feedback.", "n=10, pick=6", "6", "", "n=1, pick=1", "1", "Google"),
            ("binary-search", "medium", "Search in Rotated Sorted Array", "Search in a rotated sorted array.", "[4,5,6,7,0,1,2], 0", "4", "", "[4,5,6,7,0,1,2], 3", "-1", "Amazon"),
            ("binary-search", "medium", "Find Minimum in Rotated Sorted Array", "Find the minimum element.", "[3,4,5,1,2]", "1", "", "[4,5,6,7,0,1,2]", "0", "Amazon"),
            ("binary-search", "hard", "Median of Two Sorted Arrays", "Find median of two sorted arrays in O(log(m+n)).", "[1,3], [2]", "2.0", "", "[1,2], [3,4]", "2.5", "Amazon"),

            # ═══════════ RECURSION ═══════════
            ("recursion", "easy", "Power of Two", "Return true if n is a power of two.", "16", "true", "", "3", "false", "Google"),
            ("recursion", "easy", "Factorial", "Compute n! recursively.", "5", "120", "", "0", "1", "Amazon"),
            ("recursion", "medium", "Subsets", "Return all possible subsets of a set.", "[1,2,3]", "[[],[1],[2],[3],[1,2],[1,3],[2,3],[1,2,3]]", "", "[0]", "[[],[0]]", "Meta"),
            ("recursion", "medium", "Permutations", "Return all permutations of distinct integers.", "[1,2,3]", "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]", "", "[0,1]", "[[0,1],[1,0]]", "Amazon"),
            ("recursion", "hard", "N-Queens", "Place n queens on an n×n chessboard so no two attack each other.", "n=4", "2", "", "n=1", "1", "Google"),

            # ═══════════ SORTING ═══════════
            ("sorting", "easy", "Bubble Sort", "Implement bubble sort to sort an array.", "[64,34,25,12,22,11,90]", "[11,12,22,25,34,64,90]", "", "[5,1,4,2,8]", "[1,2,4,5,8]", "Google"),
            ("sorting", "easy", "Insertion Sort", "Implement insertion sort.", "[12,11,13,5,6]", "[5,6,11,12,13]", "", "[3,1,4,1,5]", "[1,1,3,4,5]", "Amazon"),
            ("sorting", "medium", "Merge Sort", "Implement merge sort algorithm.", "[38,27,43,3,9,82,10]", "[3,10,27,38,43,82,9]", "", "[5,2,3,1]", "[1,2,3,5]", "Microsoft"),
            ("sorting", "medium", "Quick Sort", "Implement quick sort algorithm.", "[10,80,30,90,40,50,70]", "[10,30,40,50,70,80,90]", "", "[4,2,7,1]", "[1,2,4,7]", "Google"),
            ("sorting", "hard", "Sort Colors (Dutch National Flag)", "Sort array with only 0s, 1s, 2s in-place.", "[2,0,2,1,1,0]", "[0,0,1,1,2,2]", "", "[2]", "[2]", "Amazon"),

            # ═══════════ TREES ═══════════
            ("trees", "easy", "Maximum Depth of Binary Tree", "Find the maximum depth of a binary tree.", "[3,9,20,null,null,15,7]", "3", "", "[1,null,2]", "2", "Amazon"),
            ("trees", "easy", "Invert Binary Tree", "Invert (mirror) a binary tree.", "[4,2,7,1,3,6,9]", "[4,7,2,9,6,3,1]", "", "", "", "Google"),
            ("trees", "medium", "Validate Binary Search Tree", "Check if a binary tree is a valid BST.", "[2,1,3]", "true", "", "[5,1,4,null,null,3,6]", "false", "Amazon"),
            ("trees", "medium", "Lowest Common Ancestor", "Find the lowest common ancestor of two nodes.", "p=5, q=1, tree=[6,2,8,0,4,7,9]", "6", "", "", "", "Amazon"),
            ("trees", "hard", "Binary Tree Maximum Path Sum", "Find the maximum path sum in a binary tree.", "[1,2,3]", "6", "", "[-10,9,20,null,null,15,7]", "42", "Google"),

            # ═══════════ GRAPHS ═══════════
            ("graphs", "easy", "Number of Islands", "Count islands of '1' in a grid of '1's and '0's.", '["1","1","0","0","0";"1","1","0","0","0";"0","0","1","0","0";"0","0","0","1","1"]', "3", "", '["1","1","1";"0","1","0";"1","1","1"]', "1", "Amazon"),
            ("graphs", "medium", "Course Schedule", "Determine if you can finish all courses (cycle detection).", "2, [[1,0]]", "true", "", "2, [[1,0],[0,1]]", "false", "Google"),
            ("graphs", "medium", "Clone Graph", "Deep copy of an undirected graph.", "1-2-4, 1-3", "cloned", "", "", "", "Meta"),
            ("graphs", "hard", "Word Ladder", "Find shortest transformation sequence from beginWord to endWord.", "hit, cog, [hot,dot,dog,lot,log,cog]", "5", "", "hit, cog, [hot,dot,dog,lot,log]", "0", "Google"),

            # ═══════════ DYNAMIC PROGRAMMING ═══════════
            ("dynamic-programming", "easy", "Climbing Stairs", "Count distinct ways to climb n stairs (1 or 2 steps).", "2", "2", "", "3", "3", "Amazon"),
            ("dynamic-programming", "easy", "House Robber", "Rob houses (no two adjacent) to maximize money.", "[1,2,3,1]", "4", "rob house 1+3", "[2,7,9,3,1]", "12", "Amazon"),
            ("dynamic-programming", "medium", "Coin Change", "Find fewest coins to make up an amount.", "[1,5,10,25], 30", "2", "25+5", "[2], 3", "-1", "Amazon"),
            ("dynamic-programming", "medium", "Longest Increasing Subsequence", "Find length of LIS.", "[10,9,2,5,3,7,101,18]", "4", "[2,3,7,101]", "[0,1,0,3,2,3]", "4", "Amazon"),
            ("dynamic-programming", "hard", "Edit Distance", "Minimum operations to convert word1 to word2.", "horse, ros", "3", "", "intention, execution", "5", "Microsoft"),
            ("dynamic-programming", "hard", "Regular Expression Matching", "Implement regex matching with '.' and '*'.", "aa, a", "false", "", "aa, a*", "true", "Amazon"),

            # ═══════════ GREEDY ═══════════
            ("greedy", "easy", "Maximum Subarray", "Find contiguous subarray with largest sum.", "[-2,1,-3,4,-1,2,1,-5,4]", "6", "", "[1]", "1", "Google"),
            ("greedy", "easy", "Best Time to Buy Stock (Greedy)", "One-pass greedy approach for max profit.", "[7,1,5,3,6,4]", "5", "", "[7,6,4,3,1]", "0", "Amazon"),
            ("greedy", "medium", "Jump Game", "Can you reach the last index?", "[2,3,1,1,4]", "true", "", "[3,2,1,0,4]", "false", "Google"),
            ("greedy", "medium", "Task Scheduler", "Find least intervals to schedule all tasks.", '["A","A","A","B","B","B"]', "6", "", '["A","A","A","B","B","B","C"]', "8", "Amazon"),
            ("greedy", "hard", "Minimum Number of Arrows to Burst Balloons", "Find minimum arrows needed to burst all balloons.", "[[10,16],[2,8],[1,6],[7,12]]", "2", "", "[[1,2],[3,4],[5,6],[7,8]]", "4", "Google"),
        ]

        added = 0
        for item in all_questions:
            topic_slug, diff, title, desc = item[0], item[1], item[2], item[3]
            # examples, constraints, starter, solution, test_cases, company
            examples = item[4] if len(item) > 4 else ""
            output = item[5] if len(item) > 5 else ""
            explanation = item[6] if len(item) > 6 else ""
            tc_input = item[7] if len(item) > 7 else ""
            tc_output = item[8] if len(item) > 8 else ""
            company = item[9] if len(item) > 9 else ""

            t = topic_map.get(topic_slug)
            if not t:
                continue

            existing = DSAQuestion.query.filter_by(title=title, topic_id=t.id).first()
            if existing:
                continue

            # Build examples JSON
            ex_json = json.dumps([{"input": examples, "output": output, "explanation": explanation}]) if examples else "[]"
            # Build test cases JSON
            tests = []
            if tc_input:
                tests.append({"input": tc_input, "expected_output": tc_output})
            if tc_input and tc_output and len(item) > 10:
                tests.append({"input": item[9] if len(item) > 10 else tc_input, "expected_output": item[10] if len(item) > 10 else tc_output})
            tests_json = json.dumps(tests) if tests else json.dumps([{"input": examples, "expected_output": output}])

            # Build constraint hint
            constraint = f"Company: {company}" if company else ""

            # Build Python solution (simple placeholder)
            solution = f"# {title} - Solution\n# Time: O(n) | Space: O(1)\n\ndef solution(nums):\n    # Optimal approach\n    result = 0\n    for n in nums:\n        result += n\n    return result\n"

            # Multi-language starter code
            starter = starters(title, desc)

            q = DSAQuestion(
                topic_id=t.id, title=title, difficulty=diff,
                description=f"{desc}\n\n**Company Tag:** {company}" if company else desc,
                examples=ex_json, constraints=constraint,
                starter_code=starter, solution_code=solution,
                test_cases=tests_json,
            )
            db.session.add(q)
            added += 1

        db.session.commit()
        print(f"✅ Added {added} new DSA questions! (Total: {DSAQuestion.query.count()})")


if __name__ == "__main__":
    seed()
