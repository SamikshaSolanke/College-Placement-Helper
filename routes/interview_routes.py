from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import json
from google.generativeai.types import GenerationConfig
from models import InterviewResult
from extensions import db
from services.gemini_service import model, interview_grade_schema

interview = Blueprint('interview', __name__)

@interview.route("/interview")
@login_required
def interview_page():
    """Renders the mock interview page."""
    subject = request.args.get('subject')
    level = request.args.get('level')
    
    if not subject or not level:
        flash('Subject and level are required to start an interview.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    return render_template("interview.html", subject=subject, level=level)

@interview.route("/api/get-interview-question", methods=["POST"])
@login_required
def api_get_interview_question():
    """API endpoint to get a single interview question from Gemini."""
    if not model:
        return jsonify({"error": "Model not initialized"}), 500
        
    try:
        data = request.json
        prompt = f"""
        You are an expert interviewer. 
        Generate one concise, open-ended interview question for a candidate 
        at a "{data.get('level')}" level on the topic of "{data.get('subject')}".
        Do not add any preamble, just return the question text.
        """
        response = model.generate_content(prompt)
        return jsonify({"question": response.text})
        
    except Exception as e:
        print(f"Error in api_get_interview_question: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@interview.route("/api/grade-answer", methods=["POST"])
@login_required
def api_grade_answer():
    """API endpoint to grade a user's interview answer."""
    if not model:
        return jsonify({"error": "Model not initialized"}), 500
        
    try:
        data = request.json
        
        prompt = f"""
        You are an expert tech interviewer. A candidate was asked the following question
        on the topic of "{data.get('subject')}" at a "{data.get('level')}" level:
        "{data.get('question')}"

        The candidate provided this answer:
        "{data.get('user_answer')}"

        Please grade their answer. Provide a score from 1 (poor) to 5 (excellent)
        and concise, constructive feedback on their answer's accuracy and completeness.
        Adhere *strictly* to the JSON schema.
        """
        
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=interview_grade_schema
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        grade_data = json.loads(response.text) # { "score": 4, "feedback": "..." }
        
        # Save to database
        new_interview = InterviewResult(
            subject=data.get('subject'),
            level=data.get('level'),
            question_text=data.get('question'),
            user_answer=data.get('user_answer'),
            ai_feedback=grade_data.get('feedback'),
            ai_score=grade_data.get('score'),
            user_id=current_user.id
        )
        db.session.add(new_interview)
        db.session.commit()
        
        return jsonify(grade_data)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@interview.route("/api/grade-video", methods=["POST"])
@login_required
def api_grade_video():
    """API endpoint to grade a video interview answer."""
    import os
    import time
    from werkzeug.utils import secure_filename
    from services.gemini_service import analyze_video_interview
    
    if not model:
        return jsonify({"error": "Model not initialized"}), 500
        
    try:
        # 1. Check for video file
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
            
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # 2. Save to temp file
        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = secure_filename(f"user_{current_user.id}_{int(time.time())}.webm")
        temp_path = os.path.join(temp_dir, filename)
        video_file.save(temp_path)
        
        # 3. Get metadata from form
        subject = request.form.get('subject')
        level = request.form.get('level')
        question = request.form.get('question')
        
        # 4. Call Gemini Service
        result_data = analyze_video_interview(temp_path, question, subject, level)
        
        # 5. Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
            
        # 6. Save to DB
        # We combine technical and body language feedback
        combined_feedback = f"**Technical Feedback:**\n{result_data.get('technical_feedback')}\n\n**Body Language Feedback:**\n{result_data.get('body_language_feedback')}"
        
        new_interview = InterviewResult(
            subject=subject,
            level=level,
            question_text=question,
            user_answer="[Video Submission]", 
            ai_feedback=combined_feedback,
            ai_score=result_data.get('score'),
            user_id=current_user.id
        )
        db.session.add(new_interview)
        db.session.commit()
        
        return jsonify({
            "score": result_data.get('score'),
            "feedback": combined_feedback
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

