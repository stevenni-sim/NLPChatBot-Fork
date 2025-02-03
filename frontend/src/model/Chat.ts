export interface ChatData {
  inputText: string;
  latitude: number;
  longitude: number;
  mode: string;
}

export interface ChatHistory {
  sender: 'user' | 'bot'; // Define sender as either 'user' or 'bot'
  text: string;           // The actual message text
  timestamp: string;      // Timestamp of the message
  map_url?: string;  // Optional Google Maps embed URL
  richContent?: JSX.Element[]; // Add this property if valid for ChatHistory

}

export interface ChatResponse {
  message: string; // General chatbot message for "basic", "mood", or "planner" modes
  map_url: string; // Optional Google Maps embed URL for relevant responses
  msg: Array<LocationItem>; // Array of location details for "location" mode
  mode: string;
}


export interface LocationItem {
  name: string; // Name of the location
  distance: string; // Distance to the location
  latitude: string; // Latitude of the location
  longitude: string; // Longitude of the location
}
