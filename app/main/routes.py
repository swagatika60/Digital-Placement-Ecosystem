from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Resource, Category, Question, QuizResult

main = Blueprint('main', __name__)


@main.route('/')
def home():
    """Home page route."""
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard - requires login."""
    # Get user's recent quiz results
    recent_results = QuizResult.query.filter_by(user_id=current_user.id)\
        .order_by(QuizResult.taken_at.desc()).limit(5).all()

    # Get categories count
    categories_count = Category.query.count()

    # Get questions count
    questions_count = Question.query.count()

    # Get total resources count
    resources_count = Resource.query.count()

    # Calculate average score if user has results
    avg_score = 0
    total_attempts = QuizResult.query.filter_by(user_id=current_user.id).count()
    if total_attempts > 0:
        total_percentage = sum(result.percentage for result in QuizResult.query.filter_by(user_id=current_user.id).all() if result.percentage)
        avg_score = round(total_percentage / total_attempts, 2)

    return render_template('dashboard.html',
                           user=current_user,
                           recent_results=recent_results,
                           categories_count=categories_count,
                           questions_count=questions_count,
                           resources_count=resources_count,
                           avg_score=avg_score,
                           total_attempts=total_attempts)


@main.route('/resources')
def resources():
    """View all placement resources."""
    # Group resources by type
    all_resources = Resource.query.order_by(Resource.resource_type, Resource.created_at.desc()).all()

    # Create a dictionary of resources grouped by type
    resources_by_type = {}
    for resource in all_resources:
        res_type = resource.resource_type or 'General'
        if res_type not in resources_by_type:
            resources_by_type[res_type] = []
        resources_by_type[res_type].append(resource)

    return render_template('resources.html', resources_by_type=resources_by_type)
