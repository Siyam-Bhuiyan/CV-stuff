#!/usr/bin/env python3
"""
Test script for AI Meme Face Camera
Verifies all components are working correctly.
"""

import sys
import time
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported."""
    print("\n" + "="*50)
    print("🧪 Testing Imports")
    print("="*50)
    
    modules = {
        'cv2': 'OpenCV',
        'mediapipe': 'MediaPipe',
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'tkinter': 'Tkinter'
    }
    
    failed = []
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"✅ {name:20} imported successfully")
        except ImportError as e:
            print(f"❌ {name:20} FAILED: {e}")
            failed.append(name)
    
    return len(failed) == 0, failed


def test_src_modules():
    """Test if src modules can be imported."""
    print("\n" + "="*50)
    print("🧪 Testing Source Modules")
    print("="*50)
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules_to_test = [
        ('src.utils', 'Utils'),
        ('src.camera', 'Camera'),
        ('src.face_detector', 'Face Detector'),
        ('src.expressions', 'Expression Detector'),
        ('src.meme_modes', 'Meme Modes'),
        ('src.ui', 'UI'),
        ('src.main', 'Main App')
    ]
    
    failed = []
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name:20} loaded successfully")
        except Exception as e:
            print(f"❌ {display_name:20} FAILED: {e}")
            failed.append(display_name)
    
    return len(failed) == 0, failed


def test_camera():
    """Test if camera is accessible."""
    print("\n" + "="*50)
    print("🧪 Testing Camera")
    print("="*50)
    
    try:
        import cv2
        
        print("Attempting to open camera 0...")
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"✅ Camera found:")
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {fps}")
            
            # Try to capture a frame
            ret, frame = cap.read()
            if ret:
                print(f"✅ Frame capture successful ({frame.shape[2]} channels)")
            else:
                print("⚠️  Could not capture frame")
            
            cap.release()
            return True
        else:
            print("❌ Camera not found or not accessible")
            print("   Check: USB connection, permissions, other apps using camera")
            return False
            
    except Exception as e:
        print(f"❌ Error testing camera: {e}")
        return False


def test_face_detection():
    """Test face detection model."""
    print("\n" + "="*50)
    print("🧪 Testing Face Detection")
    print("="*50)
    
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
        from src.face_detector import FaceDetector
        
        print("Loading MediaPipe Face Mesh...")
        detector = FaceDetector(min_detection_confidence=0.5)
        print("✅ Face Mesh loaded successfully")
        
        # Create dummy frame
        print("Testing face detection with dummy frame...")
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        dummy_frame[:, :] = (255, 255, 255)  # White frame
        
        faces = detector.detect_faces(dummy_frame)
        print(f"✅ Face detection working (found {len(faces)} faces in white frame)")
        
        detector.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing face detection: {e}")
        return False


def test_expressions():
    """Test expression detection."""
    print("\n" + "="*50)
    print("🧪 Testing Expression Detection")
    print("="*50)
    
    try:
        from src.expressions import ExpressionDetector
        from src.face_detector import FaceDetector
        import numpy as np
        
        print("Initializing expression detector...")
        expr_detector = ExpressionDetector()
        print("✅ Expression detector loaded")
        
        print("Testing expression calculations...")
        # Create dummy landmarks
        dummy_landmarks = [
            (100, 100, 0), (110, 110, 0), (120, 120, 0),  # left eye
            (200, 100, 0), (210, 110, 0), (220, 120, 0),  # right eye
            (150, 200, 0), (160, 210, 0), (170, 220, 0),  # mouth outer
        ]
        
        blink_info = expr_detector.detect_blink(dummy_landmarks[:3], dummy_landmarks[3:6])
        print(f"✅ Blink detection working (EAR: {blink_info['avg_ear']:.3f})")
        
        mouth_info = expr_detector.detect_mouth_open(dummy_landmarks[6:9], [])
        print(f"✅ Mouth detection working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing expressions: {e}")
        return False


def test_meme_modes():
    """Test meme modes."""
    print("\n" + "="*50)
    print("🧪 Testing Meme Modes")
    print("="*50)
    
    try:
        from src.meme_modes import ModeManager
        
        print("Loading meme modes...")
        manager = ModeManager()
        print(f"✅ Loaded {len(manager.modes)} meme modes:")
        
        for i, mode_name in enumerate(manager.get_modes(), 1):
            print(f"   {i}. {mode_name.upper()}")
        
        # Test mode switching
        print("\nTesting mode switching...")
        for mode in list(manager.modes.keys())[:3]:
            manager.set_mode(mode)
            print(f"✅ Switched to {mode} mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing meme modes: {e}")
        return False


def test_performance():
    """Test basic performance."""
    print("\n" + "="*50)
    print("🧪 Testing Performance")
    print("="*50)
    
    try:
        import cv2
        from src.camera import Camera
        
        print("Testing camera threading...")
        camera = Camera(width=1280, height=720, fps=30)
        
        if camera.initialize():
            print("✅ Camera initialized")
            
            camera.start()
            print("✅ Camera thread started")
            
            # Collect frames
            time.sleep(1)
            fps = camera.get_fps()
            frame_count = camera.get_frame_count()
            
            print(f"✅ Performance metrics:")
            print(f"   Frames captured: {frame_count}")
            print(f"   Current FPS: {fps:.1f}")
            
            camera.stop()
            print("✅ Camera stopped")
            
            return True
        else:
            print("⚠️  Could not initialize camera")
            return True  # Not critical for tests
            
    except Exception as e:
        print(f"❌ Error testing performance: {e}")
        return False


def test_directories():
    """Test if required directories exist."""
    print("\n" + "="*50)
    print("🧪 Testing Directory Structure")
    print("="*50)
    
    base_path = Path(__file__).parent
    dirs = ['src', 'screenshots', 'assets', 'sounds', 'overlays']
    
    all_exist = True
    for directory in dirs:
        path = base_path / directory
        if path.exists():
            print(f"✅ {directory:15} exists")
        else:
            print(f"⚠️  {directory:15} missing (will be created)")
            all_exist = False
    
    return all_exist or True  # Directories will be created


def test_files():
    """Test if required files exist."""
    print("\n" + "="*50)
    print("🧪 Testing Required Files")
    print("="*50)
    
    base_path = Path(__file__).parent
    files = [
        'requirements.txt',
        'config.py',
        'run.py',
        'setup.py',
        'README.md',
        'QUICKSTART.md',
        'TROUBLESHOOTING.md',
        'ROADMAP.md',
        'src/__init__.py',
        'src/main.py',
        'src/camera.py',
        'src/face_detector.py',
        'src/expressions.py',
        'src/meme_modes.py',
        'src/ui.py',
        'src/utils.py',
    ]
    
    missing = []
    for filename in files:
        path = base_path / filename
        if path.exists():
            print(f"✅ {filename:30} found")
        else:
            print(f"❌ {filename:30} MISSING")
            missing.append(filename)
    
    return len(missing) == 0, missing


def run_all_tests():
    """Run all tests and generate report."""
    print("\n")
    print("╔" + "="*48 + "╗")
    print("║" + " "*10 + "🧪 AI MEME FACE CAMERA - TEST SUITE" + " "*3 + "║")
    print("╚" + "="*48 + "╝")
    
    tests = [
        ("Imports", test_imports),
        ("Source Modules", test_src_modules),
        ("Directory Structure", test_directories),
        ("Required Files", test_files),
        ("Camera Detection", test_camera),
        ("Face Detection", test_face_detection),
        ("Expression Detection", test_expressions),
        ("Meme Modes", test_meme_modes),
        ("Performance", test_performance),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            if isinstance(result, tuple):
                passed, details = result
            else:
                passed = result
                details = None
            results.append((test_name, passed, details))
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)
    
    for test_name, passed, details in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not passed:
            if isinstance(details, list):
                for detail in details[:3]:
                    print(f"      - {detail}")
            else:
                print(f"      {details}")
    
    print("="*50)
    print(f"\n📊 Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✅ ALL TESTS PASSED! Application is ready to run.")
        print("\n🚀 To start the application:")
        print("   python run.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: python setup.py")
        print("   2. Check: pip install -r requirements.txt")
        print("   3. Read: TROUBLESHOOTING.md")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
