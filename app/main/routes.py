import os
from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, current_app, request, session
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.decorators import student_required
from app.models import Resource, Category, Question, QuizResult, StudentActivity, StudyGoal, StudyStreak, QuestionBookmark
from app.main.data import TOPIC_CONTENT

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Student dashboard with real stats, category progress, and a score trend."""
    results = (QuizResult.query.filter_by(user_id=current_user.id)
               .order_by(QuizResult.taken_at.desc()).all())

    total_attempts = len(results)
    avg_score = round(sum(r.percentage or 0 for r in results) / total_attempts, 2) if total_attempts else 0
    best_score = max((r.percentage or 0 for r in results), default=0)
    questions_attempted = sum(r.total_questions or 0 for r in results)

    recent_quizzes = []
    for r in results[:5]:
        cat = Category.query.get(r.category_id)
        recent_quizzes.append({
            'category': cat.name if cat else 'Unknown',
            'score': round(r.percentage or 0, 1),
            'date': r.taken_at.strftime('%b %d, %Y') if r.taken_at else ''
        })

    # Best percentage per category
    best_by_category = {}
    for r in results:
        p = r.percentage or 0
        if r.category_id not in best_by_category or p > best_by_category[r.category_id]:
            best_by_category[r.category_id] = p
    category_progress = []
    for cat_id, p in best_by_category.items():
        cat = Category.query.get(cat_id)
        category_progress.append({'name': cat.name if cat else f'Category {cat_id}',
                                  'progress': round(p, 1)})

    # Score trend for the chart (oldest -> newest, last 10 attempts)
    trend = [{'label': r.taken_at.strftime('%m/%d') if r.taken_at else '',
              'score': round(r.percentage or 0, 1)} for r in results[:10]]
    trend.reverse()

    return render_template('dashboard.html',
                           user=current_user,
                           quizzes_taken=total_attempts,
                           average_score=avg_score,
                           questions_attempted=questions_attempted,
                           best_score=best_score,
                           recent_quizzes=recent_quizzes,
                           category_progress=category_progress,
                           trend=trend)

@main.route('/resources')
@login_required
@student_required
def resources():
    all_resources = Resource.query.order_by(Resource.resource_type, Resource.created_at.desc()).all()
    resources_by_type = {}
    for resource in all_resources:
        res_type = resource.resource_type or 'General'
        resources_by_type.setdefault(res_type, []).append(resource)
    return render_template('resources.html', resources_by_type=resources_by_type)

@main.route('/resource/topic/<topic_id>')
def view_topic(topic_id):
    """Expert-curated content database for placement success."""
    resource_data = TOPIC_CONTENT.get(topic_id)
    if not resource_data:
        flash('This resource module is being updated with the latest data.', 'info')
        return redirect(url_for('main.resources'))

    return render_template('view_resource.html', resource=resource_data)

@main.route('/download/<filename>')
@login_required
@student_required
def download_pdf(filename):
    pdf_directory = os.path.join(current_app.root_path, 'static', 'pdfs')
    file_path = os.path.join(pdf_directory, filename)

    if os.path.exists(file_path):
        return send_from_directory(pdf_directory, filename, as_attachment=True)
    else:
        display_name = filename.replace('_', ' ').replace('.pdf', '').upper()
        flash(f"The module '{display_name}' is currently in review. Check back shortly!", "info")
        return redirect(url_for('main.resources'))


@main.route('/analytics')
@login_required
@student_required
def analytics():
    """Detailed performance analytics for the current user."""
    results = (QuizResult.query.filter_by(user_id=current_user.id)
               .order_by(QuizResult.taken_at.desc()).all())

    total_quizzes = len(results)
    if total_quizzes == 0:
        return render_template('analytics.html',
                               total_quizzes=0, avg_score=0, best_score=0,
                               total_questions_attempted=0, category_stats=[],
                               strengths=[], weaknesses=[], improvement=[],
                               recent_results=[], trend_data=[])

    scores = [r.percentage or 0 for r in results]
    avg_score = round(sum(scores) / len(scores), 1)
    best_score = round(max(scores), 1)
    total_questions_attempted = sum(r.total_questions or 0 for r in results)

    # Category-wise stats
    cat_data = {}
    for r in results:
        cid = r.category_id
        if cid not in cat_data:
            cat = Category.query.get(cid)
            cat_data[cid] = {'name': cat.name if cat else f'Category {cid}',
                             'scores': [], 'best': 0, 'attempts': 0}
        cat_data[cid]['scores'].append(r.percentage or 0)
        cat_data[cid]['attempts'] += 1
        cat_data[cid]['best'] = max(cat_data[cid]['best'], r.percentage or 0)

    category_stats = []
    for cid, d in cat_data.items():
        avg = round(sum(d['scores']) / len(d['scores']), 1)
        category_stats.append({
            'id': cid,
            'name': d['name'],
            'avg_score': avg,
            'best_score': round(d['best'], 1),
            'attempts': d['attempts'],
        })
    category_stats.sort(key=lambda x: x['avg_score'], reverse=True)

    # Strengths (>=70%) and weaknesses (<50%)
    strengths = [c for c in category_stats if c['avg_score'] >= 70]
    weaknesses = [c for c in category_stats if c['avg_score'] < 50 and c['attempts'] >= 2]

    # ── Intelligent Weakness Auditor ──────────────────────────────
    # Compiles targeted 5-minute warm-up drills from the weakest areas.
    # Diagnosis is derived from honest, un-padded category averages.
    drill_suggestions = []
    for c in category_stats:
        avg = c['avg_score']
        if avg >= 60:
            continue
        if avg < 35:
            note = ("Foundational gap — revisit the topic notes first, then "
                    "re-attempt a relaxed practice set without the timer.")
        elif avg < 50:
            note = ("Core idea is shaky — run a focused drill and read every "
                    "explanation slowly before moving on.")
        else:
            note = ("On the cusp — lock it in with timed drills at 60s per "
                    "question to build speed under pressure.")
        drill_suggestions.append({
            'name': c['name'],
            'avg_score': c['avg_score'],
            'attempts': c['attempts'],
            'category_id': c['id'],
            'note': note,
            'href': url_for('quiz.start_quiz', category_id=c['id']),
        })
    drill_suggestions.sort(key=lambda x: x['avg_score'])

    # Improvement trend: compare first half vs second half of attempts per category
    improvement = []
    for cid, d in cat_data.items():
        if len(d['scores']) < 2:
            continue
        mid = len(d['scores']) // 2
        # scores are newest-first, so first half = recent, second half = older
        recent_avg = sum(d['scores'][:mid]) / mid
        older_avg = sum(d['scores'][mid:]) / (len(d['scores']) - mid)
        change = round(recent_avg - older_avg, 1)
        improvement.append({'category': d['name'], 'change': change})
    improvement.sort(key=lambda x: abs(x['change']), reverse=True)

    # Recent results for the table
    recent_results = []
    for r in results[:15]:
        cat = Category.query.get(r.category_id)
        recent_results.append({
            'category_name': cat.name if cat else 'Unknown',
            'score': r.score,
            'total_questions': r.total_questions,
            'percentage': round(r.percentage or 0, 1),
            'date': r.taken_at.strftime('%b %d, %Y') if r.taken_at else '',
        })

    # Trend data for the chart (newest last for left-to-right display)
    trend_data = [{'label': (r.taken_at.strftime('%m/%d') if r.taken_at else ''),
                   'score': round(r.percentage or 0, 1)} for r in results[:20]]
    trend_data.reverse()

    return render_template('analytics.html',
                           total_quizzes=total_quizzes,
                           avg_score=avg_score,
                           best_score=best_score,
                           total_questions_attempted=total_questions_attempted,
                           category_stats=category_stats,
                           strengths=strengths,
                           weaknesses=weaknesses,
                           improvement=improvement,
                           recent_results=recent_results,
                           trend_data=trend_data,
                           drill_suggestions=drill_suggestions)


# ── Study Planner ─────────────────────────────────────────────────

def _get_or_create_streak():
    streak = StudyStreak.query.filter_by(user_id=current_user.id).first()
    if not streak:
        streak = StudyStreak(user_id=current_user.id)
        db.session.add(streak)
        db.session.commit()
    return streak


def _update_streak(streak, quiz_date=None):
    """Update streak when a quiz is taken."""
    today = quiz_date or date.today()
    if streak.last_study_date == today:
        return  # already counted today

    if streak.last_study_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_study_date = today
    streak.total_study_days += 1
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    db.session.commit()


@main.route('/study-plan')
@login_required
@student_required
def study_plan():
    """Study planner with goals, streaks, and priorities."""
    streak = _get_or_create_streak()
    today = date.today()

    # Today's goal
    today_goal = StudyGoal.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    # Week calendar
    week_start = today - timedelta(days=today.weekday())
    week_days = []
    study_dates = {
        g.date for g in StudyGoal.query.filter(
            StudyGoal.user_id == current_user.id,
            StudyGoal.date >= week_start,
            StudyGoal.date <= today
        ).all() if g.completed_questions > 0
    }
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i in range(7):
        d = week_start + timedelta(days=i)
        week_days.append({
            'name': day_names[i],
            'num': d.day,
            'is_today': d == today,
            'studied': d in study_dates,
        })

    # Categories
    all_categories = Category.query.order_by(Category.type, Category.name).all()

    # Priority categories (stored in session for simplicity)
    priority_ids = set()
    if 'priority_categories' in request.args:
        pass  # handled by toggle route
    # Get from session
    priority_ids = set(session.get('priority_categories', []))

    # Weak categories (avg < 50%)
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    cat_scores = {}
    for r in results:
        cid = r.category_id
        if cid not in cat_scores:
            cat_scores[cid] = []
        cat_scores[cid].append(r.percentage or 0)

    weak_categories = []
    for cid, scores in cat_scores.items():
        avg = sum(scores) / len(scores)
        if avg < 50 and len(scores) >= 2:
            cat = Category.query.get(cid)
            if cat:
                weak_categories.append({'name': cat.name, 'avg_score': round(avg, 1), 'id': cid})

    return render_template('study_plan.html',
                           streak=streak,
                           today_goal=today_goal,
                           week_days=week_days,
                           all_categories=all_categories,
                           priority_ids=priority_ids,
                           weak_categories=weak_categories)


@main.route('/study-plan/update-goal', methods=['POST'])
@login_required
@student_required
def update_goal():
    """Update today's study goal."""
    today = date.today()
    goal = StudyGoal.query.filter_by(user_id=current_user.id, date=today).first()
    if not goal:
        goal = StudyGoal(user_id=current_user.id, date=today)
        db.session.add(goal)

    goal.target_questions = int(request.form.get('target_questions', 10))
    goal.target_minutes = int(request.form.get('target_minutes', 30))
    db.session.commit()
    flash('Study goal updated!', 'success')
    return redirect(url_for('main.study_plan'))


