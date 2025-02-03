import firebase_admin
from firebase_admin import firestore
from models.chatbot import FAQ


class FAQService:
    
    def __init__(self):
        self.db = firestore.client()
        self.sessions = {}
        
    def get_faq(self):

        faq_ref = self.db.collection("faq")
        docs = faq_ref.stream()
        faqs = [doc.to_dict() for doc in docs]
        print(faqs)
        return faqs
        
        
    def add_faq(self, faq: FAQ):
        
        faq_dict = faq.dict()
        faq_ref = self.db.collection("faq").add(faq_dict)
        return {"message": "FAQ added successfully", "user_id": faq_ref[1].id}


    def list_faq(self):
        
        faq_ref = self.db.collection("faq")
        docs = faq_ref.stream()
        faqs = [doc.to_dict() for doc in docs]
        return faqs