import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # Hide main window
folder = filedialog.askdirectory(title="Select a folder")
print("Selected folder:", folder)
