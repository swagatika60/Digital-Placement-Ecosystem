# from flask import Blueprint, render_template
# from flask_login import login_required, current_user
# from app.models import Resource, Category, Question, QuizResult

# main = Blueprint('main', __name__)


# @main.route('/')
# def home():
#     """Home page route."""
#     return render_template('index.html')


# @main.route('/dashboard')
# @login_required
# def dashboard():
#     """Student dashboard - requires login."""
#     # Get user's recent quiz results
#     recent_results = QuizResult.query.filter_by(user_id=current_user.id)\
#         .order_by(QuizResult.taken_at.desc()).limit(5).all()

#     # Get categories count
#     categories_count = Category.query.count()

#     # Get questions count
#     questions_count = Question.query.count()

#     # Get total resources count
#     resources_count = Resource.query.count()

#     # Calculate average score if user has results
#     avg_score = 0
#     total_attempts = QuizResult.query.filter_by(user_id=current_user.id).count()
#     if total_attempts > 0:
#         total_percentage = sum(result.percentage for result in QuizResult.query.filter_by(user_id=current_user.id).all() if result.percentage)
#         avg_score = round(total_percentage / total_attempts, 2)

#     return render_template('dashboard.html',
#                            user=current_user,
#                            recent_results=recent_results,
#                            categories_count=categories_count,
#                            questions_count=questions_count,
#                            resources_count=resources_count,
#                            avg_score=avg_score,
#                            total_attempts=total_attempts)


# @main.route('/resources')
# def resources():
#     """View all placement resources."""
#     # Group resources by type
#     all_resources = Resource.query.order_by(Resource.resource_type, Resource.created_at.desc()).all()

#     # Create a dictionary of resources grouped by type
#     resources_by_type = {}
#     for resource in all_resources:
#         res_type = resource.resource_type or 'General'
#         if res_type not in resources_by_type:
#             resources_by_type[res_type] = []
#         resources_by_type[res_type].append(resource)

#     return render_template('resources.html', resources_by_type=resources_by_type)





import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, current_app
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


