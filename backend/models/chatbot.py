from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChatbotRequest(BaseModel):
    inputText: str
    latitude: float  
    longitude: float 
    mode:str

# Model for chat history response
class ChatMessage(BaseModel):
    sender: str  # "user" or "bot"
    text: str  # Message text, can be None if map_url is provided
    timestamp: str  # ISO-formatted timestamp
    map_url: Optional[str] = None  # Optional map URL 
    
# FAQ class
class FAQ(BaseModel):
    ques: str
    answer: str