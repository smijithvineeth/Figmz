#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Face Recognition AI - Main Entry Point
Run this script to start the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Get the backend directory
    backend_dir = Path(__file__).parent.absolute()

    # Check if dependencies are installed
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import face_recognition
        import cv2
    except ImportError:
        print("\n⚠️  Some dependencies are missing!")
        print("Installing required packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r",
            str(backend_dir / "requirements.txt")
        ])

    # Change to backend directory
    os.chdir(backend_dir)

    # Run the FastAPI server
    print("\n" + "="*60)
    print("🚀 Starting Face Recognition AI Server")
    print("="*60)
    print("\n📍 Server running at: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("\n🎯 Open your browser and navigate to http://localhost:8000")
    print("\nPress Ctrl+C to stop the server\n")

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

if __name__ == "__main__":
    main()
