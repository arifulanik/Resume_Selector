import os
import shutil
import PyPDF2
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ResumeSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Analytics & Sorter Pro")
        self.root.geometry("850x750")
        self.root.configure(bg="#f8f9fa")

        self.categories = []  
        self.source_dir = tk.StringVar()
        
        # Expanded Synonym Mapping - handles different variations
        self.synonym_map = {
            "eee": [
                "electrical and electronics engineering", 
                "electrical & electronics engineering", 
                "electrical and electronic engineering", 
                "electrical & electronic engineering", 
                "electrical engineering",
                "electronics and electrical"
            ],
            "cse": [
                "computer science engineering", 
                "computer science and engineering", 
                "computer science", 
                "software engineering", 
                "it engineering"
            ],
            "physics": ["applied physics", "theoretical physics", "physics department"]
        }

        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#0d6efd", height=100)
        header.pack(fill='x')
        tk.Label(header, text="Resume Sorter & Analyzer", font=('Segoe UI', 20, 'bold'), fg="white", bg="#0d6efd").pack(pady=25)

        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(padx=30, pady=10, fill='both', expand=True)

        card1 = tk.LabelFrame(main_frame, text=" 1. Folder Selection ", font=('Segoe UI', 10, 'bold'), bg="white", padx=15, pady=15)
        card1.pack(fill='x', pady=10)
        tk.Button(card1, text="Select Folder", command=self.browse_folder, bg="#6c757d", fg="white", font=('Segoe UI', 9, 'bold'), relief='flat', padx=15).pack(side='left')
        tk.Label(card1, textvariable=self.source_dir, fg="#495057", bg="white", font=('Segoe UI', 9), wraplength=500, justify="left").pack(side='left', padx=15)

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

        card3 = tk.LabelFrame(main_frame, text=" 3. Live Analytics ", font=('Segoe UI', 10, 'bold'), bg="white", padx=15, pady=15)
        card3.pack(fill='both', expand=True, pady=10)
        style = ttk.Style()
        style.theme_use('clam')
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
        self.tree.bind("<Double-1>", self.on_double_click)

        btn_row = tk.Frame(main_frame, bg="#f8f9fa")
        btn_row.pack(fill='x', pady=5)
        tk.Button(btn_row, text="Delete Selected", command=self.remove_category, bg="#dc3545", fg="white", relief='flat').pack(side='left', padx=5)
        tk.Button(btn_row, text="Open Result Folder", command=self.open_selected_folder, bg="#ffc107", fg="black", relief='flat').pack(side='right', padx=5)

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

    def remove_category(self):
        selected = self.tree.selection()
        if selected:
            for item in selected:
                idx = self.tree.index(item)
                self.categories.pop(idx); self.tree.delete(item)

    def open_selected_folder(self):
        selected = self.tree.selection()
        if not selected: return
        folder_name = self.tree.item(selected[0])['values'][0]
        path = os.path.normpath(os.path.join(self.source_dir.get(), str(folder_name)))
        if os.path.exists(path): os.startfile(path)

    def on_double_click(self, event):
        self.open_selected_folder()

    def extract_and_clean_text(self, pdf_path):
        """Extracts text and removes extra spaces/newlines for better matching."""
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content: text += " " + content
            
            # THE FIX: Replace all newlines/tabs with space, then shrink multiple spaces to one
            text = text.lower()
            text = re.sub(r'\s+', ' ', text).strip() 
            return text
        except: return ""

    def process_files(self):
        src = self.source_dir.get()
        if not src or not self.categories: return

        for cat in self.categories: cat['count'] = 0
        others_path = os.path.join(src, "Other_Resumes")
        if not os.path.exists(others_path): os.makedirs(others_path)

        files = [f for f in os.listdir(src) if f.lower().endswith('.pdf')]
        
        for filename in files:
            file_path = os.path.join(src, filename)
            text = self.extract_and_clean_text(file_path) # Using the new cleaning function
            matched = False

            for cat in self.categories:
                # Search using the cleaned text
                if any(re.search(rf"\b{re.escape(k)}\b", text) for k in cat['keywords']):
                    dest = os.path.join(src, cat['folder'])
                    if not os.path.exists(dest): os.makedirs(dest)
                    shutil.copy(file_path, os.path.join(dest, filename))
                    cat['count'] += 1
                    matched = True
                    break

            if not matched:
                shutil.copy(file_path, os.path.join(others_path, filename))

        # Update table
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(self.categories[i]['folder'], ", ".join(self.categories[i]['keywords']), self.categories[i]['count']))
        messagebox.showinfo("Done", "Resumes have been sorted.")

if __name__ == "__main__":
    root = tk.Tk(); app = ResumeSorterApp(root); root.mainloop()