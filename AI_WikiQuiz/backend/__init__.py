"""
AI_WIKIQUIZ Backend Package
---------------------------
This file marks the backend folder as a Python package and allows
imports between modules such as:
    from backend import database, models, crud, llm_quiz, scraper
"""

# Optional: automatically import core components for convenience
from .database import Base, engine, SessionLocal
from .models import QuizRecord

__all__ = ["Base", "engine", "SessionLocal", "QuizRecord"]
