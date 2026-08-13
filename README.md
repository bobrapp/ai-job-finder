# ai-job-finder

AI-assisted job search assistant for technical writing & editing roles. Upload a
LinkedIn profile PDF, discover niche/global roles, filter by distance radius, and
generate ATS-optimized resumes and tailored cover letters. Built with Streamlit,
pdfplumber, geopy, reportlab, and Playwright.

> **DEMO NOTICE:** The bundled job listings are simulated sample data for
> demonstration only and are **not** live openings. Replace with a compliant
> job-source integration before production use.

## Project structure

| File | Purpose |
|------|---------|
| `ui.py` | Streamlit front-end (upload, inputs, results) |
| `main.py` | PDF parsing, geo/rank filtering, resume + cover letter generation, headless Playwright form filler |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container image (Playwright base + Chromium); binds Render's `$PORT` |
| `render.yaml` | Render Blueprint (Docker web service) |
| `.gitignore` | Ignores runtime PDFs, secrets, caches |

## Run locally

```bash
pip install -r requirements.txt
playwright install chromium
streamlit run ui.py
```

Then open http://localhost:8501

## Deploy to Render (ship list)

1. Sign in to Render with your account.
2. **New -> Blueprint**, connect this repository, select branch `main`.
3. Render reads `render.yaml` and provisions the Docker web service.
4. Use a **paid instance** (Starter or higher) - the free tier can OOM running
   Chromium/Playwright.
5. Add any API/geocoding secrets as Render environment variables (never commit them).
6. Deploy and share the assigned `*.onrender.com` URL.

`autoDeploy: true` in `render.yaml` redeploys automatically on every push to `main`.

## Notes / hardening before production

- The automated application filler stops before final submit (human-in-the-loop);
  keep it that way so applications are reviewed before sending.
- Users upload resumes containing personal data: add file size/type validation,
  content scanning, short-lived storage, and a deletion policy.
- Nominatim (geopy) has rate limits and usage policy; consider a dedicated geocoder
  for production traffic.
