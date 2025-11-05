from sqlalchemy.orm import Session
from models import Quiz
import json

# --------------------------------------------------
# 🧠 Create and store a new quiz record
# --------------------------------------------------
def create_quiz(db: Session, url: str, title: str, quiz_data: dict):
    """
    Save a generated quiz to the database.
    Stores title, URL, summary, and full quiz JSON (including mcq + fill sections).
    """
    # Safely store the entire quiz structure (not just one list)
    quiz_json = json.dumps({
        "summary": quiz_data.get("summary", ""),
        "mcq": quiz_data.get("mcq", []),
        "fill": quiz_data.get("fill", []),
        "related_topics": quiz_data.get("related_topics", [])
    })

    quiz = Quiz(
        title=title,
        url=url,
        quiz_data=quiz_json,
        summary=quiz_data.get("summary", "")
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


# --------------------------------------------------
# 📜 Fetch all quiz records (history)
# --------------------------------------------------
def get_all_quizzes(db: Session):
    """
    Retrieve all saved quizzes ordered by most recent.
    """
    return db.query(Quiz).order_by(Quiz.created_at.desc()).all()


# --------------------------------------------------
# 🔍 Get single quiz by ID
# --------------------------------------------------
def get_quiz(db: Session, quiz_id: int):
    """
    Retrieve a quiz by its database ID.
    """
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


# --------------------------------------------------
# 🗑️ Delete all quizzes (Clear History)
# --------------------------------------------------
def delete_all_quizzes(db: Session):
    """
    Permanently deletes all quiz records from the database.
    """
    db.query(Quiz).delete()
    db.commit()
