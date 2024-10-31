import tkinter as tk
from tkinter import filedialog, messagebox
import time
import os
import re

# Brute Force Search Algorithm
def brute_force_search(text, pattern):
    matches = []
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i + len(pattern)] == pattern:
            matches.append(i)
    return matches

# Knuth-Morris-Pratt (KMP) Algorithm
def kmp_search(text, pattern):
    lsp = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lsp[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            lsp[i] = j

    matches = []
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lsp[j - 1]
        if text[i] == pattern[j]:
            j += 1
            if j == len(pattern):
                matches.append(i - j + 1)
                j = lsp[j - 1]
    return matches

# Extract the full word containing the match
def get_full_word(text, position, pattern_length):
    start = position
    end = position + pattern_length

    while start > 0 and text[start - 1].isalnum():
        start -= 1
    while end < len(text) and text[end].isalnum():
        end += 1

    return text[start:end]

# Check if match is a whole word
def is_whole_word(text, pos, pattern):
    if (pos > 0 and text[pos - 1].isalnum()) or (pos + len(pattern) < len(text) and text[pos + len(pattern)].isalnum()):
        return False
    return True

# Search function for files
def search_files(search_term, files, case_sensitive=False, whole_word=False):
    results = []

    for file_path in files:
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            file_matches = {'file': file_path, 'matches': []}

            for row_number, line in enumerate(lines):
                text = line.strip()

                if not case_sensitive:
                    text_lower = text.lower()
                    search_term_lower = search_term.lower()
                else:
                    text_lower = text
                    search_term_lower = search_term

                # Brute Force Search
                start_time = time.time()
                bf_positions = brute_force_search(text_lower, search_term_lower)
                bf_time = time.time() - start_time

                # KMP Search
                start_time = time.time()
                kmp_positions = kmp_search(text_lower, search_term_lower)
                kmp_time = time.time() - start_time

                # Apply whole word condition if required
                if whole_word:
                    bf_positions = [pos for pos in bf_positions if is_whole_word(text_lower, pos, search_term_lower)]
                    kmp_positions = [pos for pos in kmp_positions if is_whole_word(text_lower, pos, search_term_lower)]

                for pos in bf_positions:
                    matched_word = get_full_word(text, pos, len(search_term))
                    file_matches['matches'].append({
                        'row': row_number + 1,
                        'col': pos + 1,
                        'matched_text': matched_word,
                    })

            file_matches['brute_force_time'] = round(bf_time, 5)
            file_matches['kmp_time'] = round(kmp_time, 5)

            results.append(file_matches)

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    return results

# Main Application GUI
class WordSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Search Application")

        # Search Term Entry
        self.search_term_var = tk.StringVar()
        tk.Label(root, text="Search Term:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(root, textvariable=self.search_term_var).grid(row=0, column=1)

        # Options
        self.case_sensitive_var = tk.BooleanVar()
        self.whole_word_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Case Sensitive", variable=self.case_sensitive_var).grid(row=1, column=0, sticky=tk.W)
        tk.Checkbutton(root, text="Whole Word", variable=self.whole_word_var).grid(row=1, column=1, sticky=tk.W)

        # Select Files Button
        self.files = []
        tk.Button(root, text="Select Files", command=self.select_files).grid(row=2, column=0, columnspan=2)

        # Search Button
        tk.Button(root, text="Search", command=self.perform_search).grid(row=3, column=0, columnspan=2)

        # Results Text Box
        self.result_text = tk.Text(root, wrap="word", width=80, height=20)
        self.result_text.grid(row=4, column=0, columnspan=2, pady=10)

    # File selection dialog
    def select_files(self):
        self.files = filedialog.askopenfilenames(title="Select Text Files", filetypes=(("Text files", "*.txt"),))
        if self.files:
            messagebox.showinfo("Files Selected", f"{len(self.files)} files selected.")

    # Perform search and display results
    def perform_search(self):
        self.result_text.delete(1.0, tk.END)
        search_term = self.search_term_var.get()
        case_sensitive = self.case_sensitive_var.get()
        whole_word = self.whole_word_var.get()

        if not search_term:
            messagebox.showerror("Input Error", "Please enter a search term.")
            return

        if not self.files:
            messagebox.showerror("File Selection Error", "Please select files to search.")
            return

        results = search_files(search_term, self.files, case_sensitive, whole_word)

        # Format output to match specified requirements
        self.result_text.insert(tk.END, f"Searched Word: '{search_term}'\n\n")
        
        for result in results:
            self.result_text.insert(tk.END, f"File: {os.path.basename(result['file'])}\n")
            for match in result['matches']:
                self.result_text.insert(
                tk.END,
                f"Location: (Row: {match['row']}, Col: {match['col']}), Matched Text: '{match['matched_text']}'\n"
            )
        # Format times to 5 decimal places
        self.result_text.insert(tk.END, f"Brute Force Time: {result['brute_force_time']:.5f} seconds\n")
        self.result_text.insert(tk.END, f"KMP Time: {result['kmp_time']:.5f} seconds\n")
        self.result_text.insert(tk.END, "-" * 50 + "\n\n")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WordSearchApp(root)
    root.mainloop()
