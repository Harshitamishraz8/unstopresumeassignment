from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import streamlit as st  # ✅ add this for Streamlit Secrets support

# Load local .env (for local development)
load_dotenv()

class ResumeScreeningModel:
    def __init__(self):
        """Initialize the Resume Screening Model with Gemini API."""
        # Try Streamlit secrets first, then fallback to .env
        self.api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        
        if not self.api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY not found! Please add it to Streamlit Secrets or .env file."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def screen_resume(self, resume_text, job_description_text):
        """
        Screen a resume against a job description.
        
        Args:
            resume_text (str): The candidate's resume content
            job_description_text (str): The job description content
            
        Returns:
            str: JSON formatted evaluation response
        """
        if not resume_text or not job_description_text:
            raise ValueError("Both resume text and job description text are required.")
        
        prompt = f"""
        You are an expert technical recruiter specializing in screening resumes for technology roles.
        Carefully analyze the candidate's resume against the given job description and provide a comprehensive evaluation.

        **Job Description:**
        ```
        {job_description_text}
        ```

        **Candidate's Resume:**
        ```
        {resume_text}
        ```

        Please provide your evaluation in the following JSON format (ensure valid JSON output):
        {{
            "score": [integer between 0-100 based on overall match],
            "summary": "[2-3 sentence summary of the candidate's fit for this role]",
            "matched_skills": ["list of skills/technologies from resume that match job requirements"],
            "missing_skills": ["list of important skills/technologies mentioned in job description but missing from resume"]
        }}

        Evaluation Criteria:
        - Technical skills alignment with job requirements
        - Relevant work experience and projects
        - Educational background relevance
        - Overall career progression and achievements

        Provide only the JSON response without any additional text or formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating content from Gemini API: {str(e)}")

# Test function (optional)
if __name__ == "__main__":
    try:
        resume_model = ResumeScreeningModel()
        print("✅ Resume Screening Model initialized successfully!")
        
        # Test with sample data
        sample_resume = "Python developer with 3 years experience in web development using Django and Flask."
        sample_jd = "Looking for a Python developer with Django experience for web application development."
        
        result = resume_model.screen_resume(sample_resume, sample_jd)
        print("Test result:")
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
