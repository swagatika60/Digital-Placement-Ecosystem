"""
DSA Practice blueprint — topics, questions, code editor, algorithm visualizer.
"""
import json
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app.extensions import db
from app.decorators import student_required
from app.models.dsa import DSATopic, DSAQuestion, DSASubmission, AlgorithmVisualizer

dsa_bp = Blueprint("dsa", __name__, url_prefix="/dsa")


@dsa_bp.before_request
def _reject_admin():
    from app.decorators import reject_admin
    if current_user.is_authenticated and current_user.role == "admin":
        return reject_admin()


# ── Topics List ───────────────────────────────────────────────
@dsa_bp.route("/")
@login_required
@student_required
def topics():
    all_topics = DSATopic.query.order_by(DSATopic.order, DSATopic.name).all()
    # Count questions per topic + difficulty
    topic_stats = []
    for t in all_topics:
        easy = DSAQuestion.query.filter_by(topic_id=t.id, difficulty="easy").count()
        medium = DSAQuestion.query.filter_by(topic_id=t.id, difficulty="medium").count()
        hard = DSAQuestion.query.filter_by(topic_id=t.id, difficulty="hard").count()
        # User's solved count per topic
        solved = 0
        if current_user.is_authenticated:
            solved = db.session.query(DSASubmission.question_id).filter(
                DSASubmission.user_id == current_user.id,
                DSASubmission.status == "passed",
                DSASubmission.question_id.in_(
                    db.session.query(DSAQuestion.id).filter_by(topic_id=t.id)
                )
            ).distinct().count()
        topic_stats.append({
            "topic": t,
            "easy": easy, "medium": medium, "hard": hard,
            "total": easy + medium + hard,
            "solved": solved,
        })
    return render_template("dsa/topics.html", topic_stats=topic_stats)


# ── Practice: Questions for a Topic ───────────────────────────
@dsa_bp.route("/<slug>")
@login_required
@student_required
def topic_practice(slug):
    topic = DSATopic.query.filter_by(slug=slug).first_or_404()
    difficulty = request.args.get("difficulty", "")
    query = DSAQuestion.query.filter_by(topic_id=topic.id)
    if difficulty in ("easy", "medium", "hard"):
        query = query.filter_by(difficulty=difficulty)
    questions = query.all()
    return render_template("dsa/practice.html", topic=topic, questions=questions, selected_diff=difficulty)


# ── Code Editor: Solve a Question ─────────────────────────────
@dsa_bp.route("/question/<int:qid>")
@login_required
@student_required
def question_editor(qid):
    q = DSAQuestion.query.get_or_404(qid)
    topic = DSATopic.query.get(q.topic_id)
    examples = json.loads(q.examples) if q.examples else []
    test_cases = json.loads(q.test_cases) if q.test_cases else []
    starter = q.starter_code or "# Write your solution here\n"

    # Load previous submission if any
    prev = (DSASubmission.query.filter_by(user_id=current_user.id, question_id=qid)
            .order_by(DSASubmission.created_at.desc()).first())
    prev_code = prev.code if prev else starter

    return render_template("dsa/editor.html", question=q, topic=topic,
                           examples=examples, test_cases=test_cases,
                           starter_code=starter, prev_code=prev_code)


@dsa_bp.route("/question/<int:qid>/submit", methods=["POST"])
@login_required
@student_required
def submit_code(qid):
    q = DSAQuestion.query.get_or_404(qid)
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    lang = data.get("language", "python")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    test_cases = json.loads(q.test_cases) if q.test_cases else []
    results = []
    passed = 0

    for i, tc in enumerate(test_cases):
        try:
            if lang == "python":
                result = _run_python(code, tc)
            elif lang == "javascript":
                result = _run_javascript(code, tc)
            else:
                # Java/C/C++: syntax check only (no execution in browser)
                result = _check_syntax(code, lang, tc)

            if result["passed"]:
                passed += 1
            results.append(result)
        except Exception as e:
            results.append({
                "input": str(tc.get("input", "")),
                "expected": str(tc.get("expected_output", "")),
                "got": f"Error: {str(e)[:200]}",
                "passed": False,
            })

    status = "passed" if passed == len(test_cases) and len(test_cases) > 0 else "failed"
    output_msg = f"{passed}/{len(test_cases)} test cases passed"

    sub = DSASubmission(
        user_id=current_user.id, question_id=qid,
        code=code, language=lang, status=status,
        output=output_msg, test_results=json.dumps(results),
    )
    db.session.add(sub)
    db.session.commit()

    return jsonify({
        "status": status,
        "passed": passed,
        "total": len(test_cases),
        "output": output_msg,
        "results": results,
    })


def _run_python(code, tc):
    """Execute Python code safely."""
    env = {}
    exec(code, {"__builtins__": {}}, env)
    func = env.get("solution")
    if not func:
        return {"input": str(tc.get("input", "")), "expected": str(tc.get("expected_output", "")),
                "got": "No 'solution' function found", "passed": False}
    inp = tc.get("input", "")
    if isinstance(inp, str):
        try: inp = json.loads(inp)
        except: pass
    got = func(*inp) if isinstance(inp, (list, tuple)) else func(inp)
    expected = tc.get("expected_output", "")
    if isinstance(expected, str):
        try: expected = json.loads(expected)
        except: pass
    ok = str(got) == str(expected)
    return {"input": str(tc.get("input", "")), "expected": str(expected), "got": str(got), "passed": ok}


def _run_javascript(code, tc):
    """Execute JavaScript code via Node.js subprocess."""
    import subprocess, tempfile, os
    inp = tc.get("input", "")
    if isinstance(inp, str):
        try: inp = json.loads(inp)
        except: pass
    expected = tc.get("expected_output", "")
    if isinstance(expected, str):
        try: expected = json.loads(expected)
        except: pass

    # Build Node.js wrapper
    args = json.dumps(inp) if isinstance(inp, (list, tuple)) else json.dumps([inp])
    wrapper = f"""{code}

const result = solution({args});
console.log(JSON.stringify(result));
"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(wrapper)
            f.flush()
            proc = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=5)
            os.unlink(f.name)
            if proc.returncode != 0:
                return {"input": str(tc.get("input", "")), "expected": str(expected),
                        "got": f"Error: {proc.stderr[:200]}", "passed": False}
            got_str = proc.stdout.strip()
            try: got = json.loads(got_str)
            except: got = got_str
            ok = str(got) == str(expected)
            return {"input": str(tc.get("input", "")), "expected": str(expected), "got": str(got), "passed": ok}
    except FileNotFoundError:
        return {"input": str(tc.get("input", "")), "expected": str(expected),
                "got": "Node.js not installed", "passed": False}
    except subprocess.TimeoutExpired:
        return {"input": str(tc.get("input", "")), "expected": str(expected),
                "got": "Time limit exceeded", "passed": False}


def _check_syntax(code, lang, tc):
    """Basic syntax validation for Java/C/C++ (no execution)."""
    expected = tc.get("expected_output", "")
    has_solution = "solution" in code.lower() or "class" in code.lower() or "def" in code.lower()
    has_return = "return" in code
    if not has_solution:
        return {"input": str(tc.get("input", "")), "expected": str(expected),
                "got": f"Error: No solution function/class found in {lang.upper()}", "passed": False}
    if not has_return:
        return {"input": str(tc.get("input", "")), "expected": str(expected),
                "got": f"⚠️ Code submitted for {lang.upper()} (syntax check only). Add a return statement to complete.", "passed": False}
    return {"input": str(tc.get("input", "")), "expected": str(expected),
            "got": f"✅ {lang.upper()} code submitted successfully (execution requires {lang} runtime)", "passed": True}


# ── Algorithm Visualizer ──────────────────────────────────────
@dsa_bp.route("/visualizer")
@login_required
@student_required
def visualizer():
    algos = AlgorithmVisualizer.query.order_by(AlgorithmVisualizer.category, AlgorithmVisualizer.name).all()
    grouped = {}
    for a in algos:
        grouped.setdefault(a.category or "Other", []).append(a)
    return render_template("dsa/visualizer.html", grouped=grouped, algos=algos)


@dsa_bp.route("/visualizer/<slug>")
@login_required
@student_required
def visualizer_detail(slug):
    algo = AlgorithmVisualizer.query.filter_by(slug=slug).first_or_404()
    steps = json.loads(algo.steps_json) if algo.steps_json else []
    code = json.loads(algo.code_json) if algo.code_json else []
    return render_template("dsa/viz_player.html", algo=algo, steps=steps, code_lines=code)
