import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app.models import Resource, Category, Question, QuizResult

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Fetch user analytics
    recent_results = QuizResult.query.filter_by(user_id=current_user.id)\
        .order_by(QuizResult.taken_at.desc()).limit(5).all()

    avg_score = 0
    total_attempts = QuizResult.query.filter_by(user_id=current_user.id).count()
    if total_attempts > 0:
        total_percentage = sum(result.percentage for result in QuizResult.query.filter_by(user_id=current_user.id).all() if result.percentage)
        avg_score = round(total_percentage / total_attempts, 2)

    return render_template('dashboard.html',
                           user=current_user,
                           recent_results=recent_results,
                           categories_count=Category.query.count(),
                           questions_count=Question.query.count(),
                           resources_count=Resource.query.count(),
                           avg_score=avg_score,
                           total_attempts=total_attempts)

@main.route('/resources')
def resources():
    all_resources = Resource.query.order_by(Resource.resource_type, Resource.created_at.desc()).all()
    resources_by_type = {}
    for resource in all_resources:
        res_type = resource.resource_type or 'General'
        resources_by_type.setdefault(res_type, []).append(resource)
    return render_template('resources.html', resources_by_type=resources_by_type)

@main.route('/resource/topic/<topic_id>')
def view_topic(topic_id):
    """
    Expert-curated content database for placement success.
    Includes Technical Prep, Behavioral Strategies, and Resume Mastery.
    """
    content_db = {
        # --- ADVANCED TECHNICAL PREPARATION ---
        'technical-prep': {
            'title': 'The Technical Interview Blueprint',
            'description': 'A holistic approach to DSA, System Design, and Problem Solving.',
            'content': (
                "1. THE DSA TRIAD:\n"
                "• Master 'Pattern Recognition': Don't just solve problems; identify if it's a Sliding Window, Two-Pointer, or Backtracking issue.\n"
                "• Complexity Analysis: You must explain Big O for both Time and Space without being prompted.\n\n"
                "2. SYSTEM DESIGN (LFX/Scalability):\n"
                "• Understand Load Balancers, Caching (Redis), and Database Sharding.\n"
                "• Pro Tip: Always start with a high-level diagram before diving into microservices.\n\n"
                "3. THE LIVE CODING ETIQUETTE:\n"
                "• Think Out Loud: Silence is the enemy. Explain your trade-offs as you type."
            )
        },
        'coding-test-strategy': {
            'title': 'Cracking Online Assessments (OA)',
            'description': 'How to manage time and edge cases in automated coding rounds.',
            'content': (
                "1. TIME MANAGEMENT:\n• Spend 5 mins reading all problems first. Solve the easiest one to build momentum.\n\n"
                "2. EDGE CASE RADAR:\n• Always test for: Empty inputs, Negative numbers, Integer overflow, and Large constraints.\n\n"
                "3. BEYOND BRUTE FORCE:\n• If your code passes 70% of test cases, you likely have an O(N^2) solution where O(N log N) is required."
            )
        },

        # --- MODERN INTERVIEW TIPS ---
        'communication-skills': {
            'title': 'Executive Communication for Engineers',
            'description': 'Bridging the gap between technical logic and stakeholder understanding.',
            'content': (
                "1. THE STAR+ METHOD:\n"
                "• Situation, Task, Action, Result + 'What I learned'.\n\n"
                "2. THE 'I DON'T KNOW' PROTOCOL:\n"
                "• Never fake an answer. Instead, say: 'I haven't worked deeply with X, but based on my knowledge of Y, I assume it works like...' This shows logical derivation.\n\n"
                "3. CLARIFYING QUESTIONS:\n"
                "• Before solving, ask: 'Are there any memory constraints?' or 'Is the input stream real-time?'"
            )
        },
        'mock-interview-guide': {
            'title': 'Self-Mock Interview Checklist',
            'description': 'How to simulate a high-pressure environment at home.',
            'content': (
                "1. RECORD YOURSELF:\n• Watch your body language. Do you look stressed? Do you use filler words like 'um' and 'uh'?\n\n"
                "2. NO GOOGLE POLICY:\n• Solve a new LeetCode Medium without any external tabs open.\n\n"
                "3. PEER REVIEW:\n• Use platforms like Pramp or pair up with a classmate to get honest feedback on your explanation style."
            )
        },

        # --- HR & BEHAVIORAL MASTERCLASS ---
        'tell-me-about-yourself': {
            'title': 'The 60-Second Elevator Pitch',
            'description': 'Summarizing your engineering journey with impact.',
            'content': (
                "1. THE HOOK (Present):\n• 'I am a CS student at ABIT specialized in DevOps and Cloud-Native systems.'\n\n"
                "2. THE MEAT (Past):\n• Mention 1 specific achievement: 'I developed VisionMate, reducing collision risks for the visually impaired using YOLOv8.'\n\n"
                "3. THE WHY (Future):\n• 'I am here because your company’s work in AI-driven localization aligns perfectly with my recent LFX mentorship experience.'"
            )
        },
        'strengths-weaknesses': {
            'title': 'Strategic Vulnerability',
            'description': 'Turning your weaknesses into a narrative of growth.',
            'content': (
                "• STRENGTHS: Don't say 'I am hard-working.' Say 'I am highly adaptable,' and prove it by mentioning a tech stack you learned in 48 hours.\n\n"
                "• WEAKNESSES: Pick a genuine technical weakness (e.g., 'Public speaking' or 'Over-engineering solutions') and immediately explain the system you created to fix it."
            )
        },

        # --- RESUME & BRANDING ---
        'ats-format': {
            'title': 'Defeating the ATS (Robot) Filter',
            'description': 'Formatting your resume for modern Applicant Tracking Systems.',
            'content': (
                "1. NO TABLES/GRAPHICS:\n• ATS bots often fail to parse text inside tables or fancy Canva graphics. Stick to a single-column LaTeX or Word format.\n\n"
                "2. KEYWORD OPTIMIZATION:\n• If the job description mentions 'CI/CD', ensure your resume says 'CI/CD', not just 'Automation'.\n\n"
                "3. ACTION VERBS:\n• Use words like 'Architected', 'Optimized', 'Streamlined', and 'Spearheaded' to start your bullet points."
            )
        }
    }

    resource_data = content_db.get(topic_id)
    if not resource_data:
        flash('This resource module is being updated with the latest 2026 data.', 'info')
        return redirect(url_for('main.resources'))

    return render_template('view_resource.html', resource=resource_data)

@main.route('/download/<filename>')
@login_required
def download_pdf(filename):
    pdf_directory = os.path.join(current_app.root_path, 'static', 'pdfs')
    file_path = os.path.join(pdf_directory, filename)
    
    if os.path.exists(file_path):
        return send_from_directory(pdf_directory, filename, as_attachment=True)
    else:
        # User-friendly name extraction
        display_name = filename.replace('_', ' ').replace('.pdf', '').upper()
        flash(f"The module '{display_name}' is currently in review. Check back shortly!", "info")
        return redirect(url_for('main.resources'))
