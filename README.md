# Digital-Placement-Ecosystem

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A centralized web-based platform for engineering students to prepare for campus placements. Practice aptitude, technical MCQs, and access interview resources all in one place.

## Features

- **Aptitude Tests** - Quantitative, Logical Reasoning, Verbal Ability
- **Technical MCQs** - C, Python, DBMS, Operating Systems
- **Quiz System** - Randomized questions, score tracking, history
- **Resources** - Interview tips, HR questions, coding practice links
- **Admin Panel** - Manage questions, categories, and users
- **Student Dashboard** - Track progress and view statistics

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Digital-Placement-Ecosystem.git
cd Digital-Placement-EcoSystem

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
python seed_data.py

# Run the application
python run.py
```

### Access the Application

Open your browser and visit: **http://localhost:5001**

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@college.edu` | `admin123` |
| Student | Register at `/auth/register` | (your choice) |

## Project Structure

```
Digital-Placement-Ecosystem/
├── run.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── seed_data.py          # Database seeder script
├── instance/
│   └── placement.db      # SQLite database (auto-created)
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # SQLAlchemy database models
│   ├── auth/             # Authentication module
│   │   ├── routes.py     # Login, register, logout
│   │   └── forms.py      # WTForms definitions
│   ├── main/             # Main routes
│   │   └── routes.py     # Home, dashboard, resources
│   ├── quiz/             # Quiz module
│   │   └── routes.py     # Categories, quiz, results
│   ├── admin/            # Admin panel
│   │   └── routes.py     # Question/user management
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   ├── quiz/
│   │   └── admin/
│   └── static/
│       └── css/
│           └── style.css # Main stylesheet
└── venv/                 # Virtual environment
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3.0 |
| Database | SQLite (SQLAlchemy ORM) |
| Authentication | Flask-Login |
| Forms | Flask-WTF, WTForms |
| Frontend | HTML5, CSS3, JavaScript |
| Font | Inter (Google Fonts) |

## Database Models

- **User** - Students and admins with role-based access
- **Category** - Quiz categories (Aptitude/Technical)
- **Question** - MCQs with 4 options and correct answer
- **QuizResult** - User quiz attempts and scores
- **Resource** - Study materials and links
- **StudentActivity** - Activity logging

## API Routes

### Public Routes
| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/auth/login` | User login |
| `/auth/register` | Student registration |
| `/resources` | View placement resources |

### Protected Routes (Login Required)
| Route | Description |
|-------|-------------|
| `/dashboard` | Student dashboard |
| `/quiz/` | Quiz categories |
| `/quiz/start/<id>` | Start a quiz |
| `/quiz/result/<id>` | View quiz result |
| `/quiz/history` | Quiz attempt history |

### Admin Routes (Admin Only)
| Route | Description |
|-------|-------------|
| `/admin/` | Admin dashboard |
| `/admin/questions` | Manage questions |
| `/admin/questions/add` | Add new question |
| `/admin/students` | View all students |
| `/admin/resources` | Manage resources |

## Configuration

Edit `config.py` to customize settings:

```python
class Config:
    SECRET_KEY = 'your-secret-key'  # Change in production!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db'  # Or PostgreSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Using PostgreSQL (Production)

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/placement_portal'
```

## Team Roles (5 Members)

| Member | Responsibility |
|--------|----------------|
| Member 1 | Frontend design (HTML/CSS) |
| Member 2 | JavaScript (quiz logic, validation) |
| Member 3 | Backend (Flask routing, authentication,PYTHON) |
| Member 4 | Database (models, queries, migrations) |
| Member 5 | Documentation, PPT, diagrams, testing |

## Future Scope

- [ ] Mock tests with timer
- [ ] Result analytics and graphs
- [ ] Resume builder
- [ ] Company-wise preparation
- [ ] Mobile app version
- [ ] Email notifications
- [ ] Leaderboard system

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Flask-Login](https://flask-login.readthedocs.io/) - Authentication
- [WTForms](https://wtforms.readthedocs.io/) - Form validation
- [Google Fonts](https://fonts.google.com/) - Inter font

---

Made with for engineering students preparing for placements
