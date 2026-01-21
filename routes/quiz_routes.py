from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
import json
from models import QuizResult
from extensions import db
from services.gemini_service import generate_quiz_from_gemini, model

quiz = Blueprint('quiz', __name__)

@quiz.route("/test")
@login_required
def test():
    """
    Generates a new quiz (from any subject) and renders the test page.
    """
    # 1. Get subject and level from URL (e.g., /test?subject=OS&level=Beginner)
    subject = request.args.get('subject')
    level = request.args.get('level')
    
    if not subject or not level:
        flash('Subject and level are required to start a test.', 'danger')
        return redirect(url_for('main.dashboard'))

    # 2. Generate new questions from Gemini
    questions = generate_quiz_from_gemini(subject, level, num_questions=10)
    
    # 3. Store the quiz (questions and answers) in the user's session
    session['current_quiz'] = questions
    session['quiz_subject'] = subject
    session['quiz_level'] = level
    
    # 4. Pass the questions to your existing 'test.html' template
    return render_template(
        "test.html", 
        questions=questions, 
        subject=subject, 
        level=level,
        total_questions=len(questions)
    )

@quiz.route("/submit_test", methods=["POST"])
@login_required
def submit_test():
    """
    Grades the submitted quiz using the answers stored in the session.
    """
    user_answers_from_form = request.form
    questions = session.get('current_quiz')
    subject = session.get('quiz_subject', 'Unknown')
    level = session.get('quiz_level', 'Unknown')
    
    if not questions:
        flash('Quiz session expired or not found. Please try again.', 'danger')
        return redirect(url_for('main.dashboard'))

    score = 0
    total = len(questions)
    user_answers_for_db = {} 
    
    for question in questions:
        question_key = f"q_{question['id']}"
        user_answer_letter = user_answers_from_form.get(question_key)
        correct_answer_letter = question['correct_answer_letter']
        
        user_answer_text = "No Answer"
        if user_answer_letter:
            option_key = f"option_{user_answer_letter.lower()}"
            user_answer_text = question.get(option_key, "Invalid Option")

        user_answers_for_db[question['question']] = user_answer_text
        
        if user_answer_letter == correct_answer_letter:
            score += 1

    try:
        new_result = QuizResult(
            subject=subject,
            level=level,
            score=score,
            total=total,
            user_id=current_user.id,
            quiz_data_json=json.dumps(questions), 
            user_answers_json=json.dumps(user_answers_for_db)
        )
        db.session.add(new_result)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving your result: {e}', 'danger')

    session.pop('current_quiz', None)
    session.pop('quiz_subject', None)
    session.pop('quiz_level', None)
    
    return redirect(url_for('quiz.result', result_id=new_result.id))


@quiz.route("/result/<int:result_id>")
@login_required
def result(result_id):
    """
    Shows the result for a specific test.
    This also powers the "Review Your Mistakes" page.
    """
    result = QuizResult.query.get_or_404(result_id)
    
    if result.user_id != current_user.id:
        flash('You are not authorized to view this result.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    questions = json.loads(result.quiz_data_json)
    user_answers = json.loads(result.user_answers_json)
    
    return render_template(
        "result.html",
        subject=result.subject,
        level=result.level,
        score=result.score,
        total=result.total,
        questions=questions,
        user_answers=user_answers
    )

@quiz.route("/api/explain", methods=["POST"])
@login_required
def api_explain():
    """API endpoint for the 'Why was I wrong?' feature."""
    if not model:
        return jsonify({"error": "Model not initialized"}), 500
        
    try:
        data = request.json
        prompt = f"""
        You are a helpful tutor. My student was answering a quiz question.
        The question was: "{data.get('question')}"
        They answered: "{data.get('user_answer')}"
        The correct answer is: "{data.get('correct_answer')}"

        Please provide a concise, friendly explanation (2-3 sentences)
        about why their answer was incorrect and why the correct answer is correct.
        """
        response = model.generate_content(prompt)
        return jsonify({"explanation": response.text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz.route("/api/study-guide", methods=["POST"])
@login_required
def api_study_guide():
    """API endpoint to generate a study guide."""
    if not model:
        return jsonify({"error": "Model not initialized"}), 500
        
    try:
        data = request.json
        subject = data.get('subject')
        level = data.get('level', 'Intermediate') # Default to Intermediate if not provided

        prompt = f"""
        You are an expert tutor. Generate a concise study guide
        for the topic "{subject}" at a "{level}" level.
        The guide should be able to help a student who has never taken this course and be able to study for this subject with the hlp of study guide provided by you.
        Suggest key topics and subtopics to cover in the study guide. Also, Suggest youtube videos and website links to cover in the study guide.
        """
        response = model.generate_content(prompt)
        return jsonify({"guide": response.text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
