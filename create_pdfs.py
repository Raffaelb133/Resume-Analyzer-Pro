from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def convert_txt_to_pdf(txt_file, pdf_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Custom',
        fontSize=11,
        leading=14,
        spaceAfter=10
    ))
    
    # Convert content to paragraphs
    story = []
    for line in content.split('\n'):
        if line.strip():
            if line.isupper():  # Headers
                p = Paragraph(line, styles['Heading1'])
            else:
                p = Paragraph(line, styles['Custom'])
            story.append(p)
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)

# Convert all txt files in resumes folder
resumes_dir = 'resumes'
for filename in os.listdir(resumes_dir):
    if filename.endswith('.txt'):
        txt_path = os.path.join(resumes_dir, filename)
        pdf_path = os.path.join(resumes_dir, filename.replace('.txt', '.pdf'))
        convert_txt_to_pdf(txt_path, pdf_path)
        # Remove the txt file after conversion
        os.remove(txt_path)

print("PDF conversion completed!")
