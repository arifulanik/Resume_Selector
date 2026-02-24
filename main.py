import os
import shutil
import PyPDF2
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ResumeSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Resume Keyword Sorter")
        self.root.geometry("600x650")

        self.categories = []  
        self.source_dir = tk.StringVar()

        # Define Synonym Mapping
        self.synonym_map = {
            "eee": [
                "electrical and electronics engineering", 
                "electrical & electronics engineering", 
                "electrical and electronic engineering",
                "electrical & electronic engineering",
                "electrical engineering"
            ],
            "cse": [
                "computer science engineering", 
                "computer science & engineering",
                "computer science and engineering", 
                "computer science", 
                "software engineering"
            ],
            "physics": [
                "applied physics", 
                "theoretical physics"
            ]
        }

        # --- UI Layout ---
        tk.Label(root, text="Step 1: Select Source Folder", font=('Arial', 10, 'bold')).pack(pady=5)
        btn_browse = tk.Button(root, text="Browse Folder", command=self.browse_folder)
        btn_browse.pack()
        tk.Label(root, textvariable=self.source_dir, fg="blue", wraplength=500).pack()

        ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10, padx=20)

        tk.Label(root, text="Step 2: Add Categories", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_input = tk.Frame(root)
        frame_input.pack()

        tk.Label(frame_input, text="Folder Name:").grid(row=0, column=0, sticky='e')
        self.ent_folder = tk.Entry(frame_input, width=30)
        self.ent_folder.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_input, text="Main Keyword (e.g. EEE or CSE):").grid(row=1, column=0, sticky='e')
        self.ent_keywords = tk.Entry(frame_input, width=30)
        self.ent_keywords.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(root, text="(Tip: Typing 'EEE' automatically includes full degree names)", font=('Arial', 8, 'italic'), fg="gray").pack()

        btn_add = tk.Button(root, text="Add Category", command=self.add_category, bg="#e1e1e1")
        btn_add.pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("Folder", "Keywords"), show='headings', height=6)
        self.tree.heading("Folder", text="Target Folder")
        self.tree.heading("Keywords", text="Keywords being searched")
        self.tree.column("Folder", width=120)
        self.tree.column("Keywords", width=430)
        self.tree.pack(pady=10, fill='x', padx=20)
        
        btn_remove = tk.Button(root, text="Remove Selected", command=self.remove_category)
        btn_remove.pack()

        self.btn_process = tk.Button(root, text="START SORTING", bg="green", fg="white", 
                                     font=('Arial', 12, 'bold'), command=self.process_files)
        self.btn_process.pack(pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_dir.set(folder)

    def add_category(self):
        folder = self.ent_folder.get().strip()
        raw_input = self.ent_keywords.get().strip().lower()
        
        if folder and raw_input:
            # Check for synonyms
            keywords_to_search = [raw_input]
            if raw_input in self.synonym_map:
                keywords_to_search.extend(self.synonym_map[raw_input])
            
            # Save and display
            self.categories.append({"folder": folder, "keywords": keywords_to_search})
            self.tree.insert("", "end", values=(folder, ", ".join(keywords_to_search)))
            
            self.ent_folder.delete(0, tk.END)
            self.ent_keywords.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Provide folder name and keyword.")

    def remove_category(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_index = self.tree.index(selected_item)
            self.categories.pop(item_index)
            self.tree.delete(selected_item)

    def extract_text(self, pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content = page.extract_text()
                    if content: text += content
            return text.lower()
        except:
            return ""

    def process_files(self):
        src = self.source_dir.get()
        if not src or not self.categories:
            messagebox.showerror("Error", "Setup source folder and categories first.")
            return

        others_path = os.path.join(src, "Other_Resumes")
        if not os.path.exists(others_path): os.makedirs(others_path)

        files = [f for f in os.listdir(src) if f.lower().endswith('.pdf')]
        
        count = 0
        for filename in files:
            file_path = os.path.join(src, filename)
            text = self.extract_text(file_path)
            matched = False

            for cat in self.categories:
                # This Regex handles symbols like & and matches whole phrases
                if any(re.search(rf"\b{re.escape(k)}\b", text) for k in cat['keywords']):
                    dest_folder = os.path.join(src, cat['folder'])
                    if not os.path.exists(dest_folder): os.makedirs(dest_folder)
                    shutil.copy(file_path, os.path.join(dest_folder, filename))
                    matched = True
                    break 

            if not matched:
                shutil.copy(file_path, os.path.join(others_path, filename))
            count += 1

        messagebox.showinfo("Success", f"Done! Processed {count} files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeSorterApp(root)
    root.mainloop()