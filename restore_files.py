import os
import shutil

# Directory containing the resumes
resume_dir = "resumes"

# Mapping of new names to original names (reverse of previous mapping)
name_mapping = {
    "Candidate_001.pdf": "Betty.A CV.pdf",
    "Candidate_002.pdf": "Buser cv _kopia.pdf",
    "Candidate_003.pdf": "CV - MURALI GUNASEKARAN .pdf",
    "Candidate_004.docx": "CV Ruslan Khaydarov Universal.docx",
    "Candidate_005.docx": "IREM KOCAMAN kopyası.docx",
    "Candidate_006.pdf": "Reem CV - Google Dokument.pdf",
    "Candidate_007.docx": "Teresia+CV.docx",
    "Candidate_008.doc": "CV Mic.doc",
    "Candidate_009.docx": "CV.docx",
    "Candidate_010.pdf": "CV 2024.pdf.pdf",
    "Candidate_011.pdf": "CV-1 (1).pdf"
}

def restore_files():
    """Restore files to their original names."""
    for new_name, old_name in name_mapping.items():
        new_path = os.path.join(resume_dir, new_name)
        old_path = os.path.join(resume_dir, old_name)
        
        if os.path.exists(new_path):
            # Create a backup copy first
            backup_path = new_path + ".backup"
            shutil.copy2(new_path, backup_path)
            
            try:
                os.rename(new_path, old_path)
                print(f"Restored: {new_name} -> {old_name}")
            except Exception as e:
                print(f"Error restoring {new_name}: {e}")
                # Restore from backup
                shutil.copy2(backup_path, new_path)
            finally:
                # Clean up backup
                if os.path.exists(backup_path):
                    os.remove(backup_path)
        else:
            print(f"File not found: {new_name}")

if __name__ == "__main__":
    restore_files()
