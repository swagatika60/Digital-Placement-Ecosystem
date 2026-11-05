import csv
import io
import json
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Category, Question, Resource, QuizResult, StudentActivity
from app.extensions import db, csrf
from sqlalchemy import func
from app.decorators import admin_required

admin = Blueprint('admin', __name__)


# ============ Admin Login ============
@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Dedicated admin-only login page."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        flash('Your account does not have admin access.', 'warning')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.role == 'admin':
            login_user(user, remember=bool(request.form.get('remember')))
            flash('Welcome to the Admin Panel!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials or your account does not have admin access.', 'danger')

    return render_template('admin/login.html')


# ============ Dashboard ============
@admin.route('/dashboard')
@admin.route('/')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    categories_count = Category.query.count()
    questions_count = Question.query.count()
    resources_count = Resource.query.count()
    quiz_results_count = QuizResult.query.count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_results = QuizResult.query.order_by(QuizResult.taken_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           users_count=users_count, categories_count=categories_count,
                           questions_count=questions_count, resources_count=resources_count,
                           quiz_results_count=quiz_results_count, recent_users=recent_users,
                           recent_results=recent_results)

# ============ User Management ============
@admin.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot modify your own role.', 'warning')
        return redirect(url_for('admin.list_users'))
    user.role = 'admin' if user.role == 'student' else 'student'
    db.session.commit()
    flash(f'Role updated to {user.role} for {user.name}.', 'success')
    return redirect(url_for('admin.list_users'))

