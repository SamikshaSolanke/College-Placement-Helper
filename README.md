# 🎓 College Placement Helper

> **Your intelligent, AI-powered companion for mastering technical interviews and placement exams.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.2+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-000000?style=for-the-badge&logo=mysql&logoColor=white)

---

## 🚀 The Problem & Solution

### The Problem
Preparing for college placements is often a scattered and overwhelming process. Students struggle to find relevant, updated practice questions for specific technical subjects (like OS, DBMS, CN). More importantly, they lack **immediate, personalized feedback** on mock interviews, leaving them blindly guessing about their performance until it's too late.

### The Solution
**College Placement Helper** bridges this gap by creating an intelligent, centralized platform. We leverage **Google's Gemini AI** to generate infinite, customized practice resources. Whether it's a deep-dive quiz into Operating Systems or a behavioral mock interview, our platform provides **instant grading, detailed explanations, and actionable improvement tips**, effectively serving as a personal 24/7 placement tutor.

---

## ✨ Key Features to Highlight

| Feature | Description |
| :--- | :--- |
| **🤖 AI-Powered Quizzes** | Generates infinite, non-repetitive MCQs based on **Subject** and **Difficulty** (Beginner, Intermediate, Advanced). |
| **🎤 Mock Interviews** | Simulates real technical interviews. Users type answers to open-ended questions, and the AI provides a **Score (1-5)** and **Constructive Feedback**. |
| **💡 "Why Was I Wrong?"** | Instant, context-aware explanations for every incorrect quiz answer to help clear concepts immediately. |
| **📊 Smart Dashboard** | Tracks performance over time. Automatically identifies your **Weakest Subject** and suggests specific actions (e.g., "Take a Study Guide"). |
| **📚 Instant Study Guides** | One-click generation of concise, bullet-point study notes for any technical topic. |
| **🏆 Leaderboard** | Gamified global ranking system to track your standing against peers. |

---

## 🛠️ Methodology

The application is built on a modular **Flask** architecture, utilizing a **Generative AI integration pattern**:

1.  **Dynamic Prompt Engineering:** When a user requests a quiz or interview, the backend constructs highly specific prompts enforcing **JSON schemas**. This ensures the AI returns structured data (questions, options, correct answers) that the app can reliably parse and render.
2.  **State Management:** User sessions are handled securely to track quiz progress. Results are persisted in a **MySQL relational database**, allowing for historical tracking and trend analysis.
3.  **Feedback Loop:** The system doesn't just grade; it educates. Every interaction feeds into the user's profile, updating their "Average Score" and refining the personalized suggestions on the dashboard.

---

## 💻 Tech Stack

### Backend
*   **Language:** Python 3.x
*   **Framework:** Flask (Modular Blueprints Architecture)
*   **Database:** MySQL (via SQLAlchemy ORM)
*   **Authentication:** Flask-Login & Werkzeug Security

### AI & Integration
*   **Model:** Google Gemini (1.5 Flash / 2.5 Preview)
*   **Library:** `google-generativeai` SDK
*   **Environment:** managed via `python-dotenv`

### Frontend
*   **Structure:** HTML5 (Jinja2 Templating)
*   **Styling:** CSS3 (Responsive Design)
*   **Interactivity:** Vanilla JavaScript (Fetch API for async AI calls)

---

## 🗺️ Future Roadmap

*   [ ] **📄 Resume AI Scanner:** automated grading of user resumes against specific job descriptions.
*   [ ] **🏢 Company Modes:** Preset question banks tailored for specific companies (e.g., "Amazon Mode", "TCS Mode").
*   [ ] **🗣️ Voice Interview:** Implementing Speech-to-Text to allow users to speak their interview answers instead of typing.

---

<p align="center">
  <i>Built with ❤️ for Students, by Students.</i>
</p>