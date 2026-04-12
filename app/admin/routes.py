from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Category, Question, Resource, QuizResult
from app import db
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

# ============ Dashboard ============
@admin.route('/dashboard')
@admin.route('/')
@login_required
# @admin_required
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

# ============ Cheat Code ============
@admin.route('/make-me-admin')
@login_required
def make_me_admin():
    current_user.role = 'admin'
    db.session.commit()
    flash('Success! You are now an Admin.', 'success')
    return redirect(url_for('main.home'))

# ============ User Management ============
@admin.route('/users')
@login_required
# @admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
# @admin_required
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
# @admin_required
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
# @admin_required
def list_categories():
    categories = Category.query.order_by(Category.type, Category.name).all()
    return render_template('admin/categories.html', categories=categories)

# ============ Question Management ============
@admin.route('/questions')
@login_required
# @admin_required
def list_questions():
    category_id = request.args.get('category_id', type=int)
    if category_id:
        questions = Question.query.filter_by(category_id=category_id).all()
    else:
        questions = Question.query.order_by(Question.created_at.desc()).all()

    categories = Category.query.order_by(Category.type, Category.name).all()
    return render_template('admin/questions.html', questions=questions, categories=categories)

@admin.route('/questions/add', methods=['GET', 'POST'])
@admin.route('/questions/create', methods=['GET', 'POST'])
@login_required
# @admin_required
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
# @admin_required
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
# @admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.list_questions'))

# ============ Resource Management ============
@admin.route('/resources')
@login_required
# @admin_required
def list_resources():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    return render_template('admin/resources.html', resources=resources)

@admin.route('/resources/add', methods=['GET', 'POST'])
@admin.route('/resources/create', methods=['GET', 'POST'])
@login_required
# @admin_required
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
# @admin_required
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
# @admin_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted successfully!', 'success')
    return redirect(url_for('admin.list_resources'))
