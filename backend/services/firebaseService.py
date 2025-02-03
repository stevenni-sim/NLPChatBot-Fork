import firebase_admin
from firebase_admin import credentials

def initialize_firebase(cred_path: str = "firebase_cred.json"):
    
    # Initialize Firebase application with the provided credentials file.
    # If Firebase is already initialized, it will skip re-initialization.
    
    if not firebase_admin._apps:  
        try:
            print("Initializing Firebase...")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully!")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise RuntimeError("Failed to initialize Firebase.")
    else:
        print("Firebase is already initialized.")
