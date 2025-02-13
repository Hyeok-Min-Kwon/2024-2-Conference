import React, { useState } from 'react';
import { askQuestion } from '../utils/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './Home.css'; // 스타일 파일 불러오기

const Home = () => {
  const [question, setQuestion] = useState('');   // 사용자 입력 질문
  const [answer, setAnswer] = useState('');         // 백엔드에서 받은 답변
  const [loading, setLoading] = useState(false);    // 로딩 상태
  const [error, setError] = useState(null);         // 에러 상태
  const [history, setHistory] = useState([]);       // 질문-답변 히스토리

  // 폼 제출 이벤트 핸들러
  const handleSubmit = async (e) => {
    e.preventDefault();  // 기본 폼 제출 동작 방지

    // 빈 질문 입력 방지
    if (!question.trim()) {
      setError('Please enter a valid question.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 백엔드 API 호출 (예: http://localhost:5000/api/ask)
      const response = await askQuestion(question);
      setAnswer(response);

      // 히스토리에 현재 질문과 답변 추가
      setHistory((prevHistory) => [
        { question, answer: response },
        ...prevHistory,
      ]);
    } catch (err) {
      setError('Error fetching answer. Please try again later.');
    } finally {
      setLoading(false);
      setQuestion('');  // 질문 입력창 초기화
    }
  };

  return (
    <div className="home-container">
      <Header />
      <main className="main-content">
        <h2>어떤 주제의 뉴스를 알고 싶으신가요?</h2>
        <p>아래에 관심있는 분야의 뉴스 정보를 물어보면 챗봇이 요약해서 전달해줍니다!</p>

        {/* 질문 입력 폼 */}
        <form className="question-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="여기에 질문을 입력하세요"
            className="question-input"
          />
          <button type="submit" className="submit-btn">제출</button>
        </form>

        {/* 로딩 메시지 */}
        {loading && <p className="loading-message">로딩 중입니다...</p>}

        {/* 에러 메시지 */}
        {error && <p className="error-message">{error}</p>}

        {/* 백엔드에서 받은 답변 표시 */}
        {answer && (
          <div className="answer-card">
            <h3>Answer:</h3>
            <p>{answer}</p>
          </div>
        )}

        {/* 질문-답변 히스토리 */}
        {history.length > 0 && (
          <div className="history-section">
            <h3>Previous Questions</h3>
            <ul>
              {history.map((entry, index) => (
                <li key={index} className="history-item">
                  <strong>Q:</strong> {entry.question} <br />
                  <strong>A:</strong> {entry.answer}
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default Home;
