import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Paths to Intent Recognition model files
MODEL_PATH = "Intent_Recognition_Model"
TOKENIZER_PATH = "Intent_Recognition_Model"

# Define label mapping (based on the model's `config.json`)
LABEL_MAPPING = {
    0: "location_query",
    1: "general_query",
    2: "date_time",
    3: "weather_query"
}

class IntentService:
    def __init__(self):
        try:
            # Load the tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            print("Intent Recognition model loaded successfully.")
        except Exception as e:
            print(f"Failed to load intent recognition model: {e}")
            self.tokenizer = None
            self.model = None

    def classify_intent(self, input_text: str) -> str:
        """
        Classify the intent of the given input text.
        """
        try:
            if not self.tokenizer or not self.model:
                raise ValueError("Model or tokenizer not loaded.")

            # Tokenize the input text
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128
            )

            # Get model predictions
            outputs = self.model(**inputs)
            logits = outputs.logits

            # Get the predicted label
            predicted_label = torch.argmax(logits, dim=1).item()

            # Map the label to an intent
            intent = LABEL_MAPPING.get(predicted_label, "unknown")  # Default to "unknown" for unmapped labels

            return intent
        except Exception as e:
            print(f"Error classifying intent: {e}")
            return "unknown"
