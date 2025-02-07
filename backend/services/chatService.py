from firebase_admin import auth, firestore
from fastapi import HTTPException
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict  # Add this import at the top of your file

class ChatService:
    
    def __init__(self):
        self.db = firestore.client()
        self.sessions = {}
        
    def get_chat_history(self, user_id: str) -> List[Dict]:
            db = firestore.client()
            try:
                # Reference the user's chat collection in Firestore
                chats_ref = db.collection("users").document(user_id).collection("chats")
                chats = chats_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

                chat_history = []
                for chat in chats:
                    chat_data = chat.to_dict()
                    timestamp = (
                        chat_data.get("timestamp").strftime('%Y-%m-%d %H:%M:%S')
                        if chat_data.get("timestamp")
                        else ""
                    )

                    # Add user's message
                    if chat_data.get("inputText"):
                        chat_history.append({
                            "sender": "user",  # User's input is always from the user
                            "text": chat_data.get("inputText", ""),
                            "timestamp": timestamp,
                        })

                    # Add bot's response
                    if chat_data.get("response"):
                        bot_message = {
                            "sender": "bot",
                            "text": "",  # Initialize text as an empty string
                            "timestamp": timestamp,
                        }

                        # If the response is a string, assign it directly
                        if isinstance(chat_data["response"], str):
                            bot_message["text"] = chat_data["response"]

                        # If the response is a dictionary, extract the "message" and "map_url"
                        elif isinstance(chat_data["response"], dict):
                            message = chat_data["response"].get("message", "")
                            map_url = chat_data["response"].get("map_url", None)

                            # Combine message and map_url into a single string
                            bot_message["text"] = message
                            if map_url:
                                bot_message["text"] += f"\n[View Map]({map_url})"

                        chat_history.append(bot_message)

                return chat_history

            except Exception as e:
                print(f"Error fetching chat history: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch chat history")
    
    
    def get_multiple_conversation_context(self, user_id: str, num_contexts: int):
        """
        Fetches multiple recent conversation contexts for the user.
        Args:
            user_id (str): The user's ID.
            num_contexts (int): Number of previous contexts to retrieve.
        Returns:
            list: A list of conversation contexts.
        """
        try:
            db = firestore.client()
            chats_ref = db.collection('users').document(user_id).collection('chats')
            recent_chats = chats_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(num_contexts).stream()

            context_list = []
            for chat in recent_chats:
                context = chat.to_dict().get('conversation_context', {})
                if context:
                    context_list.append(context)

            return context_list  # Return all retrieved contexts
        except Exception as e:
            print(f"Error fetching conversation context for user_id {user_id}: {e}")
            return []
    
    def get_one_conversation_context(self, user_id: str):
        try:
            db = firestore.client()
            chats_ref = db.collection('users').document(user_id).collection('chats')
            latest_chat = chats_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
            for chat in latest_chat:
                return chat.to_dict().get('conversation_context', {})
            return {}
        except Exception as e:
            print(f"Error fetching conversation context for user_id {user_id}: {e}")
            return {}
        
    
    def save_chat_to_firestore(self, input_text: str, response: str, mode: str, lat: float, long: float, user_id: str, conversation_context: dict):
        try:
            db = firestore.client()

            # Reference to Firestore collection
            chat_ref = db.collection('users').document(user_id).collection('chats').document()

            # Save chat data
            chat_ref.set({
                'inputText': input_text,
                'response': response,
                'mode': mode,
                'lat': lat,
                'long': long,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'conversation_context': conversation_context,
            })
            print(f"Chat saved successfully under user ID: {user_id}")
        except Exception as e:
            print(f"Error saving chat to Firestore for user_id {user_id}: {e}")

        
        
