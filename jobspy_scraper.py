import csv
import time
import os
from datetime import datetime
from jobspy import scrape_jobs

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")

COMPANIES = [
    {"name": "Mott MacDonald", "category": "Engineering"},
    {"name": "WSP", "category": "Engineering"},
    {"name": "Turner Townsend", "category": "Engineering"},
    {"name": "Amey", "category": "Engineering"},
    {"name": "Arup", "category": "Engineering"},
    {"name": "Arcadis", "category": "Engineering"},
    {"name": "Atkins", "category": "Engineering"},
    {"name": "Ramboll", "category": "Engineering"},
    {"name": "Jacobs", "category": "Engineering"},
    {"name": "Cundall", "category": "Engineering"},
    {"name": "Hoare Lea", "category": "Engineering"},
    {"name": "Balfour Beatty", "category": "Engineering"},
    {"name": "Kier", "category": "Engineering"},
    {"name": "Severn Trent", "category": "Engineering"},
    {"name": "National Grid", "category": "Energy"},
    {"name": "EDF Energy", "category": "Energy"},
    {"name": "SSE", "category": "Energy"},
    {"name": "Engie", "category": "Energy"},
    {"name": "Baker Hughes", "category": "Energy"},
    {"name": "Centrica", "category": "Energy"},
    {"name": "Veolia", "category": "Energy"},
    {"name": "Environment Agency", "category": "Urban Planning"},
    {"name": "Transport for London", "category": "Urban Planning"},
    {"name": "EY", "category": "Finance"},
    {"name": "PwC", "category": "Finance"},
    {"name": "Deloitte", "category": "Finance"},
    {"name": "KPMG", "category": "Finance"},
    {"name": "Barclays", "category": "Banking"},
    {"name": "HSBC", "category": "Banking"},
    {"name": "Lloyds", "category": "Banking"},
    {"name": "Amazon", "category": "Technology"},
    {"name": "Sky", "category": "Technology"},
    {"name": "GSK", "category": "Healthcare"},
    {"name": "AstraZeneca", "category": "Healthcare"},
    {"name": "NHS", "category": "Healthcare"},
    {"name": "Just Eat", "category": "BD and Sales"},
    {"name": "Deliveroo", "category": "BD and Sales"},
]


def scrape_company(company_name, category):
    try:
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=company_name,
            location="United Kingdom",
            results_wanted=10,
            country_indeed="UK",
            verbose=0
        )
        results = []
        for idx in range(len(jobs)):
            job = jobs.iloc[idx]
            results.append({
                "job_title": str(job.get("title", "")),
                "company": str(job.get("company", company_name)),
                "category": category,
                "location": str(job.get("location", "UK")),
                "job_type": str(job.get("job_type", "Experienced")),
                "apply_link": str(job.get("job_url", "")),
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active"
            })
        print("OK " + company_name + ": " + str(len(results)) + " jobs")
        return results
    except Exception as e:
        print("FAIL " + company_name + ": " + str(e))
        return []


all_jobs = []
total = len(COMPANIES)

for i in range(total):
    company = COMPANIES[i]
    print("[" + str(i + 1) + "/" + str(total) + "] " + company["name"])
    jobs = scrape_company(company["name"], company["category"])
    all_jobs.extend(jobs)
    time.sleep(2)

seen = set()
unique = []
for job in all_jobs:
    key = job["job_title"] + "_" + job["company"]
    if key not in seen:
        seen.add(key)
        unique.append(job)

print("Total unique jobs: " + str(len(unique)))

with open("jobs_output.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["job_title", "company", "category", "location", "job_type", "apply_link", "date_added", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(unique)

print("Done!")
