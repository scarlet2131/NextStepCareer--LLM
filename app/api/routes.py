# from flask import request, jsonify, current_app
# from flask_cors import cross_origin
# from werkzeug.utils import secure_filename
# import os
# from app import mongo
# from app.services.resume_parser import parse_resume
# from app.api import bp
#
#
# # app/api/routes.py
# from flask import jsonify
# from app.api import bp
#
#
# @bp.route('/test-cors', methods=['GET'])
# @cross_origin()
# def test_cors():
#     return jsonify({'message': 'CORS is working!'}), 200
#
# @cross_origin()
# @bp.route('/upload-resume', methods=['POST'])
# @cross_origin()
# def upload_resume():
#     if 'resume' not in request.files:
#         return jsonify({'message': 'No file part'}), 400
#
#     file = request.files['resume']
#     if file.filename == '':
#         return jsonify({'message': 'No selected file'}), 400
#
#     if file and allowed_file(file.filename):
#         # Clear the uploads folder
#         clear_uploads_folder()
#
#         # Save the new resume
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
#
#         # Parse the resume
#         skills = parse_resume(filepath)
#
#         # Save the parsed data to MongoDB
#         save_to_mongo(skills, filename)
#
#         return jsonify({'message': 'Resume uploaded successfully', 'skills': skills})
#
#     return jsonify({'message': 'Invalid file type'}), 400
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
#
# def save_to_mongo(skills, filename):
#     mongo.db.resumes.insert_one({'filename': filename, 'skills': skills})
#
# def clear_uploads_folder():
#     folder = current_app.config['UPLOAD_FOLDER']
#     for filename in os.listdir(folder):
#         file_path = os.path.join(folder, filename)
#         if os.path.isfile(file_path):
#             os.unlink(file_path)


# app/api/routes.py

from flask import Blueprint, request, jsonify, current_app

from app.services.job_scraper import should_scrape, scrape_jobs, save_jobs, update_last_scraped_time
from app.services.matching import find_matching_jobs, suggest_skill_improvements
from app.services.resume_service import handle_resume_upload
from app.api import bp
from app import mongo

# bp = Blueprint('api', __name__)

@bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Handle resume upload and processing
    response = handle_resume_upload(file, request.form)
    return jsonify(response), 200

@bp.route('/scrape-jobs', methods=['GET'])
def scrape_jobs_route():
    if should_scrape(mongo):
        jobs = scrape_jobs()
        save_jobs(mongo, jobs)
        update_last_scraped_time(mongo)
        return jsonify({"message": f"Scraped and saved {len(jobs)} jobs."}), 200
    else:
        return jsonify({"message": "Scraping not needed yet. Last scraping was less than 24 hours ago."}), 200


# @bp.route('/match-jobs', methods=['POST'])
# def match_jobs_route():
#     student_email = request.json['email']
#     student_profile = mongo.db.students.find_one({"student_id": student_email})
#
#     if not student_profile:
#         return jsonify({"error": "Student profile not found"}), 404
#
#     matched_jobs = find_matching_jobs(student_profile)
#     skill_improvements = suggest_skill_improvements(student_profile, matched_jobs)
#
#     return jsonify({
#         "matched_jobs": matched_jobs,
#         "skill_improvements": skill_improvements
#     })

@bp.route('/match-jobs', methods=['POST'])
def match_jobs_route():
    student_email = request.json['email']
    student_profile = mongo.db.students.find_one({"student_id": student_email})

    if not student_profile:
        return jsonify({"error": "Student profile not found"}), 404

    if 'embedding' not in student_profile:
        return jsonify({"error": "Embedding not found in student profile"}), 400

    matched_jobs = find_matching_jobs(student_profile)
    skill_improvements = suggest_skill_improvements(student_profile, matched_jobs)

    # Ensure all ObjectIds are converted to strings
    for job in matched_jobs:
        job['_id'] = str(job['_id'])

    return jsonify({
        "matched_jobs": matched_jobs,
        "skill_improvements": skill_improvements
    })
