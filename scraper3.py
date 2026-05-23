import csv
import time
import os
from datetime import datetime
from jobspy import scrape_jobs
import gspread
from google.oauth2.service_account import Credentials

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
print("Running: SCRAPER 3 - Banking/Tech/Healthcare/Business")
print("GOOGLE_SHEET_ID = " + GOOGLE_SHEET_ID)

COMPANIES = [
    {"name": "Barclays", "search": "barclays bank uk", "match": ["barclays"], "category": "Banking"},
    {"name": "HSBC", "search": "hsbc bank uk", "match": ["hsbc"], "category": "Banking"},
    {"name": "Lloyds", "search": "lloyds banking group", "match": ["lloyds"], "category": "Banking"},
    {"name": "Santander", "search": "santander uk bank", "match": ["santander"], "category": "Banking"},
    {"name": "Morgan Stanley", "search": "morgan stanley london", "match": ["morgan stanley"], "category": "Banking"},
    {"name": "JPMorgan", "search": "jpmorgan chase london", "match": ["jpmorgan", "jp morgan"], "category": "Banking"},
    {"name": "Starling Bank", "search": "starling bank uk", "match": ["starling"], "category": "Banking"},
    {"name": "BT Group", "search": "bt group telecom uk", "match": ["bt group", "bt plc"], "category": "Technology"},
    {"name": "Bet365", "search": "bet365 jobs", "match": ["bet365"], "category": "Technology"},
    {"name": "Sky UK", "search": "sky tv broadband uk", "match": ["sky"], "category": "Technology"},
    {"name": "Amazon", "search": "amazon uk jobs", "match": ["amazon"], "category": "Technology"},
    {"name": "GSK", "search": "gsk glaxosmithkline uk", "match": ["gsk", "glaxo"], "category": "Healthcare"},
    {"name": "AstraZeneca", "search": "astrazeneca pharma uk", "match": ["astrazeneca"], "category": "Healthcare"},
    {"name": "NHS", "search": "nhs national health service", "match": ["nhs"], "category": "Healthcare"},
    {"name": "Compass Group", "search": "compass group catering uk", "match": ["compass group"], "category": "Business"},
    {"name": "Toyota UK", "search": "toyota uk manufacturing", "match": ["toyota"], "category": "Business"},
    {"name": "Brambles", "search": "brambles chep logistics", "match": ["brambles", "chep"], "category": "Business"},
    {"name": "Mandarin Oriental", "search": "mandarin oriental hotel london", "match": ["mandarin oriental"], "category": "Business"},
    {"name": "Just Eat", "search": "just eat takeaway uk", "match": ["just eat"], "category": "BD and Sales"},
    {"name": "Deliveroo", "search": "deliveroo uk", "match": ["deliveroo"], "category": "BD and Sales"},
    {"name": "Gatwick Airport", "search": "gatwick airport jobs", "match": ["gatwick"], "category": "Operations"},
    {"name": "STFC", "search": "stfc science technology facilities council", "match": ["stfc", "ukri"], "category": "Science"},
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
        jobs2 = scrape_jobs(site_name=["glassdoor"], search_term=search,
            location="United Kingdom", results_wanted=20, verbose=0)
        for idx in range(len(jobs2)):
            job = jobs2.iloc[idx]
            if is_match(str(job.get("company", "")), match):
                results.append(make_job(job, name, cat))
    except Exception as e:
        print("  Glassdoor: " + str(e))
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
