from pydantic import BaseModel
from typing import List, Optional

# ----------------------------------------------------------
# 🧠 Question Schemas
# ----------------------------------------------------------
class MCQSchema(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: Optional[str] = None
    difficulty: Optional[str] = "medium"


class FillSchema(BaseModel):
    question: str
    answer: str
    explanation: Optional[str] = None
    difficulty: Optional[str] = "medium"


# ----------------------------------------------------------
# 🌐 Request Schema (Input)
# ----------------------------------------------------------
class QuizCreate(BaseModel):
    url: str


# ----------------------------------------------------------
# 📦 Response Schema (Output)
# ----------------------------------------------------------
class QuizResponse(BaseModel):
    id: int
    title: str
    url: str
    summary: Optional[str] = ""
    mcq: List[MCQSchema] = []
    fill: List[FillSchema] = []
    related_topics: List[str] = []

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2
