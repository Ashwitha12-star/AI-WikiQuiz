from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import Quiz
import crud, json
from schemas import QuizCreate, QuizResponse
from scraper import scrape_wikipedia_content
from llm_quiz import generate_quiz_from_text

# ------------------------------------------------------------
# 🚀 Initialize FastAPI
# ------------------------------------------------------------
app = FastAPI(
    title="AI WikiQuiz API",
    version="2.0",
    description="Automatically generate 10 MCQs + 10 Fill-in-the-Blank quizzes from Wikipedia articles using AI."
)

# Create all database tables
Base.metadata.create_all(bind=engine)

# Enable CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# 🏠 Root endpoint
# ------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "🧠 Welcome to AI WikiQuiz API",
        "endpoints": {
            "/generate_quiz": "POST – Generate quiz from a Wikipedia article",
            "/history": "GET – Fetch all saved quizzes",
            "/history/clear": "DELETE – Clear all saved quizzes",
            "/quiz/{id}": "GET – Retrieve quiz by ID",
            "/ping": "GET – Health check"
        },
    }

# ------------------------------------------------------------
# 🧠 Generate Quiz
# ------------------------------------------------------------
@app.post("/generate_quiz", response_model=QuizResponse)
def generate_quiz(request: QuizCreate, db: Session = Depends(get_db)):
    try:
        # Step 1: Scrape Wikipedia article
        title, content = scrape_wikipedia_content(request.url)
        if not content:
            raise HTTPException(status_code=400, detail="Failed to extract Wikipedia content.")

        # Step 2: Generate quiz using AI / fallback
        quiz_data = generate_quiz_from_text(title, content)

        # Step 3: Save in DB
        quiz_entry = crud.create_quiz(db, request.url, title, quiz_data)

        # Step 4: Return structured quiz
        return {
            "id": quiz_entry.id,
            "title": title,
            "url": request.url,
            "summary": quiz_data.get("summary", ""),
            "mcq": quiz_data.get("mcq", []),
            "fill": quiz_data.get("fill", []),
            "related_topics": quiz_data.get("related_topics", []),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

# ------------------------------------------------------------
# 🕓 Fetch all saved quiz history
# ------------------------------------------------------------
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    try:
        quizzes = crud.get_all_quizzes(db)
        return [
            {
                "id": q.id,
                "title": q.title,
                "url": q.url,
                "created_at": q.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for q in quizzes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

# ------------------------------------------------------------
# 🗑️ Clear quiz history
# ------------------------------------------------------------
@app.delete("/history/clear")
def clear_history(db: Session = Depends(get_db)):
    try:
        crud.delete_all_quizzes(db)
        db.commit()
        return {"message": "🧹 All quiz history cleared successfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

# ------------------------------------------------------------
# 🔍 Get quiz by ID
# ------------------------------------------------------------
@app.get("/quiz/{quiz_id}", response_model=QuizResponse)
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz_json = json.loads(quiz.quiz_data)
    return {
        "id": quiz.id,
        "title": quiz.title,
        "url": quiz.url,
        "summary": quiz.summary,
        "mcq": quiz_json.get("mcq", []),
        "fill": quiz_json.get("fill", []),
        "related_topics": quiz_json.get("related_topics", []),
    }

# ------------------------------------------------------------
# ✅ Health Check
# ------------------------------------------------------------
@app.get("/ping")
def ping():
    return {"status": "✅ API running smoothly!"}
