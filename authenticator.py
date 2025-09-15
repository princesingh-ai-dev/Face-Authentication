import time
import cv2
import numpy as np
from face_detector import initialize_webcam, capture_frame, detect_and_encode_faces, release_webcam
from embedding_manager import EmbeddingManager

class Authenticator:
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.tolerance = 0.6  # Matching threshold for face_recognition

    def enroll_user(self, user_id, num_frames=20, timeout=30, frame_skip=5):
        """
        Enroll a new user by capturing multiple frames, averaging face encodings, and storing securely.
        Args:
            user_id (str): Unique user identifier.
            num_frames (int): Number of frames to capture for averaging.
            timeout (int): Max seconds for enrollment.
            frame_skip (int): Process every nth frame for optimization.
        Returns:
            bool: True if successful, False otherwise.
        Raises:
            ValueError: If user already enrolled.
        """
        if self.embedding_manager.user_exists(user_id):
            raise ValueError(f"User {user_id} is already enrolled.")

        try:
            cap = initialize_webcam()
        except Exception as exc:
            raise RuntimeError("Failed to initialize webcam for enrollment.") from exc

        encodings = []
        start_time = time.time()
        frame_count = 0
        processed_count = 0

        print(f"Enrolling {user_id}. Please look at the camera. Capturing {num_frames} frames...")
        
        # Create and configure the preview window
        window_name = "Face Detection"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)

        while processed_count < num_frames and (time.time() - start_time) < timeout:
            frame = capture_frame(cap)
            if frame is None:
                time.sleep(0.1)
                continue

            frame_count += 1
            if frame_count % frame_skip != 0:
                # Skip frame to optimize
                cv2.imshow(window_name, frame)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                    cv2.moveWindow(window_name, 100, 50)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                continue

            face_locations, face_encodings = detect_and_encode_faces(frame)

            if face_encodings is None:
                print("No face detected. Please ensure your face is visible.")
                cv2.putText(frame, "No face detected.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow(window_name, frame)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                    cv2.moveWindow(window_name, 100, 50)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                continue

            if len(face_encodings) > 1:
                print("Multiple faces detected. Please ensure only one face is visible.")
                cv2.putText(frame, "Multiple faces detected. Please ensure only one face is visible.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow(window_name, frame)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                    cv2.moveWindow(window_name, 100, 50)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                continue

            encodings.append(face_encodings[0])
            processed_count += 1

            # Show preview with green rectangle
            if face_locations is not None:
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.imshow(window_name, frame)
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                cv2.moveWindow(window_name, 100, 50)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        release_webcam(cap)

        if len(encodings) < num_frames // 2:  # Require at least half the frames
            print("Insufficient valid frames captured for enrollment.")
            return False

        # Average the encodings
        average_encoding = np.mean(encodings, axis=0)
        self.embedding_manager.enroll_user(user_id, average_encoding)
        print(f"User {user_id} enrolled successfully.")
        return True

    def authenticate_user(self, timeout=10, frame_skip=5):
        """
        Authenticate the current user by capturing live frames and matching against stored embeddings.
        Args:
            timeout (int): Max seconds for authentication attempt.
            frame_skip (int): Process every nth frame for optimization.
        Returns:
            tuple: (bool success, str message, str user_id if success else None)
        """
        try:
            cap = initialize_webcam()
        except Exception:
            return False, "Failed to initialize webcam for authentication.", None

        start_time = time.time()
        known_encodings = list(self.embedding_manager.get_embeddings().values())
        known_ids = list(self.embedding_manager.get_embeddings().keys())

        if not known_encodings:
            release_webcam(cap)
            return False, "No users enrolled. Please enroll first.", None

        print("Authenticating... Look at the camera.")
        
        # Create and configure the preview window
        window_name = "Face Detection"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)

        frame_count = 0
        while (time.time() - start_time) < timeout:
            frame = capture_frame(cap)
            if frame is None:
                time.sleep(0.1)
                continue

            frame_count += 1
            if frame_count % frame_skip != 0:
                # Skip frame to optimize
                cv2.putText(frame, "Authenticating...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow(window_name, frame)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                    cv2.moveWindow(window_name, 100, 50)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                continue

            face_locations, face_encodings = detect_and_encode_faces(frame)

            if face_encodings is None:
                message = "No face detected."
                print(message)
                # Show frame with message
                cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow(window_name, frame)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                    cv2.moveWindow(window_name, 100, 50)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                continue

            if len(face_encodings) > 1:
                message = "Multiple faces detected. Clear the frame."
                print(message)
                cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow(window_name, frame)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                    cv2.moveWindow(window_name, 100, 50)
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)
                continue

            # Compare the detected encoding using Euclidean distance
            current_encoding = face_encodings[0]
            known_matrix = np.vstack(known_encodings)
            distances = np.linalg.norm(known_matrix - current_encoding, axis=1)
            min_distance = float(np.min(distances))
            match_index = int(np.argmin(distances))

            if min_distance < self.tolerance:
                user_id = known_ids[match_index]
                success_message = f"Authentication successful! Welcome, {user_id}."
                print(success_message)
                cv2.destroyAllWindows()
                release_webcam(cap)
                return True, success_message, user_id

            # Show preview with distance
            message = f"Matching... Distance: {min_distance:.2f}"
            cv2.putText(frame, message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if face_locations is not None:
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.imshow(window_name, frame)
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0:
                cv2.moveWindow(window_name, 100, 50)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        release_webcam(cap)
        return False, "Authentication failed or timed out.", None

    def authenticate_specific_user(self, user_id, timeout=10):
        """
        Authenticate a specific user.
        Args:
            user_id (str): The user to authenticate.
            timeout (int): Max seconds.
        Returns:
            tuple: (bool, str message)
        """
        if not self.embedding_manager.user_exists(user_id):
            return False, f"User {user_id} not enrolled."

        # Temporarily filter to specific user
        all_embeddings = self.embedding_manager.get_embeddings()
        if user_id in all_embeddings:
            temp_embeddings = {user_id: all_embeddings[user_id]}
            # Override for comparison (simplified; in practice, filter known_encodings)
            # But for this, we'll use the full authenticate and check user_id
            success, msg, matched_id = self.authenticate_user(timeout)
            if success and matched_id == user_id:
                return True, msg
        return False, "No match for specified user."