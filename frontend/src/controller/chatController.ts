import axios, { AxiosResponse } from 'axios';
import { BASE_URL } from '../service/config';
import { ChatData, ChatHistory, ChatResponse } from '../model/Chat';
import { getAuth } from 'firebase/auth';



export const chatController = {
  // Get chatbot response
  async getChatResponse(chat: ChatData): Promise<AxiosResponse<ChatResponse>> {
    try {
      // Get Firebase token for logged-in users
      const auth = getAuth();
      const currentUser = auth.currentUser;
      const token = currentUser ? await currentUser.getIdToken() : null;

      // Include the Authorization header only if the user is logged in
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      // Send chat data to the backend
      const response = await axios.post<ChatResponse>(
        `${BASE_URL}/chatbot/`,
        chat,
        { headers }
      );

      // Debug log to inspect the response
      console.log("Chatbot response from backend:", response.data);

      return response; // Return the response directly
    } catch (error) {
      console.error("Error getting chatbot response:", error);
      throw error;
    }
  },

  // Get chat history
async getChatHistory(): Promise<ChatHistory[]> {
  try {
    const auth = getAuth();
    const currentUser = auth.currentUser;

    if (!currentUser) throw new Error("User is not logged in.");

    const token = await currentUser.getIdToken();
    const headers = { Authorization: `Bearer ${token}` };

    const { data } = await axios.get<ChatHistory[]>(`${BASE_URL}/chatHistory`, { headers });

    return data || []; // Return data or an empty array if no data
  } catch (error: any) {
    console.error("Error fetching chat history:", error.message || error);
    throw new Error(
      error.response?.data?.message || "Failed to fetch chat history. Please try again."
    );
  }
},

async getFAQs(): Promise<{ ques: string; answer: string }[]> {
  try {
    // Fetch the structured JSON response from the backend
    const response = await axios.get<{ ques: string; answer: string }[]>(`${BASE_URL}/faqs`);

    return response.data; // Directly return the array of FAQ objects
  } catch (error) {
    console.error("Error fetching FAQs:", error);
    throw error; // Rethrow the error to handle it in the calling component
  }
}


};





