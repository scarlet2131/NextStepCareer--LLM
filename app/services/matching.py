import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app import mongo
from sentence_transformers import SentenceTransformer

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')


def find_matching_jobs(student_profile, threshold=0.3):
    student_embedding = np.array(student_profile['embedding']).reshape(1, -1)

    jobs = list(mongo.db.jobs.find({}))
    job_embeddings = np.array([job['embedding'] for job in jobs])

    similarities = cosine_similarity(student_embedding, job_embeddings)[0]
    print("do i have ", similarities)
    matched_jobs = []
    for idx, similarity in enumerate(similarities):
        if similarity >= threshold:
            matched_job = jobs[idx]
            matched_job['similarity'] = similarity
            matched_job['_id'] = str(matched_job['_id'])  # Convert ObjectId to string
            matched_jobs.append(matched_job)

    return sorted(matched_jobs, key=lambda x: x['similarity'], reverse=True)

def suggest_skill_improvements(student_profile, matched_jobs):
    student_skills = set(student_profile['skills'])

    required_skills = set()
    for job in matched_jobs:
        job_skills = job['tech'].split(',')
        required_skills.update([skill.strip() for skill in job_skills if skill.strip()])

    missing_skills = required_skills - student_skills
    return list(missing_skills)

