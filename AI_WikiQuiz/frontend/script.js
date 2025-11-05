document.addEventListener("DOMContentLoaded", () => {
  const apiBase = "http://127.0.0.1:8000"; // ✅ Backend FastAPI URL
  const quizOutput = document.getElementById("quizOutput");
  const historyBody = document.querySelector("#historyTable tbody");
  const clearBtn = document.getElementById("clearHistoryBtn");

  // ==========================================================
  // 🧠 Generate Quiz
  // ==========================================================
  document.getElementById("generateBtn").addEventListener("click", async () => {
    const url = document.getElementById("wikiUrl").value.trim();
    if (!url) return alert("Please enter a Wikipedia URL!");
    quizOutput.innerHTML = "<p>🌀 Generating quiz... please wait.</p>";

    try {
      const res = await fetch(`${apiBase}/generate_quiz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await res.json();

      if (res.ok) {
        renderQuiz(data);
        loadHistory(); // refresh after new quiz
      } else {
        quizOutput.innerHTML = `<p style='color:red;'>❌ ${data.detail}</p>`;
      }
    } catch (err) {
      console.error(err);
      quizOutput.innerHTML = `<p style='color:red;'>❌ Failed to connect to server.</p>`;
    }
  });

  // ==========================================================
  // 🧩 Render Quiz
  // ==========================================================
  function renderQuiz(data) {
    quizOutput.innerHTML = `
      <h2>${data.title || "Generated Quiz"}</h2>
      <p><strong>Summary:</strong> ${data.summary}</p>
      <hr>
      <div id="mcqSection"><h3>🧠 Multiple Choice Questions</h3></div>
      <div id="fillSection"><h3>✏️ Fill in the Blanks</h3></div>
      <div id="scoreBoard" style="margin-top:20px;font-weight:600;"></div>
    `;

    const mcqDiv = document.getElementById("mcqSection");
    const fillDiv = document.getElementById("fillSection");
    let correct = 0,
      answered = 0,
      total = (data.mcq?.length || 0) + (data.fill?.length || 0);

    // ------------------------------
    // 🎯 MCQs
    // ------------------------------
    (data.mcq || []).forEach((q, i) => {
      const card = document.createElement("div");
      card.className = "quizCard";
      card.innerHTML = `
        <h4>Q${i + 1}. ${q.question}</h4>
        ${q.options
          .map(
            (opt) =>
              `<button class="option-btn" data-answer="${opt}" data-correct="${q.answer}">${opt}</button>`
          )
          .join("")}
        <p class="result-msg"></p>
      `;
      mcqDiv.appendChild(card);
    });

    // ------------------------------
    // ✏️ Fill-in-the-blanks
    // ------------------------------
    (data.fill || []).forEach((q, i) => {
      const card = document.createElement("div");
      card.className = "quizCard";
      card.innerHTML = `
        <h4>Q${i + 1}. ${q.question}</h4>
        <input type="text" class="fill-input" placeholder="Type your answer" data-correct="${q.answer}">
        <button class="submit-fill">Submit</button>
        <p class="result-msg"></p>
      `;
      fillDiv.appendChild(card);
    });

    // ------------------------------
    // ✅ MCQ Logic
    // ------------------------------
    document.querySelectorAll(".option-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const correctAns = e.target.dataset.correct.trim();
        const selected = e.target.dataset.answer.trim();
        const msg = e.target.closest(".quizCard").querySelector(".result-msg");
        e.target.closest(".quizCard")
          .querySelectorAll(".option-btn")
          .forEach((b) => (b.disabled = true));
        answered++;
        if (selected === correctAns) {
          correct++;
          msg.textContent = "✅ Correct!";
          msg.style.color = "#28a745";
        } else {
          msg.textContent = `❌ Wrong! Correct: ${correctAns}`;
          msg.style.color = "#dc3545";
        }
        updateScore();
      });
    });

    // ------------------------------
    // ✅ Fill Logic
    // ------------------------------
    document.querySelectorAll(".submit-fill").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const input = e.target.previousElementSibling;
        const correctAns = input.dataset.correct.trim().toLowerCase();
        const entered = input.value.trim().toLowerCase();
        const msg = e.target.closest(".quizCard").querySelector(".result-msg");
        input.disabled = true;
        btn.disabled = true;
        answered++;
        if (entered === correctAns) {
          correct++;
          msg.textContent = "✅ Correct!";
          msg.style.color = "#28a745";
        } else {
          msg.textContent = `❌ Wrong! Correct: ${correctAns}`;
          msg.style.color = "#dc3545";
        }
        updateScore();
      });
    });

    // ------------------------------
    // 🧮 Update Score
    // ------------------------------
    function updateScore() {
      document.getElementById("scoreBoard").textContent = `Progress: ${answered}/${total} | ✅ Correct: ${correct}`;
      if (answered === total) {
        setTimeout(() => {
          alert(`🎉 Quiz Complete!\n✅ Correct: ${correct}/${total}\nAccuracy: ${Math.round((correct / total) * 100)}%`);
        }, 400);
      }
    }
  }

  // ==========================================================
  // 🕓 Load Quiz History
  // ==========================================================
  async function loadHistory() {
    try {
      const res = await fetch(`${apiBase}/history`);
      const data = await res.json();
      historyBody.innerHTML = data
        .map(
          (q) => `
        <tr>
          <td>${q.title}</td>
          <td><a href="${q.url}" target="_blank">View Article</a></td>
          <td>${q.created_at}</td>
        </tr>`
        )
        .join("");
    } catch (err) {
      historyBody.innerHTML = `<tr><td colspan="3" style="color:red;">⚠️ Failed to load history.</td></tr>`;
    }
  }

  // ==========================================================
  // 🗑️ Clear Quiz History
  // ==========================================================
  clearBtn.addEventListener("click", async () => {
    if (confirm("🧹 Are you sure you want to clear all quiz history?")) {
      try {
        const res = await fetch(`${apiBase}/history/clear`, {
          method: "DELETE",
        });
        if (res.ok) {
          alert("🧹 History cleared!");
          historyBody.innerHTML = "";
        } else {
          alert("⚠️ Failed to clear history.");
        }
      } catch (err) {
        alert("⚠️ Unable to reach the server.");
      }
    }
  });

  // Load past quizzes initially
  loadHistory();
});
