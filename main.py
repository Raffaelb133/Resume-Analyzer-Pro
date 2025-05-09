import re
import os
import sys
import nltk
from docx import Document
from PyPDF2 import PdfReader
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import webbrowser
import chardet
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template

# Initialize NLTK and download required data
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

# Folder containing resumes
RESUME_FOLDER = "resumes/"

# Ensure the resumes folder exists
os.makedirs(RESUME_FOLDER, exist_ok=True)

def analyze_resume(text):
    """Analyze resume text using NLTK"""
    # Tokenize the text
    sentences = nltk.sent_tokenize(text)
    words = nltk.word_tokenize(text)
    
    analysis = {
        'skills': extract_skills(text),
        'education': extract_education(sentences),
        'experience': extract_experience(sentences),
        'languages': extract_languages(text),
        'certifications': extract_certifications(sentences)
    }
    return analysis

def extract_skills(text):
    """Extract skills focused on home care"""
    # Home care specific skills
    care_skills = {
        'medical': [
            'medicinhantering', 'sårvård', 'insulin', 'blodtryck', 'första hjälpen',
            'hygien', 'förflyttningsteknik', 'lyftkörkort', 'dokumentation'
        ],
        'practical': [
            'matlagning', 'städning', 'tvätt', 'inköp', 'personlig hygien',
            'dusch', 'påklädning', 'toalettbesök', 'förflyttning'
        ],
        'social': [
            'kommunikation', 'bemötande', 'social aktivitet', 'empati',
            'tålamod', 'lyhörd', 'samarbete', 'flexibel', 'serviceorienterad'
        ],
        'technical': [
            'dokumentationssystem', 'treserva', 'phoniro', 'procapita',
            'office', 'excel', 'outlook', 'tidrapportering'
        ]
    }
    
    found_skills = set()
    text_lower = text.lower()
    
    # Check for care-specific skills
    for category, skills in care_skills.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.add(skill)
    
    return list(found_skills)

def extract_education(sentences):
    """Extract education information focused on healthcare and caregiving"""
    education = []
    edu_keywords = [
        # Swedish healthcare education
        'undersköterska', 'vårdbiträde', 'sjuksköterska', 'omvårdnad', 'vård och omsorg',
        'hemtjänst utbildning', 'vårdutbildning', 'omsorgsutbildning',
        # General education terms
        'utbildning', 'kurs', 'gymnasium', 'komvux', 'yrkesutbildning',
        'certifikat', 'diplom', 'betyg',
        # Healthcare terms in English
        'nursing', 'healthcare', 'care', 'medical', 'first aid', 'elderly care',
        'home care', 'caregiver', 'nursing assistant'
    ]
    
    for sentence in sentences:
        sent_lower = sentence.lower()
        if any(keyword in sent_lower for keyword in edu_keywords):
            clean_sent = sentence.strip()
            if clean_sent and clean_sent not in education:
                education.append(clean_sent)
    
    return education

def extract_experience(sentences):
    """Extract work experience information focused on home care"""
    experience = []
    exp_keywords = [
        # Swedish home care terms
        'hemtjänst', 'vårdbiträde', 'undersköterska', 'personlig assistent',
        'äldreboende', 'vård och omsorg', 'omvårdnad', 'omsorg',
        'serviceboende', 'hemsjukvård', 'boendestöd',
        # Work-related terms
        'erfarenhet', 'arbetade', 'jobbade', 'anställd', 'ansvarig',
        # Care-related activities
        'medicinhantering', 'sårvård', 'personlig hygien', 'städning',
        'matlagning', 'inköp', 'social aktivitet', 'dokumentation',
        # English terms
        'home care', 'elderly care', 'personal care', 'assisted living',
        'caregiver', 'care assistant', 'nursing home', 'senior care'
    ]
    
    for sentence in sentences:
        sent_lower = sentence.lower()
        # Look for dates or experience keywords
        has_date = bool(re.search(r'\b(19|20)\d{2}\b', sentence))
        has_keyword = any(keyword in sent_lower for keyword in exp_keywords)
        
        if has_date or has_keyword:
            clean_sent = sentence.strip()
            if clean_sent and clean_sent not in experience:
                experience.append(clean_sent)
    
    return experience

