import streamlit as st
import os
import shutil
import main as resume_processor
import base64
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Modern color palette */
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #3b82f6;
            --accent: #60a5fa;
            --background: #f8fafc;
            --surface: #ffffff;
            --text: #0f172a;
            --text-light: #475569;
            --success: #22c55e;
            --border: #e2e8f0;
        }

        /* Global styles */
        .stApp {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        }
        
        /* Main container */
        .main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Headers */
        h1 {
            color: var(--text);
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            margin-bottom: 1rem !important;
            text-align: center;
            letter-spacing: -0.025em;
        }
        
        h2 {
            color: var(--text);
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin-top: 2rem !important;
            letter-spacing: -0.025em;
        }
        
        /* Upload zone */
        .upload-container {
            padding: 3rem;
            border: 2px dashed var(--primary);
            border-radius: 1rem;
            background: var(--surface);
            text-align: center;
            margin: 2rem 0;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                       0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        .upload-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
                       0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border-color: var(--primary-dark);
        }
        
        /* Success message */
        .success-message {
            padding: 1rem 1.5rem;
            background: linear-gradient(to right, #ecfdf5, #d1fae5);
            border-left: 4px solid var(--success);
            margin: 1rem 0;
            border-radius: 0.5rem;
            animation: slideIn 0.5s ease-out;
            color: #065f46;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(-20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(to right, var(--primary), var(--secondary));
        }
        
        /* Download button */
        .download-button {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white !important;
            text-decoration: none !important;
            border-radius: 0.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            font-weight: 500;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .download-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            filter: brightness(110%);
        }
        
        /* File list */
        .file-list {
            background: var(--surface);
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Sections */
        .section {
            padding: 2rem;
            background: var(--surface);
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 1.5rem 0;
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }
        
        .section:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        /* Instructions */
        .instructions {
            background: linear-gradient(135deg, #eff6ff, #dbeafe);
            padding: 2rem;
            border-radius: 1rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            color: var(--text);
            border: 1px solid #bfdbfe;
        }
        
        .instructions h3 {
            color: var(--primary-dark);
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .instructions ol {
            margin-left: 1.2rem;
            padding-left: 0;
        }
        
        .instructions li {
            margin: 1rem 0;
            color: var(--text);
            line-height: 1.5;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 3rem 2rem 2rem;
            color: var(--text-light);
            background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.02));
        }
        
        /* Report container */
        .report-container {
            background: var(--surface);
            border-radius: 1rem;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* File item */
        .file-item {
            display: flex;
            align-items: center;
            padding: 1rem 1.25rem;
            background: var(--surface);
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
            color: var(--text);
        }
        
        .file-item:hover {
            background: #f8fafc;
            transform: translateX(2px);
        }

        /* Text styles */
        p {
            color: var(--text);
            line-height: 1.6;
        }

        /* Custom Streamlit modifications */
        .stSelectbox label,
        .stTextInput label {
            color: var(--text) !important;
        }

        .stButton>button {
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            filter: brightness(110%);
            transform: translateY(-1px);
        }

        /* Make text inputs and selects more modern */
        .stTextInput>div>div>input,
        .stSelectbox>div>div>select {
            border-radius: 0.5rem !important;
            border: 1px solid var(--border) !important;
            padding: 0.5rem 1rem !important;
        }

        /* Improve expander styling */
        .streamlit-expanderHeader {
            background: var(--surface) !important;
            border-radius: 0.5rem !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
        }
    </style>
""", unsafe_allow_html=True)

def save_uploaded_files(uploaded_files):
    """Save uploaded files and return the number of files saved."""
    if os.path.exists("resumes"):
        shutil.rmtree("resumes")
    os.makedirs("resumes")
    
    for uploaded_file in uploaded_files:
        file_path = os.path.join("resumes", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    return len(uploaded_files)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """Generate HTML for file download button."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="download-button">Download {file_label}</a>'

# App header with logo and title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='color: #6366f1;'>Resume Analyzer Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #475569; margin-bottom: 2rem;'>Professional Resume Analysis Tool</p>", unsafe_allow_html=True)

# Main content area
main_container = st.container()
with main_container:
    # Instructions section
    with st.expander("How to Use", expanded=True):
        st.markdown("""
            <div class='instructions'>
                <h3>Quick Start Guide</h3>
                <ol>
                    <li><strong>Upload Files:</strong> Drag and drop your resume files (PDF or DOCX)</li>
                    <li><strong>Automatic Analysis:</strong> Our AI will process your resumes instantly</li>
                    <li><strong>View Results:</strong> Get detailed insights and visualizations</li>
                    <li><strong>Download Report:</strong> Save your analysis for later use</li>
                </ol>
                <p><strong>Supported Formats:</strong> PDF (.pdf), Microsoft Word (.docx)</p>
            </div>
        """, unsafe_allow_html=True)

    # Upload section
    st.markdown("<h2 style='color: #4f46e5;'>Upload Resumes</h2>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drag and drop your files here",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="You can upload multiple resumes at once"
    )

    if not uploaded_files:
        st.markdown("""
            <div class='upload-container fade-in'>
                <h3 style='color: #4f46e5; margin-bottom: 1rem;'>Ready to Analyze Your Resumes</h3>
                <p style='font-size: 1.1rem; margin-bottom: 1rem; color: #0f172a;'>Drop your files here or click to browse</p>
                <p style='color: #475569; font-size: 0.9rem;'>Supported formats: PDF, DOCX</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='section fade-in'>", unsafe_allow_html=True)
        
        # Show uploaded files
        st.markdown("<h3>Uploaded Files</h3>", unsafe_allow_html=True)
        for file in uploaded_files:
            st.markdown(f"""
                <div class='file-item'>
                    <span>{file.name}</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Process files with progress bar
        with st.spinner("Analyzing resumes..."):
            progress_bar = st.progress(0)
            
            # Save files
            num_files = save_uploaded_files(uploaded_files)
            progress_bar.progress(33)
            
            # Analysis
            time.sleep(0.5)  # Visual feedback
            progress_bar.progress(66)
            resume_processor.main()
            progress_bar.progress(100)
            
            # Success message
            st.markdown(
                f"""<div class='success-message'>
                    Successfully analyzed {num_files} {'resume' if num_files == 1 else 'resumes'}!
                </div>""",
                unsafe_allow_html=True
            )
        
        # Show report
        if os.path.exists("resume_report.html"):
            st.markdown("<h2>Analysis Report</h2>", unsafe_allow_html=True)
            
            st.markdown("<div class='report-container'>", unsafe_allow_html=True)
            with open("resume_report.html", "r", encoding='utf-8') as f:
                report_content = f.read()
            st.components.v1.html(report_content, height=600, scrolling=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Download section
            st.markdown("<h3>Download Report</h3>", unsafe_allow_html=True)
            st.markdown(
                get_binary_file_downloader_html("resume_report.html", "Analysis Report"),
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class='footer'>
        <p style='font-size: 1.1rem; margin-bottom: 0.5rem; color: #1e293b;'>Resume Analyzer Pro</p>
        <p style='font-size: 0.9rem; color: #475569;'>Professional Resume Analysis Tool</p>
        <p style='font-size: 0.8rem; margin-top: 1rem; color: #64748b;'> 2025 All Rights Reserved</p>
    </div>
""", unsafe_allow_html=True)
