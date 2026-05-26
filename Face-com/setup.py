#!/usr/bin/env python3
"""
Installation and setup script for AI Meme Face Camera.
Checks dependencies and sets up the environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, you have {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_pip():
    """Check if pip is installed."""
    print("\n🔍 Checking pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"],
                            stdout=subprocess.DEVNULL)
        print("✅ pip is installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip not found")
        return False


def install_requirements():
    """Install required packages from requirements.txt."""
    print("\n📦 Installing dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ requirements.txt not found at {requirements_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r",
            str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    directories = [
        "screenshots",
        "assets",
        "sounds",
        "overlays"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ {directory}/ ready")
    
    return True


def verify_imports():
    """Verify that all imports work."""
    print("\n✔️  Verifying imports...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'PIL': 'Pillow'
    }
    
    all_ok = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {module} ({'from ' + package})")
        except ImportError:
            print(f"❌ {module} not found (install: pip install {package})")
            all_ok = False
    
    return all_ok


def check_camera():
    """Check if camera is available."""
    print("\n📹 Checking camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            print(f"✅ Camera found: {int(width)}x{int(height)} @ {int(fps)}fps")
            return True
        else:
            print("❌ Camera not accessible")
            print("   Troubleshoot: Check if camera is connected and not used by another app")
            return False
    except Exception as e:
        print(f"⚠️  Could not verify camera: {e}")
        return True  # Not critical


def main():
    """Run setup process."""
    print("=" * 50)
    print("🎭 AI Meme Face Camera - Setup")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Pip Package Manager", check_pip),
        ("Create Directories", create_directories),
        ("Install Requirements", install_requirements),
        ("Verify Imports", verify_imports),
        ("Camera Detection", check_camera)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'=' * 50}")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📋 Setup Summary:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if not result and name not in ["Camera Detection"]:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✅ Setup completed successfully!")
        print("\n🚀 To start the application, run:")
        print("   python run.py")
        return 0
    else:
        print("\n❌ Setup incomplete. Please fix errors above.")
        print("\n💡 Common fixes:")
        print("   - Update pip: python -m pip install --upgrade pip")
        print("   - Reinstall: pip install -r requirements.txt --force-reinstall")
        print("   - Clean cache: pip cache purge")
        return 1


if __name__ == "__main__":
    sys.exit(main())
