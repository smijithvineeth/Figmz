# Installation Guide - Face Recognition AI

## ⚠️ IMPORTANT: Python Version Requirements

**Your current Python version: 3.14.0**

The face recognition system requires **Python 3.10, 3.11, 3.12, or 3.13**.

**Python 3.14 is too new** and doesn't have pre-built binary wheels for the `dlib` library that face-recognition depends on.

---

## Solution: Install Python 3.12 (Recommended)

### Step 1: Install Python 3.12

1. **Download Python 3.12.7** from: https://www.python.org/downloads/release/python-3127/
   - Choose "Windows installer (64-bit)" for your system

2. **During Installation:**
   - ✅ Check: "Add Python 3.12 to PATH"
   - ✅ Check: "Install pip"
   - Choose "Customize installation" and ensure pip is selected

3. **Verify Installation:**
   ```bash
   python3.12 --version
   ```

---

## Step 2: Create Virtual Environment with Python 3.12

Navigate to your project directory and create a virtual environment:

```bash
cd c:\wamp64\www\Figmiz

# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Or if using PowerShell:
venv\Scripts\Activate.ps1
```

You should see `(venv)` prefix in your terminal.

---

## Step 3: Install Dependencies

With the virtual environment activated:

```bash
cd backend

# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install:
- ✅ FastAPI & Uvicorn (web framework)
- ✅ OpenCV (video processing)
- ✅ face_recognition (face detection & recognition)
- ✅ dlib (facial recognition library)
- ✅ NumPy, SciPy, scikit-learn (scientific computing)

---

## Step 4: Verify Installation

```bash
python -c "import fastapi, cv2, face_recognition; print('✓ All packages installed successfully!')"
```

If this command runs without errors, you're ready to go!

---

## Step 5: Run the Application

```bash
python run.py
```

You should see:
```
============================================================
🚀 Starting Face Recognition AI Server
============================================================

📍 Server running at: http://localhost:8000
📍 API Docs: http://localhost:8000/docs

🎯 Open your browser and navigate to http://localhost:8000

Press Ctrl+C to stop the server
```

Then **open your browser** to http://localhost:8000

---

## Troubleshooting Installation

### "Python 3.12 not found"
Make sure Python 3.12 is properly installed and added to PATH:
```bash
python3.12 --version
```

If not found, reinstall Python 3.12 and ensure "Add to PATH" is checked.

### "No module named 'fastapi'"
Make sure your virtual environment is activated:
```bash
# Windows Command Prompt
venv\Scripts\activate

# Windows PowerShell
venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### "pip: command not found"
Try using python -m pip instead:
```bash
python -m pip install -r requirements.txt
```

### Installation takes a long time
This is normal! dlib and numpy take 5-10 minutes to build from source. The first time is always slower.

### "PermissionError" on Windows
Try running Command Prompt as Administrator (right-click → Run as administrator)

---

## File Structure After Installation

```
c:\wamp64\www\Figmiz\
├── backend/
│   ├── venv/                 # Virtual environment (created)
│   ├── app/                  # FastAPI app
│   ├── frontend/
│   │   └── index.html       # Web interface
│   ├── data/                # Captured faces (auto-created)
│   ├── models/              # Face encodings (auto-created)
│   ├── requirements.txt
│   └── run.py
├── INSTALLATION_GUIDE.md
├── SETUP.md
└── README.md
```

---

## Quick Start Summary

```bash
# 1. Open Command Prompt in project directory
cd c:\wamp64\www\Figmiz

# 2. Create virtual environment
python3.12 -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
cd backend
pip install -r requirements.txt

# 5. Run the server
python run.py

# 6. Open browser to http://localhost:8000
```

---

## Advanced: Using Different Python Versions

If you prefer Python 3.10, 3.11, or 3.13, the same steps work:

```bash
# For Python 3.13
python3.13 -m venv venv

# For Python 3.11
python3.11 -m venv venv

# For Python 3.10
python3.10 -m venv venv
```

All versions 3.10-3.13 are fully supported.

---

## Getting Help

If you encounter issues:

1. **Check Python version:**
   ```bash
   python --version
   ```
   Should show 3.10 or higher (not 3.14)

2. **Verify virtual environment:**
   ```bash
   python -m pip list
   ```
   Should show fastapi, opencv-python, face-recognition, etc.

3. **Check camera permissions:**
   - Windows: Check privacy settings → Camera
   - Allow browser access to camera

4. **Clear and reinstall (last resort):**
   ```bash
   rmdir /s /q venv  # Remove virtual environment
   python3.12 -m venv venv  # Create new one
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## Next Steps

After successful installation:

1. **Capture** faces using the 📸 Capture tab
2. **Train** the model using the 🎓 Train tab
3. **Recognize** faces in real-time using the 🔍 Recognize tab

See [README.md](README.md) and [SETUP.md](SETUP.md) for detailed usage instructions.

Happy face recognizing! 🎉
