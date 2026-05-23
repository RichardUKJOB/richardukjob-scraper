import csv
import time
import os
from datetime import datetime
from jobspy import scrape_jobs
import gspread
from google.oauth2.service_account import Credentials

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
print("Running: SCRIPT 2 - Finance/Banking/Marketing/Tech/Business")
print("GOOGLE_SHEET_ID = " + GOOGLE_SHEET_ID)

COMPANIES = [
    # MARKETING
    {"name": "Ralph Lauren", "match": ["ralph lauren"], "category": "Marketing"},
    {"name": "SuperDry", "match": ["superdry"], "category": "Marketing"},
    {"name": "HelloFresh", "match": ["hellofresh"], "category": "Marketing"},
    {"name": "OMD media group", "match": ["omd"], "category": "Marketing"},
    {"name": "Dentsu", "match": ["dentsu"], "category": "Marketing"},
    {"name": "Mediacom", "match": ["mediacom"], "category": "Marketing"},
    {"name": "Wavemaker UK", "match": ["wavemaker"], "category": "Marketing"},
    {"name": "Mindshare", "match": ["mindshare"], "category": "Marketing"},
    {"name": "LexisNexis", "match": ["lexisnexis"], "category": "Marketing"},
    {"name": "Lindt Sprungli", "match": ["lindt"], "category": "Marketing"},
    {"name": "Omnicom Group", "match": ["omnicom"], "category": "Marketing"},
    {"name": "BSI Group", "match": ["bsi"], "category": "Marketing"},
    {"name": "Procter and Gamble", "match": ["procter", "gamble", "p&g"], "category": "Marketing"},
    # FINANCE
    {"name": "EY Ernst Young", "match": ["ernst young", "ey"], "category": "Finance"},
    {"name": "PricewaterhouseCoopers", "match": ["pwc", "pricewaterhouse"], "category": "Finance"},
    {"name": "Deloitte UK", "match": ["deloitte"], "category": "Finance"},
    {"name": "KPMG UK", "match": ["kpmg"], "category": "Finance"},
    {"name": "Grant Thornton UK", "match": ["grant thornton"], "category": "Finance"},
    {"name": "BDO UK", "match": ["bdo"], "category": "Finance"},
    {"name": "Aviva", "match": ["aviva"], "category": "Finance"},
    {"name": "Sage Group", "match": ["sage group", "sage plc"], "category": "Finance"},
    {"name": "Moodys Corporation", "match": ["moody"], "category": "Finance"},
    {"name": "Computershare", "match": ["computershare"], "category": "Finance"},
    {"name": "Kroll", "match": ["kroll"], "category": "Finance"},
    {"name": "Wavestone", "match": ["wavestone"], "category": "Finance"},
    {"name": "Genpact", "match": ["genpact"], "category": "Finance"},
    # BANKING
    {"name": "Barclays", "match": ["barclays"], "category": "Banking"},
    {"name": "HSBC", "match": ["hsbc"], "category": "Banking"},
    {"name": "Lloyds Banking Group", "match": ["lloyds"], "category": "Banking"},
    {"name": "Santander UK", "match": ["santander"], "category": "Banking"},
    {"name": "Morgan Stanley", "match": ["morgan stanley"], "category": "Banking"},
    {"name": "JPMorgan Chase", "match": ["jpmorgan", "jp morgan"], "category": "Banking"},
    {"name": "Starling Bank", "match": ["starling"], "category": "Banking"},
    # TECHNOLOGY
    {"name": "BT Group", "match": ["bt group", "bt plc"], "category": "Technology"},
    {"name": "Bet365", "match": ["bet365"], "category": "Technology"},
    {"name": "Sky UK", "match": ["sky"], "category": "Technology"},
    {"name": "Amazon UK", "match": ["amazon"], "category": "Technology"},
    # HEALTHCARE
    {"name": "GSK GlaxoSmithKline", "match": ["gsk", "glaxo"], "category": "Healthcare"},
    {"name": "AstraZeneca", "match": ["astrazeneca"], "category": "Healthcare"},
    {"name": "NHS England", "match": ["nhs"], "category": "Healthcare"},
    # BUSINESS
    {"name": "Compass Group UK", "match": ["compass group"], "category": "Business"},
    {"name": "Toyota UK", "match": ["toyota"], "category": "Business"},
    {"name": "Brambles", "match": ["brambles"], "category": "Business"},
    {"name": "Mandarin Oriental", "match": ["mandarin oriental"], "category": "Business"},
    {"name": "Just Eat UK", "match": ["just eat"], "category": "BD and Sales"},
    {"name": "Deliveroo", "match": ["deliveroo"], "category": "BD and Sales"},
    {"name": "Gatwick Airport", "match": ["gatwick"], "category": "Operations"},
    {"name": "STFC", "match": ["stfc", "ukri"], "category": "Science"},
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
    match = company["match"]
    cat = company["category"]
    results = []
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "glassdoor"],
            search_term=name,
            location="United Kingdom",
            results_wanted=25,
            country_indeed="UK",
            verbose=0
        )
        for idx in range(len(jobs)):
            job = jobs.iloc[idx]
            if is_match(str(job.get("company", "")), match):
                results.append(make_job(job, name, cat))
    except Exception as e:
        print("  Indeed/Glassdoor: " + str(e))
    try:
        gjobs = scrape_jobs(
            site_name=["google"],
            google_search_term=name + " jobs United Kingdom",
            location="United Kingdom",
            results_wanted=25,
            verbose=0
        )
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
        sheet.append_row([
            job["job_title"], job["company"], job["category"],
            job["location"], job["job_type"], job["apply_link"],
            job["date_added"], job["status"]
        ])
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
