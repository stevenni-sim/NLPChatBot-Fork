# Import models
from models.user import User,Authorised, UserProfile, EditUsername, UpdateUsernameRequest, EditEmail, UpdateEmailRequest, UpdatePasswordRequest, UpdateContactRequest, PasswordResetRequest
from models.chatbot import ChatbotRequest, ChatMessage, FAQ


# Import services
from services.userService import UserService
from services.chatService import ChatService
from services.faqService import FAQService
from services.locationService import get_google_maps_directions, search_foursquare_nearby, format_foursquare_response, get_allinfo
from services.weatherService import fetch_weather_data, convert_to_local_timestamp
from services.moodService import MoodService
from services.intentService import IntentService
from services.geminiService import general_chat, extract_entities_with_gemini, extract_date_with_gemini, extract_trip_entities_with_gemini
from services.firebaseService import initialize_firebase
from services.plannerService import Planner
from Itinerary_Planner_Model.nightlife import get_nightlife_list

#other module imports
from firebase_admin import credentials, firestore, auth
from fastapi import FastAPI, HTTPException, Header, Depends
import tensorflow as tf
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
import requests


# Initialize Firebase
initialize_firebase()
    
# Get a reference to Firestore
db = firestore.client()

queries = [
    "restaurant", "mosque", "spa", "museum", "park", "beach", "shopping", "art", "zoo", "aquarium", "historical", "theater", "coffee",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For access to UserService class
user_service = UserService()

# For access to ChatService class
chat_service = ChatService()

# For access to UserService class
faq_service = FAQService()

# Initialize the MoodService 
mood_service = MoodService()

# Initialize the intent Recognition class
intent_service = IntentService()

# Initialize the Itinerary Planner
planner = Planner()


@app.get("/")
def read_root():
    try:
        return {"message": "Welcome to the User API"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



#registration of new user and store details in firebase
@app.post("/users/", status_code=201)
async def create_user(user: User):

    try:
        # Check if email is already registered in Firebase Authentication
        try:
            firebase_user = auth.get_user_by_email(user.email)
            if firebase_user:
                raise HTTPException(status_code=409, detail="This email is already registered!")
        except auth.UserNotFoundError:
            pass  # Email is not registered, proceed to create user

        # Check if the username already exists in Firestore
        user_query = db.collection('users').where('username', '==', user.username).stream()
        if any(user_doc for user_doc in user_query):
            raise HTTPException(status_code=409, detail="This username is already taken!")

        # Create user in Firebase Authentication
        firebase_user = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.username,
        )

        # Add the user to the Firestore 'users' collection
        user_ref = db.collection('users').document(firebase_user.uid)
        user_ref.set({
            'uid': firebase_user.uid,
            'email': user.email,
            'username': user.username,
            'contact': user.contact,  
            'role' : 'tourist'
        })

        return {"message": "User registered successfully!", "user_id": firebase_user.uid}

    except HTTPException as http_exc:
        # Reraise HTTP-specific exceptions
        raise http_exc
    except Exception as e:
        # Catch other errors
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

#login
@app.post("/authentication/")
async def authorised(data: Authorised):
    try:
        # Authenticate user and generate session ID
        res = user_service.authenticate_user(data)

        # Return user info and session ID
        return {"message": res["message"], "user_id": res["user_id"], "session_id": res["session_id"], "role": res["role"]}

    except Exception as e:
        raise HTTPException(status_code=401, detail=str("User information incorrect, please try again"))


#fetch user profile information for user
@app.get("/users/{user_id}", response_model=UserProfile)
async def fetch_user_profile(user_id: str):
    print(f"Received user_id: {user_id}")  # Log the received user ID
    
    try:
        # Query Firestore for the document with the matching user_id
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore")

        # Fetch user data from the Firestore document
        user_data = user_doc.to_dict()

        # Only extract the fields needed for the UserProfile response
        user_response_data = {
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "contact": user_data.get("contact")
        }

        # Return a UserProfile model with only the necessary fields
        return UserProfile(**user_response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user profile: {str(e)}")


# Update username for a given user ID
@app.patch("/users/{user_id}/updateUsername", response_model=EditUsername)
async def update_username(user_id: str, request: UpdateUsernameRequest):
   
        # Log the received username for debugging
        print(f"Received username: {request.username}")
        username = request.username

        # Check if the username already exists in Firestore
        user_query = db.collection('users').where('username', '==', username).stream()
        if any(user_doc for user_doc in user_query):
            raise HTTPException(status_code=409, detail="This username is already taken")

        # Fetch the user document from Firestore using the user_id
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found!")

        # Update the username in the Firestore user document
        user_ref.update({'username': username})

        # Return the updated username in the response
        return EditUsername(username=username)
        

# Update email for a given user ID
@app.patch("/users/{user_id}/updateEmail", response_model=EditEmail)
async def update_email(user_id: str, request: UpdateEmailRequest):
    # Log the received email for debugging
    print(f"Received email: {request.email}")
    
    email = request.email

    # Check if the email already exists in Firestore
    user_query = db.collection('users').where('email', '==', email).stream()
    if any(user_doc for user_doc in user_query):
        raise HTTPException(status_code=409, detail="This email is already taken")

    # Fetch the user document from Firestore using the user_id
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found!")

    # Update the email in the Firestore user document
    user_ref.update({'email': email})

    # Return the updated email in the response
    return EditEmail(email=email)


# Update Password for a given user ID
@app.patch("/users/{user_id}/updatePassword")
async def update_password(user_id: str, request: UpdatePasswordRequest):
    # Validate the new password (optional, you can add more checks here)
    new_password = request.password

    try:
        # Update the password in Firebase Authentication
        user = auth.update_user(user_id, password=new_password)

        # If successful, return a success message
        return {"message": "Password updated successfully."}

    except auth.UserNotFoundError:
        # Handle the case where the user ID is invalid or the user doesn't exist
        raise HTTPException(status_code=404, detail="User not found.")

    except auth.InvalidPasswordError:
        # Handle invalid password errors (if any)
        raise HTTPException(status_code=400, detail="The new password is invalid.")

    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Update contact for a given user ID
@app.patch("/users/{user_id}/updateContact")
async def update_contact(user_id: str, request: UpdateContactRequest):
    # Validate the new contact (optional, you can add more checks here)
    new_contact = request.contact

    try:
        # Fetch the user document from Firestore using the user_id
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            # Handle the case where the user ID is invalid or the user doesn't exist
            raise HTTPException(status_code=404, detail="User not found!")

        # Update the contact in the Firestore user document
        user_ref.update({'contact': new_contact})

        # If successful, return a success message
        return {"message": "Contact updated successfully."}

    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Allow user to reset password if they forget
@app.post("/api/resetPassword")
async def reset_password_endpoint(request: PasswordResetRequest):
    try:
        # Call the reset_password function to validate the email
        UserService.reset_password(request.email)
        
        # Return a success message to the frontend
        return {"message": "Email is registered and validated."}
    except HTTPException as e:
        # Rethrow specific HTTP exceptions raised in the service layer
        raise e
    except Exception as e:
        print(f"Unexpected error in reset_password_endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


#system admin delete user
@app.delete("/users/{user_id}", status_code=200)
async def delete_user(user_id: str):
    # Deletes a user from both Firebase Authentication and Firestore.

    try:
        # Step 1: Delete user document from Firestore
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore.")

        user_ref.delete()
        print(f"Deleted Firestore document for user ID: {user_id}")

        # Step 2: Delete user from Firebase Authentication
        auth.delete_user(user_id)
        print(f"Deleted Firebase Auth user with ID: {user_id}")

        return {"message": f"User with ID: {user_id} successfully deleted."}

    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found in Firebase Authentication.")

    except Exception as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# ------------------------------------------------------------------------------------Below Chatbot related

@app.post("/nearbyLocation/")
async def nearbyLocation(request: ChatbotRequest):
    mode = request.mode
    lat = request.latitude
    long = request.longitude
    datainfo = get_allinfo(lat,long, request.inputText)
    return datainfo


# User view FAQs in chatbot
@app.get("/faqs", response_model=List[dict])
async def get_faqs():

    # Endpoint to fetch FAQs for the chatbot.
    # Returns a JSON response with a list of FAQs.

    try:
        faqs = faq_service.get_faq()  # List of FAQs (each is a dict with 'ques' and 'answer')
        return faqs  # Return FAQs as JSON
    except Exception as e:
        print(f"Error retrieving FAQs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving FAQs")
    

# Admin create new FAQs
@app.post("/CreateFaqs", status_code=201) 
async def create_faq(faq: FAQ):
    try:
        
        created_faq = faq_service.add_faq(faq)
        return created_faq  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Admin retrieve and view FAQs
@app.get("/ListFaqs", response_model=List[FAQ])
async def list_faq():
    try:
        faqs = faq_service.list_faq()
        return faqs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chatbot/")
async def chatbot_response(request: ChatbotRequest, authorization: Optional[str] = Header(None)):
    
    mode = request.mode
    lat = request.latitude
    long = request.longitude
    input_text = request.inputText
    print(f"Mode: {mode} | Latitude: {lat} | Longitude: {long}")

    user_id = None
    conversation_context = {}
    full_context_summary = ""
    
    # Authenticate user and fetch conversation context
    if authorization:
        try:
            decoded_token = auth.verify_id_token(authorization.split("Bearer ")[1])
            user_id = decoded_token.get("uid")
            if user_id:
                # Fetch the latest conversation context
                conversation_context = chat_service.get_one_conversation_context(user_id)
                if not conversation_context:
                    # Retrieve more contexts dynamically if immediate context is empty
                    all_contexts = chat_service.get_multiple_conversation_context(user_id, num_contexts=10)
                    full_context_summary = " | ".join(
                        f"Message: {ctx.get('last_message', '')}, Response: {ctx.get('last_response', '')}" for ctx in all_contexts
                    )
        except Exception as e:
            print(f"Authentication error: {e}")

    # Add a descriptive extra prompt for Gemini AI
    extra = (
        "Provide one response. Ensure the chat stays related to Singapore tourism and travel plans. "
        "If content is unrelated, steer the conversation back to Singapore Tourism or make small talk."
    )

    # Initialize a standardized response structure
    response = {
        "message": "",
        "map_url": None,
        "msg": None,
        "mode": mode
    }
 
    try:
        # Combine user input with historical context if available
        if full_context_summary:
            combined_input = f"Historical context: {full_context_summary}. Current input: {input_text}"
            main_message = general_chat(combined_input, extra, conversation_context)
        else:
            main_message = general_chat(input_text, extra, conversation_context)

        # Handle modes
        if mode == "basic":
            
            intent = intent_service.classify_intent(input_text)
            print(intent)
            
            if intent == "location_query":
                    destination = extract_entities_with_gemini(input_text, entity_type="location")
                    if destination:
                        response["message"] = main_message
                        response["map_url"] = get_google_maps_directions(lat, long, destination)
                        response["message"] = f"Here is the map for directions to {destination}."
                    else:
                        response["message"] = "Sorry, I couldn't identify the destination."
                    
            elif intent == "weather_query":
                try:
                    # Step 1: Extract the date phrase using Gemini AI
                    date_phrase = extract_date_with_gemini(input_text)
                    if not date_phrase or date_phrase.lower() == "no date found":
                        # If no date is found, fallback to main_message
                        response["message"] = main_message
                    else:
                        # Step 2: Convert the date phrase to a local timestamp
                        date_timestamp = convert_to_local_timestamp(date_phrase, timezone="Asia/Singapore")

                        # Step 3: Fetch weather data from the OpenWeather API
                        weather_data = fetch_weather_data(lat, long, date_timestamp)

                        if "error" not in weather_data:
                            # Step 4: Format the weather data into a user-friendly response
                            response["message"] = (
                                f"Weather information in Singapore for {weather_data['date']}:\n"
                                f"- Min Temperature: {weather_data['min_temp']}°C\n"
                                f"- Max Temperature: {weather_data['max_temp']}°C\n"
                                f"- Average Temperature: {weather_data['average_temp']}°C\n"
                                f"- Description: {weather_data['description'].capitalize()}\n"
                                f"- Total Rainfall: {weather_data['total_rainfall']} mm\n"
                            )
                            # Add an icon if available
                            if "icon" in weather_data:
                                response["message"] += f" ![Weather Icon]({weather_data['icon']})"
                        else:
                            # Handle errors in the weather data response
                            response["message"] = "I'm sorry, I couldn't fetch the weather data. Please try again later."

                except ValueError as ve:
                    # Handle errors in date parsing
                    print(f"Error parsing date: {ve}")
                    response["message"] = main_message

                except Exception as e:
                    # Handle unexpected errors
                    print(f"Unexpected error in weather query: {e}")
                    response["message"] = main_message
                    
            else:
                response["message"] = main_message


        elif mode == "location":
            print(f"Processing location mode for: {input_text}")

            # Step 1: Count nearby places for predefined queries
            try:
                place_counts = {
                    query: len(search_foursquare_nearby(latitude=lat, longitude=long, query=query))
                    for query in queries
                }
                print(f"Place Counts: {place_counts}")

                # Step 2: Match user input with available place categories
                matched_words = [word for word in input_text.split() if word in place_counts.keys()]
                print(f"Matched Words: {matched_words}")

                if matched_words:
                    # Step 3: Fetch detailed location info for the first matched word
                    matched_query = matched_words[0]
                    results = search_foursquare_nearby(latitude=lat, longitude=long, query=matched_query)
                    formatted_results = format_foursquare_response(results)
                    print(f"Location Info Returned: {formatted_results}")

                    # Build the response using formatted location info
                    if formatted_results:
                        response["msg"] = formatted_results
                    else:
                        response["msg"] = [{"error": f"No locations found for your query: {matched_query}"}]
                else:
                    # Step 4: Provide fallback response with aggregated counts
                    if place_counts:
                        response["msg"] = [
                            {
                                "name": f"Nearby {key}",
                                "distance": f"{value} places found",
                                "latitude": "",
                                "longitude": ""
                            }
                            for key, value in place_counts.items() if value > 0
                        ]
                    else:
                        response["msg"] = [{"error": "No nearby places found for predefined queries."}]

            except Exception as e:
                print(f"Error in location mode: {e}")
                response["msg"] = [{"error": "An error occurred while processing your location request."}]


        elif mode == "mood":
            # Handle mood-based recommendations
            mood_info = mood_service.detect_mood(input_text)
            response["message"] = general_chat(
                input_text,
                f"Mention the user's mood: {mood_info}. Suggest Singapore travel locations or activities suited to their mood between each recommendation. Ensure suggestions are helpful and focused on Singapore tourism.",
                conversation_context)
        
        
        elif mode == "planner":
            if "planner_questions_asked" not in conversation_context:
                response["message"] = (
                    "Let's plan your trip! Provide the following details:\n"
                    "\t1. How many days are you travelling?\n"
                    "\t2. Budget per day (in SGD)\n"
                    "\t3. Interests (e.g., arts, nature, adventure, shopping, relaxation, family, technology)\n please choose at least 3 categories"
                )
                conversation_context["planner_questions_asked"] = True
            else:
                try:
                    user_input = input_text
                    user_data = extract_trip_entities_with_gemini(user_input)
                    print(user_data)
                    # Validate input
                    if user_data.get("numberOfDays") is None:
                        raise ValueError("Please specify the number of days for your trip.")
                    if not user_data.get("budgetPerDay"):
                        raise ValueError("Please specify your budget.")
                    if not user_data.get("interests"):
                        raise ValueError("Please specify at least one interest.")

                    # Get the number of days
                    total_days = user_data["numberOfDays"]

                    # Get user preferences
                    user_interests = " ".join(user_data["interests"])
                    user_budget = float(user_data["budgetPerDay"])

                    # Call the itinerary model for recommendations
                    recommended_attractions = planner.recommend_with_model(user_interests, user_budget, total_days)

                    # Initialize the response message string
                    itinerary_message = "Here is your personalized itinerary:\n\n"

                    # Fill the days with the recommended attractions
                    # Iterate through each day's itinerary
                    for day_info in recommended_attractions:
                        day = day_info.get('day', 'Unknown Day')
                        day_attractions = day_info.get('activities', [])
                        
                        itinerary_message += f"**{day}**:\n"
                        
                        if day_attractions:  # If there are activities for this day
                            for attraction in day_attractions:
                                name = attraction.get('name', 'N/A')
                                description = attraction.get('description', 'N/A')
                                cost = attraction.get('cost', 'N/A')
                                rating = attraction.get('rating', 'N/A')
                                time_range = attraction.get('time_range', 'N/A')  # Get the time range for the activity

                                # Add the activity to the itinerary message
                                itinerary_message += f"- {name} \nDescription: {description}\n Cost: ${cost:.2f}\n Rating: {rating}\n Time: {time_range})\n"
                            itinerary_message += "-" * 30 + "\n"

                        else:  # If no activities are available for this day
                            itinerary_message += "No activities planned for this day.\n"
                            
                    # Add nightlife suggestions after the itinerary
                    nightlife_list = get_nightlife_list()  # Call the function to get the nightlife list
                    nightlife_suggestions = suggest_nightlife(nightlife_list)
                    itinerary_message += "\n\nSuggested Nightlife Options:\n"
                    for suggestion in nightlife_suggestions:
                        itinerary_message += (
                            f"- Name: {suggestion['name']}\n"
                            f"  Cost: {suggestion['cost']}\n"
                            f"  Review: {suggestion['review']}\n"
                            f"  Opening Hours: {suggestion['opening_hours']}\n"
                        )
                        itinerary_message += "-" * 30 + "\n"
      
                    response["message"] = itinerary_message

                    # Clear context after planning is complete
                    conversation_context.clear()

                except ValueError as e:
                    response["message"] = str(e)
                except Exception as e:
                    response["message"] = f"An error occurred: {str(e)}"
# ---------------------------------------------------

        # Debug logs for responses
        print(f"Chatbot Response: {response}")

        # Save chat context if the user is logged in
        if user_id:
            conversation_context.update({"last_message": input_text, "last_response": response})
            chat_service.save_chat_to_firestore(input_text, response, mode, lat, long, user_id, conversation_context)

        # Return the standardized response
        return response

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Function to suggest random nightlife attractions
def suggest_nightlife(nightlife_list):
    return random.sample(nightlife_list, min(3, len(nightlife_list)))



# FastAPI route to fetch chat history
@app.get("/chatHistory/", response_model=List[ChatMessage])
async def get_chat_history(
    authorization: str = Header(None),
    chat_service: ChatService = Depends(ChatService),
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        # Extract and verify Firebase token
        if "Bearer " not in authorization:
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
        token = authorization.split("Bearer ")[1]

        # Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)

        user_id = decoded_token.get("uid")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")

        # Fetch chat history for the user
        chat_history = chat_service.get_chat_history(user_id)

        # Debug: Log raw chat history from Firestore
        print(f"Raw chat history from Firestore: {chat_history}")

        # Validate and clean up chat history
        validated_chat_history = []
        for chat in chat_history:
            try:
                # Debug: Log each raw chat entry
                print(f"Processing chat entry: {chat}")

                # Extract and validate fields
                sender = chat.get("sender", "bot")  # Default to "bot" if sender is missing
                text = chat.get("text", "")  # Use "text" instead of "message"
                map_url = chat.get("map_url")  # Optional map URL
                timestamp = chat.get("timestamp", "")  # Default to empty string if missing

                # Ensure at least one of "text" or "map_url" is present
                if not text and not map_url:
                    # Debug: Log skipped entry
                    print(f"Skipping chat entry due to missing text and map_url: {chat}")
                    continue

                # Append the validated ChatMessage object to the result list
                validated_chat_history.append(
                    ChatMessage(
                        sender=sender,
                        text=str(text),  # Ensure text is always a string
                        timestamp=str(timestamp),  # Ensure timestamp is a string
                        map_url=str(map_url) if map_url else None,  # Ensure map_url is a string or None
                    )
                )
            except Exception as inner_e:
                # Debug: Log errors for individual entries
                print(f"Error validating chat entry: {inner_e}")
                continue  # Skip invalid chat entries and continue processing

        return validated_chat_history

    except Exception as e:
        # Debug: Log general exceptions
        print(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")















