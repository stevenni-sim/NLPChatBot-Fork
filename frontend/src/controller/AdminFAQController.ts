import { useState, useCallback } from 'react';
import axios, { AxiosResponse } from 'axios';
import { BASE_URL } from '../service/config';

export interface FAQ {
  id?: string;
  ques: string;
  answer: string;
}

export const useFAQLogic = () => {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Memoized function for fetching FAQs
  const listFAQ = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response: AxiosResponse<FAQ[]> = await axios.get(`${BASE_URL}/ListFaqs`);
      setFaqs(response.data);
    } catch (err) {
      console.error('Error fetching FAQs:', err);
      setError('Failed to fetch FAQs. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []); // Empty dependency array ensures this function does not change

  const createFAQ = async (faq: FAQ): Promise<void> => {
    setError(null);
    try {
      const response: AxiosResponse<FAQ> = await axios.post(`${BASE_URL}/CreateFaqs`, faq);
      setFaqs((prevFaqs) => [...prevFaqs, response.data]);
    } catch (err) {
      console.error('Error creating FAQ:', err);
      setError('Failed to create FAQ. Please try again.');
    }
  };

  return {
    faqs,
    isLoading,
    error,
    createFAQ,
    listFAQ, // Stable reference
  };
};
