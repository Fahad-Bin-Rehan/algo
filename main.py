import tkinter as tk
from tkinter import filedialog, messagebox, Text
import os
import time

# Function for Brute Force Search
def brute_force_search(text, pattern, case_sensitive=True, whole_word=True):
    positions = []
    if not case_sensitive:
        text, pattern = text.lower(), pattern.lower()
    
    text_split = text.splitlines()
    for row, line in enumerate(text_split):
        start = 0
        while start < len(line):
            start = line.find(pattern, start)
            if start == -1:
                break
            if whole_word:
                if (start == 0 or line[start - 1] == ' ') and (start + len(pattern) == len(line) or line[start + len(pattern)] == ' '):
                    positions.append((row + 1, start + 1))
            else:
                positions.append((row + 1, start + 1))
            start += len(pattern)
    return positions

# Function for KMP Search
def kmp_search(text, pattern, case_sensitive=True, whole_word=True):
    positions = []
    if not case_sensitive:
        text, pattern = text.lower(), pattern.lower()
    
    # Preprocess pattern to create "lps" array (longest prefix suffix)
    lps = [0] * len(pattern)
    j = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
            i += 1
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                lps[i] = 0
                i += 1

    text_split = text.splitlines()
    for row, line in enumerate(text_split):
        i = 0  # index for line
        j = 0  # index for pattern
        while i < len(line):
            if pattern[j] == line[i]:
                i += 1
                j += 1
            if j == len(pattern):
                if not whole_word or ((i - j == 0 or line[i - j - 1] == ' ') and (i == len(line) or line[i] == ' ')):
                    positions.append((row + 1, i - j + 1))
                j = lps[j - 1]
            elif i < len(line) and pattern[j] != line[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
    return positions

# Function to search files
def search_files(search_term, files, case_sensitive, whole_word):
    results = []
    for file in files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                bf_time_start = time.time()
                bf_results = brute_force_search(content, search_term, case_sensitive, whole_word)
                bf_time = time.time() - bf_time_start
                
                kmp_time_start = time.time()
                kmp_results = kmp_search(content, search_term, case_sensitive, whole_word)
                kmp_time = time.time() - kmp_time_start

                results.append({
                    "file": file,
                    "brute_force": bf_results,
                    "brute_force_time": bf_time,
                    "kmp": kmp_results,
                    "kmp_time": kmp_time,
                })
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file {file}: {str(e)}")
    return results

# Tkinter GUI Setup
class WordSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Search Application")

        self.files = []

        # Search Term
        tk.Label(root, text="Search Term").pack()
        self.search_term_entry = tk.Entry(root)
        self.search_term_entry.pack()

        # Options
        self.case_sensitive_var = tk.BooleanVar()
        self.whole_word_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Case Sensitive", variable=self.case_sensitive_var).pack()
        tk.Checkbutton(root, text="Whole Word Match", variable=self.whole_word_var).pack()

        # File Selection
        tk.Button(root, text="Select Files", command=self.select_files).pack()
        self.file_list_label = tk.Label(root, text="No files selected")
        self.file_list_label.pack()

        # Search Button
        tk.Button(root, text="Search", command=self.start_search).pack()

        # Results
        self.results_text = Text(root, height=20, width=80)
        self.results_text.pack()

    def select_files(self):
        self.files = filedialog.askopenfilenames(title="Select Text Files", filetypes=[("Text Files", "*.txt")])
        self.file_list_label.config(text=f"Selected Files: {len(self.files)}")
        
    def start_search(self):
        search_term = self.search_term_entry.get().strip()
        if not search_term:
            messagebox.showerror("Error", "Search term cannot be empty")
            return

        results = search_files(search_term, self.files, self.case_sensitive_var.get(), self.whole_word_var.get())
        self.display_results(results, search_term)


    def display_results(self, results, search_term):
        self.results_text.delete("1.0", tk.END)
        for result in results:
            self.results_text.insert(tk.END, f"File: {result['file']}\n")
            self.results_text.insert(tk.END, f"Searched Word: '{search_term}'\n")
            self.results_text.insert(tk.END, f"Brute Force: {result['brute_force']}, Time: {result['brute_force_time']} seconds\n")
            self.results_text.insert(tk.END, f"KMP: {result['kmp']}, Time: {result['kmp_time']} seconds\n")
            self.results_text.insert(tk.END, "\n")


# Run the App
if __name__ == "__main__":
    root = tk.Tk()
    app = WordSearchApp(root)
    root.mainloop()
