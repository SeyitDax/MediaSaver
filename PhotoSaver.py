import os
import tkinter as tk
import shutil
import hashlib
from tkinter import filedialog, messagebox
from pathlib import Path

# Supported file formats
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".wmv"}

def get_file_hash(file_path):
    """Generate a hash for a given file using SHA-256."""
    hash_algo = hashlib.sha256() # Create a hash object
    with open(file_path, "rb") as f: # Read the file in binary mode
        while chunk := f.read(4096):
            hash_algo.update(chunk) # Update hash with file data
    return hash_algo.hexdigest() # Return hash as a hex string

def find_dublicates(file_list):
    """Find duplicate files by comparing their hashes."""
    hash_dict = {} # Stores hash → file path
    duplicates = [] # Stores duplicate file paths

    for file in file_list:
        file_hash = get_file_hash(file)

        if file_hash in hash_dict:
            duplicates.append(file) # Found a duplicate
        else:
            hash_dict[file_hash] = file # Store hash
        
    return duplicates

def select_folders():
    """Allow user to select multiple folders one by one."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.update()  # Ensure Tkinter loads
    
    selected_folders = []  # Store multiple folder paths
    
    while True:
        folder = filedialog.askdirectory(title="Select a folder with photos/videos")
        if not folder:  # If user cancels selection
            break
        selected_folders.append(folder)

        # Ask if they want to add another folder
        if not messagebox.askyesno("Select Another?", "Do you want to add another folder?"):
            break
    
    root.destroy()  # Destroy the Tk instance
    return selected_folders if selected_folders else None

def list_files(folders):
    """Scan multiple folders and list all photos and videos."""
    all_files = []
    
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                filepath = Path(root) / file
                all_files.append(filepath)

    return all_files

def categorize_files(files):
    """Categorize files into images, videos, and unknown files."""
    images = [f for f in files if f.suffix.lower() in IMAGE_EXTENSIONS]
    videos = [f for f in files if f.suffix.lower() in VIDEO_EXTENSIONS]
    unknown = [f for f in files if f.suffix.lower() not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS]
    return images, videos, unknown

def get_user_choice(prompt, valid_options):
    """Prompt the user for input until a valid response is given."""
    response = input(prompt).strip().lower()
    while response not in valid_options:
        response = input(f"Invalid input. {prompt}").strip().lower()
    return response

def move_files(files, destination_folder, categorize, move):
    """Move files into their repective catorized folders."""
    destination_folder = Path(destination_folder)

    if not categorize:
        files = {"All_Files": files} # put everything in a single folder

    for category, file_list in files.items():
        category_folder = Path(destination_folder) / category
        category_folder.mkdir(parents=True, exist_ok=True) # Create a folder if missing

        for file in file_list:
            destination_path = category_folder / file.name
            if not destination_path.exists(): # Avoid overwriting
                if move:
                    file.rename(destination_path) # Move file
                else:
                    shutil.copy2(file,destination_path) # Copy file
            else:
                print(f"⚠️ Skipped (already exists): {destination_path}")
                                        
def organize_files():
    """Organize selected folders, categorize, and move/copy files into the user-defined folder."""
    print("Select folders to scan for photos and videos.")
    folders = select_folders()
    if not folders:
        print("No folders selected. Exiting.")
        return

    print(f"Scanning folders: {folders}")
    all_files = list_files(folders)
    if not all_files:
        print("No files found in the selected folders.")
        return

    # Get user preferences
    categorize = get_user_choice("Do you want the files categorized? (Yes/No): ", {"yes", "no", "y", "n"}) in ("yes", "y")
    merged_folder_name = input("Please enter the name for the main folder: ").strip()
    move = get_user_choice("Do you want the files moved or copied? (Move/Copy): ", {"move", "copy"}) == "move"
    remove_duplicates = get_user_choice("Do you want to remove duplicates? (Yes/No)", {"yes", "no", "y", "n"}) in ("yes", "y")

    # Create the main folder
    merged_folder = Path.cwd() / merged_folder_name
    merged_folder.mkdir(exist_ok=True)

    # Find duplicates first and move them
    if remove_duplicates:
        duplicates = find_dublicates(all_files) # Get duplicate files
        if duplicates:
            move_files(duplicates, merged_folder / "Duplicates", False, True) # Move duplicates to a separate folder
            all_files = [file for file in all_files if file not in duplicates] # Remove duplicates from processing list

    # Categorize files if needed
    files_to_process = categorize_files(all_files) if categorize else all_files

    # Move/Copy files
    move_files(files_to_process, merged_folder, categorize, move)
    print("\n✅ Files have been organized!")
    print(f"📂 Merged Folder Location: {merged_folder}")

def show_listed_files():
    print("Select folders to scan for photos and videos.")
    folders = select_folders()

    if not folders:
        print("No folders selected. Exiting.")
        return
    
    print(f"Scanning folders: {folders}")
    all_files = list_files(folders)

    if not all_files:
        print("No files found in the selected folders.")
        return
    
    images, videos, unknown = categorize_files(all_files)
    
    print("\n📸 Found Images:")
    for img in images:
        print(f"  - {img}")

    print("\n🎥 Found Videos:")
    for vid in videos:
        print(f"  - {vid}")

    print("\n❓ Unknown Files:")
    for unk in unknown:
        print(f"  - {unk}")

if __name__ == "__main__":
    organize_files()
