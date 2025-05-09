import streamlit as st
import os
import main as resume_processor
from pathlib import Path

st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
    }
    .stButton>button:hover {
        background-color: #4338CA;
        color: white;
    }
    .upload-section {
        padding: 2rem;
        border-radius: 0.5rem;
        border: 2px dashed #4F46E5;
        margin-bottom: 2rem;
    }
    h1 {
        color: #4F46E5;
    }
    .highlight {
        padding: 1.2rem;
        background-color: #f8fafc;
        border-radius: 0.5rem;
        border-left: 4px solid #4F46E5;
        margin: 1rem 0;
    }
    .quick-summary {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("Resume Analyzer Pro")
    
    # Create upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("Upload Resumes")
    uploaded_files = st.file_uploader("Choose PDF or DOCX files", 
                                    type=["pdf", "docx"], 
                                    accept_multiple_files=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        # Create resumes directory if it doesn't exist
        os.makedirs("resumes", exist_ok=True)
        
        # Process each uploaded file
        results = {}
        for uploaded_file in uploaded_files:
            # Save the uploaded file
            file_path = os.path.join("resumes", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Extract text from the file
                if file_path.endswith('.pdf'):
                    text = resume_processor.extract_text_from_pdf(file_path)
                else:
                    text = resume_processor.extract_text_from_docx(file_path)
                
                # Analyze the resume
                analysis = resume_processor.analyze_resume(text)
                
                # Calculate score
                score = resume_processor.calculate_score(analysis)
                
                # Store results
                results[uploaded_file.name] = {
                    'skills': analysis['skills'],
                    'education': analysis['education'],
                    'experience': analysis['experience'],
                    'languages': analysis['languages'],
                    'score': score
                }
                
                # Clean up
                os.remove(file_path)
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        # Display results
        if results:
            for filename, result in results.items():
                st.markdown(f"### 📄 {filename}")
                
                # Quick Summary Section
                st.markdown('<div class="quick-summary">', unsafe_allow_html=True)
                
                # Score and key metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Score", f"{result['score']['total']}/100")
                
                with col2:
                    # Show top 2 experience items
                    if result['experience']:
                        exp_preview = result['experience'][:2]
                        st.markdown("**🏢 Key Experience**")
                        for exp in exp_preview:
                            st.markdown(f"• {exp[:100]}...")
                
                with col3:
                    # Show top education
                    if result['education']:
                        edu_preview = result['education'][:2]
                        st.markdown("**🎓 Key Education**")
                        for edu in edu_preview:
                            st.markdown(f"• {edu[:100]}...")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed View (expandable)
                with st.expander("👉 Click for Detailed Analysis"):
                    # Score breakdown
                    st.subheader("Score Breakdown")
                    score_cols = st.columns(4)
                    with score_cols[0]:
                        st.metric("Experience", f"{result['score']['breakdown']['experience']}/40")
                    with score_cols[1]:
                        st.metric("Education", f"{result['score']['breakdown']['education']}/35")
                    with score_cols[2]:
                        st.metric("Skills", f"{result['score']['breakdown']['skills']}/15")
                    with score_cols[3]:
                        st.metric("Languages", f"{result['score']['breakdown']['languages']}/10")
                    
                    # Full Experience Section
                    if result['experience']:
                        st.markdown('<div class="highlight">', unsafe_allow_html=True)
                        st.subheader("🏢 Full Experience")
                        for exp in result['experience']:
                            st.markdown(f"• {exp}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Full Education Section
                    if result['education']:
                        st.markdown('<div class="highlight">', unsafe_allow_html=True)
                        st.subheader("🎓 Full Education")
                        for edu in result['education']:
                            st.markdown(f"• {edu}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Skills Section
                    if result['skills']:
                        st.markdown('<div class="highlight">', unsafe_allow_html=True)
                        st.subheader("💪 Skills")
                        st.write(", ".join(result['skills']))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Languages Section
                    if result['languages']:
                        st.markdown('<div class="highlight">', unsafe_allow_html=True)
                        st.subheader("🗣 Languages")
                        st.write(", ".join(result['languages']))
                        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
