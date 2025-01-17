import axios from 'axios';

export const askQuestion = async (question) => {
  try {
    const response = await axios.post('http://localhost:5000/api/ask', { question });
    return response.data.answer;
  } catch (error) {
    throw new Error('Error fetching answer');
  }
};
