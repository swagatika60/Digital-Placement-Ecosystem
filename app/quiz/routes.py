"""
Quiz Routes for Placement Preparation Portal
=============================================
This module handles all quiz-related functionality including:
- Viewing categories
- Starting and taking quizzes
- Submitting answers
- Viewing results
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from sqlalchemy import func
from app.decorators import reject_admin
from app.models import Category, Question, QuizResult, StudentActivity, User, QuestionBookmark
from app.extensions import db
from datetime import datetime, timedelta
import random

# Seconds allowed per question in the timed (mock-test) mode
SECONDS_PER_QUESTION = 60

quiz = Blueprint('quiz', __name__)


@quiz.before_request
def _reject_admin_on_student_pages():
    """Full role separation: admins are not allowed on student quiz pages."""
    if current_user.is_authenticated and current_user.role == 'admin':
        return reject_admin()


@quiz.route('/categories')
@quiz.route('/')
@login_required
def list_categories():
    """List all quiz categories."""
    aptitude_categories = Category.query.filter_by(type='aptitude').order_by(Category.name).all()
    technical_categories = Category.query.filter_by(type='technical').order_by(Category.name).all()

    # Get user's best scores for each category
    category_scores = {}
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    for result in results:
        cat_id = result.category_id
        if cat_id not in category_scores or result.percentage > category_scores[cat_id]:
            category_scores[cat_id] = result.percentage

    return render_template('quiz/categories.html',
                           aptitude_categories=aptitude_categories,
                           technical_categories=technical_categories,
                           category_scores=category_scores)


@quiz.route('/category/<int:category_id>')
@login_required
def view_category(category_id):
    """View category details and start quiz."""
    category = Category.query.get_or_404(category_id)
    questions_count = Question.query.filter_by(category_id=category_id).count()

    # Get user's previous attempts for this category
    previous_attempts = QuizResult.query.filter_by(
        user_id=current_user.id,
        category_id=category_id
    ).order_by(QuizResult.taken_at.desc()).all()

    return render_template('quiz/category.html',
                           category=category,
                           questions_count=questions_count,
                           previous_attempts=previous_attempts)


@quiz.route('/start/<int:category_id>', methods=['GET', 'POST'])
@login_required
def start_quiz(category_id):
    """Start a new quiz attempt. Fetch 10 random questions and store in session."""
    category = Category.query.get_or_404(category_id)

    # Get all questions for this category
    all_questions = Question.query.filter_by(category_id=category_id).all()

    if not all_questions:
        flash('No questions available in this category.', 'warning')
        return redirect(url_for('quiz.list_categories'))

    # Select 10 random questions (or all if less than 10)
    num_questions = min(10, len(all_questions))
    selected_questions = random.sample(all_questions, num_questions)

    # Store question IDs, start time, and timer deadline in session
    question_ids = [q.id for q in selected_questions]
    session['quiz_question_ids'] = question_ids
    session['quiz_category_id'] = category_id
    session['quiz_start_time'] = datetime.utcnow().isoformat()
    session['quiz_deadline'] = (datetime.utcnow() + timedelta(seconds=SECONDS_PER_QUESTION * num_questions)).isoformat()
    session['quiz_answers'] = {}  # answers saved per question as the user navigates

    # Log activity
    activity = StudentActivity(
        user_id=current_user.id,
        activity_type='quiz_start',
        description=f'Started quiz for category: {category.name}'
    )
    db.session.add(activity)
    db.session.commit()

    flash(f'Quiz started! You have {num_questions} questions to answer.', 'success')
    return redirect(url_for('quiz.question', question_num=1))


@quiz.route('/question/<int:question_num>')
@login_required
def question(question_num):
    """Display a specific question."""
    # Check if quiz is in progress
    if 'quiz_question_ids' not in session:
        flash('No quiz in progress. Please start a new quiz.', 'warning')
        return redirect(url_for('quiz.list_categories'))

    question_ids = session.get('quiz_question_ids', [])
    category_id = session.get('quiz_category_id')

    if question_num < 1 or question_num > len(question_ids):
        flash('Invalid question number.', 'error')
        return redirect(url_for('quiz.list_categories'))

    # Get the current question
    question_id = question_ids[question_num - 1]
    question = Question.query.get_or_404(question_id)

    # Get category info
    category = Category.query.get(category_id)

    # Calculate progress
    progress = (question_num / len(question_ids)) * 100

    # Time left for the timer (seconds)
    time_left = 0
    deadline = session.get('quiz_deadline')
    if deadline:
        try:
            time_left = max(0, int((datetime.fromisoformat(deadline) - datetime.utcnow()).total_seconds()))
        except ValueError:
            time_left = 0

    is_bookmarked = QuestionBookmark.query.filter_by(
        user_id=current_user.id, question_id=question.id
    ).first() is not None

    # Answer already saved for this question in this attempt (server-side)
    saved_answers = session.get('quiz_answers', {})
    selected_answer = saved_answers.get(str(question.id), '')

    return render_template('quiz/question.html',
                           title=f'Question {question_num}',
                           question=question,
                           question_num=question_num,
                           total_questions=len(question_ids),
                           category=category,
                           progress=progress,
                           time_left=time_left,
                           is_bookmarked=is_bookmarked,
                           selected_answer=selected_answer,
                           question_ids=question_ids,
                           saved_answer_map=saved_answers)


@quiz.route('/answer/<int:question_num>', methods=['POST'])
@login_required
def save_answer(question_num):
    """
    Save the answer for the question on the current page into the session,
    then move to the previous/next question.

    Each question is rendered on its own page, so only the current question's
    radio button exists in the form. Storing answers in the session as the user
    navigates ensures every answer reaches the server at submit time.
    """
    if 'quiz_question_ids' not in session:
        flash('No quiz in progress. Please start a new quiz.', 'warning')
        return redirect(url_for('quiz.list_categories'))

    question_ids = session.get('quiz_question_ids', [])
    total_questions = len(question_ids)
    if total_questions == 0:
        return redirect(url_for('quiz.list_categories'))

    # Clamp question_num to a valid page
    question_num = max(1, min(question_num, total_questions))
    qid = question_ids[question_num - 1]

    answers = session.get('quiz_answers', {})
    submitted = request.form.get(f'question_{qid}')
    if submitted:
        answers[str(qid)] = submitted.upper()
    elif str(qid) in answers:
        # Radio was cleared/unanswered on this page - keep the saved answer.
        pass
    session['quiz_answers'] = answers

    if request.form.get('next'):
        target = min(question_num + 1, total_questions)
    else:
        target = max(question_num - 1, 1)
    return redirect(url_for('quiz.question', question_num=target))


@quiz.route('/submit', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz answers, calculate score, save QuizResult, log StudentActivity."""
    if 'quiz_question_ids' not in session:
        flash('No quiz in progress.', 'warning')
        return redirect(url_for('quiz.list_categories'))

    question_ids = session.get('quiz_question_ids', [])
    category_id = session.get('quiz_category_id')
    start_time_str = session.get('quiz_start_time')

    # Calculate score: merge the final form's answers with the answers that were
    # saved to the session while navigating between question pages.
    saved_answers = session.get('quiz_answers', {})
    score = 0
    total_questions = len(question_ids)

    for qid in question_ids:
        question = Question.query.get(qid)
        answer = request.form.get(f'question_{qid}') or saved_answers.get(str(qid))
        if answer and question and answer.upper() == question.correct_answer:
            score += 1

    # Calculate percentage
    percentage = (score / total_questions * 100) if total_questions > 0 else 0

    # Create QuizResult
    quiz_result = QuizResult(
        user_id=current_user.id,
        category_id=category_id,
        score=score,
        total_questions=total_questions,
        percentage=round(percentage, 2)
    )
    db.session.add(quiz_result)
    db.session.flush()  # Get the ID without committing

    # Log activity
    category = Category.query.get(category_id)
    activity = StudentActivity(
        user_id=current_user.id,
        activity_type='quiz_complete',
        description=f'Completed quiz for {category.name if category else "Unknown"}: Score {score}/{total_questions} ({percentage:.1f}%)'
    )
    db.session.add(activity)
    db.session.commit()

    # Clear quiz session data
    session.pop('quiz_question_ids', None)
    session.pop('quiz_category_id', None)
    session.pop('quiz_start_time', None)
    session.pop('quiz_deadline', None)
    session.pop('quiz_answers', None)

    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('quiz.results', result_id=quiz_result.id))


