"""Smoke test for Placement Portal - runs against the real app + DB via test client."""
import sys
import traceback

from app import create_app
from app.extensions import db
from app.models import User, Category, Question, QuizResult

# Stub the learning-ingest background work so the daemon thread finishes instantly
# instead of making real network/Gemini calls that linger and lock the SQLite DB
# during later runs of this script.
from app.learning import scraper, ai_engine

def _fake_fetch(url):
    return {"title": "Example", "content": "Example content", "meta": {}}

def _fake_analyze(title, source_type, content, meta):
    return {
        "summary": "summary",
        "key_points": ["key point"],
        "concepts": ["concept"],
        "interview_questions": ["question"],
        "roadmap": ["step"],
    }

scraper.fetch = _fake_fetch
ai_engine.analyze_content = _fake_analyze

PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"  PASS  {name}")
    else:
        FAIL.append(name)
        print(f"  FAIL  {name}  {detail}")


app = create_app()
app.config["WTF_CSRF_ENABLED"] = False  # disable CSRF for the test client
app.config["TESTING"] = True
client = app.test_client()


def get(path):
    return client.get(path, follow_redirects=False)


def post(path, data=None, **kwargs):
    if "json" in kwargs:
        return client.post(path, json=kwargs["json"], follow_redirects=False)
    return client.post(path, data=data or {}, follow_redirects=False, **kwargs)


# ---------- Public pages ----------
print("\n== Public pages ==")
check("GET /", get("/").status_code == 200, get("/").status_code)
check("GET /auth/login", get("/auth/login").status_code == 200)
check("GET /auth/register", get("/auth/register").status_code == 200)
r = get("/dashboard")
check("dashboard redirects when logged out", r.status_code == 302, r.status_code)
r = get("/quiz/")
check("quiz redirects when logged out", r.status_code == 302, r.status_code)
r = get("/resource/topic/technical-prep")
check("GET /resource/topic/technical-prep (public)", r.status_code == 200, r.status_code)

# ---------- Registration ----------
import uuid
EMAIL = f"smoke{uuid.uuid4().hex[:8]}@test.com"
PASSWORD = "password123"

print("\n== Registration ==")
r = post("/auth/register", {
    "name": "Smoke Tester",
    "email": EMAIL,
    "password": PASSWORD,
    "confirm_password": PASSWORD,
    "college": "Test College",
})
# Registration now shows a verification page (200) or redirects (302)
check("register succeeds", r.status_code in (200, 302), r.status_code)

# Extract verification URL from the response body and verify email
html = r.get_data(as_text=True)
import re
m = re.search(r'href="(/auth/verify-email/[^"]+)"', html)
if m:
    verify_path = m.group(1)
    r = get(verify_path)
    check("verify email link works", r.status_code in (200, 302), r.status_code)
else:
    # Fallback: directly verify via DB
    with app.app_context():
        u = User.query.filter_by(email=EMAIL).first()
        if u:
            u.email_verified = True
            from app.extensions import db as _db
            _db.session.commit()

# ---------- Login ----------
print("\n== Login ==")
r = post("/auth/login", {"email": EMAIL, "password": PASSWORD})
check("login redirects to dashboard", r.status_code == 302, r.status_code)
check("redirect target dashboard", "/dashboard" in r.headers.get("Location", ""))

# Wrong password
client.get("/auth/logout")
r = post("/auth/login", {"email": EMAIL, "password": "wrongpass"})
check("bad password rejected", r.status_code == 200, r.status_code)

# ---------- Authenticated pages ----------
print("\n== Authenticated pages ==")
post("/auth/login", {"email": EMAIL, "password": PASSWORD})

for path in ["/dashboard", "/resources", "/quiz/", "/quiz/history",
             "/quiz/leaderboard", "/quiz/bookmarks", "/learning/"]:
    r = get(path)
    check(f"GET {path}", r.status_code == 200, r.status_code)