def extract_languages(text):
    """Extract language skills"""
    languages = {
        'english', 'spanish', 'french', 'german', 'chinese', 'japanese',
        'arabic', 'russian', 'portuguese', 'italian', 'swedish', 'norwegian',
        'danish', 'dutch', 'korean', 'hindi', 'bengali', 'urdu', 'turkish',
        'vietnamese', 'thai', 'indonesian', 'malay', 'filipino', 'greek'
    }
    
    found_languages = set()
    text_lower = text.lower()
    
    for lang in languages:
        if lang in text_lower:
            found_languages.add(lang)
    
    return list(found_languages)

def extract_certifications(sentences):
    """Extract certifications"""
    certifications = []
    cert_keywords = ['certified', 'certification', 'certificate', 'license', 'diploma',
                    'accredited', 'qualified']
    
    for sentence in sentences:
        sent_lower = sentence.lower()
        if any(keyword in sent_lower for keyword in cert_keywords):
            clean_sent = sentence.strip()
            if clean_sent and clean_sent not in certifications:
                certifications.append(clean_sent)
    
    return certifications

def calculate_score(analysis):
    """Calculate a comprehensive score based on the analysis with focus on experience and education"""
    score = 0
    
    # Experience score (up to 40 points) - Increased weight
    exp_score = min(len(analysis['experience']) * 8, 40)
    score += exp_score
    
    # Education score (up to 35 points) - Increased weight
    edu_score = min(len(analysis['education']) * 7, 35)
    score += edu_score
    
    # Skills score (up to 15 points) - Decreased weight
    skill_score = min(len(analysis['skills']) * 1.5, 15)
    score += skill_score
    
    # Languages score (up to 10 points) - Same weight
    lang_score = min(len(analysis['languages']) * 2, 10)
    score += lang_score
    
    return {
        'total': score,
        'breakdown': {
            'experience': exp_score,  # Most important
            'education': edu_score,   # Second most important
            'skills': skill_score,    # Less weight
            'languages': lang_score    # Same weight
        }
    }

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    try:
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from a Word file"""
    try:
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def generate_html_report(results_dict):
    html_content = []
    html_content.append('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CV Sammanfattning</title>
            <style>
                :root {
                    --primary-color: #2563eb;
                    --background-color: #f8fafc;
                    --text-color: #1e293b;
                    --border-color: #e2e8f0;
                    --tag-bg: #e0e7ff;
                    --tag-color: #3730a3;
                }
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    background: var(--background-color);
                    color: var(--text-color);
                }
                
                .container {
                    max-width: 1000px;
                    margin: 2rem auto;
                    padding: 0 1rem;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 3rem;
                    padding: 2rem 0;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                    color: var(--primary-color);
                    margin-bottom: 1rem;
                }
                
                .cv-list {
                    display: grid;
                    gap: 2rem;
                }
                
                .cv-item {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    padding: 2rem;
                    transition: transform 0.2s ease;
                }
                
                .cv-item:hover {
                    transform: translateY(-2px);
                }
                
                .name {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--primary-color);
                    margin-bottom: 1.5rem;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid var(--border-color);
                }
                
                .detail {
                    margin: 1.5rem 0;
                }
                
                .label {
                    display: block;
                    font-weight: 600;
                    color: var(--text-color);
                    margin-bottom: 0.5rem;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                
                .content {
                    background: var(--background-color);
                    padding: 1rem;
                    border-radius: 8px;
                }
                
                ul {
                    list-style: none;
                }
                
                li {
                    margin: 0.5rem 0;
                    padding-left: 1.5rem;
                    position: relative;
                }
                
                li:before {
                    content: "•";
                    color: var(--primary-color);
                    position: absolute;
                    left: 0;
                }
                
                .competence-item {
                    display: inline-block;
                    background: var(--tag-bg);
                    color: var(--tag-color);
                    padding: 0.3rem 0.8rem;
                    margin: 0.25rem;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: 500;
                    transition: all 0.2s ease;
                }
                
                .competence-item:hover {
                    transform: scale(1.05);
                }
                
                @media (max-width: 768px) {
                    .container {
                        margin: 1rem auto;
                    }
                    
                    .cv-item {
                        padding: 1.5rem;
                    }
                    
                    .header h1 {
                        font-size: 2rem;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header class="header">
                    <h1>CV Sammanfattning</h1>
                </header>
                <div class="cv-list">
    ''')

    for name, result in results_dict.items():
        html_content.append(f'''
            <div class="cv-item">
                <div class="name">{name}</div>
                
                <div class="detail">
                    <span class="label">Färdigheter</span>
                    <div class="content">
                        {''.join(f"<span class='competence-item'>{skill}</span>" for skill in result['skills']) if result['skills'] else 'Inga färdigheter angivna'}
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Utbildning</span>
                    <div class="content">
                        <ul>
                            {''.join(f"<li>{edu}</li>" for edu in result['education']) if result['education'] else '<li>Ingen utbildning angiven</li>'}
                        </ul>
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Arbetslivserfarenhet</span>
                    <div class="content">
                        <ul>
                            {''.join(f"<li>{exp}</li>" for exp in result['experience']) if result['experience'] else '<li>Ingen arbetslivserfarenhet angiven</li>'}
                        </ul>
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Språkkunskaper</span>
                    <div class="content">
                        <ul>
                            {''.join(f"<li>{lang}</li>" for lang in result['languages']) if result['languages'] else '<li>Inga språk angivna</li>'}
                        </ul>
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Certifikat</span>
                    <div class="content">
                        <ul>
                            {''.join(f"<li>{cert}</li>" for cert in result['certifications']) if result['certifications'] else '<li>Inga certifikat angivna</li>'}
                        </ul>
                    </div>
                </div>
            </div>
        ''')

    html_content.append('''
                </div>
            </div>
        </body>
        </html>
    ''')

    return ''.join(html_content)

def send_email_report(recipient_email, sender_email, sender_password):
    """Send the resume report via email"""
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = 'Resume Analysis Report'

        # Add body text
        body = 'Please find attached the resume analysis report.'
        msg.attach(MIMEText(body, 'plain'))

        # Attach the HTML report
        with open('resume_report.html', 'r', encoding='utf-8') as f:
            attachment = MIMEText(f.read(), 'html')
            attachment.add_header('Content-Disposition', 'attachment', filename='resume_report.html')
            msg.attach(attachment)

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.send_message(msg)
        server.quit()
        print(f'Report sent successfully to {recipient_email}')
        return True
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return False

def main():
    # Process all resumes in the folder
    results = []
    for filename in os.listdir(RESUME_FOLDER):
        if filename.startswith('.'):  # Skip hidden files like .DS_Store
            continue
            
        file_path = os.path.join(RESUME_FOLDER, filename)
        try:
            if verify_document(file_path):
                if file_path.lower().endswith('.pdf'):
                    content = extract_text_from_pdf(file_path)
                else:
                    content = extract_text_from_docx(file_path)
                
                result = analyze_resume(content)
                if result:
                    # Add filename as name if not found in content
                    if 'Name' not in result or not result['Name']:
                        result['Name'] = os.path.splitext(filename)[0].replace('_', ' ')
                    results.append(result)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    # Convert results to dictionary
    results_dict = {result['Name']: result for result in results}
    
    # Calculate scores
    scores = [calculate_score(result) for result in results_dict.values()]
    
    # Generate and save the HTML report
    html_content = generate_html_report(results_dict)
    
    # Save the report
    report_file = 'resume_report.html'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Save results to CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv('cv_report.csv', index=False, encoding='utf-8')
        print(f"Successfully processed {len(results)} resumes")

if __name__ == "__main__":
    main()
    # Open the generated report in the default web browser
    report_path = os.path.abspath('resume_report.html')
    print(f"Opening report: {report_path}")
    webbrowser.open('file://' + report_path)
