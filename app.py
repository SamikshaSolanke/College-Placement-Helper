from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from extensions import db, login_manager
from config import Config
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from routes.auth_routes import auth
    from routes.main_routes import main
    from routes.quiz_routes import quiz
    from routes.interview_routes import interview

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(quiz)
    app.register_blueprint(interview)

    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Create all database tables if they don't exist
        db.create_all()
    app.run(host="0.0.0.0", port=5005, debug=True)