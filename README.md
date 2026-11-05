# Digital-Placement-Ecosystem :

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A web platform for engineering students preparing for campus placements. Practice aptitude and technical MCQs under realistic time limits, drill DSA with an interactive visualizer and a browser code editor, review company-specific patterns, analyze your performance with honest metrics, and use an AI workspace to ingest study material into summaries and interview prep — all in one place.

> **Design language:** the UI follows a "Paper & Wireframe Editorial" aesthetic — warm paper backgrounds, deep charcoal ink typography, red marker accents, monospace metadata tags, and crisp black borders with hard offset shadows.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Default Credentials](#default-credentials)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Database Models](#database-models)
- [Routes](#routes)
- [Configuration](#configuration)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### Core Drills

- **Aptitude Tests** — Quantitative, Logical Reasoning, Verbal Ability.
- **Technical MCQs** — Python, Java, DSA, SQL, Operating Systems, Computer Networks, System Design, DevOps, and more.
- **Quiz System** — randomized questions, score tracking, attempt history.
- **Timed Mock Tests** — 60 seconds per question, countdown timer, auto-submit.
- **Leaderboard** — ranked by best score across peers.
- **Question Bookmarks** — save questions mid-quiz and review them later.
- **Dashboard Analytics** — score trend chart, category progress, performance stats.

### DSA & System Design

- **DSA Practice** — topic-wise questions (Easy/Medium/Hard) with a browser code editor and test-case verification (Python and JavaScript execute; Java/C/C++ get syntax checks).
- **Algorithm Visualizer** — step-through visualizations of sorting, searching, and tree/graph algorithms.
- **DSA Labs & Visualizer** — university lab program tracks (sorting, searching, tree traversals, graph algorithms) with complexity tags and canvas-based step-through cards.
- **System Design Vault** — architecture blueprints and practical scaling scenarios tagged with real engineering concepts (`#distributed-caching`, `#concurrency`, `#database-indexing`, `#rate-limiting`).

### AI Workspace

- **Learning Assistant** — ingest YouTube videos, GitHub repos, PDFs, or any URL. Get AI-generated summaries, key points, concept breakdowns, roadmaps, and an interactive chat tutor (Google Gemini).

### Unique Tools

- **Peer Code-Duel Rooms** — create a 1v1 timed room with a 6-character code, challenge a peer, and race through the same question set with a synchronized countdown.
- **University Lab Code Vault** — peer-sourced repository of verified lab solutions with viva (oral exam) prep questions; upvote useful entries.
- **ScopeSentry** — paste a resume or README to get an honest, rule-based risk audit: vague metrics, missing technical depth, filler words, and (for READMEs) setup/auth gaps. Scores 0–100.

### Platform

- **Admin Panel** — manage questions, categories, resources, and users.
- **Student Dashboard** — track progress and view statistics.
- **Resources** — interview tips, HR questions, coding links, curated topic guides.
- **Company-Wise Preparation** — dedicated quiz categories and downloadable PDF guides for Amazon, Google, Microsoft, TCS NQT, Infosys, Wipro, Accenture, and Cognizant.
- **Downloadable PDF Guides** — study notes, cheat sheets, HR Q&A, aptitude formula sheet, and a resume-building guide (generate with `python scripts/generate_pdfs.py`).

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- (Optional) A [Google AI Studio](https://aistudio.google.com/) API key for the Learning Assistant

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Digital-Placement-Ecosystem.git
cd Digital-Placement-Ecosystem

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database (creates admin user + sample data)
python3 seed_data.py

# [Optional] Seed DSA topics/questions
python3 seed_dsa.py
python3 seed_dsa_full.py

# Run the application
python3 run.py
```

> **Note:** if the bundled `venv/` directory fails to start (it was created on another machine/OS), recreate it with the steps above before running the app.

### Access the Application

Open your browser and visit: **http://localhost:5001**

---

## Default Credentials

| Role    | Email                        | Password      |
| ------- | ---------------------------- | ------------- |
| Admin   | `admin@college.edu`          | `admin123`    |
| Student | Register at `/auth/register` | (your choice) |

---

## Project Structure

```
Digital-Placement-Ecosystem/
├── run.py                 # Application entry point (port 5001)
├── config.py              # Configuration settings (env-var overridable)
├── requirements.txt       # Python dependencies
├── seed_data.py           # Seeder: admin user + sample quiz data
├── seed_dsa.py            # Seeder: DSA topics/questions
├── seed_dsa_full.py       # Seeder: expanded DSA dataset
├── migrate_add_columns.py # Helper migration script
├── smoke_test.py          # Smoke tests
├── scripts/
│   └── generate_pdfs.py   # Generates the text-based placement PDF guides
├── app/
│   ├── __init__.py        # Flask app factory (extensions, blueprints, auto-migrate)
│   ├── extensions.py      # Shared extension instances (db, login_manager, csrf)
│   ├── decorators.py      # Role-guard decorators (student_required, reject_admin)
│   ├── models/            # SQLAlchemy models (one module per domain)
│   │   ├── user.py        # User
│   │   ├── quiz.py        # Category, Question, QuizResult, QuestionBookmark
│   │   ├── resource.py    # Resource
│   │   ├── learning.py    # LearningResource, ChatHistory
│   │   ├── activity.py    # StudentActivity
│   │   ├── planner.py     # StudyGoal, StudyStreak, UserComment
│   │   ├── dsa.py         # DSATopic, DSAQuestion, DSASubmission, AlgorithmVisualizer
│   │   └── workspace.py   # LabVaultEntry, DuelRoom, ScopeSentryAudit
│   ├── auth/              # Login, register, logout, password reset, verification
│   ├── main/              # Home, dashboard, resources, profile, study plan
│   ├── quiz/              # Categories, quizzes, results, history, leaderboard
│   ├── admin/             # Manage questions, categories, resources, users
│   ├── learning/          # AI Learning Assistant (scraper + ai_engine)
│   ├── dsa/               # DSA practice, code editor, algorithm visualizer
│   ├── workspace/         # System Design Vault, DSA Labs, ScopeSentry, Lab Vault, Duel
│   ├── templates/         # Jinja2 HTML templates (one folder per blueprint)
│   └── static/
│       ├── css/
│       │   ├── style.css          # Base stylesheet
│       │   ├── paper-editorial.css # Editorial "Paper & Wireframe" design system
│       │   └── portal-modern.css   # Modern portal component styles
│       ├── js/
│       │   ├── quiz-engine.js      # Keyboard-first quiz engine + localStorage persistence
│       │   ├── palette.js          # Global command palette (press "/")
│       │   ├── duel-room.js        # Duel room countdown + keyboard nav
│       │   ├── lab-visualizer.js   # DSA lab step-through animations
│       │   └── scope-sentry.js     # Client-side ScopeSentry heuristics
│       └── pdfs/                  # Generated/static PDF guides
└── venv/                  # Virtual environment (recreate if it fails to start)
```

---

## Technology Stack

| Layer             | Technology                                                         |
| ----------------- | ------------------------------------------------------------------ |
| Backend           | Flask 3.0                                                          |
| Database          | SQLite (SQLAlchemy ORM); SQLAlchemy URI overridable for PostgreSQL |
| Authentication    | Flask-Login (role-based: student / admin)                          |
| CSRF              | Flask-WTF                                                          |
| Forms             | WTForms, email-validator                                           |
| AI                | Google Gemini (`google-genai`)                                     |
| Content Ingestion | trafilatura, BeautifulSoup, youtube-transcript-api, pypdf          |
| Frontend          | HTML5, CSS3, vanilla JavaScript (Jinja2 templates)                 |
| Fonts             | Fraunces, Space Grotesk, JetBrains Mono (Google Fonts)             |

---

## Database Models

| Model                                       | Purpose                                                                            |
| ------------------------------------------- | ---------------------------------------------------------------------------------- |
| `User`                                      | Students and admins, role-based access, password-reset & email-verification fields |
| `Category`                                  | Quiz categories (Aptitude / Technical)                                             |
| `Question`                                  | MCQs with 4 options, correct answer, explanation, difficulty                       |
| `QuizResult`                                | Quiz attempts, scores, percentages                                                 |
| `QuestionBookmark`                          | Questions saved by a user for later review                                         |
| `Resource`                                  | Study materials, notes, links                                                      |
| `StudentActivity`                           | Activity logging                                                                   |
| `LearningResource`                          | Ingested sources (URL/YouTube/GitHub/PDF) with AI summary and roadmap              |
| `ChatHistory`                               | Chat turns between a user and the AI tutor for a resource                          |
| `StudyGoal` / `StudyStreak` / `UserComment` | Study-planning and streaks                                                         |
| `DSATopic`                                  | DSA topics (slug, order, difficulty counts)                                        |
| `DSAQuestion`                               | DSA problems with examples, test cases, starter code                               |
| `DSASubmission`                             | A user's code submission and test results for a question                           |
| `AlgorithmVisualizer`                       | Curated algorithms with step and code JSON for the visualizer                      |
| `LabVaultEntry`                             | Peer-sourced lab solution (code + viva questions + upvotes)                        |
| `DuelRoom`                                  | 1v1 duel room (code, topic, duration, scores, question set)                        |
| `ScopeSentryAudit`                          | Stored resume/README audit results (score + findings JSON)                         |

The workspace models (`LabVaultEntry`, `DuelRoom`, `ScopeSentryAudit`) are opt-in tables that Flask's `create_all()` creates automatically on boot — no manual migration needed.

---

## Routes

Blueprints are registered with URL prefixes in `app/__init__.py`.

### Public Routes

| Route                        | Description                   |
| ---------------------------- | ----------------------------- |
| `/`                          | Landing page                  |
| `/auth/login`                | User login                    |
| `/auth/register`             | Student registration          |
| `/resource/topic/<topic_id>` | Curated placement topic guide |

### Protected Routes (Student Login Required)

| Route                    | Description                                  |
| ------------------------ | -------------------------------------------- |
| `/dashboard`             | Student dashboard with stats and trend chart |
| `/resources`             | Placement resources                          |
| `/download/<filename>`   | Download a PDF resource                      |
| `/quiz/`                 | Quiz categories                              |
| `/quiz/start/<id>`       | Start a quiz                                 |
| `/quiz/take/<id>`        | Timed mock test (60s/question)               |
| `/quiz/result/<id>`      | Quiz result                                  |
| `/quiz/history`          | Quiz attempt history                         |
| `/quiz/leaderboard`      | Leaderboard                                  |
| `/quiz/bookmarks`        | Saved questions                              |
| `/learning/`             | AI Learning Assistant resource list          |
| `/dsa/`                  | DSA topics                                   |
| `/dsa/<slug>`            | Practice questions for a topic               |
| `/dsa/question/<id>`     | Code editor for a question                   |
| `/dsa/visualizer`        | Algorithm visualizer index                   |
| `/dsa/visualizer/<slug>` | Step-through visualization player            |

### Workspace Routes (Student Login Required)

| Route                        | Description                                          |
| ---------------------------- | ---------------------------------------------------- |
| `/design`                    | System Design Vault                                  |
| `/dsa/labs`                  | DSA Labs hub                                         |
| `/dsa/labs/<slug>/visualize` | Interactive lab visualization                        |
| `/scope-sentry`              | ScopeSentry resume/README auditor                    |
| `POST /scope-sentry/analyze` | Run an audit (JSON body: `source`, `text`)           |
| `/vault`                     | University Lab Code Vault                            |
| `POST /vault/upload`         | Publish a lab solution                               |
| `POST /vault/<id>/upvote`    | Upvote an entry                                      |
| `/duel`                      | Peer Code-Duel lobby                                 |
| `POST /duel/create`          | Create a duel room (JSON or form; returns room code) |
| `/duel/<code>`               | Duel room                                            |

### Learning Assistant API (JSON, Login Required)

| Route                                     | Description                                           |
| ----------------------------------------- | ----------------------------------------------------- |
| `POST /learning/api/ingest`               | Ingest a URL (returns `202`, processed in background) |
| `GET /learning/api/resource/<rid>/status` | Poll processing status                                |
| `GET /learning/api/resource/<rid>`        | Resource JSON (summary, roadmap, status)              |
| `DELETE /learning/api/resource/<rid>`     | Delete a resource                                     |
| `POST /learning/api/resource/<rid>/chat`  | Send a message to the AI tutor                        |

### Admin Routes (Admin Only)

| Route                  | Description           |
| ---------------------- | --------------------- |
| `/admin/`              | Admin dashboard       |
| `/admin/questions`     | Manage questions      |
| `/admin/questions/add` | Add new question      |
| `/admin/categories`    | Manage categories     |
| `/admin/resources`     | Manage resources      |
| `/admin/users`         | View and manage users |

---

## Configuration

Settings live in `config.py` and can be overridden with environment variables. The app supports development, production, and testing configs (selected via `FLASK_ENV`).

| Variable         | Default                                | Description                                                              |
| ---------------- | -------------------------------------- | ------------------------------------------------------------------------ |
| `SECRET_KEY`     | `placement-portal-secret-key-2024`     | Flask secret key — change in production!                                 |
| `DATABASE_URL`   | `sqlite:///<project>/app/placement.db` | SQLAlchemy database URI (e.g. PostgreSQL)                                |
| `GEMINI_API_KEY` | unset                                  | Google Gemini API key — required for the AI Workspace                    |
| `GEMINI_MODEL`   | `gemini-2.0-flash`                     | Gemini model name used for analysis/chat                                 |
| `GITHUB_TOKEN`   | unset                                  | Optional; raises GitHub API rate limit (60 → 5000/hr) for repo ingestion |

### Using PostgreSQL (Production)

```bash
export DATABASE_URL='postgresql://user:password@localhost/placement_portal'
```

---

## Keyboard Shortcuts

The quiz engine and duel rooms are keyboard-first:

| Key                    | Action                                                  |
| ---------------------- | ------------------------------------------------------- |
| `J` / `K` (or `1`–`4`) | Select an MCQ option                                    |
| `Enter`                | Confirm the selected option                             |
| `Ctrl`/`Cmd` + `Enter` | Submit the quiz                                         |
| `Space`                | Flag / bookmark the current question                    |
| `/`                    | Open the global command palette (search across modules) |

Quiz state (selected answers, remaining time, flags) is persisted in `localStorage`, so a refresh or network drop doesn't wipe your progress.

---

## Testing

A smoke test script is included:

```bash
python smoke_test.py
```

You can also run the app's own verification flows manually (seed data, register a student, take a quiz, create a duel room, run a ScopeSentry audit).

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgements

<<<<<<< HEAD
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Flask-Login](https://flask-login.readthedocs.io/) - Authentication
- [WTForms](https://wtforms.readthedocs.io/) - Form validation
- [Google Fonts](https://fonts.google.com/) - Inter font
---

Made with for engineering students preparing for placements
=======
- [Flask](https://flask.palletsprojects.com/) — Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
- [Flask-Login](https://flask-login.readthedocs.io/) — Authentication
- [WTForms](https://wtforms.readthedocs.io/) — Form validation
- [Google Gemini](https://ai.google.dev/) — AI summaries, roadmaps, and chat tutor
- [Google Fonts](https://fonts.google.com/) — Fraunces, Space Grotesk, JetBrains Mono
>>>>>>> afc4d80 (feat(ui): simplify navigation and feature names for better clarity)