# 🔥 RESTORED DELETE USER ROUTE 🔥
@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete your own account.', 'warning')
        return redirect(url_for('admin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} has been deleted.', 'success')
    return redirect(url_for('admin.list_users'))

# ============ Category Management ============
@admin.route('/categories')
@login_required
@admin_required
def list_categories():
    categories = Category.query.order_by(Category.type, Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/add', methods=['GET', 'POST'])
@admin.route('/categories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_category():
    if request.method == 'POST':
        category = Category(
            name=request.form.get('name'),
            type=request.form.get('type'),
            description=request.form.get('description')
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin.list_categories'))

    return render_template('admin/category_form.html', category=None)

@admin.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.type = request.form.get('type')
        category.description = request.form.get('description')
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin.list_categories'))

    return render_template('admin/category_form.html', category=category)

@admin.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Delete questions in this category first (matches the template's warning)
    Question.query.filter_by(category_id=category.id).delete()
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" deleted successfully!', 'success')
    return redirect(url_for('admin.list_categories'))

# ============ Question Management ============
@admin.route('/questions')
@login_required
@admin_required
def list_questions():
    category_id = request.args.get('category_id', type=int)
    difficulty = request.args.get('difficulty', type=str)

    query = Question.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    questions = query.order_by(Question.created_at.desc()).all()

    categories = Category.query.order_by(Category.type, Category.name).all()

    # Analytics for question bank
    total_questions = Question.query.count()
    questions_by_category = db.session.query(
        Category.name, func.count(Question.id)
    ).join(Question).group_by(Category.name).all()
    questions_by_difficulty = db.session.query(
        Question.difficulty, func.count(Question.id)
    ).group_by(Question.difficulty).all()

    return render_template('admin/questions.html',
                           questions=questions, categories=categories,
                           total_questions=total_questions,
                           questions_by_category=questions_by_category,
                           questions_by_difficulty=dict(questions_by_difficulty),
                           selected_category=category_id,
                           selected_difficulty=difficulty)

@admin.route('/questions/add', methods=['GET', 'POST'])
@admin.route('/questions/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_question():
    categories = Category.query.order_by(Category.type, Category.name).all()

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        question = Question(
            category_id=category_id,
            question_text=request.form.get('question_text'),
            option_a=request.form.get('option_a'),
            option_b=request.form.get('option_b'),
            option_c=request.form.get('option_c'),
            option_d=request.form.get('option_d'),
            correct_answer=request.form.get('correct_answer'),
            explanation=request.form.get('explanation'),
            difficulty=request.form.get('difficulty')
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.list_questions'))

    return render_template('admin/add_question.html', question=None, categories=categories)

@admin.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    categories = Category.query.order_by(Category.type, Category.name).all()

    if request.method == 'POST':
        question.category_id = request.form.get('category_id')
        question.question_text = request.form.get('question_text')
        question.option_a = request.form.get('option_a')
        question.option_b = request.form.get('option_b')
        question.option_c = request.form.get('option_c')
        question.option_d = request.form.get('option_d')
        question.correct_answer = request.form.get('correct_answer')
        question.explanation = request.form.get('explanation')
        question.difficulty = request.form.get('difficulty')

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.list_questions'))

    return render_template('admin/add_question.html', question=question, categories=categories)

@admin.route('/questions/delete/<int:question_id>', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.list_questions'))

# ============ Resource Management ============
@admin.route('/resources')
@login_required
@admin_required
def list_resources():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    return render_template('admin/resources.html', resources=resources)

@admin.route('/resources/add', methods=['GET', 'POST'])
@admin.route('/resources/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_resource():
    if request.method == 'POST':
        resource = Resource(
            title=request.form.get('title'),
            description=request.form.get('description'),
            resource_type=request.form.get('resource_type'),
            content=request.form.get('content'),
            link=request.form.get('link'),
            created_by=current_user.id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource created successfully!', 'success')
        return redirect(url_for('admin.list_resources'))

    return render_template('admin/resource_form.html', resource=None)

# 🔥 RESTORED EDIT RESOURCE ROUTE 🔥
@admin.route('/resources/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if request.method == 'POST':
        resource.title = request.form.get('title')
        resource.description = request.form.get('description')
        resource.resource_type = request.form.get('resource_type')
        resource.content = request.form.get('content')
        resource.link = request.form.get('link')
        db.session.commit()
        flash('Resource updated successfully!', 'success')
        return redirect(url_for('admin.list_resources'))
    return render_template('admin/resource_form.html', resource=resource)

# 🔥 RESTORED DELETE RESOURCE ROUTE 🔥
@admin.route('/resources/delete/<int:resource_id>', methods=['POST'])
@admin.route('/resources/<int:resource_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted successfully!', 'success')
    return redirect(url_for('admin.list_resources'))

# ============ Bulk Question Import ============
@admin.route('/questions/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_questions():
    categories = Category.query.order_by(Category.type, Category.name).all()

    if request.method == 'POST':
        file = request.files.get('file')
        category_id = request.form.get('category_id')
        default_difficulty = request.form.get('difficulty', 'medium')

        if not file or not file.filename:
            flash('Please upload a file.', 'danger')
            return redirect(url_for('admin.import_questions'))

        filename = file.filename.lower()
        content = file.read().decode('utf-8-sig')  # handle BOM
        imported = 0
        errors = []

        try:
            if filename.endswith('.csv'):
                reader = csv.DictReader(io.StringIO(content))
                for i, row in enumerate(reader, 1):
                    try:
                        q = Question(
                            category_id=category_id,
                            question_text=row.get('question_text', '').strip(),
                            option_a=row.get('option_a', '').strip(),
                            option_b=row.get('option_b', '').strip(),
                            option_c=row.get('option_c', '').strip(),
                            option_d=row.get('option_d', '').strip(),
                            correct_answer=row.get('correct_answer', '').strip().upper(),
                            explanation=row.get('explanation', '').strip(),
                            difficulty=row.get('difficulty', default_difficulty).strip()
                        )
                        if q.question_text and q.option_a and q.option_b and q.correct_answer:
                            db.session.add(q)
                            imported += 1
                        else:
                            errors.append(f'Row {i}: missing required fields')
                    except Exception as e:
                        errors.append(f'Row {i}: {str(e)}')

            elif filename.endswith('.json'):
                data = json.loads(content)
                items = data if isinstance(data, list) else data.get('questions', [])
                for i, row in enumerate(items, 1):
                    try:
                        q = Question(
                            category_id=category_id,
                            question_text=row.get('question_text', '').strip(),
                            option_a=row.get('option_a', '').strip(),
                            option_b=row.get('option_b', '').strip(),
                            option_c=row.get('option_c', '').strip(),
                            option_d=row.get('option_d', '').strip(),
                            correct_answer=row.get('correct_answer', '').strip().upper(),
                            explanation=row.get('explanation', '').strip(),
                            difficulty=row.get('difficulty', default_difficulty).strip()
                        )
                        if q.question_text and q.option_a and q.option_b and q.correct_answer:
                            db.session.add(q)
                            imported += 1
                        else:
                            errors.append(f'Item {i}: missing required fields')
                    except Exception as e:
                        errors.append(f'Item {i}: {str(e)}')

            elif filename.endswith('.txt'):
                # Simple format: questions separated by blank lines
                blocks = content.strip().split('\n\n')
                for i, block in enumerate(blocks, 1):
                    lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                    if len(lines) >= 6:
                        q = Question(
                            category_id=category_id,
                            question_text=lines[0],
                            option_a=lines[1].lstrip('Aa.) '),
                            option_b=lines[2].lstrip('Bb.) '),
                            option_c=lines[3].lstrip('Cc.) '),
                            option_d=lines[4].lstrip('Dd.) '),
                            correct_answer=lines[5].strip().upper()[:1],
                            difficulty=default_difficulty
                        )
                        if len(lines) > 6:
                            q.explanation = lines[6]
                        db.session.add(q)
                        imported += 1
                    else:
                        errors.append(f'Block {i}: not enough lines (need at least 6)')
            else:
                flash('Unsupported file format. Please upload CSV, JSON, or TXT.', 'danger')
                return redirect(url_for('admin.import_questions'))

            if imported > 0:
                db.session.commit()

            if errors:
                flash(f'Imported {imported} questions. {len(errors)} errors: {errors[:3]}', 'warning')
            else:
                flash(f'Successfully imported {imported} questions!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Import failed: {str(e)}', 'danger')

        return redirect(url_for('admin.list_questions'))

    return render_template('admin/import_questions.html', categories=categories)

# ============ Export Questions ============
@admin.route('/questions/export')
@login_required
@admin_required
def export_questions():
    category_id = request.args.get('category_id', type=int)
    fmt = request.args.get('format', 'csv')

    query = Question.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    questions = query.order_by(Question.created_at.desc()).all()

    if fmt == 'json':
        data = [{
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'correct_answer': q.correct_answer,
            'explanation': q.explanation or '',
            'difficulty': q.difficulty or 'medium',
            'category': q.category.name if q.category else ''
        } for q in questions]

        output = io.BytesIO()
        output.write(json.dumps(data, indent=2).encode('utf-8'))
        output.seek(0)
        return send_file(output, mimetype='application/json',
                         as_attachment=True, download_name='questions_export.json')

    # Default: CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
        'correct_answer', 'explanation', 'difficulty', 'category'
    ])
    writer.writeheader()
    for q in questions:
        writer.writerow({
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'correct_answer': q.correct_answer,
            'explanation': q.explanation or '',
            'difficulty': q.difficulty or 'medium',
            'category': q.category.name if q.category else ''
        })

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv', as_attachment=True,
        download_name='questions_export.csv'
    )

# ============ Bulk Delete Questions ============
@admin.route('/questions/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete_questions():
    question_ids = request.form.getlist('question_ids')
    if question_ids:
        Question.query.filter(Question.id.in_(question_ids)).delete(synchronize_session=False)
        db.session.commit()
        flash(f'Deleted {len(question_ids)} questions.', 'success')
    else:
        flash('No questions selected.', 'warning')
    return redirect(url_for('admin.list_questions'))

# ============ Clone Category ============
@admin.route('/categories/clone/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def clone_category(category_id):
    source = Category.query.get_or_404(category_id)
    new_cat = Category(
        name=f'{source.name} (Copy)',
        type=source.type,
        description=source.description
    )
    db.session.add(new_cat)
    db.session.flush()

    for q in source.questions:
        new_q = Question(
            category_id=new_cat.id,
            question_text=q.question_text,
            option_a=q.option_a, option_b=q.option_b,
            option_c=q.option_c, option_d=q.option_d,
            correct_answer=q.correct_answer,
            explanation=q.explanation, difficulty=q.difficulty
        )
        db.session.add(new_q)

    db.session.commit()
    flash(f'Cloned "{source.name}" with {len(source.questions)} questions.', 'success')
    return redirect(url_for('admin.list_categories'))

# ============ Admin Analytics ============
@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    # Overall stats
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_admins = User.query.filter_by(role='admin').count()
    total_questions = Question.query.count()
    total_categories = Category.query.count()
    total_quizzes = QuizResult.query.count()

    # Average score
    avg_score = db.session.query(func.avg(QuizResult.percentage)).scalar() or 0

    # Questions by category
    questions_by_cat = db.session.query(
        Category.name, func.count(Question.id)
    ).outerjoin(Question).group_by(Category.name).all()

    # Questions by difficulty
    questions_by_diff = db.session.query(
        Question.difficulty, func.count(Question.id)
    ).group_by(Question.difficulty).all()

    # Top performers
    top_performers = db.session.query(
        User.name, func.max(QuizResult.percentage).label('best'),
        func.count(QuizResult.id).label('attempts')
    ).join(QuizResult).group_by(User.name).order_by(
        func.max(QuizResult.percentage).desc()
    ).limit(10).all()

    # Recent activity
    recent_results = QuizResult.query.order_by(
        QuizResult.taken_at.desc()
    ).limit(10).all()

    return render_template('admin/analytics.html',
        total_users=total_users, total_students=total_students,
        total_admins=total_admins, total_questions=total_questions,
        total_categories=total_categories, total_quizzes=total_quizzes,
        avg_score=round(avg_score, 1),
        questions_by_cat=questions_by_cat,
        questions_by_diff=dict(questions_by_diff),
        top_performers=top_performers,
        recent_results=recent_results
    )

# ============ Quick Add Question (AJAX) ============
@admin.route('/questions/quick-add', methods=['POST'])
@login_required
@admin_required
def quick_add_question():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        q = Question(
            category_id=data.get('category_id'),
            question_text=data.get('question_text', '').strip(),
            option_a=data.get('option_a', '').strip(),
            option_b=data.get('option_b', '').strip(),
            option_c=data.get('option_c', '').strip(),
            option_d=data.get('option_d', '').strip(),
            correct_answer=data.get('correct_answer', '').strip().upper(),
            explanation=data.get('explanation', '').strip(),
            difficulty=data.get('difficulty', 'medium')
        )
        db.session.add(q)
        db.session.commit()
        return jsonify({'success': True, 'id': q.id, 'message': 'Question added!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
