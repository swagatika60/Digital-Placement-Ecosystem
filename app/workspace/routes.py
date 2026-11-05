# -*- coding: utf-8 -*-
"""
Workspace blueprint — the "high-velocity developer platform" modules:

  * System Design Vault      (/design)         — architecture blueprints + tags
  * DSA Labs & Visualizer    (/dsa/labs)       — university lab programs + canvas viz
  * ScopeSentry              (/scope-sentry)   — resume / README risk auditor
  * University Lab Code Vault(/vault)          — peer-sourced lab solutions
  * Peer Code-Duel Rooms     (/duel)           — 1v1 timed algorithm sprints
"""
import io
import json
import logging
import secrets
from datetime import datetime

from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, flash, session,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.decorators import student_required
from app.models import LabVaultEntry, DuelRoom, ScopeSentryAudit
from app.models.dsa import DSAQuestion, DSATopic
from app.workspace.data import SYSTEM_DESIGN_VAULT, DSA_LABS

try:  # pypdf is in requirements; guard so dev run still boots without it
    from pypdf import PdfReader
    _HAS_PYPdf = True
except Exception:  # pragma: no cover
    _HAS_PYPdf = False

workspace = Blueprint("workspace", __name__)

_log = logging.getLogger(__name__)


@workspace.before_request
def _guard():
    from app.decorators import reject_admin
    if current_user.is_authenticated and current_user.role == "admin":
        return reject_admin()


# ── System Design Vault ────────────────────────────────────────────
@workspace.route("/design")
@login_required
@student_required
def design_vault():
    return render_template("workspace/design_vault.html", vault=SYSTEM_DESIGN_VAULT)


# ── DSA Labs & Visualizer ──────────────────────────────────────────
@workspace.route("/dsa/labs")
@login_required
@student_required
def dsa_labs():
    data = DSA_LABS
    # Attach live question counts from the DB where we can match them.
    topics = {t.slug: t for t in DSATopic.query.all()}
    for lab in data:
        linked = topics.get(lab.get("topic_slug", ""))
        if linked:
            lab["question_total"] = DSAQuestion.query.filter_by(topic_id=linked.id).count()
            lab["topic_name"] = linked.name
    return render_template("workspace/dsa_labs.html", labs=data)


@workspace.route("/dsa/labs/<slug>/visualize")
@login_required
@student_required
def lab_visualize(slug):
    for lab in DSA_LABS:
        if lab.get("slug") == slug:
            return render_template("workspace/lab_visualize.html", lab=lab)
    flash("That lab module was not found.", "warning")
    return redirect(url_for("workspace.dsa_labs"))


# ── ScopeSentry: resume / README risk auditor ──────────────────────
@workspace.route("/scope-sentry")
@login_required
@student_required
def scope_sentry():
    # Show the most recent saved audit, if any.
    audit = (ScopeSentryAudit.query.filter_by(user_id=current_user.id)
             .order_by(ScopeSentryAudit.created_at.desc()).first())
    findings = json.loads(audit.findings) if audit and audit.findings else []
    return render_template("workspace/scope_sentry.html", audit=audit, findings=findings)


@workspace.route("/scope-sentry/analyze", methods=["POST"])
@login_required
@student_required
def scope_sentry_analyze():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "resume")
    text = (data.get("text") or "").strip()
    if len(text) < 10:
        return jsonify({"error": "Paste at least a few bullet points to audit."}), 400

    findings, score = _analyze_scope(text, source)

    audit = ScopeSentryAudit(
        user_id=current_user.id, source=source, score=score,
        findings=json.dumps(findings),
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"score": score, "findings": findings})


