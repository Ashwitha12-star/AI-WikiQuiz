from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    quiz_data = Column(Text, nullable=False)  # JSON string for quiz content
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON array of options
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), default="medium")
