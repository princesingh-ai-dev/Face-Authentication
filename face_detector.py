import cv2
import numpy as np
import os
import logging

# Set up logging for warnings
logging.basicConfig(level=logging.WARNING)

print(f"OpenCV version: {cv2.__version__}")

def initialize_webcam():
    """
    Initialize and return the webcam capture object.
    Returns: cv2.VideoCapture object or None if failed.
    """
    cap = cv2.VideoCapture(0)  # Use default camera (index 0)
    if not cap.isOpened():
        raise RuntimeError("Error: Could not open webcam.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    # Verify properties set
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Webcam initialized: {width}x{height} @ {fps} FPS")
    if width != 640 or height != 480 or fps != 30:
        print("Warning: Webcam properties may vary by hardware.")
    return cap

def capture_frame(cap):
    """
    Capture a single frame from the webcam.
    Args:
        cap (cv2.VideoCapture): The webcam capture object.
    Returns:
        numpy.ndarray: The captured frame as BGR image, or None if failed.
    """
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def preprocess_frame(frame):
    """
    Preprocess the frame for better detection in low-light or occlusion scenarios.
    Applies CLAHE to enhance contrast.
    Args:
        frame (numpy.ndarray): BGR frame.
    Returns:
        numpy.ndarray: Preprocessed RGB frame or original if error.
    """
    try:
        print("Applying CLAHE preprocessing for low-light enhancement.")
        # Convert to LAB for CLAHE (works well for low-light)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        rgb_frame = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
        print("CLAHE preprocessing succeeded.")
        return rgb_frame
    except Exception as e:
        logging.warning(f"CLAHE preprocessing failed: {e}; using original frame.")
        print("CLAHE failed; using original RGB frame.")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def detect_and_encode_faces(frame, model="hog"):
    """
    Detect faces in the frame and compute their encodings.
    Args:
        frame (numpy.ndarray): Input frame in BGR format.
        model (str): Detection model, 'hog' for speed or 'cnn' for accuracy (slower).
    Returns:
        tuple: (list of face locations, list of face encodings) or (None, None) if no faces.
    Note: Install face-recognition with 'pip install face-recognition' for full functionality. Haar fallback works without it for detection/rectangles.
    """
    # Preprocess for better detection
    rgb_frame = preprocess_frame(frame)
    
    face_locations = []
    face_recognition_available = False
    # Lazy import to avoid import-time errors if package missing
    try:
        import face_recognition  # type: ignore
        print("Using face_recognition library.")
        face_recognition_available = True
        # Locate faces with face_recognition
        try:
            face_locations = face_recognition.face_locations(rgb_frame, model=model)
            print(f"face_recognition detected {len(face_locations)} faces.")
        except Exception as e:
            print(f"face_recognition detection failed: {e}; trying Haar fallback.")
            face_locations = []
    except Exception as e:
        print(f"face_recognition library not available: {e}; attempting Haar fallback.")
        face_locations = []
        # Comment: Install with 'pip install face-recognition' for full functionality. Haar fallback works without it.
    else:
        # If import succeeded but detection failed, face_locations is already []
        pass

    if len(face_locations) == 0:
        print("No faces detected by face_recognition; attempting Haar fallback.")
        # Fallback to Haar cascade for locations (always attempt, even if face_recognition missing)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        haar_cascade_path = None
        try:
            # Try to access cv2.data.haarcascades safely
            if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
                haar_cascade_dir = cv2.data.haarcascades
                haar_cascade_path = os.path.join(haar_cascade_dir, 'haarcascade_frontalface_default.xml')
                print(f"Using bundled Haar cascade at: {haar_cascade_path}")
            else:
                raise AttributeError("cv2.data.haarcascades not available")
        except (AttributeError, Exception) as e:
            print(f"cv2.data.haarcascades not available (OpenCV <4.3 or headless?): {e}")
            logging.warning("Download haarcascade_frontalface_default.xml from https://github.com/opencv/opencv/tree/master/data/haarcascades to the project root or 'models/' folder.")
            # Try manual path in project dir or models/
            manual_paths = ['haarcascade_frontalface_default.xml', 'models/haarcascade_frontalface_default.xml']
            for manual_path in manual_paths:
                if os.path.exists(manual_path):
                    haar_cascade_path = manual_path
                    print(f"Using manual Haar cascade at: {haar_cascade_path}")
                    break
            if not haar_cascade_path:
                print("No manual cascade found; Haar fallback unavailable.")
        except Exception as e:
            logging.warning(f"Error accessing cv2.data: {e}; skipping Haar fallback.")
            print("Error accessing cv2.data; Haar fallback unavailable.")

        if haar_cascade_path and os.path.exists(haar_cascade_path):
            try:
                face_cascade = cv2.CascadeClassifier(haar_cascade_path)
                if face_cascade.empty():
                    logging.warning("Haar cascade loaded but empty (invalid XML); skipping fallback.")
                    print("Haar cascade empty; no fallback detection.")
                else:
                    print("Haar cascade loaded successfully; detecting faces.")
                    haar_locations = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    if len(haar_locations) > 0:
                        # Convert Haar to face_locations format (top, right, bottom, left)
                        face_locations = []
                        for (x, y, w, h) in haar_locations:
                            top = y
                            right = x + w
                            bottom = y + h
                            left = x
                            face_locations.append((top, right, bottom, left))
                        print(f"Haar fallback detected {len(face_locations)} faces.")
                    else:
                        print("Haar fallback detected 0 faces.")
            except (FileNotFoundError, IOError) as e:
                logging.warning(f"Haar cascade file not found or IO error: {e}; skipping fallback.")
                print(f"Haar file error: {e}")
            except Exception as e:
                logging.warning(f"Error loading Haar cascade: {e}; skipping fallback.")
                print(f"Haar load failed: {e}")
        else:
            if haar_cascade_path:
                logging.warning(f"Haar cascade file not found at {haar_cascade_path}; download as instructed.")
            print("Haar fallback not available; no detections.")
    else:
        print(f"Using face_recognition results with {len(face_locations)} faces.")
    
    if len(face_locations) == 0:
        print("No faces detected overall.")
        return None, None
    
    # Compute encodings (only if face_recognition available)
    face_encodings = None
    if face_recognition_available:
        try:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model=model)
            print(f"Computed {len(face_encodings)} encodings from {len(face_locations)} locations.")
            if len(face_encodings) < len(face_locations):
                print("Warning: Some encodings failed (e.g., partial occlusion or poor quality).")
        except Exception as e:
            print(f"Encoding failed: {e}; returning locations only (rectangles still drawn).")
            face_encodings = None
    else:
        print("face_recognition not available; returning locations only (no encodings, but rectangles drawn in authenticator.py).")
    
    print(f"Final output: {len(face_locations)} locations, {len(face_encodings) if face_encodings is not None else 0} encodings.")
    return face_locations, face_encodings

def release_webcam(cap):
    """
    Safely release the webcam capture.
    Args:
        cap (cv2.VideoCapture): The webcam capture object.
    """
    if cap:
        cap.release()