import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Message {
  id: number;
  raw_text: string;
  time_created: string;
  author: string;
  details: {
    BHK: number;
    Bedroom: string;
    Sharing: boolean;
    Gender: string[];
    Address: string;
    Rent: number | string;
    Restrictions: string[];
    Furnished: string;
    Deposit: number | string;
    Brokerage: number;
    AvailableDate: string;
    ContactDetail: string;
  };
}

export const fetchMessages = async (): Promise<Message[]> => {
  try {
    const response = await axios.get(`${API_URL}/messages`);
    return response.data;
  } catch (error) {
    console.error("Error fetching messages:", error);
    return [];
  }
};
