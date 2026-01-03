from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, case
from models import User, QuizResult, InterviewResult
from extensions import db
from services.gemini_service import model

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/dashboard")
@login_required
def dashboard():
    """Renders the main dashboard page with a personalized AI tutor tip."""
    
    ai_tutor_tip = "Welcome! Choose a subject to get started." # Default tip
    
    try:
        # Get all quiz results to find weakest subject
        results = current_user.quiz_results.all()
        
        if results:
            subject_scores = {}
            subject_counts = {}
            
            for r in results:
                if r.subject not in subject_scores:
                    subject_scores[r.subject] = 0
                    subject_counts[r.subject] = 0
                # Ensure r.total is not zero to avoid DivisionZeroError
                if r.total > 0:
                    subject_scores[r.subject] += (r.score / r.total)
                    subject_counts[r.subject] += 1
            
            # Calculate average for each subject
            subject_averages = {}
            for subject, total_score in subject_scores.items():
                if subject_counts[subject] > 0:
                    subject_averages[subject] = (total_score / subject_counts[subject]) * 100
            
            # Find weakest subject
            if subject_averages:
                weakest_subject = min(subject_averages, key=subject_averages.get)
                weakest_score = subject_averages[weakest_subject]
                
                if weakest_score < 70: # Only give tip if score is below 70%
                    if model:
                        # Call Gemini for a personalized tip
                        prompt = f"""
                        You are a friendly, encouraging tutor. My student, {current_user.display_name or 'there'}, is struggling with '{weakest_subject}' (average score: {weakest_score:.0f}%).
                        Give them one short (2-3 sentence) piece of encouragement and suggest *one* specific action from this list to improve: ['Take a Beginner quiz', 'Get a Study Guide', 'Try a Mock Interview'].
                        Be friendly and concise.
                        """
                        response = model.generate_content(prompt)
                        ai_tutor_tip = response.text
                    else:
                         ai_tutor_tip = "Keep practicing to improve your scores!"

    except Exception as e:
        print(f"Error generating AI tutor tip: {e}")
        ai_tutor_tip = "Ready to learn? Pick a subject and start a quiz!"

    return render_template("dashboard.html", user=current_user, ai_tutor_tip=ai_tutor_tip)


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Renders the profile page and handles updates."""
    
    if request.method == "POST":
        # Handle profile update logic (e.g., from an edit form)
        display_name = request.form.get('displayName') 
        current_user.display_name = display_name
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    # --- GET Request: Prepare all data for the profile page ---
    
    display_name = current_user.display_name
    if not display_name:
        display_name = current_user.email.split('@')[0]
    user_info_tuple = (display_name, current_user.email)
    
    all_quiz_results = current_user.quiz_results.order_by(QuizResult.timestamp.desc()).all()
    
    test_history_list = []
    for r in all_quiz_results:
        test_history_list.append((
            r.subject,
            r.level,
            r.score,
            r.total,
            r.timestamp,
            r.id  # Pass the ID for the "Review" link
        ))
        
    total_tests = len(all_quiz_results)
    total_score = sum(r.score for r in all_quiz_results)
    total_questions = sum(r.total for r in all_quiz_results)
    
    avg_score_percent = 0
    if total_questions > 0:
        avg_score_percent = (total_score / total_questions) * 100
        
    best_score_percent = 0
    if total_tests > 0:
        # Use a generator expression to avoid errors on empty list
        best_score_percent = max(((r.score / r.total) * 100) for r in all_quiz_results if r.total > 0)
        
    subjects_attempted = len(set(r.subject for r in all_quiz_results))

    stats_overview = {
        "total_tests": total_tests,
        "avg_score": round(avg_score_percent, 1),
        "best_score": round(best_score_percent, 1),
        "subjects_attempted": subjects_attempted
    }

    subject_stats_query = db.session.query(
        QuizResult.subject,
        func.count(QuizResult.id).label('test_count'),
        func.avg(case((QuizResult.total > 0, (QuizResult.score / QuizResult.total) * 100), else_=0)).label('avg_score'),
        func.max(case((QuizResult.total > 0, (QuizResult.score / QuizResult.total) * 100), else_=0)).label('best_score')
    ).filter_by(user_id=current_user.id).group_by(QuizResult.subject).all()

    subject_stats_list = []
    for stat in subject_stats_query:
        subject_stats_list.append({
            "name": stat.subject,
            "test_count": stat.test_count,
            "avg_score_percent": round(stat.avg_score, 1),
            "best_score_percent": round(stat.best_score, 1)
        })

    # 4. Get Interview History
    interview_history = current_user.interview_results.order_by(InterviewResult.timestamp.desc()).all()

    # 5. Pass all data to the template
    return render_template(
        "profile.html", 
        user_info=user_info_tuple,           
        test_history=test_history_list,      
        stats=stats_overview,                
        subject_stats=subject_stats_list,    
        interview_history=interview_history
    )


@main.route("/explore")
@login_required
def explore():
    """Renders the 'Explore' page for custom quizzes."""
    return render_template("explore.html")


@main.route("/leaderboard")
@login_required
def leaderboard():
    """Renders the global leaderboard page."""
    
    avg_score_calc = func.avg(
        case(
            (QuizResult.total > 0, (QuizResult.score / QuizResult.total) * 100),
            else_=0
        )
    )

    display_name_with_fallback = func.coalesce(User.display_name, User.email) 

    leaderboard_data = db.session.query(
        display_name_with_fallback.label('display_name'), # Use the new fallback
        func.count(QuizResult.id).label('test_count'),
        avg_score_calc.label('avg_score')
    ).join(
        QuizResult, User.id == QuizResult.user_id
    ).group_by(
        User.id
    ).order_by(
        avg_score_calc.desc()
    ).limit(20).all()

    return render_template("leaderboard.html", leaderboard_data=leaderboard_data)
