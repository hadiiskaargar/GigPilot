"""
scraper.py
Module for scraping freelance job listings from Upwork.com based on keywords using Playwright (headless).
"""

import requests
import sys
import os
import time
import random
from typing import List, Dict
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://www.freelancer.com/jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_freelancer_jobs(keywords: List[str], max_pages: int = 2, delay: float = 2.0) -> List[Dict]:
    jobs = []
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    for keyword in keywords:
        for page_num in range(1, max_pages + 1):
            url = f"https://www.freelancer.com/jobs/?keyword={keyword}&page={page_num}"
            try:
                resp = session.get(url, headers=HEADERS, timeout=(10, 60))
                if resp.status_code == 404:
                    print(f"[INFO] Page not found (404) for '{keyword}' page {page_num}. Skipping.")
                    continue
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                job_cards = soup.find_all("div", class_="JobSearchCard-item")
                if not job_cards:
                    print(f"[INFO] No jobs found for '{keyword}' page {page_num}.")
                for card in job_cards:
                    try:
                        title_tag = card.find("a", class_="JobSearchCard-primary-heading-link")
                        title = title_tag.text.strip() if title_tag else ""
                        link = f"https://www.freelancer.com{title_tag['href']}" if title_tag and title_tag.has_attr('href') else ""
                        desc_tag = card.find("p", class_="JobSearchCard-primary-description")
                        snippet = desc_tag.text.strip() if desc_tag else ""
                        budget_tag = card.find("div", class_="JobSearchCard-primary-price")
                        budget = budget_tag.text.strip() if budget_tag else ""
                        location_tag = card.find("span", class_="JobSearchCard-primary-location")
                        location = location_tag.text.strip() if location_tag else ""
                        skills = [s.text.strip() for s in card.find_all("a", class_="JobSearchCard-primary-skill")]
                        job_dict = {
                            "title": title,
                            "snippet": snippet,
                            "budget": budget,
                            "country": location,
                            "skills": skills,
                            "link": link,
                            "keyword": keyword
                        }
                        jobs.append(job_dict)
                    except Exception as e:
                        print(f"[ERROR] Error parsing job card: {e}")
            except requests.exceptions.ConnectTimeout:
                print(f"[TIMEOUT] ConnectTimeout for '{keyword}' page {page_num}.")
                continue
            except requests.exceptions.ReadTimeout:
                print(f"[TIMEOUT] ReadTimeout for '{keyword}' page {page_num}.")
                continue
            except requests.HTTPError as e:
                print(f"[ERROR] HTTP error for '{keyword}' page {page_num}: {e}")
                continue
            except Exception as e:
                print(f"[ERROR] Request failed for '{keyword}' page {page_num}: {e}")
                continue
            time.sleep(random.uniform(1.5, 3.5))
    return jobs

if __name__ == "__main__":
    from database import JobDatabase
    import argparse
    print("GigPilot Freelancer.com Scraper")
    parser = argparse.ArgumentParser(description="Scrape Freelancer.com jobs by keyword.")
    parser.add_argument("keywords", nargs="*", help="Keywords to search for.")
    parser.add_argument("--pages", type=int, default=2, help="Number of pages to scrape per keyword.")
    args = parser.parse_args()
    if args.keywords:
        keywords = args.keywords
    else:
        keywords = input("Enter keywords separated by commas: ").split(",")
        keywords = [k.strip() for k in keywords if k.strip()]
    if not keywords:
        print("No keywords provided. Exiting.")
        sys.exit(1)
    print(f"Scraping for keywords: {keywords}")
    try:
        jobs = fetch_freelancer_jobs(keywords, max_pages=args.pages)
        print(f"Found {len(jobs)} jobs. Saving to database...")
        db_path = os.path.join("jobs.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
        db = JobDatabase(db_path)
        db.insert_jobs(jobs)
        print("Done.")
    except Exception as e:
        print(f"[FATAL] An error occurred: {e}")
        sys.exit(1)
