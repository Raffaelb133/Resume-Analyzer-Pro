import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
import main as resume_processor
import webbrowser

class ResumeAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Analyzer")
        
        # Set window size and position
        window_width = 600
        window_height = 400
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=10)
        style.configure('Header.TLabel', font=('Helvetica', 24))
        style.configure('Info.TLabel', font=('Helvetica', 12))
        
        # Create main container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Add widgets
        ttk.Label(main_frame, text="Resume Analyzer", style='Header.TLabel').grid(column=0, row=0, columnspan=2, pady=20)
        
        ttk.Label(main_frame, text="Selected Files:", style='Info.TLabel').grid(column=0, row=1, sticky=tk.W, pady=(20,5))
        
        # Create listbox for selected files
        self.file_listbox = tk.Listbox(main_frame, height=8, width=50)
        self.file_listbox.grid(column=0, row=2, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        # Add scrollbar to listbox
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(column=2, row=2, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(column=0, row=3, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Select Files", command=self.select_files).grid(column=0, row=0, padx=5)
        ttk.Button(button_frame, text="Clear Files", command=self.clear_files).grid(column=1, row=0, padx=5)
        ttk.Button(button_frame, text="Analyze Resumes", command=self.analyze_resumes).grid(column=2, row=0, padx=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=500)
        self.status_label.grid(column=0, row=4, columnspan=2, pady=10)
        
        self.selected_files = []

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Resume Files",
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")]
        )
        if files:
            # Clear existing files in resumes directory
            resumes_dir = "resumes"
            if os.path.exists(resumes_dir):
                for file in os.listdir(resumes_dir):
                    file_path = os.path.join(resumes_dir, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
            else:
                os.makedirs(resumes_dir)
            
            # Copy new files
            self.selected_files = []
            self.file_listbox.delete(0, tk.END)
            for file in files:
                filename = os.path.basename(file)
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, filename)
                shutil.copy2(file, os.path.join(resumes_dir, filename))
            
            self.status_var.set(f"Selected {len(files)} files")

    def clear_files(self):
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.status_var.set("All files cleared")

    def analyze_resumes(self):
        if not self.selected_files:
            self.status_var.set("Please select some resume files first")
            return
        
        try:
            self.status_var.set("Analyzing resumes...")
            self.root.update()
            
            resume_processor.main()
            
            report_path = os.path.abspath('resume_report.html')
            webbrowser.open('file://' + report_path)
            
            self.status_var.set("Analysis complete! Opening report in your browser.")
        except Exception as e:
            self.status_var.set(f"Error during analysis: {str(e)}")

def main():
    root = tk.Tk()
    app = ResumeAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
