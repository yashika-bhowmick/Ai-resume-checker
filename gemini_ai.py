import time
import os
import json
from google import genai
from google.genai import types


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a strict and helpful technical hiring manager.

Analyze the resume for the specific job role provided.

Job role: {user_goal}

Resume:
{resume_text}

Instructions:
1. List skills relevant to the job role supported by the resume.
2. Identify important skills required for the role that are missing.
3. Create a learning roadmap only for missing skills.
4. Create 5 interview questions relevant to the role and resume.
5. Do not invent experience, qualifications, or achievements.
6. Keep suggestions practical and specific.
7. Return JSON with these four fields:
skills, missing_skills, roadmap, interview_questions.
"""

    try:
        client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"]
        )
        start_time = time.time()
        
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "skills": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "missing_skills": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "roadmap": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "interview_questions": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        }
                    },
                    "required": [
                        "skills",
                        "missing_skills",
                        "roadmap",
                        "interview_questions"
                    ]
                },
                temperature=0.1
            )
        )
        print("Gemini API time:", round(time.time() - start_time, 2), "seconds")

        result = json.loads(response.text)

        return result

    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }
