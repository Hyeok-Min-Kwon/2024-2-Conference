import React, { useState } from 'react';

const QuestionInput = ({ onSubmit }) => {
  const [question, setQuestion] = useState('');

  const handleInputChange = (e) => {
    setQuestion(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(question);
    setQuestion('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={question}
        onChange={handleInputChange}
        placeholder="Ask a question"
        required
      />
      <button type="submit">Submit</button>
    </form>
  );
};

export default QuestionInput;
