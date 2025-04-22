# 📷 PhotoSaver

PhotoSaver is a smart, GUI-powered desktop tool built with Python that helps you **merge, organize, deduplicate, and transfer photos and videos** from devices like iPhones into structured folders on your PC. Designed for reliability, it overcomes common issues like iPhone copy interruptions and photo duplication.

---

## Features

- 👜 **Drag & Drop or Manual Folder Selection**
- 🌐 **Multi-language file format support** (JPG, PNG, HEIC, MP4, MOV, etc.)
- 🔍 **Perceptual Hashing for Image Similarity Detection**
- 📂 **Categorize Files** into `Images`, `Videos`, `Unknown`
- 📊 **Progress Bar UI** with live status and cancel button
- 🚫 **Optional Duplicate Removal** with adjustable similarity threshold
- 🛠️ **Portable .exe Support** via PyInstaller
- 📲 **iPhone Folder Watcher Mode** for uninterrupted transfers

---

## 🚀 Getting Started

### Requirements
- Python 3.10+
- Windows 10+ (for `.exe` support)

### Dependencies
```bash
pip install pillow imagehash tkinterdnd2
```

### Run from Source
```bash
python PhotoSaver.py
```

Or run the bundled `.exe` (see below).

---

## 📁 How to Use

### Option A: One-Time Folder Merge
1. Run PhotoSaver
2. Choose Drag-and-Drop or Manual Folder Selection
3. Select destination folder for saving
4. Choose options:
   - Categorize files
   - Move or Copy files
   - Remove duplicates (with similarity threshold slider)
5. Done! Organized files are saved in structured folders

### Option B: Watcher Mode (iPhone Optimized)
1. Connect your iPhone and browse DCIM
2. Open PhotoSaver > Watch Mode
3. Copy/paste or drag files into the staging folder (`From_iPhone`)
4. PhotoSaver watches, deduplicates, and sorts automatically

---

## 🛋️ Build as Standalone `.exe`

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Bundle tkdnd (for drag-and-drop support)
- Download `tkdnd2.8`
- Extract it into your Tcl path: `...\tcl\tkdnd2.8\`

### Step 3: Build the Executable
```bash
pyinstaller --onefile --add-data "<path-to-tkdnd2.8>;tkdnd" PhotoSaver.py
```

Output is located in `dist/PhotoSaver.exe`

---
<!--
## 🤖 Screenshots
*(Add your screenshots here)*

---
-->
## 🎓 Learning Goals
This project was built with the intention to:
- Practice advanced **Tkinter GUI design**
- Handle **threaded background processing** safely
- Explore **image hashing and perceptual similarity**
- Create production-level, **cross-device desktop tools**

---

##  Roadmap
- [ ] Add logging console panel
- [ ] Add pause/resume to watcher
- [ ] Add file-type filters
- [ ] macOS support

---

##  Credits
Made with care by Seyit Ahmet DEMİR.
Contributions, ideas, and bug reports are welcome!