@quiz.route('/take/<int:category_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(category_id):
    """Take the quiz - display questions and handle submission."""
    category = Category.query.get_or_404(category_id)
    questions = Question.query.filter_by(category_id=category_id).all()

    if not questions:
        flash('No questions available in this category.', 'warning')
        return redirect(url_for('quiz.list_categories'))

    if request.method == 'POST':
        # Calculate score
        score = 0
        total_questions = len(questions)

        for question in questions:
            answer = request.form.get(f'question_{question.id}')
            if answer and answer.upper() == question.correct_answer:
                score += 1

        # Calculate percentage
        percentage = (score / total_questions * 100) if total_questions > 0 else 0

        # Save result
        result = QuizResult(
            user_id=current_user.id,
            category_id=category_id,
            score=score,
            total_questions=total_questions,
            percentage=percentage
        )
        db.session.add(result)
        db.session.commit()

        # Clear any in-progress timed-test / question-by-question session data
        session.pop('quiz_deadline', None)
        session.pop('quiz_question_ids', None)
        session.pop('quiz_category_id', None)
        session.pop('quiz_start_time', None)
        session.pop('quiz_answers', None)
        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('quiz.results', result_id=result.id))

    # Timed mock-test countdown. Reuse an in-progress deadline so that
    # refreshing the page does NOT grant the user extra time; otherwise
    # start a fresh countdown.
    deadline = session.get('quiz_deadline')
    time_left = 0
    if deadline:
        try:
            time_left = int((datetime.fromisoformat(deadline) - datetime.utcnow()).total_seconds())
        except (TypeError, ValueError):
            time_left = 0

    if time_left <= 0:
        session['quiz_deadline'] = (
            datetime.utcnow() + timedelta(seconds=SECONDS_PER_QUESTION * len(questions))
        ).isoformat()
        time_left = SECONDS_PER_QUESTION * len(questions)

    # Don't let a leftover question-by-question attempt bleed into the mock test
    session.pop('quiz_question_ids', None)
    session.pop('quiz_category_id', None)
    session.pop('quiz_start_time', None)
    session.pop('quiz_answers', None)

    return render_template('quiz/take.html', category=category, questions=questions, time_left=time_left)