@main.route('/study-plan/toggle-priority/<int:category_id>', methods=['POST'])
@login_required
@student_required
def toggle_priority(category_id):
    """Toggle a category as priority for focused study."""
    priorities = session.get('priority_categories', [])
    if category_id in priorities:
        priorities.remove(category_id)
    else:
        priorities.append(category_id)
    session['priority_categories'] = priorities
    return redirect(url_for('main.study_plan'))


# ── User Profile ──────────────────────────────────────────────────

@main.route('/profile/<int:user_id>')
@login_required
@student_required
def public_profile(user_id):
    """Public user profile with stats."""
    from app.models import User
    user = User.query.get_or_404(user_id)

    results = (QuizResult.query.filter_by(user_id=user.id)
               .order_by(QuizResult.taken_at.desc()).all())

    total_quizzes = len(results)
    scores = [r.percentage or 0 for r in results]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    best_score = round(max(scores), 1) if scores else 0
    total_questions = sum(r.total_questions or 0 for r in results)

    # Category breakdown
    cat_data = {}
    for r in results:
        cid = r.category_id
        if cid not in cat_data:
            cat = Category.query.get(cid)
            cat_data[cid] = {'name': cat.name if cat else 'Unknown', 'scores': []}
        cat_data[cid]['scores'].append(r.percentage or 0)

    category_stats = []
    for cid, d in cat_data.items():
        avg = round(sum(d['scores']) / len(d['scores']), 1)
        category_stats.append({'name': d['name'], 'avg_score': avg, 'attempts': len(d['scores'])})
    category_stats.sort(key=lambda x: x['avg_score'], reverse=True)

    # Recent quizzes
    recent = []
    for r in results[:10]:
        cat = Category.query.get(r.category_id)
        recent.append({
            'category': cat.name if cat else 'Unknown',
            'score': round(r.percentage or 0, 1),
            'date': r.taken_at.strftime('%b %d') if r.taken_at else '',
        })

    return render_template('profile.html',
                           profile_user=user,
                           total_quizzes=total_quizzes,
                           avg_score=avg_score,
                           best_score=best_score,
                           total_questions=total_questions,
                           category_stats=category_stats,
                           recent=recent)
