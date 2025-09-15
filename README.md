<!-- # Face Authentication System

A complete Python-based face authentication system inspired by smartphone/laptop face unlock. Uses OpenCV and face_recognition for real-time face detection and matching, secure embedding storage with encryption, and a Flask web interface for post-auth access.

## Features
- Live webcam capture for enrollment and authentication with enhanced preview: Standardized "Face Detection" window positioned at top-left (100,50), always-on-top, green rectangles around detected faces, red text warnings for no/multiple faces, and stable frame rate.
- Secure storage of face embeddings using Fernet encryption.
- Real-time matching with tolerance threshold (0.6).
- Error handling for camera issues, no/multiple faces.
- Protected Flask dashboard on successful auth.
- Optimized for performance (processes every 5th frame).

## Requirements
- Python **3.10 or 3.11** (avoid 3.12+ due to lack of wheels for face-recognition; do not use Microsoft Store Python as it has restrictions—install from python.org).
- Windows/Linux/macOS (Windows requires Visual Studio Build Tools for dlib if compiling from source; use Python 3.11 for pre-built wheels).
- Webcam.

### Python Setup (Windows)
1. Download Python 3.11 from [python.org downloads](https://www.python.org/downloads/release/python-31110/) (Windows installer 64-bit).
2. Run the installer:
   - Check "Add python.exe to PATH".
   - Select "Install Now" or customize to include pip.
   - Avoid "Install for all users" if permissions issue.
3. Verify installation:
   - Open Command Prompt: `python --version` (should show Python 3.11.x).
   - If not in PATH, add manually: Search "Environment Variables" → Edit PATH → Add Python install dir (e.g., C:\Python311) and Scripts folder.
4. Install VS Build Tools if needed (for potential compilation):
   - Download from [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
   - Install with C++ build tools workload.
5. Create virtual environment (recommended):
   - `python -m venv venv`
   - Activate: `venv\\Scripts\\activate`
6. Upgrade pip: `python -m pip install --upgrade pip setuptools wheel`

Install dependencies:
```
pip install -r requirements.txt
```
Note: `face-recognition` is optional in this fork; the app runs without it (graceful fallback). To enable face matching, install `face-recognition` and prerequisites (CMake and Visual C++ Build Tools). On Python 3.11, pre-built wheels are often available. If build fails, install CMake via `pip install cmake` or from cmake.org, and ensure VS Build Tools.

## Setup
1. Ensure Python 3.11 setup as above.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run enrollment: `python main.py` and follow prompts (enter user_id, e.g., 'admin', look at camera for 20 frames). The "Face Detection" window opens automatically, positioned at top-left, stays on top, shows green rectangles on your face, red warnings if no/multiple faces, and closes on completion or 'q'.
4. Launch the app: `python app.py`.
5. Open browser to `http://localhost:5000`.
6. Click "Authenticate with Face" – look at camera; the "Face Detection" window activates with real-time preview, green bounding box and matching status; on success, redirect to dashboard.
 
## Demo Flow
1. **Enrollment**: Run `main.py`, input user_id, position face in frame. The preview window shows live feed with green rectangle on detection, red text for issues, captures 20 frames, averages encoding, stores encrypted.
2. **Authentication**: In Flask app (`app.py`), home page → Authenticate button → Webcam activates, preview window opens with "Authenticating...", green rectangle and distance text; matches face → Success: Dashboard with welcome; Fail: Error message and window closes.
3. **Dashboard**: Shows user welcome, logout option.
4. **Logout**: Clears session, back to home.

## File Structure
- `requirements.txt`: Dependencies.
- `face_detector.py`: Webcam and face encoding functions.
- `embedding_manager.py`: Secure embedding storage.
- `authenticator.py`: Enrollment and auth logic.
- `app.py`: Flask app with auth integration.
- `main.py`: Entry for enrollment.
- `templates/`: HTML for home and dashboard.

## Optimization & Notes
- Uses 'hog' model for speed (change to 'cnn' for accuracy, but slower).
- Frame skipping (every 5th) for real-time (~6 FPS processing).
- Tolerance 0.6; adjust in authenticator.py for stricter/looser matching.
- Security: Embeddings encrypted; key generated/stored locally. For production, use secure key management (e.g., env vars, HSM).
- Lighting: Ensure good lighting; poor conditions may affect accuracy.
- Multiple users: Enroll multiple IDs; matches closest.
- Errors: Camera not found? Check index in face_detector.py. Multiple faces? Clear area.

## Troubleshooting
- ImportError for dlib/face_recognition: Install CMake, Visual Studio Build Tools (Windows), or use `pip install face-recognition --no-cache-dir`.
- Webcam issues: Verify camera access, try index 1 if 0 fails.
- No match: Re-enroll under similar lighting; adjust tolerance.

## License
MIT - Feel free to use/modify. -->