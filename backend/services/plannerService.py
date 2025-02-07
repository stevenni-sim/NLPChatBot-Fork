import os
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler

# Get the base directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct paths for the dataset and model dynamically
DATASET_PATH = os.path.join(BASE_DIR, "../Itinerary_Planner_Model/itinerarydataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "../Itinerary_Planner_Model/Planner_Model.h5")


class Planner:
    def __init__(self, dataset_path=DATASET_PATH, model_path=MODEL_PATH):
        """
        Initialize the Planner with the dataset path and model path.

        Args:
            dataset_path (str): Path to the dataset CSV file.
            model_path (str): Path to the pre-trained model file.
        """
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.attractions = self.import_attractions_dataset()
        self.model = self.load_model()

    def import_attractions_dataset(self):
        """
        Import the attractions dataset from the dataset path.
        """
        try:
            # Read the dataset
            attractions = pd.read_csv(self.dataset_path)

            # Preprocess: Ensure necessary columns exist
            required_columns = ["name", "tags", "cost", "description", "rating", "opening_hours"]
            for column in required_columns:
                if column not in attractions.columns:
                    raise ValueError(f"Missing required column: {column}")

            # Drop rows with missing values in required columns
            attractions = attractions.dropna(subset=required_columns)

            # Convert cost to float
            attractions["cost"] = attractions["cost"].astype(float)

            # Convert rating to float
            attractions["rating"] = attractions["rating"].astype(float)

            # Return the cleaned dataset
            return attractions

        except Exception as e:
            print(f"An error occurred while importing the dataset: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on failure

    def load_model(self):
        """
        Load the pre-trained model from the model path.
        """
        try:
            model = tf.keras.models.load_model(self.model_path)
            print(f"Model loaded from {self.model_path}")
            return model
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
            return None

    @staticmethod
    def parse_opening_hours(opening_hours):
        """
        Parse the opening hours string to extract opening and closing times.
        """
        try:
            opening, closing = opening_hours.split(" - ")
            opening_time = datetime.strptime(opening, "%I:%M %p")
            closing_time = datetime.strptime(closing, "%I:%M %p")
            return opening_time, closing_time
        except ValueError:
            return None, None  # For 24-hour places or invalid formats




    def recommend_with_model(self, user_interests, user_budget, number_of_days):
        """
        Recommend attractions based on user preferences and budget.
        """
        attractions_data = self.attractions
        itinerary_model = self.model

        # Validate inputs
        if attractions_data.empty:
            raise ValueError("The attractions data is empty. Cannot make recommendations.")

        # Filter attractions based on user budget
        filtered_attractions = attractions_data[attractions_data["cost"] <= user_budget]
        if filtered_attractions.empty:
            raise ValueError("No attractions found within the specified budget.")

        # Calculate tag relevance (number of matching tags)
        user_tags = set(user_interests.split())
        filtered_attractions["tag_relevance"] = filtered_attractions["tags"].apply(
            lambda x: len(user_tags.intersection(set(x.split()))))

        # Filter attractions with at least one matching tag
        filtered_attractions = filtered_attractions[filtered_attractions["tag_relevance"] > 0]
        if filtered_attractions.empty:
            raise ValueError("No attractions found with matching tags.")

        # Normalize ratings
        scaler = MinMaxScaler()
        filtered_attractions["normalized_rating"] = scaler.fit_transform(filtered_attractions[["rating"]])

        # Preprocess input features for the model
        input_features = {
            "interests": user_interests,
            "budget": user_budget,
        }
        processed_input = self.preprocess_for_model(input_features, filtered_attractions)

        # Generate predictions from the model
        predictions = itinerary_model.predict(processed_input).flatten()

        # Assign predictions as scores
        filtered_attractions["model_score"] = predictions

        # Combine model score, tag relevance, and normalized rating into a weighted score
        filtered_attractions["final_score"] = (
            0.5 * filtered_attractions["model_score"] +
            0.4 * filtered_attractions["tag_relevance"] +
            0.2 * filtered_attractions["normalized_rating"]
        )

        # Sort attractions by final score
        sorted_attractions = filtered_attractions.sort_values(by="final_score", ascending=False).reset_index(drop=True)

        # Separate user-interest attractions and others
        user_interest_attractions = sorted_attractions[sorted_attractions["tag_relevance"] > 0]
        other_attractions = sorted_attractions[sorted_attractions["tag_relevance"] == 0]

        # Initialize the itinerary
        itinerary = []
        current_time = datetime.strptime("9:00 AM", "%I:%M %p")
        day_counter = 1
        current_day = f"Day {day_counter}"
        daily_itinerary = []
        daily_cost = 0

        # Calculate how many attractions to fit into each day
        attractions_per_day = len(user_interest_attractions) // number_of_days
        remaining_attractions = len(user_interest_attractions) % number_of_days

        # Iterate over user interest attractions first
        for idx, attraction in user_interest_attractions.iterrows():
            opening, closing = self.parse_opening_hours(attraction["opening_hours"])

            if opening and closing:
                if current_time <= opening:
                    if current_time + timedelta(hours=3) <= closing:
                        end_time = current_time + timedelta(hours=3)
                        daily_itinerary.append({
                            "name": attraction["name"],
                            "description": attraction.get("description", "No description available"),
                            "cost": attraction["cost"],
                            "rating": attraction["rating"],
                            "opening_hours": attraction["opening_hours"],
                            "time_range": f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
                        })
                        daily_cost += attraction["cost"]
                        current_time = end_time + timedelta(hours=1)
                elif current_time + timedelta(hours=3) <= closing:
                    end_time = current_time + timedelta(hours=3)
                    daily_itinerary.append({
                        "name": attraction["name"],
                        "description": attraction.get("description", "No description available"),
                        "cost": attraction["cost"],
                        "rating": attraction["rating"],
                        "opening_hours": attraction["opening_hours"],
                        "time_range": f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
                    })
                    daily_cost += attraction["cost"]
                    current_time = end_time + timedelta(hours=1)

            # If the time reaches 9 PM, the day ends
            if current_time >= datetime.strptime("9:00 PM", "%I:%M %p") or len(daily_itinerary) >= attractions_per_day + (1 if day_counter <= remaining_attractions else 0):
                itinerary.append({"day": current_day, "activities": daily_itinerary})
                day_counter += 1
                current_day = f"Day {day_counter}"
                daily_itinerary = []
                current_time = datetime.strptime("9:00 AM", "%I:%M %p")
                daily_cost = 0

        # Fill up remaining days with other attractions if needed
        for idx, attraction in other_attractions.iterrows():
            opening, closing = self.parse_opening_hours(attraction["opening_hours"])
            if opening and closing:
                if current_time <= opening and current_time + timedelta(hours=3) <= closing:
                    end_time = current_time + timedelta(hours=3)
                    daily_itinerary.append({
                        "name": attraction["name"],
                        "description": attraction.get("description", "No description available"),
                        "cost": attraction["cost"],
                        "rating": attraction["rating"],
                        "opening_hours": attraction["opening_hours"],
                        "time_range": f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
                    })
                    daily_cost += attraction["cost"]
                    current_time = end_time + timedelta(hours=1)
            if len(daily_itinerary) >= attractions_per_day:
                itinerary.append({"day": current_day, "activities": daily_itinerary})
                day_counter += 1
                current_day = f"Day {day_counter}"
                daily_itinerary = []
                current_time = datetime.strptime("9:00 AM", "%I:%M %p")
                daily_cost = 0

        return itinerary



    def preprocess_for_model(self, input_features, attractions):
        """
        Preprocess user input for the model.

        Args:
            input_features (dict): User inputs like interests and budget.
            attractions (pd.DataFrame): Attraction data.

        Returns:
            np.array: Input array with rows corresponding to each attraction.
        """
        # Vectorize user interests
        interests_vector = self.vectorize_interests(input_features["interests"])
        budget_normalized = input_features["budget"] / 1000  # Normalize budget

        # Ensure consistent feature size (e.g., 94 features total)
        input_rows = []
        for _, row in attractions.iterrows():
            tags_vector = self.vectorize_interests(row["tags"])  # Vectorize attraction tags
            # Combine interests, attraction tags, and budget into a single row
            combined_features = interests_vector + tags_vector + [budget_normalized]

            # Ensure that the feature size is 94 by padding or truncating
            if len(combined_features) > 81:
                combined_features = combined_features[:81]
            else:
                # Pad with zeros if fewer than 94 features
                combined_features.extend([0] * (81 - len(combined_features)))

            input_rows.append(combined_features)

        return np.array(input_rows)




    def postprocess_model_output(self, predictions, attractions):
        """
        Convert model predictions into a list of recommended attractions.
        Args:
            predictions (np.array): Model predictions.
            attractions (pd.DataFrame): Original attraction details.
        Returns:
            pd.DataFrame: Recommended attractions.
        """
        # Assume predictions are scores for attractions
        if len(predictions) != len(attractions):
            raise ValueError("Length of predictions does not match the number of rows in the DataFrame.")

        # Sort attractions by score
        return attractions.sort_values(by="score", ascending=False)

    @staticmethod
    def vectorize_interests(interests):
        """
        Convert user interests into a numerical vector.
        Args:
            interests (str): User's interests as a space-separated string (e.g., "arts nature family").
        Returns:
            list: A binary vector indicating the presence of predefined keywords.
        """
        # Predefined keywords for interests
        interest_keywords = ["arts", "nature", "adventure", "shopping", "relaxation", "family", "nightlife", "technology"]

        # Create a binary vector
        return [1 if keyword in interests.lower() else 0 for keyword in interest_keywords]


