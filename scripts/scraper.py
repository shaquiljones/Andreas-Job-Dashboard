import os
import requests
import json

# Fetch keys from GitHub Secrets
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Andrea's details
ANDREA_EMAIL = "andream.b.101@gmail.com"
LOCATION = "East Orange, NJ"

# Job categories based on her resume
SEARCH_TERMS = ["Cosmetology", "Customer Service Representative", "Patient Care Advocate", "Event Coordinator"]

def get_jobs():
    all_jobs = []
    for term in SEARCH_TERMS:
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&what={term}&where={LOCATION}&distance=20&results_per_page=5"
        try:
            response = requests.get(url)
            data = response.json()
            for job in data.get("results", []):
                all_jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name", "Unknown"),
                    "url": job.get("redirect_url"),
                    "description": job.get("description", "No description provided.")[:200] + "..."
                })
        except Exception as e:
            print(f"Error fetching {term}: {e}")
    return all_jobs

def send_email(jobs):
    if not jobs:
        print("No jobs found today. No email sent.")
        return

    # Build HTML email
    html_content = "<h2 style='color:#001F3F;'>Daily Job Leads for Andrea</h2>"
    html_content += "<p>Here are the latest opportunities near East Orange, NJ tailored to your resume.</p><hr>"
    
    for job in jobs:
        html_content += f"""
        <div style='margin-bottom: 25px; padding: 15px; border-left: 4px solid #D4AF37; background: #f9f9f9;'>
            <h3 style='color:#001F3F; margin:0 0 10px 0;'>{job['title']}</h3>
            <p style='margin:0 0 10px 0;'><strong>{job['company']}</strong></p>
            <p style='font-size: 14px; color: #555;'>{job['description']}</p>
            <a href='{job['url']}' style='background-color:#001F3F; color:white; padding:10px 15px; text-decoration:none; border-radius:5px; display:inline-block; margin-top:10px;'>Apply Here</a>
        </div>
        """

    # Send via SendGrid
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "personalizations": [
            {
                "to": [{"email": ANDREA_EMAIL}],
                "subject": f"Daily Job Dashboard: {len(jobs)} New Leads Found!"
            }
        ],
        "from": {"email": ANDREA_EMAIL}, # Using her own email as sender (verified by default on free tier)
        "content": [{"type": "text/html", "value": html_content}]
    }
    
    response = requests.post("https://api.sendgrid.com/v3/mail/send", headers=headers, json=payload)
    if response.status_code == 202:
        print(f"Success! Email sent to {ANDREA_EMAIL} with {len(jobs)} jobs.")
    else:
        print(f"Failed to send email: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Scraping jobs for Andrea...")
    jobs = get_jobs()
    print(f"Found {len(jobs)} jobs. Sending email...")
    send_email(jobs)
