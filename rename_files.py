import os
import shutil

# Directory containing the resumes
resume_dir = "resumes"

# Mapping of old names to new names
name_mapping = {
    "Betty.A CV.pdf": "Candidate_001.pdf",
    "Buser cv _kopia.pdf": "Candidate_002.pdf",
    "CV - MURALI GUNASEKARAN .pdf": "Candidate_003.pdf",
    "CV Ruslan Khaydarov Universal.docx": "Candidate_004.docx",
    "IREM KOCAMAN kopyası.docx": "Candidate_005.docx",
    "Reem CV - Google Dokument.pdf": "Candidate_006.pdf",
    "Teresia+CV.docx": "Candidate_007.docx",
    "CV Mic.doc": "Candidate_008.doc",
    "CV.docx": "Candidate_009.docx",
    "CV 2024.pdf.pdf": "Candidate_010.pdf",
    "CV-1 (1).pdf": "Candidate_011.pdf"
}

def rename_files():
    """Rename files according to the mapping."""
    for old_name, new_name in name_mapping.items():
        old_path = os.path.join(resume_dir, old_name)
        new_path = os.path.join(resume_dir, new_name)
        
        if os.path.exists(old_path):
            # Create a backup copy first
            backup_path = old_path + ".backup"
            shutil.copy2(old_path, backup_path)
            
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {old_name} -> {new_name}")
            except Exception as e:
                print(f"Error renaming {old_name}: {e}")
                # Restore from backup
                shutil.copy2(backup_path, old_path)
            finally:
                # Clean up backup
                if os.path.exists(backup_path):
                    os.remove(backup_path)
        else:
            print(f"File not found: {old_name}")

if __name__ == "__main__":
    rename_files()
