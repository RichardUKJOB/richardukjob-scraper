import csv
import time
import os
from datetime import datetime
from jobspy import scrape_jobs
import gspread
from google.oauth2.service_account import Credentials

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
print("Running: SCRAPER 1 - Engineering Part 1")
print("GOOGLE_SHEET_ID = " + GOOGLE_SHEET_ID)

COMPANIES = [
    {"name": "Mott MacDonald", "search": "Mott MacDonald", "match": ["mott macdonald", "mott mac", "mottmac"], "category": "Engineering"},
    {"name": "WSP", "search": "WSP", "match": ["wsp"], "category": "Engineering"},
    {"name": "Turner Townsend", "search": "Turner Townsend", "match": ["turner townsend", "turner & townsend"], "category": "Engineering"},
    {"name": "Amey", "search": "Amey", "match": ["amey"], "category": "Engineering"},
    {"name": "Arup", "search": "Arup", "match": ["arup"], "category": "Engineering"},
    {"name": "Arcadis", "search": "Arcadis", "match": ["arcadis"], "category": "Engineering"},
    {"name": "AtkinsRealis", "search": "AtkinsRealis", "match": ["atkins"], "category": "Engineering"},
    {"name": "Ramboll", "search": "Ramboll", "match": ["ramboll"], "category": "Engineering"},
    {"name": "Jacobs", "search": "Jacobs Engineering", "match": ["jacobs"], "category": "Engineering"},
    {"name": "Sweco UK", "search": "Sweco UK", "match": ["sweco"], "category": "Engineering"},
    {"name": "Cundall", "search": "Cundall", "match": ["cundall"], "category": "Engineering"},
    {"name": "Hoare Lea", "search": "Hoare Lea", "match": ["hoare lea"], "category": "Engineering"},
]

def is_match(company_col, match_keywords):
    col = company_col.lower()
    for kw in match_keywords:
        if kw.lower() in col:
            return True
    return False

def make_job(job, company_name, category):
    return {
        "job_title": str(job.get("title", "")),
        "company": str(job.get("company", company_name)),
        "category": category,
        "location": str(job.get("location", "UK")),
        "job_type": str(job.get("job_type", "Experienced")),
        "apply_link": str(job.get("job_url", "")),
        "date_added": datetime.now().strftime("%Y-%m-%d"),
        "status": "Active"
    }

def scrape_company(company):
    name = company["name"]
    search = company["search"]
    match = company["match"]
    cat = company["category"]
    results = []
    try:
        jobs = scrape_jobs(site_name=["indeed"], search_term=search,
            location="United Kingdom", results_wanted=30, country_indeed="UK", verbose=0)
        for idx in range(len(jobs)):
            job = jobs.iloc[idx]
            if is_match(str(job.get("company", "")), match):
                results.append(make_job(job, name, cat))
    except Exception as e:
        print("  Indeed: " + str(e))
    try:
        gjobs = scrape_jobs(site_name=["google"],
            google_search_term=search + " jobs United Kingdom",
            location="United Kingdom", results_wanted=20, verbose=0)
        for idx in range(len(gjobs)):
            job = gjobs.iloc[idx]
            if is_match(str(job.get("company", "")), match):
                results.append(make_job(job, name, cat))
    except Exception as e:
        print("  Google: " + str(e))
    print("OK " + name + ": " + str(len(results)) + " jobs")
    return results

def save_to_sheets(all_jobs):
    print("Connecting to Google Sheets...")
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("jobs")
    print("Connected!")
    existing = set()
    try:
        for row in sheet.get_all_values()[1:]:
            if len(row) >= 6:
                existing.add(row[5])
    except Exception as e:
        print("Read error: " + str(e))
    added = 0
    for job in all_jobs:
        if job["apply_link"] in existing:
            continue
        sheet.append_row([job["job_title"], job["company"], job["category"],
            job["location"], job["job_type"], job["apply_link"],
            job["date_added"], job["status"]])
        existing.add(job["apply_link"])
        added += 1
        time.sleep(1)
    print("Added " + str(added) + " new jobs!")

all_jobs = []
total = len(COMPANIES)
for i in range(total):
    co = COMPANIES[i]
    print("[" + str(i+1) + "/" + str(total) + "] " + co["name"])
    all_jobs.extend(scrape_company(co))
    time.sleep(2)

seen = set()
unique = []
for job in all_jobs:
    key = job["job_title"] + "_" + job["company"]
    if key not in seen:
        seen.add(key)
        unique.append(job)

print("Total unique jobs: " + str(len(unique)))
if GOOGLE_SHEET_ID:
    try:
        save_to_sheets(unique)
    except Exception as e:
        print("Sheets error: " + str(e))
print("Done!")
