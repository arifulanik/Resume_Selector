import os
import shutil
import PyPDF2
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess

class ResumeSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Analytics & Sorter Pro")
        self.root.geometry("850x750")
        self.root.configure(bg="#f8f9fa")

        self.categories = []  
        self.source_dir = tk.StringVar()
        
        # Professional Synonym Mapping
        self.synonym_map = {
            "eee": ["electrical and electronics engineering", "electrical & electronics engineering", 
                    "electrical and electronic engineering", "electrical & electronic engineering", "electrical engineering"],
            "cse": ["computer science engineering", "computer science and engineering", "computer science", "software engineering", "it engineering"],
            "physics": ["applied physics", "theoretical physics", "physics department"]
        }

        self.setup_ui()

    def setup_ui(self):
        # Header Area
        header = tk.Frame(self.root, bg="#0d6efd", height=100)
        header.pack(fill='x')
        tk.Label(header, text="Resume Sorter & Analyzer", font=('Segoe UI', 20, 'bold'), fg="white", bg="#0d6efd").pack(pady=25)

        # Main Body
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(padx=30, pady=10, fill='both', expand=True)

        # --- 1. Source Folder Section ---
        card1 = tk.LabelFrame(main_frame, text=" 1. Folder Selection ", font=('Segoe UI', 10, 'bold'), bg="white", padx=15, pady=15)
        card1.pack(fill='x', pady=10)

        tk.Button(card1, text="Select Folder", command=self.browse_folder, bg="#6c757d", fg="white", font=('Segoe UI', 9, 'bold'), relief='flat', padx=15).pack(side='left')
        tk.Label(card1, textvariable=self.source_dir, fg="#495057", bg="white", font=('Segoe UI', 9), wraplength=500, justify="left").pack(side='left', padx=15)

        # --- 2. Configuration Section ---
        card2 = tk.LabelFrame(main_frame, text=" 2. Categories & Keywords ", font=('Segoe UI', 10, 'bold'), bg="white", padx=15, pady=15)
        card2.pack(fill='x', pady=10)

        input_grid = tk.Frame(card2, bg="white")
        input_grid.pack(fill='x')

        tk.Label(input_grid, text="Target Folder Name:", bg="white").grid(row=0, column=0, sticky='w')
        self.ent_folder = tk.Entry(input_grid, width=25, font=('Segoe UI', 10))
        self.ent_folder.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_grid, text="Primary Keyword (e.g. EEE):", bg="white").grid(row=0, column=2, sticky='w')
        self.ent_keywords = tk.Entry(input_grid, width=25, font=('Segoe UI', 10))
        self.ent_keywords.grid(row=0, column=3, padx=10, pady=5)

        tk.Button(card2, text="+ Add to List", command=self.add_category, bg="#198754", fg="white", font=('Segoe UI', 9, 'bold'), relief='flat', width=15).pack(pady=10)

        # --- 3. Results Section ---
        card3 = tk.LabelFrame(main_frame, text=" 3. Live Analytics ", font=('Segoe UI', 10, 'bold'), bg="white", padx=15, pady=15)
        card3.pack(fill='both', expand=True, pady=10)

        # Corrected Styling Logic
        style = ttk.Style()
        style.theme_use('clam') # Use a theme that supports more styling
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=30)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background="#e9ecef")

        self.tree = ttk.Treeview(card3, columns=("Folder", "Keywords", "Count"), show='headings', height=6)
        self.tree.heading("Folder", text="Destination Folder")
        self.tree.heading("Keywords", text="Keywords Filter")
        self.tree.heading("Count", text="Resumes Found")
        
        self.tree.column("Folder", width=150)
        self.tree.column("Keywords", width=400)
        self.tree.column("Count", width=120, anchor='center')
        self.tree.pack(fill='both', expand=True, side='left')

        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(card3, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind("<Double-1>", self.on_double_click)

        # Action Buttons
        btn_row = tk.Frame(main_frame, bg="#f8f9fa")
        btn_row.pack(fill='x', pady=5)

        tk.Button(btn_row, text="Delete Selected", command=self.remove_category, bg="#dc3545", fg="white", relief='flat', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(btn_row, text="Open Result Folder", command=self.open_selected_folder, bg="#ffc107", fg="black", relief='flat', font=('Segoe UI', 9)).pack(side='right', padx=5)

        # Process Button
        self.btn_process = tk.Button(self.root, text="🚀 RUN SORTING ENGINE", command=self.process_files, 
                                     bg="#0d6efd", fg="white", font=('Segoe UI', 13, 'bold'), relief='flat', pady=15)
        self.btn_process.pack(fill='x', side='bottom', padx=30, pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder: self.source_dir.set(folder)

    def add_category(self):
        folder = self.ent_folder.get().strip()
        raw_key = self.ent_keywords.get().strip().lower()
        if folder and raw_key:
            keys = [raw_key]
            if raw_key in self.synonym_map: keys.extend(self.synonym_map[raw_key])
            self.categories.append({"folder": folder, "keywords": keys, "count": 0})
            self.tree.insert("", "end", values=(folder, ", ".join(keys), "0"))
            self.ent_folder.delete(0, tk.END); self.ent_keywords.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Missing", "Please enter both folder name and keyword.")

    def remove_category(self):
        selected = self.tree.selection()
        if selected:
            for item in selected:
                idx = self.tree.index(item)
                self.categories.pop(idx)
                self.tree.delete(item)

    def open_selected_folder(self):
        selected = self.tree.selection()
        if not selected: 
            messagebox.showinfo("Hint", "Select a row from the table first.")
            return
        folder_name = self.tree.item(selected[0])['values'][0]
        path = os.path.normpath(os.path.join(self.source_dir.get(), str(folder_name)))
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showinfo("Not Found", "Folder not created yet. Please click 'Run Sorting Engine' first.")

    def on_double_click(self, event):
        self.open_selected_folder()

    def extract_text(self, pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content: text += content
            return text.lower()
        except: return ""

    def process_files(self):
        src = self.source_dir.get()
        if not src or not self.categories:
            messagebox.showerror("Setup Error", "Select source folder and add at least one category.")
            return

        for cat in self.categories: cat['count'] = 0
        others_count = 0
        others_path = os.path.join(src, "Other_Resumes")
        if not os.path.exists(others_path): os.makedirs(others_path)

        files = [f for f in os.listdir(src) if f.lower().endswith('.pdf')]
        
        for filename in files:
            file_path = os.path.join(src, filename)
            text = self.extract_text(file_path)
            matched = False

            for cat in self.categories:
                if any(re.search(rf"\b{re.escape(k)}\b", text) for k in cat['keywords']):
                    dest = os.path.join(src, cat['folder'])
                    if not os.path.exists(dest): os.makedirs(dest)
                    shutil.copy(file_path, os.path.join(dest, filename))
                    cat['count'] += 1
                    matched = True
                    break

            if not matched:
                shutil.copy(file_path, os.path.join(others_path, filename))
                others_count += 1

        # Update table view
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(self.categories[i]['folder'], ", ".join(self.categories[i]['keywords']), self.categories[i]['count']))

        messagebox.showinfo("Process Complete", f"Successfully sorted {len(files)} resumes.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeSorterApp(root)
    root.mainloop()