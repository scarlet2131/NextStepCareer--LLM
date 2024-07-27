# app/services/resume_parser.py

import openai
import os
import json
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI

from app.config import settings

# Initialize OpenAI API key
openai_api_key = settings.OPENAI_API_KEY
client = OpenAI(api_key=openai_api_key)


def extract_text_from_pdf(file_path):
    text = ''
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text


def generate_prompt(text):
    prompt = f"""
            Extract the skills and experiences from the following resume text:

            {text}

            Skills should be listed clearly and accurately.
            Experiences should include job titles, companies, and duration.

            Provide the response in the following JSON format:
            {{
                "skills": ["skill1", "skill2", ...],
                "experiences": ["experience1", "experience2", ...]
            }}
            """
    return prompt


def get_response_with_chatgpt(user_input: str) -> dict:
    try:
        prompt_text = generate_prompt(user_input)
        print("Prompt Text:", prompt_text)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant designed to extract skills and experiences from resumes."},
                {"role": "user", "content": prompt_text}
            ]
        )

        response_text = response.choices[0].message.content.strip()
        print("Response Text:", response_text)

        response_data = json.loads(response_text)  # Parse the response as JSON
        return response_data
    except Exception as e:
        print("Error:", e)
        return {}


def parse_resume(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif extension == '.docx':
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError('Unsupported file type')

    response = get_response_with_chatgpt(text)
    skills = response.get("skills", [])
    experiences = response.get("experiences", [])

    print('Skills:', skills)
    print('Experiences:', experiences)
    return skills, experiences