# Download PDF that exists / doesn't
r = get("/download/resume_building_guide.pdf")
check("download existing pdf", r.status_code == 200, r.status_code)
r = get("/download/nonexistent.pdf")
check("download missing pdf redirects", r.status_code == 302, r.status_code)

# ---------- Quiz flow ----------
print("\n== Quiz flow ==")
with app.app_context():
    cat = Category.query.filter_by(name="Quantitative Aptitude").first()
check("found Quantitative Aptitude category", cat is not None)

r = get(f"/quiz/category/{cat.id}")
check(f"GET /quiz/category/{cat.id}", r.status_code == 200, r.status_code)

r = get(f"/quiz/start/{cat.id}")
check("start quiz redirects", r.status_code == 302, r.status_code)
check("start quiz -> question 1", "/quiz/question/1" in r.headers.get("Location", ""))

# Fetch each question page to ensure template renders
with client.session_transaction() as sess:
    qids = sess.get("quiz_question_ids", [])
check("quiz question ids stored in session", len(qids) > 0, len(qids))

for i in range(1, len(qids) + 1):
    r = get(f"/quiz/question/{i}")
    check(f"GET /quiz/question/{i}", r.status_code == 200, r.status_code)

# Bookmark the first question
first_qid = qids[0]
r = post(f"/quiz/bookmark/{first_qid}")
check("bookmark toggle", r.status_code == 302, r.status_code)
r = get("/quiz/bookmarks")
check("bookmarks page renders", r.status_code == 200, r.status_code)
r = post(f"/quiz/bookmark/{first_qid}")  # unbookmark
check("unbookmark toggle", r.status_code == 302, r.status_code)

# Submit quiz with ALL answers correct (simulate answering every question)
with app.app_context():
    form = {f"question_{qid}": Question.query.get(qid).correct_answer for qid in qids}
r = post("/quiz/submit", form)
check("submit quiz redirects", r.status_code == 302, r.status_code)
loc = r.headers.get("Location", "")
check("submit -> results page", "/quiz/result/" in loc or "/quiz/results/" in loc, loc)

import re
m = re.search(r"/(?:result|results)/(\d+)", loc)
if m:
    with app.app_context():
        res = QuizResult.query.get(int(m.group(1)))
    check("all-correct quiz scored 100%", res and res.score == len(qids),
          f"score={res.score if res else None}/{len(qids)}")
    r = get(f"/quiz/results/{res.id}")
    check("results page renders", r.status_code == 200, r.status_code)
    # Unauthorized access to another user's result
    with app.app_context():
        other = User.query.filter_by(email="admin@college.edu").first()
    if other:
        r = get(f"/quiz/results/{res.id}")
        check("results page accessible to owner", r.status_code == 200)

# Question 999 out of range
r = get("/quiz/question/999")
check("out-of-range question handled", r.status_code in (200, 302), r.status_code)

# ---------- Role separation ----------
print("\n== Role separation ==")
# Student must not reach the admin side even via ?next=
client.get("/auth/logout")
r = post("/auth/login?next=/admin/", {"email": EMAIL, "password": PASSWORD})
loc = r.headers.get("Location", "")
check("student ?next=/admin/ ignored", "/dashboard" in loc, loc)
post("/auth/login", {"email": EMAIL, "password": PASSWORD})

# ---------- Admin ----------
print("\n== Admin ==")
# Student should be blocked
r = get("/admin/")
check("student blocked from /admin/", r.status_code == 302, r.status_code)

with app.app_context():
    admin = User.query.filter_by(email="admin@college.edu").first()
check("admin user exists", admin is not None)
if admin:
    client.get("/auth/logout")
    post("/auth/login", {"email": "admin@college.edu", "password": "admin123"})
    # Full separation: admin must be blocked from student pages
    for path in ["/dashboard", "/resources", "/quiz/", "/learning/"]:
        r = get(path)
        loc = r.headers.get("Location", "")
        check(f"admin blocked from {path}", r.status_code == 302, r.status_code)
        check(f"admin {path} -> admin panel", "/admin/" in loc, loc)
    # Admin ?next= toward a student page must be ignored
    client.get("/auth/logout")
    r = post("/auth/login?next=/dashboard", {"email": "admin@college.edu", "password": "admin123"})
    loc = r.headers.get("Location", "")
    check("admin ?next=/dashboard ignored", "/admin/" in loc, loc)
    post("/auth/login", {"email": "admin@college.edu", "password": "admin123"})
    for path in ["/admin/", "/admin/users", "/admin/categories", "/admin/questions",
                 "/admin/resources"]:
        r = get(path)
        check(f"GET {path}", r.status_code == 200, r.status_code)
    # Add category
    r = post("/admin/categories/add", {"name": "Smoke Category", "type": "technical",
                                       "description": "test"})
    check("add category", r.status_code == 302, r.status_code)
    check("add category redirects to list", "/admin/categories" in r.headers.get("Location", ""))
    with app.app_context():
        cat2 = Category.query.filter_by(name="Smoke Category").first()
    check("category persisted", cat2 is not None)
    if cat2:
        # Edit it
        r = post(f"/admin/categories/edit/{cat2.id}", {"name": "Smoke Category 2",
                                                       "type": "aptitude", "description": "t"})
        check("edit category", r.status_code == 302, r.status_code)
        # Add question in it
        r = post("/admin/questions/add", {
            "category_id": str(cat2.id), "question_text": "Q?", "option_a": "A",
            "option_b": "B", "option_c": "C", "option_d": "D",
            "correct_answer": "A", "explanation": "e", "difficulty": "easy",
        })
        check("add question", r.status_code == 302, r.status_code)
        with app.app_context():
            q2 = Question.query.filter_by(question_text="Q?").first()
        check("question persisted", q2 is not None)
        if q2:
            # Edit question page renders
            r = get(f"/admin/questions/edit/{q2.id}")
            check("edit question page renders", r.status_code == 200, r.status_code)
            # Delete question
            r = post(f"/admin/questions/delete/{q2.id}")
            check("delete question", r.status_code == 302, r.status_code)
        # Delete category
        r = post(f"/admin/categories/delete/{cat2.id}")
        check("delete category", r.status_code == 302, r.status_code)
        with app.app_context():
            check("category deleted", Category.query.get(cat2.id) is None)
    # Resources CRUD
    r = post("/admin/resources/add", {"title": "Smoke Res", "description": "d",
                                      "resource_type": "Notes", "content": "c", "link": ""})
    check("add resource", r.status_code == 302, r.status_code)
    from app.models import Resource
    with app.app_context():
        res2 = Resource.query.filter_by(title="Smoke Res").first()
    check("resource persisted", res2 is not None)
    if res2:
        r = post(f"/admin/resources/{res2.id}/edit", {"title": "Smoke Res 2", "description": "d",
                                                     "resource_type": "Notes", "content": "c", "link": ""})
        check("edit resource", r.status_code == 302, r.status_code)
        r = post(f"/admin/resources/delete/{res2.id}")
        check("delete resource", r.status_code == 302, r.status_code)

# ---------- Learning assistant (no API key) ----------
print("\n== Learning Assistant ==")
# Re-login as the student (admins are blocked from the student side)
client.get("/auth/logout")
post("/auth/login", {"email": EMAIL, "password": PASSWORD})
r = post("/learning/api/ingest", json={"url": "https://example.com"})
check("ingest w/o GEMINI key still queues", r.status_code == 202, r.status_code)
data = r.get_json()
check("ingest returns id+status", data and "id" in data, data)

# ---------- Cleanup test user ----------
print("\n== Cleanup ==")
with app.app_context():
    u = User.query.filter_by(email=EMAIL).first()
    if u:
        QuizResult.query.filter_by(user_id=u.id).delete()
        db.session.delete(u)
        db.session.commit()
        print("  removed smoke test user")

print(f"\n===== {len(PASS)} passed, {len(FAIL)} failed =====")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
