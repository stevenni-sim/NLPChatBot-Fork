import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
# Specify the path to your .env file
env_path = os.path.join(os.path.dirname(__file__), "../.env")  # Adjust the relative path to your .env file
load_dotenv(dotenv_path=env_path)

# Get the Gen AI API key from the environment variables
api_key = os.getenv("GEN_AI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=api_key)

# Default generation configuration
DEFAULT_GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
MODEL_NAME = "gemini-1.5-flash"

def general_chat(inputdata, extra, conversation_context=None):

    try:
        # Initialize the model and start a chat session
        model = genai.GenerativeModel(model_name=MODEL_NAME, 
                                      generation_config=DEFAULT_GENERATION_CONFIG)
        
        chat_session = model.start_chat(history=[])

        # Combine context, input, and extra instructions
        context_prompt = ""
        if conversation_context:
            context_prompt = "Context from previous conversation: " + \
                             " | ".join(f"{key}: {value}" for key, value in conversation_context.items())

        full_prompt = f"{context_prompt} Current input: {inputdata} {extra}".strip()

        # Send the message to Gemini AI
        chat_response = chat_session.send_message(full_prompt)

        return chat_response.text if hasattr(chat_response, 'text') else str(chat_response)
    except Exception as e:
        print(f"Error in Gemini AI communication: {e}")
        return None


def extract_entities_with_gemini(input_text, entity_type="location"):
   
    prompt = (
        f"Extract the {entity_type} mentioned in the following text:\n\n"
        f"Text: {input_text}\n\n"
        f"Response: Provide only the {entity_type} name or say 'None' if no {entity_type} is found."
    )

    response = general_chat(prompt, extra="Focus only on entity extraction.")
    if response:
        extracted_entity = response.strip()
        return None if extracted_entity.lower() == "none" else extracted_entity
    return None


def extract_date_with_gemini(input_text):
   
    prompt = (
        "Identify and extract the date mentioned in the input in natural language. "
        "For example, 'today', 'next Sunday', or 'tomorrow'. If no date is found, respond with 'no date found'."
    )
    response = general_chat(input_text, prompt)
    
    # Clean and return the extracted date phrase
    date_phrase = response.strip().lower()
    if date_phrase == "no date found":
        print("No valid date could be determined.")
        return None

    print(f"Extracted Date Phrase: {date_phrase}")
    return date_phrase



def extract_trip_entities_with_gemini(input_text):
    """
    Returns a dict containing extracted details including budgetPerDay, interests, and numberOfDays.
    """
    entities_to_extract = [
        "budgetPerDay", "interests", "numberOfDays"
    ]
    extracted_data = {}

    for entity in entities_to_extract:
        prompt = (
            f"Extract the {entity} mentioned in the following text:\n\n"
            f"Text: {input_text}\n\n"
            f"Response: Provide only the {entity} or say 'None' if no {entity} is found."
            f"just extract the budget dont need to divide by numberOfDays"
        )
        
        # Call Gemini AI to process the prompt
        try:
            response = general_chat(prompt, extra="Focus only on entity extraction.")
            extracted_entity = response.strip()
            
            # Handle 'None' responses from Gemini AI
            if extracted_entity.lower() == "none":
                extracted_data[entity] = None
            else:
                # Post-process based on entity type
                if entity == "budgetPerDay":
                    # Convert budget to float if valid
                    try:
                        extracted_data[entity] = float(extracted_entity)
                    except ValueError:
                        print(f"Invalid budget value: {extracted_entity}")
                        extracted_data[entity] = None
                elif entity == "interests":
                    # Split interests into a list
                    extracted_data[entity] = [
                        interest.strip() for interest in extracted_entity.split(",")
                    ]
                elif entity == "numberOfDays":
                    # Try to extract the number of days directly as a number
                    try:
                        # Look for numeric values and set them as days
                        extracted_data[entity] = int(extracted_entity)
                    except ValueError:
                        print(f"Invalid number of days or unable to extract: {extracted_entity}")
                        extracted_data[entity] = None
        except Exception as e:
            print(f"Error extracting {entity} with Gemini AI: {e}")
            extracted_data[entity] = None  # Default to None on failure
    print(extracted_data)
    
    return extracted_data
