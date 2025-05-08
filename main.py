import os
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
from datetime import datetime
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import sys
import chardet
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Set UTF-8 encoding for proper handling of Swedish characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Folder containing resumes
RESUME_FOLDER = "resumes/"

# Ensure the resumes folder exists
os.makedirs(RESUME_FOLDER, exist_ok=True)

# Enhanced criteria for filtering resumes
CRITERIA = {
    "utbildning": [
        "Undersköterska",
        "Vårdbiträde",
        "Vård- och omsorgsprogrammet",
        "Omvårdnadsprogram",
        "Vårdutbildning",
        "Omvårdnadsutbildning",
        "Äldreomsorgsutbildning",
        "Yrkespaket Vårdbiträde"
    ],
    "kompetenser": [
        "Hemtjänst",
        "Äldreomsorg",
        "Hemsjukvård",
        "Personlig assistans",
        "Vårdhem",
        "Särskilt boende",
        "SÄBO",
        "LSS",
        "Vård",
        "Omsorg",
        "Vårdare",
        "Omsorgsarbete",
        "Sjukvård",
        "Äldrevård",
        "Demensboende",
        "Serviceboende",
        "Gruppboende",
        "Boendestöd",
        "Vårdavdelning",
        "Vårdcentral",
        "Sjukhem",
        "Omsorgsboende",
        "Behandlingsassistent",
        "Stödassistent",
        "Stödpedagog",
        "Undersköterska",
        "Vårdbiträde",
        "Sjukhus",
        "Akutsjukvård",
        "Habilitering",
        "Rehabilitering",
        "Psykiatrisk vård",
        "Social omsorg",
        "Utvecklingsstörning",
        "Funktionshinder",
        "Funktionsnedsättning",
        "Omvårdnad",
        "APL",
        "Äldreboende",  # Added for elderly care
        "Äldre",        # Added for elderly care
        "Senior",       # Added for elderly care
        "Geriatrik",   # Added for elderly care
        "Pensionär"    # Added for elderly care
    ],
    "körkort": [
        "B-körkort",
        "Körkort B",
        "Körkort klass B",
        "Har körkort"
    ],
    "språk": [
        "Svenska",
        "Engelska",
        "English",
        "Swedish",
        "Tigrinja",
        "Tigrinya",
        "Amhariska",
        "Amharic"
    ]
}

