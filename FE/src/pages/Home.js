import React, { useState } from 'react';
import { askQuestion } from '../utils/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import QuestionInput from '../components/QuestionInput';

const Home = () => {
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (question) => {
    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion(question);
      setAnswer(response);
    } catch (err) {
      setError('Error fetching answer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header />
      <main>
        <h2>Ask a Question</h2>
        <QuestionInput onSubmit={handleSubmit} />
        
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {answer && <p><strong>Answer:</strong> {answer}</p>}
      </main>
      <Footer />
    </div>
  );
};

export default Home;
