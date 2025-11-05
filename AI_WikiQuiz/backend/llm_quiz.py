import os, re, random, json
import google.generativeai as genai
from dotenv import load_dotenv

# ============================================================
# 🔐 Load Gemini API key
# ============================================================
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print("⚠️ Gemini API configuration failed:", e)
else:
    print("⚠️ Gemini API key missing in .env")


# ============================================================
# 🧹 Clean extracted text
# ============================================================
def clean_text(text: str):
    """Normalize and limit extracted Wikipedia text."""
    text = re.sub(r"\s+", " ", text)
    return " ".join(text.split()[:2000])


# ============================================================
# 🧠 Generate quiz (Gemini → smart fallback)
# ============================================================
def generate_quiz_from_text(title: str, text: str):
    summary = text[:400] + "..." if len(text) > 400 else text
    cleaned = clean_text(text)

    # ========================================================
    # 🚀 1. Try Gemini (structured factual generator)
    # ========================================================
    if GEMINI_KEY:
        try:
            prompt = f"""
            You are a professional factual quiz generator.
            Based only on the following Wikipedia article about "{title}",
            create a structured quiz with:
            - 10 factual multiple-choice questions (MCQs)
            - 10 factual fill-in-the-blank questions

            Rules:
            • Questions must be based on real facts (dates, achievements, people, places).
            • Each MCQ has exactly 4 distinct options and one correct answer.
            • No grammar or language questions.
            • Keep all questions short and meaningful.

            Output ONLY valid JSON in this format:
            {{
              "summary": "short factual summary",
              "mcq": [
                {{"question": "...", "options": ["A","B","C","D"], "answer": "Correct"}}
              ],
              "fill": [
                {{"question": "Sentence with ____ missing factual word", "answer": "Correct"}}
              ]
            }}

            TEXT:
            {cleaned}
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.3}
            )

            if response and hasattr(response, "text") and response.text.strip():
                output_text = response.text.strip()
                match = re.search(r"\{.*\}", output_text, re.S)
                if match:
                    data = json.loads(match.group())
                    if "mcq" in data and "fill" in data:
                        print("✅ Gemini generated structured quiz successfully.")
                        return data
        except Exception as e:
            print("⚠️ Gemini failed, using fallback:", e)

    # ========================================================
    # 🔁 2. Smart fallback factual generator
    # ========================================================
    print("⚙️ Using fallback factual generator...")
    sentences = re.split(r"(?<=[.!?]) +", cleaned)
    sentences = [s.strip() for s in sentences if 8 < len(s.split()) < 25]
    random.shuffle(sentences)

    mcq_data, fill_data = [], []

    def get_factual_options(answer, text_pool):
        """Generate 3 realistic distractor options (names, places, years)."""
        distractors = set()
        words = re.findall(r"\b[A-Z][a-z]+\b", text_pool)  # Proper nouns
        while len(distractors) < 3 and words:
            word = random.choice(words)
            if word != answer:
                distractors.add(word)
        # fallback if not enough distractors
        while len(distractors) < 3:
            distractors.add(random.choice(["India", "England", "Australia", "2011", "2018", "Delhi"]))
        return list(distractors)

    # --- 10 MCQs ---
    for sent in sentences[:10]:
        words = sent.split()
        keyword_candidates = [w for w in words if w[0].isupper() or w.isdigit()]
        if not keyword_candidates:
            continue
        answer = random.choice(keyword_candidates)
        options = get_factual_options(answer, cleaned)
        options.append(answer)
        random.shuffle(options)
        mcq_data.append({
            "question": f"What is true about: “{sent}”?",
            "options": options,
            "answer": answer
        })

    # --- 10 Fill-in-the-Blanks ---
    for sent in sentences[10:20]:
        words = sent.split()
        keyword_candidates = [w for w in words if w[0].isupper() or w.isdigit()]
        if not keyword_candidates:
            continue
        answer = random.choice(keyword_candidates)
        blank_sentence = re.sub(rf"\b{re.escape(answer)}\b", "____", sent, count=1)
        fill_data.append({
            "question": blank_sentence,
            "answer": answer
        })

    return {
        "summary": summary,
        "mcq": mcq_data[:10],
        "fill": fill_data[:10],
    }
