import os
import tkinter as tk
import shutil
import hashlib
import imagehash
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import simpledialog
from tkinter import ttk

# Supported file formats
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".wmv"}

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

def get_file_hash(file_path):
    """Generate a hash for a given file.
    - Uses perceptual hashing for images
    - Uses SHA-256 for videos & other files
    """
    try:
        # if the file is an image, use perceptual hashing
        if file_path.suffix.lower() in IMAGE_EXTENSIONS:
            with Image.open(file_path) as img:
                img_hash = imagehash.average_hash(img, hash_size=8)
                return img_hash # Convert hash to string
        else:
            # For non images (videos, documents), use standard SHA-256 hashing
            hash_algo = hashlib.sha256() # Create a hash object
            with open(file_path, "rb") as f: # Read the file in binary mode
                while chunk := f.read(4096):
                    hash_algo.update(chunk) # Update hash with file data
            return hash_algo.hexdigest() # Return hash as a hex string
    except Exception as e:
        print(f"Error hashing file {file_path}: {e}")
        return None

def drag_and_drop():
    """Create a simple window for drag-and-drop folder selection."""
    root = TkinterDnD.Tk() # Initialize drag-and-drop capable window

    root.title("Drag & Drop folders") # Set window title
    root.geometry("500x500") # Set window size

    folders = []

    # Add a Label for instructions
    label = tk.Label(root, text="Drag and Drop Folders Here", font=("Arial", 14), padx=20, pady=20)
    label.pack(pady=50)

    # Add a Listbox to display dropped items
    listbox = tk.Listbox(root, width=50, height=10)
    listbox.pack(pady=10)

    def on_drop(event):
        """Capture dropped files."""
        dropped_files = root.tk.splitlist(event.data) # Convert dropped files into a list
        for item in dropped_files:
            if os.path.isdir(item): # Ensure it's a folder
                folders.append(item)
                listbox.insert(tk.END, item)

    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    def confirm_selection():
        """Close the window when the user confirms selection"""
        root.destroy()

    tk.Button(root, text="Confirm", command=confirm_selection).pack(pady=10)
    root.mainloop()

    return folders if folders else None

def find_dublicates(file_list, similarity_threshold=5):
    """Find duplicate images/videos by comparing their hashes.
       - Exact matches for videos/documents
       - Near-matches (threshold) for images 
    """
    hash_dict = {} # Stores hash → file path
    duplicates = [] # Stores duplicate file paths

    for file in file_list:
        file_hash = get_file_hash(file)
        if not file_hash:
            continue # Skip files that couldn't be hashed

        found_duplicate = False

        for existing_hash, existing_file in hash_dict.items():
            # For images, check similarity instead of exact match
            if file.suffix.lower() in IMAGE_EXTENSIONS and isinstance(file_hash, imagehash.ImageHash):
                # -Handle images separately
                if isinstance(existing_hash, imagehash.ImageHash):
                    if abs(file_hash - existing_hash) <= similarity_threshold:
                        duplicates.append(file)
                        found_duplicate = True
                        break # Stop checking once we find a near-duplicate
            elif isinstance(file_hash, str) and isinstance(existing_hash, str): # Ensure bıth are string hashes
                if file_hash == existing_hash:
                    duplicates.append(file)
                    found_duplicate = True
                    break
        
        if not found_duplicate:
            hash_dict[file_hash] = file # Store only unique hashes
    
    return duplicates

def get_threshold():
    """Retrieve user-selected similarity threshold from slider."""
    root = tk.Tk()
    root.title("Select Similarity Threshold")

    tk.Label(root, text="Adjust the similarity threshold:").pack()

    slider = tk.Scale(root, from_=0, to=15, orient="horizontal", tickinterval=5)
    slider.pack()

    def submit():
        global threshold
        threshold = slider.get()
        root.destroy()
    tk.Button(root, text="Confirm", command=submit).pack()

    root.mainloop()
    return threshold

