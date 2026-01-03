import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.generativeai.protos import Schema, Type
import json
import os

# --- Configuration ---
# MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
MODEL_NAME = "gemini-1.5-flash" 

MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

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
