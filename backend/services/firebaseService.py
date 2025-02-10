import os
import json
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    """
    Initialize Firebase using credentials from an environment variable or file.
    - If the environment variable `FIREBASE_CREDENTIALS` is set, it uses the JSON content directly.
    - Otherwise, it falls back to a file-based approach using `FIREBASE_CREDENTIALS_PATH` or the default file path.
    """
    if not firebase_admin._apps:  
        try:
            print("Initializing Firebase...")

            # Check for credentials in the environment variable
            firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")
            if firebase_credentials_json:
                # Load credentials from environment variable
                print("Using Firebase credentials from environment variable.")
                cred = credentials.Certificate(json.loads(firebase_credentials_json))
            else:
                # Fallback to file-based credentials
                cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_cred.json")
                print(f"Using Firebase credentials from file: {cred_path}")
                cred = credentials.Certificate(cred_path)
            
            # Initialize Firebase app
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully!")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise RuntimeError("Failed to initialize Firebase.")
    else:
        print("Firebase is already initialized.")