@quiz.route('/result/<int:result_id>')
@quiz.route('/results/<int:result_id>')
@login_required
def results(result_id):
    """View quiz results."""
    result = QuizResult.query.get_or_404(result_id)

    # Verify result belongs to current user
    if result.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('quiz.list_categories'))

    category = Category.query.get(result.category_id)
    questions = Question.query.filter_by(category_id=result.category_id).all()
    bookmarked_ids = {b.question_id for b in QuestionBookmark.query.filter_by(
        user_id=current_user.id).all()}

    return render_template('quiz/results.html',
                           result=result,
                           category=category,
                           questions=questions,
                           bookmarked_ids=bookmarked_ids)


@quiz.route('/full/<int:category_id>', methods=['GET', 'POST'])
@login_required
def full_quiz(category_id):
    """
    Full-length single-page quiz: every question in the category on one page,
    with a question-number palette, countdown timer, and per-answer review.
    """
    category = Category.query.get_or_404(category_id)
    questions = Question.query.filter_by(category_id=category_id).all()

    if not questions:
        flash('No questions available in this category.', 'warning')
        return redirect(url_for('quiz.list_categories'))

    if request.method == 'POST':
        score = 0
        total = len(questions)
        user_answers = {}

        for question in questions:
            answer = request.form.get(f'question_{question.id}')
            if answer:
                user_answers[str(question.id)] = answer.upper()
                if answer.upper() == question.correct_answer:
                    score += 1

        percentage = round(score / total * 100, 2) if total else 0

        result = QuizResult(
            user_id=current_user.id,
            category_id=category_id,
            score=score,
            total_questions=total,
            percentage=percentage,
        )
        db.session.add(result)
        db.session.commit()

        # Time taken (from the attempt start stored on first page load)
        time_taken = None
        start_str = session.get('quiz_full_start')
        if start_str:
            try:
                seconds = int((datetime.utcnow() - datetime.fromisoformat(start_str)).total_seconds())
                time_taken = f'{seconds // 60}:{seconds % 60:02d}'
            except (TypeError, ValueError):
                time_taken = None

        # Keep answers + meta in the session so the review page can render them
        review_meta = session.get('quiz_review_meta', {})
        review_meta[str(result.id)] = {'answers': user_answers, 'time_taken': time_taken}
        session['quiz_review_meta'] = review_meta
        session.pop('quiz_full_deadline', None)
        session.pop('quiz_full_start', None)

        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('quiz.full_result', result_id=result.id))

    # GET: reuse an in-progress deadline so a refresh doesn't grant extra time
    deadline = session.get('quiz_full_deadline')
    time_left = 0
    if deadline:
        try:
            time_left = int((datetime.fromisoformat(deadline) - datetime.utcnow()).total_seconds())
        except (TypeError, ValueError):
            time_left = 0

    if time_left <= 0:
        session['quiz_full_deadline'] = (
            datetime.utcnow() + timedelta(seconds=SECONDS_PER_QUESTION * len(questions))
        ).isoformat()
        time_left = SECONDS_PER_QUESTION * len(questions)

    if 'quiz_full_start' not in session:
        session['quiz_full_start'] = datetime.utcnow().isoformat()

    return render_template('quiz/quiz.html',
                           category=category,
                           questions=questions,
                           total_questions=len(questions),
                           time_left=time_left)


