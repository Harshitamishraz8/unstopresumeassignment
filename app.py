import streamlit as st
from src.resume_screening import ResumeScreeningModel
from src.extract_text import extract_text_from_file
import json
import tempfile
import os

# -----------------------------
# Load Resume Model
# -----------------------------
@st.cache_resource
def load_model():
    """Initialize the resume screening model"""
    try:
        model = ResumeScreeningModel()
        return model
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None

# Initialize model
resume_model = load_model()

# -----------------------------
# Streamlit Interface
# -----------------------------
st.set_page_config(page_title="Resume Screening", layout="wide")
st.title("📄 Resume Screening using Gemini LLM")
st.markdown(
    "Upload a candidate's resume and a job description, and get an AI evaluation!"
)

# Check if model loaded successfully
if resume_model is None:
    st.error("❌ Failed to load the resume screening model. Please check your API key in .env file.")
    st.stop()

# --- Upload Resume ---
resume_file = st.file_uploader("Upload Candidate Resume (PDF or DOCX)", type=["pdf", "docx"])

# --- Upload Job Description ---
jd_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"])

# --- Process Files ---
if st.button("Evaluate Resume"):
    if not resume_file or not jd_file:
        st.warning("Please upload both a resume and a job description!")
    else:
        try:
            # Save uploaded files temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.name)[1]) as tmp_resume:
                tmp_resume.write(resume_file.getbuffer())
                tmp_resume_path = tmp_resume.name
            
            # Extract text from resume
            resume_text = extract_text_from_file(tmp_resume_path)
            
            # Extract text from job description with encoding detection
            jd_bytes = jd_file.read()
            
            # Try multiple encodings
            encodings_to_try = ['utf-8', 'utf-8-sig', 'windows-1252', 'iso-8859-1', 'cp1252']
            jd_text = None
            
            for encoding in encodings_to_try:
                try:
                    jd_text = jd_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if jd_text is None:
                st.error("❌ Could not decode job description file. Please save it as UTF-8 encoded text file.")
                st.stop()
            
            # Clean up temporary file
            os.unlink(tmp_resume_path)
            
            # Validate extracted text
            if not resume_text or resume_text.strip() == "":
                st.error("❌ Failed to extract text from resume. Please check if the file is valid.")
            elif not jd_text or jd_text.strip() == "":
                st.error("❌ Job description appears to be empty.")
            else:
                # Run evaluation
                with st.spinner("Screening resume..."):
                    try:
                        result_text = resume_model.screen_resume(resume_text, jd_text)
                        
                        if result_text:
                            # Clean and display JSON
                            try:
                                # Remove markdown code blocks if present
                                clean_result = result_text.replace("```json\n", "").replace("```", "").strip()
                                parsed_result = json.loads(clean_result)
                                
                                st.success("✅ Evaluation Complete!")
                                
                                # Display Score prominently
                                col1, col2, col3 = st.columns(3)
                                with col2:
                                    score = parsed_result.get("score", 0)
                                    st.metric("Match Score", f"{score}/100", delta=None)
                                
                                # Show Summary
                                st.subheader("📝 Summary")
                                st.write(parsed_result.get("summary", "No summary available"))

                                # Show Matched and Missing Skills side by side
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.subheader("✅ Matched Skills")
                                    matched_skills = parsed_result.get("matched_skills", [])
                                    if matched_skills:
                                        for skill in matched_skills:
                                            st.write(f"• {skill}")
                                    else:
                                        st.write("No matched skills found")
                                
                                with col2:
                                    st.subheader("❌ Missing Skills")
                                    missing_skills = parsed_result.get("missing_skills", [])
                                    if missing_skills:
                                        for skill in missing_skills:
                                            st.write(f"• {skill}")
                                    else:
                                        st.write("No missing skills identified")

                                # Show Raw JSON in an expander
                                with st.expander("🔍 View Raw JSON Response"):
                                    st.json(parsed_result)

                            except json.JSONDecodeError as e:
                                st.error(f"❌ Failed to parse JSON from model output: {e}")
                                st.subheader("Raw Response:")
                                st.code(result_text)
                        else:
                            st.error("❌ No response received from the model.")
                            
                    except Exception as e:
                        st.error(f"❌ Error calling Gemini API: {e}")
                        
        except Exception as e:
            st.error(f"❌ Error processing files: {e}")

# --- Sidebar with Instructions ---
with st.sidebar:
    st.subheader("📋 Instructions")
    st.markdown("""
    1. **Upload Resume**: PDF or DOCX format
    2. **Upload Job Description**: TXT format
    3. **Click Evaluate**: Get AI-powered screening results
    
    **Features:**
    - Match score (0-100)
    - Detailed summary
    - Matched skills analysis
    - Missing skills identification
    """)
    
    st.subheader("⚙️ Requirements")
    st.markdown("""
    - Valid Gemini API key in `.env` file
    - Resume in PDF or DOCX format
    - Job description in TXT format
    """)