# 🔑 Face Authentication System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A complete Python-based face authentication system inspired by smartphone/laptop face unlock.**

Uses OpenCV and face_recognition for real-time face detection and matching, secure embedding storage with Fernet encryption, and a Flask web interface for post-authentication access.

</div>

---

## ✨ Features

- 🎥 **Live Webcam Capture** — Real-time face detection with green bounding boxes and status indicators
- 🔐 **Encrypted Face Embeddings** — Secure storage using Fernet symmetric encryption
- ⚡ **Real-Time Matching** — Face verification with configurable tolerance threshold (0.6)
- 🌐 **Flask Web Dashboard** — Protected routes accessible only after successful authentication
- 🚀 **Optimized Performance** — Processes every 5th frame for smooth real-time operation (~6 FPS)
- 🛡️ **Error Handling** — Graceful handling of camera issues, no/multiple faces detected

## 🎬 How It Works

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Enrollment │────▶│ Face Capture │────▶│ Encrypt & Store  │────▶│  Ready ✅   │
│  (main.py)  │     │  (20 frames) │     │  (Fernet AES)    │     │             │
└─────────────┘     └──────────────┘     └──────────────────┘     └─────────────┘

┌─────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│    Auth      │────▶│ Live Detect  │────▶│ Match Embedding  │────▶│ Dashboard 🎉│
│  (app.py)   │     │  (Webcam)    │     │  (Distance < 0.6)│     │             │
└─────────────┘     └──────────────┘     └──────────────────┘     └─────────────┘
```

## 📋 Requirements

- **Python 3.10 or 3.11** (avoid 3.12+ — no pre-built wheels for `face-recognition`)
- Windows / Linux / macOS
- Webcam
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Windows, for dlib compilation)

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/princesingh1702/Face-Authentication.git
cd Face-Authentication

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Enroll your face
python main.py
# Enter user_id (e.g., 'admin'), look at camera for 20 frames

# 5. Launch the web app
python app.py
# Open http://localhost:5000 → Click "Authenticate with Face"
```

## 📁 Project Structure

```
Face-Authentication/
├── main.py              # Face enrollment entry point
├── app.py               # Flask web application
├── face_detector.py     # Webcam handling & face encoding
├── embedding_manager.py # Encrypted embedding storage (Fernet)
├── authenticator.py     # Enrollment & authentication logic
├── requirements.txt     # Python dependencies
└── templates/
    ├── home.html        # Landing page with auth button
    └── dashboard.html   # Protected dashboard (post-auth)
```

## 🔧 Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Detection Model | `hog` | Use `cnn` for higher accuracy (slower) |
| Frame Skip | Every 5th | Adjust for speed vs. accuracy tradeoff |
| Tolerance | `0.6` | Lower = stricter, Higher = more lenient |
| Encryption | Fernet (AES) | Key auto-generated and stored locally |

## 🔒 Security Notes

- Face embeddings are encrypted at rest using **Fernet symmetric encryption**
- Encryption key is auto-generated on first run
- For production: use environment variables or HSM for key management
- Session-based authentication in Flask

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: dlib` | Install CMake + VS Build Tools, or use Python 3.11 for pre-built wheels |
| Webcam not found | Check camera index in `face_detector.py` (try index 1) |
| No match found | Re-enroll under similar lighting conditions; adjust tolerance |
| Multiple faces | Ensure only one face is visible in the frame |

## 📄 License

MIT License — Feel free to use and modify!