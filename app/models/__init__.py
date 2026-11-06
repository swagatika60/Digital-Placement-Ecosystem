"""
Models package — re-exports every model so that existing imports like
``from app.models import User, Category, …`` keep working unchanged.
"""
from app.models.user import User
from app.models.quiz import Category, Question, QuizResult, QuestionBookmark
from app.models.resource import Resource
from app.models.activity import StudentActivity
from app.models.planner import StudyGoal, StudyStreak, UserComment
from app.models.dsa import DSATopic, DSAQuestion, DSASubmission, AlgorithmVisualizer
from app.models.workspace import LabVaultEntry, DuelRoom, ScopeSentryAudit

__all__ = [
    "User",
    "Category",
    "Question",
    "QuizResult",
    "QuestionBookmark",
    "Resource",
    "StudentActivity",
    "StudyGoal",
    "StudyStreak",
    "UserComment",
    "DSATopic",
    "DSAQuestion",
    "DSASubmission",
    "AlgorithmVisualizer",
    "LabVaultEntry",
    "DuelRoom",
    "ScopeSentryAudit",
]
