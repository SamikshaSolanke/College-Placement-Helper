# College Placement Helper - Project Explanation & Interview Guide

This document provides a comprehensive overview of the **College Placement Helper** project. It is designed to help you answer technical and non-technical interview questions about the application.

---

## 1. Introduction

**Project Name:** College Placement Helper  
**Tagline:** Your intelligent, AI-powered companion for mastering technical interviews and placement exams.

### **What is it?**
College Placement Helper is a web application designed to assist students in preparing for campus placements. It acts as a centralized platform offering personalized practice resources for technical subjects (like Operating Systems, DBMS, Computer Networks) and behavioral/technical interview simulations.

### **Core Problem Solved**
Students often struggle with:
*   Finding relevant and updated practice questions.
*   Lack of immediate feedback on their answers.
*   Not knowing *why* an answer is wrong.
*   The high cost or unavailability of personal tutors for mock interviews.

### **The Solution**
This application leverages **Generative AI (Google Gemini)** to:
*   Create distinct, non-repetitive quizzes on demand.
*   Simulate real-world technical interviews with instant AI grading and feedback.
*   Provide detailed explanations for incorrect answers to facilitate learning.
*   Generate one-click study guides for quick revision.

---

## 2. User Guide (How to Use)

The application follows a simple, user-friendly workflow:

1.  **Registration/Login**:
    *   Users sign up or log in securely to access the dashboard.
    *   This ensures their progress and scores are saved personally.

2.  **The Dashboard**:
    *   The central hub where users can see their statistics (Average Score, Weakest Subject).
    *   From here, they can choose to **"Take a Test"** or **"Start Mock Interview"**.

3.  **Taking a Quiz**:
    *   User selects a **Subject** (e.g., OS) and **Difficulty** (e.g., Beginner).
    *   The AI generates a unique set of 10 Multiple Choice Questions (MCQs).
    *   User answers them and submits the test.
    *   **Result Page**: The user sees their score instantly. They can review every question, see what they got wrong, and click **"Why was I wrong?"** to get an AI-generated explanation.

4.  **Mock Interview**:
    *   User selects a topic for the interview.
    *   The AI acts as an interviewer, creating an open-ended question.
    *   The user types their detailed answer.
    *   The AI grades the answer on a scale of 1-5 and provides constructive feedback on how to improve.

5.  **Study Guides**:
    *   On the dashboard, the user can request a study guide for a specific topic, which is generated instantly by the AI.

---

## 3. Data Flow

Understanding how data moves through the system is crucial for technical questions.

### **A. Quiz Generation & Submission Flow**
1.  **Request**: User clicks "Start Test" -> Frontend sends GET request with `subject` and `level`.
2.  **Generation**:
    *   The backend (Flask) calls the `Gemini Service`.
    *   A structured prompt is sent to the Gemini API requesting 10 MCQs in a strict JSON format.
    *   Gemini returns the JSON data.
3.  **Session Storage**: The questions and correct answers are stored in the user's **Session** (server-side storage) to prevent cheating and avoid re-fetching.
4.  **Rendering**: The frontend renders the questions.
5.  **Submission**: User submits the form -> POST request to `/submit_test`.
6.  **Grading**: The backend compares user answers against the session data.
7.  **Persistence**: The final score, full quiz data, and user answers are saved to the **MySQL Database** (`QuizResult` table).
8.  **Review**: The result page fetches this data from the DB to show the report card.

### **B. Mock Interview Flow**
1.  **Question Generation**: Frontend calls `/api/get-interview-question` -> Backend prompts Gemini for a single open-ended question -> Returns to Frontend.
2.  **Answering**: User types their answer and clicks Submit.
3.  **Grading (AI-in-the-loop)**:
    *   Frontend sends the `question` and `user_answer` to `/api/grade-answer`.
    *   Backend constructs a prompt: *"You are an interviewer. Question was X, Answer was Y. Grade this."*
    *   Gemini returns a JSON response with a Score (1-5) and Feedback text.
4.  **Storage**: The result is saved to the `InterviewResult` table in the database.
5.  **Feedback**: The feedback is displayed instantly to the user on the screen.

---

## 4. Tech Stack

### **Backend**
*   **Language**: **Python 3.x**
*   **Framework**: **Flask** (Micro web framework)
    *   *Why Flask?* It is lightweight, easy to set up for small-to-medium projects, and offers great flexibility for integrating AI services.
    *   **Architecture**: Modular "Blueprints" (separating user auth, main logic, and quiz logic).
