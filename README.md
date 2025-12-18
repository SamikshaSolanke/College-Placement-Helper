# College-Placement-Helper

Gemini api code use this in terminal 
export GOOGLE_API_KEY='YOUR_KEY'

SQL DATABASE code

/* 1. Delete the old database and user (if they exist) to start fresh */
DROP DATABASE IF EXISTS quiz_app_db;
DROP USER IF EXISTS 'quiz_user'@'localhost';

/* 2. Create your new, empty database */
CREATE DATABASE quiz_app_db;

/* 3. Create a user that your Flask app will use to log in */
ALTER USER 'quiz_user'@'localhost' IDENTIFIED BY 'swaraj123';

/* 4. Give your new user full permissions on your new database */
GRANT ALL PRIVILEGES ON quiz_app_db.* TO 'quiz_user'@'localhost';

/* 5. Apply all the changes */
FLUSH PRIVILEGES;

CHANGE THE DATABASE PASSWORD IN APP.PY