from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from app.services.job_scraper import should_scrape, scrape_jobs, save_jobs, update_last_scraped_time
from app import create_app
from app.services.matching import store_job_embeddings

app = create_app()
scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', hours=1)  # Check every hour
def scheduled_job():
    with app.app_context():
        print('Checking if scraping is needed...')
        if should_scrape():
            print('Performing scraping...')
            jobs = scrape_jobs()
            save_jobs(jobs)
            store_job_embeddings()
            update_last_scraped_time()
            print(f"Scraped and saved {len(jobs)} jobs.")
        else:
            print('Scraping not needed yet. Last scraping was less than 24 hours ago.')

if __name__ == "__main__":
    scheduler.start()
    app.run()
