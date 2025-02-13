import axios from 'axios';

export const askQuestion = async (question) => {
  try {
    const response = await axios.post(
      "http://4.217.250.63:8080/api/ask", 
      { question },
      {
        headers: {
          "Content-Type": "application/json"
        },
        withCredentials: true,
        timeout: 30000
      }
    );
    return response.data.answer;
  } catch (error) {
    console.error("Axios Error", error.response ? error.response.data : error.message);
    throw new Error('Error fetching answer');
  }
};