def show_progress_bar(total_files):
    """Create a progress bar window to track file processing."""
    progress_root = tk.Tk()
    progress_root.title("Processing Files...")

    status_label = tk.Label(progress_root, text="Starting...", font=("Arial", 12))
    status_label.pack(pady=10)

    progress = ttk.Progressbar(progress_root, length=300, mode="determinate")
    progress.pack(pady=10)

    progress["maximum"] = total_files

    return progress_root, progress, status_label

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
    return {"Images": images, "Videos": videos, "Unknown": unknown}

def get_user_choice(prompt, valid_options):
    """Prompt the user for input using a GUI dialog box instead of terminal input."""
    response = simpledialog.askstring("Input Required", prompt) 
    if response:
        response = response.strip().lower()

    while response not in valid_options:
        response = simpledialog.askstring("Invalid Input", f"Invalid Input, {prompt}")
        if response:
            response = response.strip().lower()

    return response

def move_files(files, destination_folder, categorize, move, progress=None):
    """Move files into their repective catorized folders."""
    destination_folder = Path(destination_folder)

    if not categorize:
        files = {"All_Files": files} # put everything in a single folder

    if isinstance(files, list):  
        total_files = len(files)  # If it's a list, just count the items
    else:
        total_files = sum(len(file_list) for file_list in files.values())  # If it's a dictionary, count total files
    
    processed_files = 0

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
            
            processed_files += 1
            if progress:
                progress["value"] = processed_files
                progress.update_idletasks()
    
    if progress:
        progress.master.destroy()
                                        
def organize_files():
    """Organize selected folders, categorize, and move/copy files into the user-defined folder."""
    print("Select folders to scan for photos and videos.")

    # Let the user choose how to select files
    selection_method = get_user_choice("Select method (1: Manual Slecetion, 2: Drag & Drop): ", {"1","2"})

    if selection_method == "1":
        folders = select_folders() # Standard selection
    else:
        folders = drag_and_drop() # Drag & Drop

    if not folders:
        print("No folders selected. Exiting.")
        return

    print(f"Scanning folders: {folders}")
    all_files = list_files(folders)
    if not all_files:
        print("No files found in the selected folders.")
        return

    # Let the user choose the Merged Files destination
    merged_folder_name = filedialog.askdirectory(title="Select Destination for Merged Files")
    if not merged_folder_name:
        print("No destination selected. Exiting.")
        return
    merged_folder = Path(merged_folder_name)

    # Get user preferences
    categorize = get_user_choice("Do you want the files categorized? (Yes/No): ", {"yes", "no", "y", "n"}) in ("yes", "y")
    move = get_user_choice("Do you want the files moved or copied? (Move/Copy): ", {"move", "copy"}) == "move"
    remove_duplicates = get_user_choice("Do you want to remove duplicates? (Yes/No)", {"yes", "no", "y", "n"}) in ("yes", "y")
    user_threshold = get_threshold() if remove_duplicates else 0

    merged_folder.mkdir(exist_ok=True) # Ensure folder exists

    # Show progress bar before the categorization starts
    total_steps = len(all_files) + 10
    progress_root, progress, status_label = show_progress_bar(total_steps)

    # Find duplicates first and move them
    if remove_duplicates:
        status_label.config(text="Finding duplicates...")
        progress.update_idletasks()

        duplicates = find_dublicates(all_files, user_threshold) # Get duplicate files
        if duplicates:
            move_files(duplicates, merged_folder / "Duplicates", False, True) # Move duplicates to a separate folder
            all_files = [file for file in all_files if file not in duplicates] # Remove duplicates from processing list

    if categorize:
        status_label.config(text="Categorizing files...")
        progress.update_idletasks()

    # Categorize files if needed
    files_to_process = categorize_files(all_files) if categorize else all_files

    status_label.config(text="Moving/Copying files...")
    progress.update_idletasks()

    # Move/Copy files
    move_files(files_to_process, merged_folder, categorize, move, progress)

    messagebox.showinfo("Process Complete", "✅ All files have been organized successfully!")

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
