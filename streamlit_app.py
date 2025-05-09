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
                    'certifications': analysis['certifications'],
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
                with st.expander(f"Results for {filename}"):
                    # Display overall score
                    score = result['score']
                    st.metric("Overall Score", f"{score['total']}/100")
                    
                    # Score breakdown
                    st.subheader("Score Breakdown")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Skills", f"{score['breakdown']['skills']}/30")
                    with col2:
                        st.metric("Education", f"{score['breakdown']['education']}/25")
                    with col3:
                        st.metric("Experience", f"{score['breakdown']['experience']}/25")
                    with col4:
                        st.metric("Languages", f"{score['breakdown']['languages']}/10")
                    with col5:
                        st.metric("Certifications", f"{score['breakdown']['certifications']}/10")
                    
                    # Detailed sections
                    st.subheader("Skills")
                    if result['skills']:
                        st.write(", ".join(result['skills']))
                    else:
                        st.write("No skills detected")
                        
                    st.subheader("Education")
                    if result['education']:
                        for edu in result['education']:
                            st.write(f"• {edu}")
                    else:
                        st.write("No education details detected")
                        
                    st.subheader("Experience")
                    if result['experience']:
                        for exp in result['experience']:
                            st.write(f"• {exp}")
                    else:
                        st.write("No experience details detected")
                        
                    st.subheader("Languages")
                    if result['languages']:
                        st.write(", ".join(result['languages']))
                    else:
                        st.write("No languages detected")
                        
                    st.subheader("Certifications")
                    if result['certifications']:
                        for cert in result['certifications']:
                            st.write(f"• {cert}")
                    else:
                        st.write("No certifications detected")

if __name__ == "__main__":
    main()
