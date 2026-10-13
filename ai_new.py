
import ollama
import json


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a strict and helpful technical hiring manager.

Analyze the resume for the specific job role provided.

Job role: {user_goal}

Resume:
{resume_text}

Instructions:
1. List skills relevant to the job role that are actually supported by the resume.
2. Identify important skills required for the role that are missing from the resume.
3. Create a learning roadmap only for those missing skills.
4. Create 5 interview questions relevant to the job role and resume.
5. Do not invent experience, qualifications, or achievements.
6. Keep suggestions practical and specific.
7. Return only valid JSON matching this structure:

{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}
"""

    try:
        response = ollama.chat(
            model="llama3.2:1b",
            format="json",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a technical hiring manager. "
                        "Analyze resumes carefully and return valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={"temperature": 0.1}
        )

        content = response["message"]["content"].strip()
        result = json.loads(content)

        # Check that the required fields exist.
        required_fields = [
            "skills",
            "missing_skills",
            "roadmap",
            "interview_questions"
        ]

        for field in required_fields:
            if field not in result:
                result[field] = []

        return result

    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }
