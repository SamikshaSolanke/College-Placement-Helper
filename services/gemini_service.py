import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.generativeai.protos import Schema, Type
import json
import os

MODEL_NAME = "gemini-2.5-flash-lite" 
api_key = os.getenv("GOOGLE_API_KEY")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=MODEL_NAME)
    print("Gemini model initialized successfully.")
except Exception as e:
    print(f"Error initializing model: {e}")
    model = None

# --- Define Quiz JSON structure ---
quiz_schema = Schema(
    type=Type.OBJECT,
    properties={
        'questions': Schema(
            type=Type.ARRAY,
            items=Schema(
                type=Type.OBJECT,
                properties={
                    'id': Schema(
                        type=Type.INTEGER,
                        description="A unique ID for the question, starting from 1."
                    ),
                    'question': Schema(
                        type=Type.STRING,
                        description="The full text of the quiz question."
                    ),
                    'option_a': Schema(
                        type=Type.STRING,
                        description="The text for answer option A."
                    ),
                    'option_b': Schema(
                        type=Type.STRING,
                        description="The text for answer option B."
                    ),
                    'option_c': Schema(
                        type=Type.STRING,
                        description="The text for answer option C."
                    ),
                    'option_d': Schema(
                        type=Type.STRING,
                        description="The text for answer option D."
                    ),
                    'correct_answer_letter': Schema(
                        type=Type.STRING,
                        description="The correct answer *letter* (e.g., 'A', 'B', 'C', or 'D')."
                    )
                },
                required=['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer_letter']
            )
        )
    },
    required=['questions']
)

# --- Define Interview Grade JSON structure ---
interview_grade_schema = Schema(
    type=Type.OBJECT,
    properties={
        'score': Schema(
            type=Type.INTEGER,
            description="A score from 1 (poor) to 5 (excellent)."
        ),
        'feedback': Schema(
            type=Type.STRING,
            description="Concise, constructive feedback on the user's answer, explaining what was right and wrong."
        )
    },
    required=['score', 'feedback']
)


def generate_quiz_from_gemini(subject, level, num_questions=10):
    """
    Calls the Gemini API to generate quiz questions and returns them
    as a Python dictionary (parsed from the JSON response).
    """
    if not model:
        raise Exception("Gemini model is not initialized.")
        
    try:
        prompt = f"""
        You are an expert quiz creator.
        Generate a {num_questions}-question multiple-choice quiz on the topic of "{subject}"
        at a "{level}" difficulty level.

        For each question, provide:
        1. "id": A unique integer ID for the question (e.g., 1, 2, 3...).
        2. "question": The full text of the question.
        3. "option_a": The text for option A.
        4. "option_b": The text for option B.
        5. "option_c": The text for option C.
        6. "option_d": The text for option D.
        7. "correct_answer_letter": The *letter* of the correct answer (e.g., 'A', 'B', 'C', or 'D').

        Do NOT include 'A)', 'B)', etc. prefixes in the option_a, option_b... strings.
        Adhere *strictly* to the JSON schema provided.
        """

        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=quiz_schema
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        quiz_data = json.loads(response.text)
        
        if 'questions' not in quiz_data or not quiz_data['questions']:
            raise Exception("AI returned empty or invalid quiz data.")
            
        return quiz_data["questions"] # Return just the list of questions

    except Exception as e:
        print(f"Error generating quiz from Gemini: {e}")
        return [
            {
                "id": 1,
                "question": f"Error: Could not generate quiz. The AI model may be temporarily unavailable or rate limits exceeded. Please try again later. (Error: {str(e)})",
                "option_a": "Sorry, please try again.", "option_b": "Option B",
                "option_c": "Option C", "option_d": "Option D",
                "correct_answer_letter": "A"
            }
        ]

# --- Define Video Interview Grade JSON structure ---
video_interview_grade_schema = Schema(
    type=Type.OBJECT,
    properties={
        'score': Schema(
            type=Type.INTEGER,
            description="A score from 1 (poor) to 5 (excellent) based on technical accuracy."
        ),
        'technical_feedback': Schema(
            type=Type.STRING,
            description="Feedback on the technical content of the answer."
        ),
        'body_language_feedback': Schema(
            type=Type.STRING,
            description="Feedback on non-verbal cues (eye contact, confidence, tone, pacing)."
        )
    },
    required=['score', 'technical_feedback', 'body_language_feedback']
)

def analyze_video_interview(video_path, question_text, subject, level):
    """
    Uploads a video to Gemini and gets technical + body language feedback.
    """
    if not model:
        raise Exception("Gemini model is not initialized.")

    import time
    
    try:
        # 1. Upload the video
        print(f"Uploading video: {video_path}")
        video_file = genai.upload_file(path=video_path)
        print(f"Completed upload: {video_file.uri}")

        # 2. Wait for processing
        while video_file.state.name == "PROCESSING":
            print("Processing video...")
            time.sleep(1)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise Exception("Video processing failed by Gemini.")

        # 3. Generate Content
        prompt = f"""
        You are an expert interviewer. 
        A candidate is answering the following interview question on "{subject}" (Level: {level}):
        "{question_text}"

        Please analyze the attached video response.
        1. Listen to their answer and evaluate its technical accuracy.
        2. Watch their body language and evaluate their confidence, eye contact, and delivery.

        Provide the output in strict JSON format with:
        - score (1-5)
        - technical_feedback (string)
        - body_language_feedback (string)
        """

        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=video_interview_grade_schema
        )

        response = model.generate_content(
            [video_file, prompt],
            generation_config=generation_config
        )
        
        # Clean up (optional but recommended to delete file from cloud if possible, 
        # though genai.delete_file(name) exists, we might want to keep it or delete it later. 
        # For now, let's leave it or delete it.)
        try:
            genai.delete_file(video_file.name)
        except:
            pass

        return json.loads(response.text)

    except Exception as e:
        print(f"Error analyzing video: {e}")
        raise e

