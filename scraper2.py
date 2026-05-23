import csv
import time
import os
from datetime import datetime
from jobspy import scrape_jobs
import gspread
from google.oauth2.service_account import Credentials

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
print("Running: SCRAPER 2 - Engineering Part 2 + Energy")
print("GOOGLE_SHEET_ID = " + GOOGLE_SHEET_ID)

COMPANIES = [
    {"name": "Balfour Beatty", "search": "Balfour Beatty", "match": ["balfour beatty"], "category": "Engineering"},
    {"name": "Kier", "search": "Kier Group", "match": ["kier"], "category": "Engineering"},
    {"name": "Severn Trent", "search": "Severn Trent", "match": ["severn trent"], "category": "Engineering"},
    {"name": "GE Vernova", "search": "GE Vernova", "match": ["ge vernova", "vernova"], "category": "Engineering"},
    {"name": "GE Aerospace", "search": "GE Aerospace", "match": ["ge aerospace"], "category": "Engineering"},
    {"name": "Airbus", "search": "Airbus", "match": ["airbus"], "category": "Engineering"},
    {"name": "Siemens", "search": "Siemens", "match": ["siemens"], "category": "Engineering"},
    {"name": "VINCI Energies", "search": "VINCI Energies", "match": ["vinci"], "category": "Engineering"},
    {"name": "Dyson", "search": "Dyson", "match": ["dyson"], "category": "Engineering"},
    {"name": "Oxford Instruments", "search": "Oxford Instruments", "match": ["oxford instruments"], "category": "Engineering"},
    {"name": "JLR", "search": "JLR", "match": ["jlr", "jaguar land rover"], "category": "Engineering"},
    {"name": "National Grid", "search": "National Grid", "match": ["national grid"], "category": "Energy"},
    {"name": "EDF Energy", "search": "EDF Energy", "match": ["edf"], "category": "Energy"},
    {"name": "SSE", "search": "SSE", "match": ["sse"], "category": "Energy"},
    {"name": "Engie", "search": "Engie", "match": ["engie"], "category": "Energy"},
    {"name": "Air Products", "search": "Air Products", "match": ["air products"], "category": "Energy"},
    {"name": "Baker Hughes", "search": "Baker Hughes", "match": ["baker hughes"], "category": "Energy"},
    {"name": "Cornwall Insight", "search": "Cornwall Insight", "match": ["cornwall insight"], "category": "Energy"},
    {"name": "Ofgem", "search": "Ofgem", "match": ["ofgem"], "category": "Energy"},
    {"name": "Centrica", "search": "Centrica", "match": ["centrica", "british gas"], "category": "Energy"},
    {"name": "Veolia", "search": "Veolia", "match": ["veolia"], "category": "Energy"},
    {"name": "Environment Agency", "search": "Environment Agency", "match": ["environment agency"], "category": "Urban Planning"},
    {"name": "Transport for London", "search": "Transport for London", "match": ["transport for london", "tfl"], "category": "Urban Planning"},
    {"name": "QUOD", "search": "QUOD", "match": ["quod"], "category": "Urban Planning"},
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
