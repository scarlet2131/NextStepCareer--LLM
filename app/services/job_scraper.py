import logging
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sentence_transformers import SentenceTransformer
from webdriver_manager.chrome import ChromeDriverManager

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')


logging.basicConfig(level=logging.INFO)


def scrape_jobs():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://hiring.cafe/")

    # Wait until job cards are present
    wait = WebDriverWait(driver, 10)
    job_cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.my-masonry-grid_column div.relative")))

    jobs = []
    # print("size of  jobs card ", job_cards[0])

    for job_card in job_cards:
        try:
            title = job_card.find_element(By.CSS_SELECTOR, 'span.font-bold.text-start.mt-1.line-clamp-2').text.strip()
            location = job_card.find_element(By.CSS_SELECTOR, 'div.mt-1.flex.items-center.space-x-1 span').text.strip()
            # Extract company
            company_elements = job_card.find_elements(By.CSS_SELECTOR, 'span.line-clamp-1')
            company = company_elements[0].text.strip() if company_elements else 'N/A'
            # description = job_card.find_element(By.CSS_SELECTOR, 'span.line-clamp-5.font-light').text.strip()
            description_elements = job_card.find_elements(By.CSS_SELECTOR,
                                                          'span.line-clamp-5.font-light, span.line-clamp-5.font-light span, span.line-clamp-6.font-light, span.line-clamp-6.font-light span' )
            description = ' '.join([desc.text.strip() for desc in description_elements])
            # description = job_card.find_element(By.CSS_SELECTOR,
            #                                     'div.flex.flex-col.space-y-1 span.line-clamp-6.font-light').text.strip()
            try:
                tech_elements = job_card.find_elements(By.CSS_SELECTOR,
                                                       'div.flex.flex-col.space-y-1 span.line-clamp-2.font-light')
                tech = ', '.join([tech_element.text.strip() for tech_element in tech_elements])
            except Exception as e:
                tech = "N/A"

            # Generate embedding for the job description
            job_text = f"{title} {location} {company} {description} {tech}"
            embedding = model.encode(job_text).tolist()

            # print("is job title found ", title)
            job = {
                'title': title,
                'location': location,
                'company': company,
                'description': description,
                'tech': tech,
                'embedding': embedding,
                'scraped_at': datetime.now()
            }
            jobs.append(job)
        except Exception as e:
            logging.error(f"Error processing job card: {e}")

    driver.quit()
    logging.info(f"Scraped {len(jobs)} jobs")
    return jobs


def save_jobs(mongo, jobs):
    if jobs:
        mongo.db.jobs.insert_many(jobs)

def should_scrape(mongo):
    scraping_info = mongo.db.scraping_info.find_one({})
    if scraping_info:
        last_scraped_at = scraping_info.get('last_scraped_at')
        if last_scraped_at:
            time_diff = datetime.now() - last_scraped_at
            return time_diff > timedelta(hours=24)
    return True

def update_last_scraped_time(mongo):
    mongo.db.scraping_info.update_one(
        {},
        {"$set": {"last_scraped_at": datetime.now()}},
        upsert=True
    )
