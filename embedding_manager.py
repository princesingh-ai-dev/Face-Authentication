import json
import os
from cryptography.fernet import Fernet
import base64
import numpy as np

EMBEDDINGS_FILE = "embeddings.json"
KEY_FILE = "secret.key"

class EmbeddingManager:
    def __init__(self):
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
        self.embeddings = self._load_embeddings()

    def _load_or_generate_key(self):
        """
        Load encryption key from file or generate a new one.
        Returns: bytes - the Fernet key.
        """
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key

    def _load_embeddings(self):
        """
        Load and decrypt embeddings from JSON file.
        Returns: dict - {user_id: embedding (numpy array)}.
        """
        if not os.path.exists(EMBEDDINGS_FILE):
            return {}
        
        with open(EMBEDDINGS_FILE, "rb") as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            data_str = decrypted_data.decode()
            data = json.loads(data_str)
            # Convert base64 strings back to numpy arrays
            embeddings = {}
            for user_id, enc_str in data.items():
                enc_bytes = base64.b64decode(enc_str)
                embedding = np.frombuffer(enc_bytes, dtype=np.float64)
                embeddings[user_id] = embedding
            return embeddings
        except Exception:
            # If decryption fails, assume corrupted and start fresh
            os.remove(EMBEDDINGS_FILE)
            return {}

    def _save_embeddings(self):
        """
        Encrypt and save embeddings to JSON file.
        """
        # Convert numpy arrays to base64 for JSON serialization
        serializable = {}
        for user_id, embedding in self.embeddings.items():
            enc_bytes = base64.b64encode(embedding.tobytes()).decode()
            serializable[user_id] = enc_bytes
        
        data_str = json.dumps(serializable)
        encrypted_data = self.cipher.encrypt(data_str.encode())
        
        with open(EMBEDDINGS_FILE, "wb") as f:
            f.write(encrypted_data)

    def enroll_user(self, user_id, embedding):
        """
        Store or update a user's face embedding.
        Args:
            user_id (str): Unique identifier for the user.
            embedding (numpy.ndarray): The face encoding array.
        """
        self.embeddings[user_id] = embedding
        self._save_embeddings()

    def get_embeddings(self):
        """
        Get all stored embeddings.
        Returns: dict - {user_id: embedding}.
        """
        return self.embeddings

    def user_exists(self, user_id):
        """
        Check if a user is already enrolled.
        Args:
            user_id (str): The user ID.
        Returns: bool.
        """
        return user_id in self.embeddings

    def delete_user(self, user_id):
        """
        Remove a user's embedding.
        Args:
            user_id (str): The user ID.
        """
        if user_id in self.embeddings:
            del self.embeddings[user_id]
            self._save_embeddings()