@workspace.route("/scope-sentry/upload", methods=["POST"])
@login_required
@student_required
def scope_sentry_upload():
    """Accept a resume file (PDF / TXT / MD), extract text, run the audit.

    Text is extracted server-side (pypdf for PDFs, utf-8 for plain text) and
    the same heuristic scan runs, persisting a ScopeSentryAudit. The raw file
    is never stored — only the score + findings.
    """
    uploaded = request.files.get("resume")
    if not uploaded or not uploaded.filename:
        return jsonify({"error": "No file uploaded."}), 400

    filename = uploaded.filename.lower()
    try:
        if filename.endswith(".pdf"):
            if not _HAS_PYPdf:
                return jsonify({
                    "error": "PDF support is not installed (pip install pypdf)."
                }), 500
            reader = PdfReader(io.BytesIO(uploaded.read()))
            text = "\n".join(
                (page.extract_text() or "") for page in reader.pages
            )
        else:
            if not (filename.endswith(".txt") or filename.endswith(".md")):
                return jsonify({
                    "error": "Supported formats: PDF, TXT, Markdown."
                }), 400
            text = uploaded.read().decode("utf-8", errors="replace")
    except Exception as exc:
        _log.error("[sentry] file parse failed for %s: %s", filename, exc)
        return jsonify({
            "error": "Could not read that file. Is it a valid PDF or text file?"
        }), 400

    text = (text or "").strip()
    if len(text) < 10:
        return jsonify({"error": "No readable text found in the file."}), 400

    findings, score = _analyze_scope(text, "resume")
    audit = ScopeSentryAudit(
        user_id=current_user.id, source="resume_upload", score=score,
        findings=json.dumps(findings),
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({"score": score, "findings": findings, "source": "resume_upload"})


def _analyze_scope(text, source):
    """Heuristic risk scan. Honest, rule-based — no AI boilerplate."""
    lower = text.lower()
    findings = []
    score = 100

    def _add(severity, title, note):
        findings.append({"severity": severity, "title": title, "note": note})

    # 1. Vague metrics — numbers are the antidote.
    metric_words = ["improved", "increased", "reduced", "boosted", "optimized", "enhanced"]
    has_metric = any(w in lower for w in metric_words)
    has_number = any(ch.isdigit() for ch in text)
    if has_metric and not has_number:
        score -= 20
        _add("high", "Improvement claims lack numbers",
             "You say 'improved X' without a metric. Add a baseline → result figure "
             "(e.g. 'cut latency 40%').")
    if not has_metric and not has_number:
        score -= 15
        _add("medium", "No measurable outcomes",
             "No quantified impact anywhere. Recruiters scan for numbers first.")

    # 2. Missing technical depth.
    depth_terms = ["architecture", "schema", "api", "database", "caching",
                   "asynchronous", "concurrency", "load", "latency", "throughput",
                   "algorithm", "complexity", "distributed", "scaling"]
    found_depth = [w for w in depth_terms if w in lower]
    if not found_depth:
        score -= 18
        _add("high", "No technical surface",
             "None of the expected depth signals appear. Name the stack pieces you "
             "actually touched: schema, API, caching, async, complexity.")
    elif len(found_depth) < 2:
        score -= 10
        _add("medium", "Thin technical depth",
             f"Only {len(found_depth)} technical signal(s): {', '.join(found_depth)}. "
             "Add one or two more concrete implementation details.")

    # 3. Time / duration phrasing (often filler).
    if any(w in lower for w in ["passionate", "highly motivated", "hardworking",
                                "team player", "go-getter"]):
        score -= 8
        _add("low", "Buzzy filler",
             "Generic trait words (passionate, team player…) read as filler. Replace "
             "them with a concrete thing you built.")

    # 4. Architecture risk signal for READMEs.
    if source == "readme":
        if "setup" not in lower and "install" not in lower and "getting started" not in lower:
            score -= 10
            _add("medium", "Missing setup instructions",
                 "A good README is runnable. Add a Setup/Install section so a reviewer "
                 "can run the project in minutes.")
        if "api" in lower and "authentication" not in lower and "auth" not in lower:
            score -= 6
            _add("low", "Auth unspecified",
                 "You mention an API but not authentication. Even a half-line on how "
                 "requests are authorized matters.")

    score = max(0, min(100, score))
    findings.sort(key=lambda f: {"high": 0, "medium": 1, "low": 2}[f["severity"]])
    return findings, score


# ── University Lab Code Vault ──────────────────────────────────────
@workspace.route("/vault")
@login_required
@student_required
def vault():
    entries = (LabVaultEntry.query.order_by(LabVaultEntry.created_at.desc())
               .limit(50).all())
    return render_template("workspace/vault.html", entries=entries)


@workspace.route("/vault/upload", methods=["POST"])
@login_required
@student_required
def vault_upload():
    program = (request.form.get("program") or "").strip()
    code = (request.form.get("code") or "").strip()
    if not program or not code:
        flash("Program title and code are required.", "warning")
        return redirect(url_for("workspace.vault"))

    viva_qs = [q.strip() for q in
               (request.form.get("viva_questions") or "").splitlines() if q.strip()]
    entry = LabVaultEntry(
        user_id=current_user.id,
        subject=(request.form.get("subject") or "General").strip(),
        lab_no=(request.form.get("lab_no") or "").strip(),
        program=program,
        language=(request.form.get("language") or "python").strip(),
        code=code,
        explanation=(request.form.get("explanation") or "").strip(),
        viva_questions=json.dumps(viva_qs),
        tags=(request.form.get("tags") or "").strip(),
    )
    db.session.add(entry)
    db.session.commit()
    flash("Lab solution published to the vault. Viva notes included.", "success")
    return redirect(url_for("workspace.vault"))


@workspace.route("/vault/<int:entry_id>/upvote", methods=["POST"])
@login_required
@student_required
def vault_upvote(entry_id):
    entry = LabVaultEntry.query.get_or_404(entry_id)
    entry.upvotes = (entry.upvotes or 0) + 1
    db.session.commit()
    return jsonify({"upvotes": entry.upvotes})


# ── Peer Code-Duel Rooms ───────────────────────────────────────────
@workspace.route("/duel")
@login_required
@student_required
def duel_lobby():
    return render_template("workspace/duel.html")


@workspace.route("/duel/create", methods=["POST"])
@login_required
@student_required
def duel_create():
    # Accept both a JSON body (REST clients) and classic form submission.
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or request.form.get("topic") or "Mixed").strip()
    raw_duration = payload.get("duration_min") or request.form.get("duration_min", 15)
    try:
        duration = int(raw_duration)
    except (TypeError, ValueError):
        duration = 15

    try:
        code = secrets.token_hex(3).upper()[:6]
        # Pick a small set of questions for the duel (random-ish, capped).
        questions = DSAQuestion.query.order_by(db.func.random()).limit(10).all()
        qids = [q.id for q in questions]

        room = DuelRoom(
            code=code, creator_id=current_user.id, topic=topic,
            duration_min=duration, question_ids=json.dumps(qids),
            status="waiting", created_at=datetime.utcnow(),
        )
        db.session.add(room)
        db.session.commit()
    except Exception as exc:
        # Surface the real failure instead of a silent 500 / generic "try again".
        db.session.rollback()
        _log.error("[duel] room creation failed: %s", exc)
        if request.accept_mimetypes.accept_json:
            return jsonify({"success": False, "error": str(exc)}), 500
        flash("Could not create room \u2014 please try again.", "danger")
        return redirect(url_for("workspace.duel_lobby"))

    # JSON clients (the duel lobby JS) get the room code directly; plain
    # browser submits keep the classic redirect flow.
    if request.accept_mimetypes.accept_json:
        return jsonify({
            "success": True, "room_code": code,
            "redirect": url_for("workspace.duel_room", code=code),
        }), 200

    flash(f"Duel room {code} created. Share the code to challenge a peer.", "success")
    return redirect(url_for("workspace.duel_room", code=code))


@workspace.route("/duel/<code>")
@login_required
@student_required
def duel_room(code):
    room = DuelRoom.query.filter_by(code=code.upper()).first_or_404()
    if room.opponent_id is None and room.creator_id != current_user.id:
        room.opponent_id = current_user.id
        room.status = "active"
        room.started_at = datetime.utcnow()
        db.session.commit()
    qids = json.loads(room.question_ids or "[]")
    questions = DSAQuestion.query.filter(DSAQuestion.id.in_(qids)).all()
    if not room.is_member(current_user.id):
        flash("You are not part of this duel room.", "warning")
        return redirect(url_for("workspace.duel_lobby"))
    return render_template("workspace/duel_room.html", room=room, questions=questions)
