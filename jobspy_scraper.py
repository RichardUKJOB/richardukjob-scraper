import csv
import time
import os
from datetime import datetime
from jobspy import scrape_jobs
import gspread
from google.oauth2.service_account import Credentials

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_CREDS_FILE = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")

print("GOOGLE_SHEET_ID = " + GOOGLE_SHEET_ID)

COMPANIES = [
    {"name": "Mott MacDonald", "category": "Engineering"},
    {"name": "WSP", "category": "Engineering"},
    {"name": "Turner Townsend", "category": "Engineering"},
    {"name": "Amey", "category": "Engineering"},
    {"name": "Arup", "category": "Engineering"},
    {"name": "Arcadis", "category": "Engineering"},
    {"name": "AtkinsRealis", "category": "Engineering"},
    {"name": "Ramboll", "category": "Engineering"},
    {"name": "Jacobs", "category": "Engineering"},
    {"name": "Sweco", "category": "Engineering"},
    {"name": "Cundall", "category": "Engineering"},
    {"name": "Hoare Lea", "category": "Engineering"},
    {"name": "Balfour Beatty", "category": "Engineering"},
    {"name": "Kier", "category": "Engineering"},
    {"name": "Severn Trent Water", "category": "Engineering"},
    {"name": "General Electric", "category": "Engineering"},
    {"name": "Airbus", "category": "Engineering"},
    {"name": "Siemens", "category": "Engineering"},
    {"name": "Vinci", "category": "Engineering"},
    {"name": "Dyson", "category": "Engineering"},
    {"name": "Oxford Instruments", "category": "Engineering"},
    {"name": "Jaguar Land Rover", "category": "Engineering"},
    {"name": "Calford Seaden", "category": "Engineering"},
    {"name": "National Grid", "category": "Energy"},
    {"name": "EDF Energy", "category": "Energy"},
    {"name": "SSE", "category": "Energy"},
    {"name": "Engie", "category": "Energy"},
    {"name": "Air Products", "category": "Energy"},
    {"name": "Baker Hughes", "category": "Energy"},
    {"name": "Cornwall Insight", "category": "Energy"},
    {"name": "Ofgem", "category": "Energy"},
    {"name": "Centrica", "category": "Energy"},
    {"name": "Veolia", "category": "Energy"},
    {"name": "Environment Agency", "category": "Urban Planning"},
    {"name": "Transport for London", "category": "Urban Planning"},
    {"name": "QUOD", "category": "Urban Planning"},
    {"name": "Bristol City Council", "category": "Urban Planning"},
    {"name": "Ralph Lauren", "category": "Marketing"},
    {"name": "SuperDry", "category": "Marketing"},
    {"name": "HelloFresh", "category": "Marketing"},
    {"name": "OMD", "category": "Marketing"},
    {"name": "Dentsu", "category": "Marketing"},
    {"name": "Mediacom", "category": "Marketing"},
    {"name": "Wavemaker", "category": "Marketing"},
    {"name": "Mindshare", "category": "Marketing"},
    {"name": "LexisNexis", "category": "Marketing"},
    {"name": "Lindt", "category": "Marketing"},
    {"name": "BSI Group", "category": "Marketing"},
    {"name": "IPG Mediabrands", "category": "Marketing"},
    {"name": "EY", "category": "Finance"},
    {"name": "PwC", "category": "Finance"},
    {"name": "Deloitte", "category": "Finance"},
    {"name": "KPMG", "category": "Finance"},
    {"name": "Grant Thornton", "category": "Finance"},
    {"name": "BDO", "category": "Finance"},
    {"name": "Aviva", "category": "Finance"},
    {"name": "Sage", "category": "Finance"},
    {"name": "Moody's", "category": "Finance"},
    {"name": "Computershare", "category": "Finance"},
    {"name": "Kroll", "category": "Finance"},
    {"name": "Wavestone", "category": "Finance"},
    {"name": "Efficio", "category": "Finance"},
    {"name": "Genpact", "category": "Finance"},
    {"name": "Barclays", "category": "Banking"},
    {"name": "HSBC", "category": "Banking"},
    {"name": "Lloyds Banking Group", "category": "Banking"},
    {"name": "Santander", "category": "Banking"},
    {"name": "Morgan Stanley", "category": "Banking"},
    {"name": "JPMorgan", "category": "Banking"},
    {"name": "Starling Bank", "category": "Banking"},
    {"name": "BT", "category": "Technology"},
    {"name": "Bet365", "category": "Technology"},
    {"name": "Sky", "category": "Technology"},
    {"name": "Amazon", "category": "Technology"},
    {"name": "Huawei", "category": "Technology"},
    {"name": "GetGround", "category": "Technology"},
    {"name": "GSK", "category": "Healthcare"},
    {"name": "AstraZeneca", "category": "Healthcare"},
    {"name": "NHS", "category": "Healthcare"},
    {"name": "MHRA", "category": "Healthcare"},
    {"name": "GMC", "category": "Healthcare"},
    {"name": "MND Association", "category": "Healthcare"},
    {"name": "Compass Group", "category": "Business"},
    {"name": "Brambles", "category": "Business"},
    {"name": "Toyota", "category": "Business"},
    {"name": "Mandarin Oriental", "category": "Business"},
    {"name": "Just Eat", "category": "BD and Sales"},
    {"name": "Deliveroo", "category": "BD and Sales"},
    {"name": "Clarivate", "category": "BD and Sales"},
    {"name": "eBay", "category": "BD and Sales"},
    {"name": "Gatwick Airport", "category": "Operations"},
    {"name": "STFC", "category": "Science"},
    {"name": "P&G", "category": "Marketing"},
    {"name": "American Express", "category": "Finance"},
    {"name": "Deloitte", "category": "Finance"},
    {"name": "Arup", "category": "Engineering"},
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


def save_to_sheets(all_jobs):
    print("Connecting to Google Sheets...")
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("jobs")
    print("Connected!")

    existing = set()
    try:
        rows = sheet.get_all_values()
        for row in rows[1:]:
            if len(row) >= 6:
                existing.add(row[5])
    except Exception as e:
        print("Could not read existing: " + str(e))

    added = 0
    for job in all_jobs:
        if job["apply_link"] in existing:
            continue
        sheet.append_row([
            job["job_title"],
            job["company"],
            job["category"],
            job["location"],
            job["job_type"],
            job["apply_link"],
            job["date_added"],
            job["status"]
        ])
        existing.add(job["apply_link"])
        added += 1

    print("Added " + str(added) + " new jobs!")


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

if GOOGLE_SHEET_ID:
    try:
        save_to_sheets(unique)
    except Exception as e:
        print("Google Sheets error: " + str(e))

print("Done!")
