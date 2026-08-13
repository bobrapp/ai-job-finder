import streamlit as st
from main import (
    parse_linkedin_pdf,
    rank_and_filter_jobs,
    generate_ats_resume,
    generate_cover_letter,
)

st.set_page_config(page_title="AI Technical Writing Job Matching Engine", layout="wide")
st.title("AI Technical Writing & Editing Job Search Assistant")
st.write(
    "Upload your LinkedIn Profile PDF to discover niche global roles, calculate "
    "location radius matches, and generate tailored ATS resumes."
)

st.warning(
    "DEMO NOTICE: Job listings below are simulated sample data for demonstration "
    "purposes only and are not live openings."
)

st.sidebar.header("Search Preferences")
user_zip = st.sidebar.text_input("Zip Code (Y)", value="98101")
max_radius = st.sidebar.number_input(
    "Target Radius (X Miles)", min_value=5, max_value=500, value=35
)
uploaded_file = st.sidebar.file_uploader("Upload linkedin_profile.pdf", type=["pdf"])

if uploaded_file and st.sidebar.button("Run Job Search Strategy"):
    pdf_path = "temp_profile.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Parsing LinkedIn Profile & Mapping Technical Writing Taxonomy...")
    candidate_data = parse_linkedin_pdf(pdf_path, user_zip, max_radius)
    st.success(
        "Detected Skills: " + ", ".join(candidate_data["candidate"]["core_skills"])
    )

    # Simulated sample job data for demonstration only (not live listings).
    sample_raw_jobs = [
        {
            "title": "API Documentation Engineer",
            "company": "TechCorp",
            "is_remote": True,
            "keywords": ["OpenAPI", "Git", "Markdown"],
            "seniority_score": 30,
            "recency_score": 30,
            "url": "https://example.com/job1",
        },
        {
            "title": "Senior Technical Writer",
            "company": "DataDoc",
            "is_remote": False,
            "latitude": 47.6062,
            "longitude": -122.3321,
            "keywords": ["Docs-as-Code", "DITA"],
            "seniority_score": 30,
            "recency_score": 30,
            "url": "https://example.com/job2",
        },
    ]

    st.info("Searching Niche Technical Writing Boards & Filtering Distance Radius...")
    top_10_jobs = rank_and_filter_jobs(candidate_data, sample_raw_jobs)

    st.subheader("Top Matched Technical Editing & Writing Opportunities")
    for idx, job in enumerate(top_10_jobs, 1):
        with st.expander(
            f"#{idx} {job['title']} at {job['company']} - Match Index: {job['match_score']}%"
        ):
            st.write(f"**Application Link:** {job['url']}")

            resume_path = f"ATS_Resume_Job_{idx}.pdf"
            generate_ats_resume(candidate_data, job, resume_path)
            cover_letter = generate_cover_letter(candidate_data, job)

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Generated Cover Letter Preview:**")
                st.text_area("Cover Letter", cover_letter, height=200, key=f"cl_{idx}")
            with col2:
                st.write("**Tailored ATS Resume:**")
                with open(resume_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Tailored ATS Resume PDF",
                        data=pdf_file,
                        file_name=f"ATS_Resume_{job['company']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{idx}",
                    )