# ========================================================
# ENGINE 1: TEXT ARTICLES ("Read More")
# ========================================================
@main.route('/resource/topic/<topic_id>')
def view_topic(topic_id):
    """Backend handler that opens the specific reading pages."""
    
    # Database of text content for your frontend cards
    content_db = {
        # --- INTERVIEW TIPS ---
        'technical-prep': {
            'title': 'Technical Interview Preparation',
            'description': 'Essential tips for cracking technical interviews including coding rounds and system design.',
            'content': '1. Master the Fundamentals:\n• Data Structures: Arrays, Linked Lists, Trees, Graphs.\n• Algorithms: Sorting, Searching, DP.\n\n2. Think Out Loud:\n• Always explain your thought process to the interviewer before writing code.\n\n3. Write Clean Code:\n• Practice writing on a whiteboard. Use meaningful variable names.'
        },
        'dress-code': {
            'title': 'Dress Code & Body Language',
            'description': 'Learn about professional attire and positive body language for interviews.',
            'content': 'DRESS CODE:\n• Dress one step above the daily office attire. Ironed shirts, dark trousers, formal shoes.\n• Ensure grooming is neat.\n\nBODY LANGUAGE:\n• Handshake: Firm and confident.\n• Posture: Sit up straight. Lean slightly forward.\n• Eye Contact: Maintain natural eye contact with the interviewer.'
        },
        'communication-skills': {
            'title': 'Communication Skills',
            'description': 'Improve your communication skills to express your thoughts clearly.',
            'content': '1. The STAR Method:\nUse this for behavioral questions:\n• Situation: Provide context.\n• Task: What was your responsibility?\n• Action: What steps did YOU take?\n• Result: What was the outcome?\n\n2. Clarity over Speed:\nSpeak clearly and at a moderate pace. It is okay to take a pause to gather your thoughts.'
        },
        'interview-mistakes': {
            'title': 'Common Interview Mistakes',
            'description': 'Avoid these common mistakes that candidates make during interviews.',
            'content': '1. Lying on your Resume: Never list a skill you cannot defend.\n2. Badmouthing Past Employers: Always frame past challenges positively.\n3. Lack of Research: Know the company\'s core products.\n4. "I don\'t have any questions": Always prepare 2-3 questions to ask at the end.'
        },

        # --- HR QUESTIONS ---
        'tell-me-about-yourself': {
            'title': 'Tell Me About Yourself',
            'description': 'How to craft a perfect introduction.',
            'content': 'Use the Present-Past-Future formula:\n\nPRESENT: "I am a final year CS student with a strong foundation in Web Development."\nPAST: "Previously, I built an API that improved load times by 20%."\nFUTURE: "I am looking for a role where I can contribute these skills, which is why I am excited about this company."'
        },
        'strengths-weaknesses': {
            'title': 'Strengths & Weaknesses',
            'description': 'Answer the tricky question professionally.',
            'content': 'STRENGTHS: Pick 2 relevant skills and give an example. "My greatest strength is adaptability. I learned React from scratch in two weeks for a project."\n\nWEAKNESSES: Be honest but show growth. "I used to struggle with delegating tasks, but taking a leadership role in a college club taught me to trust my team."'
        },
        'why-hire-you': {
            'title': 'Why Should We Hire You?',
            'description': 'Craft a compelling answer that sets you apart.',
            'content': '"You should hire me because my skills in Python align perfectly with the job description. Beyond my technical abilities, my recent project experience taught me how to work effectively under tight deadlines. I am highly motivated and ready to add value to your team from day one."'
        },
        'where-do-you-see-yourself': {
            'title': 'Where Do You See Yourself in 5 Years?',
            'description': 'Answer career goal questions with ambition.',
            'content': '"In five years, I see myself as an experienced software engineer who has mastered the core technologies we use here. I hope to have taken on leadership responsibilities, perhaps mentoring junior developers, and contributing to the architectural decisions."'
        },
        'why-this-company': {
            'title': 'Why This Company?',
            'description': 'Research-based strategies to answer why you want to join.',
            'content': '"I want to work here because I deeply admire your recent shift towards cloud-based solutions. I read your engineering blog, and it aligns perfectly with my interest in distributed systems. Furthermore, I appreciate the company\'s culture of continuous learning."'
        },
        'salary-expectations': {
            'title': 'Salary Expectations',
            'description': 'Negotiate salary professionally.',
            'content': '"As a fresher, my primary focus is to start my career in a dynamic environment where I can learn and grow. However, based on my research for similar roles in this city, I would expect a salary in the range of [X to Y]. I am open to discussing this based on the full package."'
        },

        # --- RESUME BUILDING ---
        'resume-templates': {
            'title': 'Resume Templates',
            'description': 'Professional resume templates designed for freshers.',
            'content': 'The best resumes are simple, clean, and ONE PAGE long.\n\nAvoid adding progress bars for skills. Keep the text black and white, ensure plenty of whitespace, and make sure your GitHub and LinkedIn links are clickable!'
        },
        'resume-checklist': {
            'title': 'Resume Checklist',
            'description': 'Essential elements every placement resume should include.',
            'content': '✓ Contact Info (Phone, Email, LinkedIn, GitHub).\n✓ Education (Reverse chronological).\n✓ Technical Skills (Grouped by Languages, Frameworks).\n✓ Projects (Include specific technologies used and measurable outcomes).\n✓ Experience (Internships or freelance work).'
        },
        'ats-format': {
            'title': 'ATS-Friendly Format',
            'description': 'How to format your resume to pass Applicant Tracking Systems.',
            'content': 'ATS are bots that read your resume before a human does.\n\nTo pass ATS:\n1. Avoid complex formatting (No columns, tables, or weird graphics).\n2. Save and submit your resume as a standard PDF.\n3. Use exact keywords found in the job description.\n4. Use standard section headers (Experience, Education, Projects).'
        }
    }

    # Fetch the requested topic from the backend dictionary
    resource_data = content_db.get(topic_id)
    
    # If the content isn't typed out yet, gracefully alert the user
    if not resource_data:
        flash('Content for this topic is being updated. Check back soon!', 'info')
        return redirect(url_for('main.resources'))

    return render_template('view_resource.html', resource=resource_data)


# ========================================================
# ENGINE 2: SECURE FILE DOWNLOADS ("Download PDF")
# ========================================================
# @main.route('/download/<filename>')
# def download_pdf(filename):
#     """Safely sends a PDF file from the server to the user's computer."""
#     # This points Flask to your 'app/static/pdfs' folder
#     pdf_directory = os.path.join(current_app.root_path, 'static', 'pdfs')
    
#     try:
#         # as_attachment=True forces the browser to download the file
#         return send_from_directory(pdf_directory, filename, as_attachment=True)
#     except FileNotFoundError:
#         flash('Sorry, this PDF file is currently unavailable.', 'danger')
#         return redirect(url_for('main.resources'))

@main.route('/download/<filename>')
@login_required
def download_pdf(filename):
    import os
    from flask import send_from_directory, current_app, flash, redirect, url_for
    
    # Path to the static/pdfs folder
    pdf_directory = os.path.join(current_app.root_path, 'static', 'pdfs')
    
    # Check if the file actually exists in the folder
    file_path = os.path.join(pdf_directory, filename)
    
    if os.path.exists(file_path):
        return send_from_directory(pdf_directory, filename, as_attachment=True)
    else:
        # If the file isn't there (like sql_notes.pdf), show this message
        flash(f"The PDF for '{filename.replace('_', ' ').replace('.pdf', '').upper()}' is coming soon!", "info")
        return redirect(url_for('main.resources'))