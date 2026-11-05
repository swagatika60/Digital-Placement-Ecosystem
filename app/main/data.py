"""
Curated topic content for the Resources page.

Each key maps to a placement-preparation topic with a title,
description, and rich text content displayed on view_resource.html.
"""
TOPIC_CONTENT = {
    # ── Advanced Technical Preparation ────────────────────────────
    "technical-prep": {
        "title": "The Technical Interview Blueprint",
        "description": "A holistic approach to DSA, System Design, and Problem Solving.",
        "content": (
            "1. THE DSA TRIAD:\n"
            "• Master 'Pattern Recognition': Don't just solve problems; identify if it's a Sliding Window, Two-Pointer, or Backtracking issue.\n"
            "• Complexity Analysis: You must explain Big O for both Time and Space without being prompted.\n\n"
            "2. SYSTEM DESIGN (LFX/Scalability):\n"
            "• Understand Load Balancers, Caching (Redis), and Database Sharding.\n"
            "• Pro Tip: Always start with a high-level diagram before diving into microservices.\n\n"
            "3. THE LIVE CODING ETIQUETTE:\n"
            "• Think Out Loud: Silence is the enemy. Explain your trade-offs as you type."
        ),
    },
    "coding-test-strategy": {
        "title": "Cracking Online Assessments (OA)",
        "description": "How to manage time and edge cases in automated coding rounds.",
        "content": (
            "1. TIME MANAGEMENT:\n• Spend 5 mins reading all problems first. Solve the easiest one to build momentum.\n\n"
            "2. EDGE CASE RADAR:\n• Always test for: Empty inputs, Negative numbers, Integer overflow, and Large constraints.\n\n"
            "3. BEYOND BRUTE FORCE:\n• If your code passes 70% of test cases, you likely have an O(N^2) solution where O(N log N) is required."
        ),
    },

    # ── Modern Interview Tips ─────────────────────────────────────
    "communication-skills": {
        "title": "Executive Communication for Engineers",
        "description": "Bridging the gap between technical logic and stakeholder understanding.",
        "content": (
            "1. THE STAR+ METHOD:\n"
            "• Situation, Task, Action, Result + 'What I learned'.\n\n"
            "2. THE 'I DON'T KNOW' PROTOCOL:\n"
            "• Never fake an answer. Instead, say: 'I haven't worked deeply with X, but based on my knowledge of Y, I assume it works like...' This shows logical derivation.\n\n"
            "3. CLARIFYING QUESTIONS:\n"
            "• Before solving, ask: 'Are there any memory constraints?' or 'Is the input stream real-time?'"
        ),
    },
    "mock-interview-guide": {
        "title": "Self-Mock Interview Checklist",
        "description": "How to simulate a high-pressure environment at home.",
        "content": (
            "1. RECORD YOURSELF:\n• Watch your body language. Do you look stressed? Do you use filler words like 'um' and 'uh'?\n\n"
            "2. NO GOOGLE POLICY:\n• Solve a new LeetCode Medium without any external tabs open.\n\n"
            "3. PEER REVIEW:\n• Use platforms like Pramp or pair up with a classmate to get honest feedback on your explanation style."
        ),
    },

    # ── HR & Behavioral Masterclass ──────────────────────────────
    "tell-me-about-yourself": {
        "title": "The 60-Second Elevator Pitch",
        "description": "Summarizing your engineering journey with impact.",
        "content": (
            "1. THE HOOK (Present):\n• 'I am a CS student at ABIT specialized in DevOps and Cloud-Native systems.'\n\n"
            "2. THE MEAT (Past):\n• Mention 1 specific achievement: 'I developed VisionMate, reducing collision risks for the visually impaired using YOLOv8.'\n\n"
            "3. THE WHY (Future):\n• 'I am here because your company's work in AI-driven localization aligns perfectly with my recent LFX mentorship experience.'"
        ),
    },
    "strengths-weaknesses": {
        "title": "Strategic Vulnerability",
        "description": "Turning your weaknesses into a narrative of growth.",
        "content": (
            "• STRENGTHS: Don't say 'I am hard-working.' Say 'I am highly adaptable,' and prove it by mentioning a tech stack you learned in 48 hours.\n\n"
            "• WEAKNESSES: Pick a genuine technical weakness (e.g., 'Public speaking' or 'Over-engineering solutions') and immediately explain the system you created to fix it."
        ),
    },

    # ── Resume & Branding ────────────────────────────────────────
    "ats-format": {
        "title": "Defeating the ATS (Robot) Filter",
        "description": "Formatting your resume for modern Applicant Tracking Systems.",
        "content": (
            "1. NO TABLES/GRAPHICS:\n• ATS bots often fail to parse text inside tables or fancy Canva graphics. Stick to a single-column LaTeX or Word format.\n\n"
            "2. KEYWORD OPTIMIZATION:\n• If the job description mentions 'CI/CD', ensure your resume says 'CI/CD', not just 'Automation'.\n\n"
            "3. ACTION VERBS:\n• Use words like 'Architected', 'Optimized', 'Streamlined', and 'Spearheaded' to start your bullet points."
        ),
    },
    "dress-code": {
        "title": "Dress Code & Body Language",
        "description": "Professional attire and confident body language for interviews.",
        "content": (
            "1. FORMAL ATTIRE:\n• For tech interviews: business casual or formal. Ironed shirt, closed shoes, neat hair.\n• Avoid flashy accessories, heavy perfume, and wrinkled clothes.\n\n"
            "2. BODY LANGUAGE:\n• Firm handshake, eye contact, and a genuine smile.\n• Sit upright, lean slightly forward, and keep hands visible.\n\n"
            "3. DURING VIDEO CALLS:\n• Test camera, mic, and lighting beforehand. Look into the camera, not the screen."
        ),
    },
    "interview-mistakes": {
        "title": "Common Interview Mistakes",
        "description": "Avoid these frequent mistakes that cost candidates the offer.",
        "content": (
            "1. POOR PREPARATION:\n• Not researching the company or role before the interview.\n\n"
            "2. RAMBLING ANSWERS:\n• Answer the question asked. Use STAR and stop.\n\n"
            "3. FAKING KNOWLEDGE:\n• Interviewers detect bluffing instantly. Say what you know and what you would do to learn.\n\n"
            "4. NEGATIVE TALK:\n• Never badmouth previous employers or colleagues.\n\n"
            "5. NOT ASKING QUESTIONS:\n• Always have 2-3 thoughtful questions for the interviewer."
        ),
    },
    "why-hire-you": {
        "title": "Why Should We Hire You?",
        "description": "Craft a compelling answer that sets you apart.",
        "content": (
            "1. THE FORMULA:\n• 'You should hire me because I bring X (skill), proven by Y (achievement), which helps you with Z (company need).'\n\n"
            "2. MATCH THE JOB DESCRIPTION:\n• Pick the 3 most important requirements and map your strongest proof to each.\n\n"
            "3. ADD YOUR EDGE:\n• Mention what makes you unique: speed, communication, domain interest, or project depth."
        ),
    },
    "where-do-you-see-yourself": {
        "title": "Where Do You See Yourself in 5 Years?",
        "description": "Answer career-goal questions with ambition and realism.",
        "content": (
            "1. SHOW GROWTH:\n• 'I want to grow into a senior engineer who owns complex systems and mentors juniors.'\n\n"
            "2. ALIGN WITH THE COMPANY:\n• Connect your growth to the company roadmap, not a competing firm.\n\n"
            "3. AVOID:\n• 'I want your job' or vague answers like 'I want to be successful'."
        ),
    },
    "why-this-company": {
        "title": "Why This Company?",
        "description": "Research-based strategies to answer the company-fit question.",
        "content": (
            "1. RESEARCH FIRST:\n• Study products, engineering culture, tech stack, and recent news.\n\n"
            "2. THE ANSWER STRUCTURE:\n• Company strength (what they do well) + your alignment (why it excites you) + your contribution (what you bring).\n\n"
            "3. USE EVIDENCE:\n• Reference a specific product, blog, or hiring initiative to prove genuine interest."
        ),
    },
    "salary-expectations": {
        "title": "Salary Expectations",
        "description": "Negotiate salary professionally without underselling yourself.",
        "content": (
            "1. RESEARCH THE RANGE:\n• Use Glassdoor, levels.fyi, and campus placement stats for your role and location.\n\n"
            "2. GIVE A RANGE, NOT A NUMBER:\n• 'Based on market research, I expect between X and Y, but I am open to discussing total compensation.'\n\n"
            "3. COUNT THE WHOLE PACKAGE:\n• Base, bonus, stock, joining bonus, and benefits.\n\n"
            "4. NEVER LOWBALL:\n• Let them name a number first when possible; stay polite and confident."
        ),
    },
    "resume-templates": {
        "title": "Resume Templates",
        "description": "Professional templates designed for freshers and experienced candidates.",
        "content": (
            "1. CLEAN SINGLE-COLUMN:\n• ATS-safe: no tables, images, or multi-column layouts. Use Word or LaTeX.\n\n"
            "2. STANDARD SECTIONS:\n• Contact, Summary, Education, Skills, Projects, Internships, Achievements, Certifications.\n\n"
            "3. FONTS & SIZE:\n• Calibri/Arial 10-11pt, margins 0.5-1 inch, consistent bold/italic usage.\n\n"
            "4. ONE PAGE FOR FRESHERS:\n• Cut filler; every line should earn its place."
        ),
    },
    "resume-checklist": {
        "title": "Resume Checklist",
        "description": "Essential elements every placement resume should include.",
        "content": (
            "1. CONTACT INFO:\n• Email, phone, LinkedIn, GitHub, and location at the top.\n\n"
            "2. IMPACTFUL BULLETS:\n• Action verb + what you did + measurable result for every project.\n\n"
            "3. KEYWORDS:\n• Match terms from the job description (CI/CD, React, SQL, etc.).\n\n"
            "4. PROOFREAD:\n• Zero typos. Read aloud and get a second pair of eyes.\n\n"
            "5. HONESTY:\n• Only list skills and projects you can defend in an interview."
        ),
    },
}
