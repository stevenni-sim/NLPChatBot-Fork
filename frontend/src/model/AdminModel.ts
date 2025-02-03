import { getFirestore, collection, getDocs, doc, updateDoc } from 'firebase/firestore';
import { getApp } from 'firebase/app';
import axios from 'axios';
import { BASE_URL } from '../service/config';

export interface User {
  id: string;
  username: string;
  email: string;
  contact: string;
  password: string;
}

// Function to fetch users from Firestore
export const fetchUsers = async (): Promise<User[]> => {
  const db = getFirestore(getApp()); // Get Firestore instance
  const usersCollection = collection(db, 'users');
  const userSnapshot = await getDocs(usersCollection);
  const userList: User[] = userSnapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data() as Omit<User, 'id'>, // Exclude 'id' as Firestore uses it as doc ID
  }));
  return userList;
};

// Function to update a user's details in Firestore
export const updateUser = async (id: string, updatedUser: User) => {
  const db = getFirestore(getApp());
  const userRef = doc(db, 'users', id);
  const { id: userId, ...userData } = updatedUser; // Exclude 'id' as Firestore already uses it as the document ID
  await updateDoc(userRef, userData);
};


export const deleteUser = async (userId: string): Promise<void> => {
  try {
    // Send DELETE request to the Python backend
    const response = await axios.delete(`${BASE_URL}/users/${userId}`);

    // Ensure the response status indicates success
    if (response.status !== 200) {
      throw new Error(`Failed to delete user. Server responded with status: ${response.status}`);
    }

    console.log(`User with ID ${userId} deleted successfully.`);
  } catch (error) {
    console.error("Error deleting user:", error);

    // Log more details if it's an Axios error
    if (axios.isAxiosError(error)) {
      console.error("Axios error details:", error.response?.data || "No additional details provided.");
    }

    // Re-throw the error for further handling
    throw error;
  }
};

