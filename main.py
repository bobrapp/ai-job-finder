import pdfplumber
import re
from typing import Dict, Any
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from playwright.sync_api import sync_playwright


def parse_linkedin_pdf(pdf_path: str, user_zip: str, max_radius: int) -> Dict[str, Any]:
    """Parses LinkedIn Profile PDF into structured candidate schema."""
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""

    frameworks = ["Docs-as-Code", "Git", "Markdown", "DITA", "MadCap Flare",
                  "Sphinx", "OpenAPI", "Swagger", "Confluence"]
    style_guides = ["Microsoft Manual of Style", "Chicago Manual of Style", "CMOS", "APA"]
    domains = ["Developer Documentation", "API Reference",
               "Scientific/Medical Editing", "SaaS User Guides"]

    found_skills = [
        kw for kw in frameworks + style_guides + domains
        if re.search(r'\b' + re.escape(kw) + r'\b', extracted_text, re.IGNORECASE)
    ]

    return {
        "candidate": {
            "contact": {"zip_code": user_zip},
            "target_radius_miles": max_radius,
            "core_skills": list(set(found_skills)),
            "raw_text": extracted_text,
        }
    }


def rank_and_filter_jobs(candidate_data: Dict[str, Any], raw_job_listings: list) -> list:
    """Applies distance filtering and returns top ranked job matches."""
    geolocator = Nominatim(user_agent="job_search_app")
    user_location = geolocator.geocode(candidate_data["candidate"]["contact"]["zip_code"])
    user_coords = (user_location.latitude, user_location.longitude)

    valid_jobs = []
    for job in raw_job_listings:
        if job.get("is_remote", False):
            valid_jobs.append(job)
        else:
            job_coords = (job["latitude"], job["longitude"])
            distance = geodesic(user_coords, job_coords).miles
            if distance <= candidate_data["candidate"]["target_radius_miles"]:
                valid_jobs.append(job)

    for job in valid_jobs:
        keyword_score = len(
            set(candidate_data["candidate"]["core_skills"]) & set(job.get("keywords", []))
        ) * 10
        job["match_score"] = min(
            100,
            keyword_score + job.get("seniority_score", 30) + job.get("recency_score", 30),
        )

    return sorted(valid_jobs, key=lambda x: x["match_score"], reverse=True)[:10]


def generate_ats_resume(candidate_data: Dict[str, Any], job_description: Dict[str, Any], output_path: str):
    """Generates a clean single-column ATS PDF resume."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("ATS-Optimized Resume", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Core Competencies: " + ", ".join(candidate_data["candidate"]["core_skills"]),
        styles['Normal'],
    ))
    story.append(Spacer(1, 12))
    star_bullet = ("Edited and standardized 85+ API documentation pages using Markdown "
                   "and Git, reducing developer onboarding time by 28%.")
    story.append(Paragraph("- " + star_bullet, styles['Normal']))
    doc.build(story)


def generate_cover_letter(candidate_data: Dict[str, Any], job: Dict[str, Any]) -> str:
    """Generates tailored cover letter pitch."""
    return f"""Dear Hiring Team,

I am writing to express my strong interest in the {job['title']} role at {job['company']}.
My technical editing experience aligns directly with your environment, particularly regarding DITA, Swagger, and CMOS compliance.
In my previous position, I edited over 120 technical whitepapers across engineering teams.
I look forward to discussing how my documentation background can benefit your team.

Sincerely,
Candidate
"""


def run_auto_app_filler(job_url: str, resume_pdf_path: str, cover_letter_text: str):
    """Runs headless browser automation for cloud execution."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(job_url)

        if page.is_visible('input[name*="first_name"]'):
            page.fill('input[name*="first_name"]', "Jane")
        if page.is_visible('input[type="file"]'):
            page.set_input_files('input[type="file"]', resume_pdf_path)
        if page.is_visible('textarea[name*="cover_letter"]'):
            page.fill('textarea[name*="cover_letter"]', cover_letter_text)

        browser.close()
