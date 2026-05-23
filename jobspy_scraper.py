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
    {"name": "General Electric", "category": "Engineering"},
    {"name": "Airbus", "category": "Engineering"},
    {"name": "Siemens", "category": "Engineering"},
    {"name": "Vinci", "category": "Engineering"},
    {"name": "Dyson", "category": "Engineering"},
    {"name": "National Grid", "category": "Energy"},
    {"name": "EDF Energy", "category": "Energy"},
    {"name": "SSE", "category": "Energy"},
    {"name": "Engie", "category": "Energy"},
    {"name": "Baker Hughes", "category": "Energy"},
    {"name": "Cornwall Insight", "category": "Energy"},
    {"name": "Ofgem", "category": "Energy"},
    {"name": "Centrica", "category": "Energy"},
    {"name": "Veolia", "category": "Energy"},
    {"name": "Environment Agency", "category": "Urban Planning"},
    {"name": "Transport for London", "category": "Urban Planning"},
    {"name": "QUOD", "category": "Urban Planning"},
    {"name": "Ralph Lauren", "category": "Marketing"},
    {"name": "HelloFresh", "category": "Marketing"},
    {"name": "Dentsu", "category": "Marketing"},
    {"name": "Mediacom", "category": "Marketing"},
    {"name": "Wavemaker", "category": "Marketing"},
    {"name": "EY", "category": "Finance"},
    {"name": "PwC", "category": "Finance"},
    {"name": "Deloitte", "category": "Finance"},
    {"name": "KPMG", "category": "Finance"},
    {"name": "Grant Thornton", "category": "Finance"},
    {"name": "BDO", "category": "Finance"},
    {"name": "Aviva", "category": "Finance"},
    {"name": "Barclays", "category": "Banking"},
    {"name": "HSBC", "category": "Banking"},
    {"name": "Lloyds", "category": "Banking"},
    {"name": "Santander", "category": "Banking"},
    {"name": "Morgan Stanley", "category": "Banking"},
    {"name": "JPMorgan", "category": "Banking"},
    {"name": "Starling Bank", "category": "Banking"},
    {"name": "Amazon", "category": "Technology"},
    {"name": "Sky", "category": "Technology"},
    {"name": "Bet365", "category": "Technology"},
    {"name": "British Telecom", "category": "Technology"},
    {"name": "GSK", "category": "Healthcare"},
    {"name": "AstraZeneca", "category": "Healthcare"},
    {"name": "NHS", "category": "Healthcare"},
    {"name": "Compass Group", "category": "Business"},
    {"name": "Toyota", "category": "Business"},
    {"name": "Just Eat", "category": "BD and Sales"},
    {"name": "Deliveroo", "category": "BD and Sales"},
]


def scrape_company(company_name, category):
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "google"],
            search_term=company_name,
            google_search_term=company_name + " jobs United Kingdom",
            location="United Kingdom",
            results_wanted=15,
            hours_old=168,
            country_indeed="UK",
            verbose=0
        )
        results = []
        for idx in range(len(jobs)):
            job = jobs.iloc[idx]
            company_col = str(job.get("company", "")).lower()
            first_word = company_name.lower().split()[0]
            if first_word not in company_col:
                continue
            results.append({
                "job_title": str(job.get("title", "")),
                "company": str(job.get("company", company_name)),
                "category": category,
                "location": str(job.get("location", "UK")),
                "job_type": str(job.get("job_type", "Experienced")),
                "apply_link": str(job.get("job_url", "")),
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "status": "Active",
                "source": str(job.get("site", ""))
            })
        print("OK " + company_name + ": " + str(len(results)) + " jobs")
        return results
    except Exception as e:
        print("FAIL " + company_name + ": " + str(e))
        return []


def save_to_google_sheets(all_jobs):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Jobs")
        existing = set()
        try:
            rows = sheet.get_all_values()
            for row in rows[1:]:
                if len(row) >= 6:
                    existing.add(row[5])
        except Exception:
            pass
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
                job["status"],
                job["source"]
            ])
            existing.add(job["apply_link"])
            added += 1
        print("Added " + str(added) + " new jobs to Google Sheets")
    except Exception as e:
        print("Google Sheets error: " + str(e))


def run():
    print("RichardUKJob Scraper - " + datetime.now().strftime("%Y-%m-%d %H:%M"))
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
        fieldnames = ["job_title", "company", "category", "location",
                      "job_type", "apply_link", "date_added", "status", "source"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique)

    print("Saved to jobs_output.csv")

    if GOOGLE_SHEET_ID:
        save_to_google_sheets(unique)

    print("Done!")


run()