*   **Authentication**: **Flask-Login** (Manages user sessions and cookies).

### **Database**
*   **Database System**: **MySQL** (Relational Database).
*   **ORM (Object-Relational Mapper)**: **SQLAlchemy**.
    *   *Why SQLAlchemy?* It allows us to work with Python classes (`User`, `QuizResult`) instead of writing raw SQL queries, making the code cleaner and safer (prevents SQL injection).

### **AI & Third-Party APIs**
*   **AI Model**: **Google Gemini (1.5 Flash / 2.5)** via `google-generativeai` SDK.
    *   *Role*: Generates content (questions, study guides) and acts as the evaluator (grading interviews).
*   **Environment Management**: `python-dotenv` (Used to securely store API keys).

### **Frontend**
*   **Templating Engine**: **Jinja2** (Built into Flask). allow us to inject Python variables (like questions or scores) directly into HTML.
*   **Styling**: **CSS3** (Custom responsive design).
*   **Interactivity**: **Vanilla JavaScript** (ES6).
    *   Uses the **Fetch API** for asynchronous calls (AJAX) to the backend (e.g., getting an explanation without reloading the page).

---

## 5. Key Technical Concepts & "Why" Questions

**Q: Why did you use `session` to store quiz questions?**
**A:** Storing the correct answers in the user's session (server-side) ensures security. If we sent the correct answers to the frontend JavaScript, a user could easily inspect the code and cheat.

**Q: How do you ensure the AI gives structured data?**
**A:** We use **Prompt Engineering** with strict instructions (e.g., "Return only JSON"). For critical components, we can also use Gemini's `response_schema` feature to enforce a specific JSON structure, ensuring our code doesn't crash while parsing.

**Q: What is the benefit of Blueprints in Flask?**
**A:** Blueprints allow us to organize our application into distinct components (`auth`, `quiz`, `interview`). This makes the code maintainable, readable, and scalable. If we put everything in one `app.py`, it would be a messy "spaghetti code".

**Q: How is the database connected?**
**A:** We use `db.init_app(app)` within a factory function (`create_app`). This is a best practice in Flask called the **Application Factory Pattern**, which helps with circular imports and makes testing easier.

---

## 6. Codebase Structure (Directory Map)

*   `app.py`: Entry point. Creates the app and initializes the DB.
*   `models.py`: Defines the Database Schema (Tables for Users, Results).
*   `extensions.py`: Sets up shared tools like the Database (`db`) and Login Manager.
*   `services/`:
    *   `gemini_service.py`: Contains all the logic for communicating with Google's AI. Segregating this logic keeps the routes clean.
*   `routes/`:
    *   `auth_routes.py`: Login, Signup, Logout.
    *   `quiz_routes.py`: Logic for taking tests and viewing results.
    *   `interview_routes.py`: Logic for mock interviews.
*   `templates/`: HTML files for each page (`dashboard.html`, `test.html`, `result.html`).

---

## 7. Future Improvements
*(Mention these to show you have a vision for the project)*

1.  **Resume Scanner**: Adding feature to upload a PDF resume and have the AI grade it against a job description.
2.  **Voice Interaction**: Using Speech-to-Text so users can speak their interview answers instead of typing.
3.  **Company-Specific Modes**: Specialized question banks for companies like TCS, Infosys, or Amazon.

---

## 8. New Feature: Video Mock Interview (Multimodal AI)

**Overview**
We have recently upgraded the mock interview system to support **Video Responses**. This allows the AI to analyze not just the *content* of the answer, but also the candidate's **body language**.

**How it Works (Technical Flow)**
1.  **Frontend**: Uses the **MediaRecorder API** to capture video execution in the browser.
2.  **Upload**: The video (WebM format) is sent via `FormData` to the backend.
3.  **Analysis**:
    *   The backend uploads the video to **Gemini 1.5 Flash**.
    *   A multimodal prompt is sent: *"Watch this video, listen to the answer, and grade both technical accuracy and non-verbal cues (confidence, eye contact)."*
4.  **Feedback**: The user receives a combined report covering their technical knowledge and their presentation skills.

--- 
*This document covers the functional, architectural, and technical aspects of the College Placement Helper project.*
