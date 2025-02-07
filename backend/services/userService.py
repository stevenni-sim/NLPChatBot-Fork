import firebase_admin
from firebase_admin import auth, firestore
from models.user import User,Authorised
from fastapi import HTTPException
import uuid



class UserService:
    def __init__(self):
        self.db = firestore.client()
        self.sessions = {}


    def authenticate_user(self, data: Authorised):
        
        db = firestore.client()
        try:
            # Step 1: Verify the ID token using Firebase Admin SDK
            decoded_token = auth.verify_id_token(data.idToken)
            user_id = decoded_token.get("uid")
            
            # Step 2: Fetch user role from Firestore
            user_ref = db.collection("users").document(user_id)
            user_data = user_ref.get().to_dict()

            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")

            # Default to 'user' role if no role is set
            role = user_data.get("role", "user")

            # Step 3: Create a session ID
            session_id = self.create_session(user_id)

            # Step 4: Return authentication details, including the user's role
            return {
                "message": "Authentication successful",
                "user_id": user_id,
                "session_id": session_id,
                "role": role,  # Include the role in the response
        }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid ID token")


    def create_session(self, user_id: str):
        # Get a reference to Firestore
        db = firestore.client()

        # Generate a session ID
        session_id = str(uuid.uuid4())

        # Store session data in Firestore
        session_ref = db.collection('sessions').document(session_id)
        session_ref.set({
            'user_id': user_id,
            'created_at': firestore.SERVER_TIMESTAMP,  # Automatically set timestamp
        })

        # Optionally store session in memory for debugging
        self.sessions[session_id] = {"user_id": user_id}

        return session_id

    def validate_session(self, session_id: str) -> str:
        try:
            # Get a reference to Firestore
            db = firestore.client()

            # Retrieve session data
            session_ref = db.collection("sessions").document(session_id).get()
            if not session_ref.exists:
                raise HTTPException(status_code=401, detail="Session not found")

            session_data = session_ref.to_dict()
            user_id = session_data.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid session")

            return user_id
        except Exception as e:
            print(f"Error validating session: {e}")
            raise HTTPException(status_code=500, detail="Error validating session")
    
    
    def reset_password(email: str) -> dict:
        try:
            # Verify if the email exists in Firebase
            user_record = auth.get_user_by_email(email)

            # Return a confirmation that the email is associated with a user
            return {"message": "Email is registered and validated."}
        except auth.UserNotFoundError:
            raise HTTPException(status_code=404, detail="The email address is not registered in the system.")
        except Exception as e:
            print(f"Error resetting password: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
            
            