def verify_document(file_path):
    """
    Verifies a document to ensure it exists, is a PDF or DOCX, and is readable.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File does not exist at {file_path}"

        if not (file_path.lower().endswith('.pdf') or file_path.lower().endswith('.docx')):
            return "Error: File is not a supported document type (PDF or DOCX)."

        if file_path.lower().endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                if len(reader.pages) > 0:
                    return "Document verification successful."
                else:
                    return "Error: PDF appears to be empty."
            except Exception as e:
                return f"Error: Unable to read PDF file. Details: {e}"
        elif file_path.lower().endswith('.docx'):
            try:
                Document(file_path)
                return "Document verification successful."
            except Exception as e:
                return f"Error: Unable to read DOCX file. Details: {e}"

    except Exception as general_error:
        return f"An unexpected error occurred: {general_error}"

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file with improved encoding handling."""
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = []
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    # Remove the common header
                    content = re.sub(r'Annette Frohm.*?E-post:', '', content, flags=re.DOTALL)
                    text.append(content)
            
            full_text = '\n'.join(text)
            
            # Get the filename without extension as a fallback name
            filename = os.path.splitext(os.path.basename(file_path))[0]
            name = filename.replace('_', ' ')
            
            # Add the name to the beginning of the text
            full_text = f"Name: {name}\n{full_text}"
            
            return full_text
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from a Word file with improved encoding handling."""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        # Ensure proper encoding of Swedish characters
        if not isinstance(text, str):
            encoding = chardet.detect(text.encode())['encoding']
            text = text.encode().decode(encoding or 'utf-8', errors='ignore')
        return text.strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def analyze_resume(content):
    """Analyze the resume content with enhanced metrics."""
    if not content:
        return None
        
    result = {
        'Name': '',
        'Utbildning': '',
        'Kompetenser': [],
        'Erfarenhet': [],
        'Körkort': False,
        'Språk': []
    }
    
    # Split content into lines for better analysis
    lines = content.split('\n')
    current_section = ''
    experience_entry = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Convert line to lowercase for case-insensitive matching
        line_lower = line.lower()
        
        # Skip header/footer lines
        if any(skip in line_lower for skip in ['arbetsförmedlingen', 'fe 8055', 'stockholm', 'sida', 'post', 'besök', 'telefon', 'e-post']):
            continue
            
        # Extract name
        if line.startswith('Name:'):
            result['Name'] = line.replace('Name:', '').strip()
            continue
            
        # Check for competencies
        for comp in CRITERIA['kompetenser']:
            if comp.lower() in line_lower:
                if line not in result['Kompetenser']:
                    result['Kompetenser'].append(line)
        
        # Check for languages
        for lang in CRITERIA['språk']:
            if lang.lower() in line_lower:
                if lang not in result['Språk']:
                    result['Språk'].append(lang)
            
        # Detect sections
        if 'Inriktning Anordnare Period' in line or 'Utbildning' in line:
            current_section = 'education'
            continue
        elif 'Yrke Arbetsgivare Period' in line or 'Erfarenhet' in line:
            current_section = 'experience'
            continue
        elif any(keyword in line_lower for keyword in ['språk', 'language', 'languages', 'språkkunskaper']):
            current_section = 'language'
            continue
            
        # Process content based on section
        if current_section == 'education':
            if any(edu.lower() in line_lower for edu in CRITERIA['utbildning']):
                if result['Utbildning']:
                    result['Utbildning'] += "; " + line
                else:
                    result['Utbildning'] = line
                
        elif current_section == 'experience':
            if any(comp.lower() in line_lower for comp in CRITERIA['kompetenser']):
                if line.startswith('Beskrivning:'):
                    if experience_entry:
                        experience_entry.append(line.replace('Beskrivning:', '').strip())
                        result['Erfarenhet'].append(' - '.join(experience_entry))
                        experience_entry = []
                else:
                    if experience_entry:
                        result['Erfarenhet'].append(' - '.join(experience_entry))
                    experience_entry = [line]
            
        elif current_section == 'language':
            for lang in CRITERIA['språk']:
                if lang.lower() in line_lower and lang not in result['Språk']:
                    result['Språk'].append(lang)
            
        # Check for driver's license
        if any(keyword in line_lower for keyword in ['körkort', 'driver', 'license', 'driving']):
            result['Körkort'] = True
            
    # Add any remaining experience entry
    if experience_entry:
        result['Erfarenhet'].append(' - '.join(experience_entry))
    
    # Clean up experience entries
    result['Erfarenhet'] = [exp for exp in result['Erfarenhet'] 
                           if not any(skip in exp.lower() for skip in ['arbetsförmedlingen', 'fe 8055', 'stockholm'])]
    
    # Clean up competencies and languages
    result['Kompetenser'] = list(set(result['Kompetenser']))  # Remove duplicates
    result['Språk'] = list(set(result['Språk']))  # Remove duplicates
    
    return result

def calculate_criteria_scores(results):
    """Calculate scores for each criterion and overall match."""
    scores = []
    
    for result in results:
        # Initialize score dictionary
        score = {'name': result['Name']}
        
        # Education score (35%)
        education = result.get('Utbildning', 'Not specified')
        if education != 'Not specified':
            score['education_match'] = 1.0
        else:
            score['education_match'] = 0.0
        
        # Relevant Experience score (35%)
        relevant_experience = result.get('Erfarenhet', [])
        if isinstance(relevant_experience, str):
            relevant_experience = [relevant_experience]
        if relevant_experience and relevant_experience[0] != 'None':
            score['experience_match'] = min(1.0, len(relevant_experience) / 3)  # Normalize to 3 relevant experiences
        else:
            score['experience_match'] = 0.0
        
        # Driver's license score (20%)
        license = result.get('Körkort', 'No')
        if license == 'Yes':
            score['drivers_license_match'] = 1.0
        else:
            score['drivers_license_match'] = 0.0
        
        # Language skills score (5%)
        languages = result.get('Språk', [])
        if isinstance(languages, str):
            languages = [languages]

        # Certifications score (5%)
        certifications = result.get('Certifieringar', 'None')
        if certifications != 'None':
            score['certifications_match'] = 1.0
        else:
            score['certifications_match'] = 0.0
        
        # Calculate weighted overall match
        weights = {
            'education_match': 0.35,      # 35%
            'experience_match': 0.35,     # 35%
            'drivers_license_match': 0.20, # 20%
            'certifications_match': 0.05,   # 5%
            'language_match': 0.05       # 5%
        }
        
        score['overall_match'] = sum(
            score[criterion] * weight 
            for criterion, weight in weights.items()
        )
        
        scores.append(score)
    
    return scores

def generate_html_report(results_dict, scores):
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

    for result in results_dict.values():
        name = result.get('Name', '')
        education = result.get('Utbildning', '')
        experience = result.get('Erfarenhet', [])
        if isinstance(experience, str):
            experience = [experience]
        has_license = result.get('Körkort', False)
        languages = result.get('Språk', [])
        if isinstance(languages, str):
            languages = [languages]
        competencies = result.get('Kompetenser', [])
        if isinstance(competencies, str):
            competencies = [competencies]

        html_content.append(f'''
            <div class="cv-item">
                <div class="name">{name}</div>
                
                <div class="detail">
                    <span class="label">Vårdutbildning</span>
                    <div class="content">
                        {education if education else 'Ingen vårdutbildning angiven'}
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Vårdkompetenser</span>
                    <div class="content">
                        {''.join(f"<span class='competence-item'>{comp}</span>" for comp in competencies) if competencies else 'Inga vårdkompetenser angivna'}
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Relevant arbetslivserfarenhet</span>
                    <div class="content">
                        <ul>
                            {''.join(f"<li>{exp}</li>" for exp in experience) if experience else '<li>Ingen relevant erfarenhet angiven</li>'}
                        </ul>
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Körkort</span>
                    <div class="content">
                        {'Ja' if has_license else 'Anges inte'}
                    </div>
                </div>

                <div class="detail">
                    <span class="label">Språkkunskaper</span>
                    <div class="content">
                        <ul>
                            {''.join(f"<li>{lang}</li>" for lang in languages) if languages else '<li>Inga språk angivna</li>'}
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
    
    # Calculate scores (empty for now as we're focusing on qualitative data)
    scores = []
    
    # Generate and save the HTML report
    html_content = generate_html_report(results_dict, scores)
    
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
