import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences 
from tensorflow.keras.callbacks import EarlyStopping ,ModelCheckpoint,ReduceLROnPlateau,CSVLogger
from keras.models import load_model
from sklearn.preprocessing import LabelEncoder




# Construct paths relative to the base directory
MODEL_PATH = ("Emotion_model/emotion_model.h5")
DATASET_PATH = ("Emotion_model/train.txt")

class MoodService:
    def __init__(self):
        try:
            # Load and preprocess the dataset
            self.data = pd.read_csv(DATASET_PATH, sep=';')
            self.data.columns = ["Text", "Emotions"]

            # Prepare tokenizer and label encoder
            self.texts = self.data['Text'].tolist()
            self.labels = self.data['Emotions'].tolist()
            self.tokenizer = Tokenizer()
            self.tokenizer.fit_on_texts(self.texts)
            self.label_encoder = LabelEncoder()
            self.labels_encoded = self.label_encoder.fit_transform(self.labels)

            # Pad sequences and find max length
            self.max_len = max(len(seq) for seq in self.tokenizer.texts_to_sequences(self.texts))

            # Load the pre-trained model
            self.model = load_model(MODEL_PATH)
            print("Mood detection model loaded successfully.")

        except Exception as e:
            print(f"Error initializing MoodService: {e}")
            raise

    def detect_mood(self, input_text: str) -> str:
        try:
            # Convert input text to padded sequences
            input_seq = self.tokenizer.texts_to_sequences([input_text])
            padded_input_sequence = pad_sequences(input_seq, maxlen=self.max_len)

            # Predict the emotion
            prediction = self.model.predict(padded_input_sequence)
            predicted_label = self.label_encoder.inverse_transform([np.argmax(prediction[0])])
            print(f"Predicted Emotion: {predicted_label[0]}")
            return predicted_label[0]

        except Exception as e:
            print(f"Error detecting mood: {e}")
            return "Unknown"