@quiz.route('/review/<int:result_id>')
@login_required
def full_result(result_id):
    """Review page for a full-length quiz: score summary + per-question answers."""
    result = QuizResult.query.get_or_404(result_id)

    # Verify result belongs to current user
    if result.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('quiz.list_categories'))

    category = Category.query.get(result.category_id)
    questions = Question.query.filter_by(category_id=result.category_id).all()

    meta = session.get('quiz_review_meta', {}).get(str(result.id), {})
    user_answers = meta.get('answers', {})
    time_taken = meta.get('time_taken')

    review_data = []
    correct = 0
    for question in questions:
        ua = user_answers.get(str(question.id), '')
        is_correct = bool(ua) and ua == question.correct_answer
        if is_correct:
            correct += 1
        review_data.append({
            'question': question,
            'user_answer': ua,
            'is_correct': is_correct,
        })

    wrong = sum(1 for r in review_data if r['user_answer'] and not r['is_correct'])
    unanswered = sum(1 for r in review_data if not r['user_answer'])

    # Consume the review data once viewed (refreshes fall back gracefully)
    review_meta = session.get('quiz_review_meta', {})
    review_meta.pop(str(result.id), None)
    session['quiz_review_meta'] = review_meta

    return render_template('quiz/result.html',
                           category=category,
                           result=result,
                           percentage=result.percentage or 0,
                           score=result.score,
                           total_questions=result.total_questions,
                           correct_answers=correct,
                           wrong_answers=wrong,
                           unanswered=unanswered,
                           time_taken=time_taken or '—',
                           date=result.taken_at.strftime('%Y-%m-%d %H:%M') if result.taken_at else '',
                           review_data=review_data)


@quiz.route('/history')
@login_required
def history():
    """View user's quiz attempt history."""
    results = QuizResult.query.filter_by(user_id=current_user.id)\
        .order_by(QuizResult.taken_at.desc()).all()

    # Get category details for each result
    results_with_categories = []
    for result in results:
        category = Category.query.get(result.category_id)
        results_with_categories.append({
            'result': result,
            'category': category
        })

    return render_template('quiz/history.html', results_with_categories=results_with_categories)


@quiz.route('/leaderboard')
@login_required
def leaderboard():
    """Top students ranked by best quiz percentage."""
    rows = (db.session.query(
                User.id, User.name, User.college,
                func.max(QuizResult.percentage).label('best'),
                func.count(QuizResult.id).label('attempts'),
                func.max(QuizResult.taken_at).label('last_taken')
            )
            .join(QuizResult, QuizResult.user_id == User.id)
            .group_by(User.id)
            .order_by(func.max(QuizResult.percentage).desc(),
                      func.count(QuizResult.id).desc())
            .limit(20).all())

    # Current user's rank by best percentage
    user_rank = None
    user_best = db.session.query(func.max(QuizResult.percentage)).filter_by(user_id=current_user.id).scalar()
    if user_best is not None:
        better = db.session.query(func.count(func.distinct(QuizResult.user_id)))\
            .filter(QuizResult.percentage > user_best).scalar()
        user_rank = better + 1

    return render_template('quiz/leaderboard.html', rows=rows, user_rank=user_rank, user_best=user_best)


@quiz.route('/bookmark/<int:question_id>', methods=['POST'])
@login_required
def toggle_bookmark(question_id):
    """Add or remove a question bookmark for the current user."""
    Question.query.get_or_404(question_id)
    existing = QuestionBookmark.query.filter_by(
        user_id=current_user.id, question_id=question_id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash('Question removed from bookmarks.', 'info')
    else:
        db.session.add(QuestionBookmark(user_id=current_user.id, question_id=question_id))
        db.session.commit()
        flash('Question saved to bookmarks!', 'success')
    return redirect(request.referrer or url_for('quiz.bookmarks'))


@quiz.route('/bookmarks')
@login_required
def bookmarks():
    """List questions the current user saved for review."""
    saved = QuestionBookmark.query.filter_by(user_id=current_user.id)\
        .order_by(QuestionBookmark.created_at.desc()).all()
    return render_template('quiz/bookmarks.html', saved=saved)
