import os
import shutil
import PyPDF2
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ResumeSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Keyword Sorter")
        self.root.geometry("600x600")

        self.categories = []  # List to store [folder_name, keywords]
        self.source_dir = tk.StringVar()

        # --- UI Layout ---
        # 1. Source Folder Selection
        tk.Label(root, text="Step 1: Select Source Folder", font=('Arial', 10, 'bold')).pack(pady=5)
        btn_browse = tk.Button(root, text="Browse Folder", command=self.browse_folder)
        btn_browse.pack()
        tk.Label(root, textvariable=self.source_dir, fg="blue", wraplength=500).pack()

        # FIXED LINE BELOW: Changed tk to ttk
        ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10, padx=20)

        # 2. Add Category Section
        tk.Label(root, text="Step 2: Add Categories (Folder & Keywords)", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_input = tk.Frame(root)
        frame_input.pack()

        tk.Label(frame_input, text="Folder Name:").grid(row=0, column=0, sticky='e')
        self.ent_folder = tk.Entry(frame_input, width=30)
        self.ent_folder.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_input, text="Keywords (split by comma):").grid(row=1, column=0, sticky='e')
        self.ent_keywords = tk.Entry(frame_input, width=30)
        self.ent_keywords.grid(row=1, column=1, padx=5, pady=2)

        btn_add = tk.Button(root, text="Add Category", command=self.add_category, bg="#e1e1e1")
        btn_add.pack(pady=5)

        # 3. List of Categories
        self.tree = ttk.Treeview(root, columns=("Folder", "Keywords"), show='headings', height=6)
        self.tree.heading("Folder", text="Target Folder")
        self.tree.heading("Keywords", text="Keywords")
        self.tree.column("Folder", width=150)
        self.tree.column("Keywords", width=350)
        self.tree.pack(pady=10, fill='x', padx=20)
        
        btn_remove = tk.Button(root, text="Remove Selected Category", command=self.remove_category)
        btn_remove.pack()

        # 4. Process Button
        self.btn_process = tk.Button(root, text="START SORTING", bg="green", fg="white", 
                                     font=('Arial', 12, 'bold'), command=self.process_files)
        self.btn_process.pack(pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_dir.set(folder)

    def add_category(self):
        folder = self.ent_folder.get().strip()
        keywords = self.ent_keywords.get().strip()
        
        if folder and keywords:
            self.categories.append({"folder": folder, "keywords": [k.strip().lower() for k in keywords.split(",")]})
            self.tree.insert("", "end", values=(folder, keywords))
            self.ent_folder.delete(0, tk.END)
            self.ent_keywords.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please provide both folder name and keywords.")

    def remove_category(self):
        selected_item = self.tree.selection()
        if selected_item:
            # Find the index to remove from list
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
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""

    def process_files(self):
        src = self.source_dir.get()
        if not src or not self.categories:
            messagebox.showerror("Error", "Select source folder and add at least one category.")
            return

        # Create 'Other_Resumes' folder by default
        others_path = os.path.join(src, "Other_Resumes")
        if not os.path.exists(others_path): os.makedirs(others_path)

        files = [f for f in os.listdir(src) if f.lower().endswith('.pdf')]
        
        if not files:
            messagebox.showwarning("No Files", "No PDF files found in the source folder.")
            return

        count = 0
        for filename in files:
            file_path = os.path.join(src, filename)
            text = self.extract_text(file_path)
            matched = False

            for cat in self.categories:
                # Check if any keyword matches as a whole word
                if any(re.search(rf"\b{re.escape(k)}\b", text) for k in cat['keywords']):
                    dest_folder = os.path.join(src, cat['folder'])
                    if not os.path.exists(dest_folder): os.makedirs(dest_folder)
                    shutil.copy(file_path, os.path.join(dest_folder, filename))
                    matched = True
                    break 

            if not matched:
                shutil.copy(file_path, os.path.join(others_path, filename))
            
            count += 1

        messagebox.showinfo("Success", f"Finished! {count} resumes processed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeSorterApp(root)
    root.mainloop()