import os
import uuid
from werkzeug.utils import secure_filename
from app.services.resume_parser import parse_resume
from app import mongo, settings
from sentence_transformers import SentenceTransformer
import numpy as np

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def save_resume_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(settings.UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def handle_resume_upload(file, form_data):
    filepath = save_resume_file(file)
    skills, experiences = parse_resume(filepath)

    # Generate embedding for the student's skills and experiences
    student_text = ' '.join(skills + experiences)
    embedding = model.encode(student_text).tolist()  # Convert the NumPy array to a list

    student_id = str(uuid.uuid4())  # Generate a unique student ID
    student_data = {
        "student_id": student_id,
        "name": form_data.get("name"),
        "email": form_data.get("email"),
        "resume": filepath,
        "skills": skills,
        "experiences": experiences,
        "embedding": embedding  # Store the embedding as a list
    }

    mongo.db.students.insert_one(student_data)
    return {'message': 'Resume uploaded and skills extracted successfully', 'student_id': student_id}
