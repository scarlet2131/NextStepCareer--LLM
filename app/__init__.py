from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import settings
from app.services.job_scraper import scrape_jobs, save_jobs, should_scrape, update_last_scraped_time

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Set the configuration from settings
    app.config['MONGO_URI'] = settings.MONGO_URI
    app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = settings.ALLOWED_EXTENSIONS

    mongo.init_app(app)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Initialize the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: job_scraping_task(mongo), trigger="interval", hours=1)
    scheduler.start()

    return app

def job_scraping_task(mongo):
    print('Checking if scraping is needed...')
    if should_scrape(mongo):
        print('Performing scraping...')
        jobs = scrape_jobs()
        save_jobs(mongo, jobs)
        update_last_scraped_time(mongo)
        print(f"Scraped and saved {len(jobs)} jobs.")
    else:
        print('Scraping not needed yet. Last scraping was less than 24 hours ago.')
