import React, { useEffect, useState } from 'react';
import UserHeader from '../../component/userHeader';
import { useFAQLogic } from '../../controller/AdminFAQController';
import { FAQ } from '../../model/FAQ';

const FAQPage: React.FC = () => {
  const { faqs, isLoading, error, createFAQ, listFAQ } = useFAQLogic();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newFAQ, setNewFaq] = useState<FAQ>({ ques: '', answer: '' });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // Fetch FAQs once on mount
  useEffect(() => {
    listFAQ();
  }, [listFAQ]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewFaq((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const validateForm = () => {
    const formErrors: { [key: string]: string } = {};
    if (!newFAQ.ques.trim()) formErrors.ques = 'Question is required.';
    if (!newFAQ.answer.trim()) formErrors.answer = 'Answer is required.';
    setErrors(formErrors);
    return Object.keys(formErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      await createFAQ(newFAQ);
      setNewFaq({ ques: '', answer: '' });
      setIsModalOpen(false);
      listFAQ(); // Refresh FAQs
    } catch (error) {
      console.error('Error adding new FAQ:', error);
    }
  };

  return (
    <main>
      <UserHeader />
      <div className="admin-dashboard">
      <button
      className="add-user-btn"
      onClick={() => setIsModalOpen(true)}
      style={{
        padding: "15px 30px", 
        fontSize: "18px", 
        backgroundColor: "#007BFF", // Primary blue background
        color: "white", // White text color
        border: "none", // Remove border
        borderRadius: "8px", // Rounded corners
        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.2)", // Add a shadow for depth
        cursor: "pointer", // Pointer cursor for better UX
        transition: "background-color 0.3s, transform 0.2s", // Smooth transitions
        marginTop: "20px", 
        marginLeft: "30px", 
      }}
      onMouseOver={(e) => {
        (e.target as HTMLElement).style.backgroundColor = "#0056b3"; // Darker blue on hover
      }}
      onMouseOut={(e) => {
        (e.target as HTMLElement).style.backgroundColor = "#007BFF"; // Revert to original color
      }}
    >
      Add FAQ
    </button>

        {isLoading && <p>Loading FAQs...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}

        <table className="user-list">
          <thead>
            <tr>
              <th>Question</th>
              <th>Answer</th>
            </tr>
          </thead>
          <tbody>
            {faqs.map((item, index) => (
              <tr key={index}>
                <td>{item.ques}</td>
                <td>{item.answer}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {isModalOpen && (
          <div className="modal-overlay">
            <div className="modal-content"
              style={{
                width: "60%", // Larger width
                padding: "40px", // Increased padding
                borderRadius: "10px",
              }}
              >
              <h3>Add New FAQ</h3>
              <input
                type="text"
                name="ques"
                placeholder="Question"
                value={newFAQ.ques}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "15px", // Larger padding for inputs
                  marginBottom: "20px",
                  fontSize: "18px", // Larger font size for inputs
                }}
              />
              {errors.ques && <p className="error-text">{errors.ques}</p>}
              <input
                type="text"
                name="answer"
                placeholder="Answer"
                value={newFAQ.answer}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "15px", // Larger padding for inputs
                  marginBottom: "20px",
                  fontSize: "18px", // Larger font size for inputs

                }}
              />
              {errors.answer && <p className="error-text">{errors.answer}</p>}
              <div className="modal-actions"
              style={{
              display: "flex", // Use flexbox for alignment
              justifyContent: "space-between", // Spread buttons apart
              gap: "20px", // Add spacing between buttons
              marginTop: "20px", // Add space above the buttons
              }}
              >
                <button onClick={handleSubmit}
                style={{
                  padding: "12px 25px", // Larger padding for buttons
                  fontSize: "14px", // Larger font size for buttons
                }}
                >Submit</button>

                <button onClick={() => setIsModalOpen(false)}
                style={{
                  padding: "12px 25px", // Larger padding for buttons
                  fontSize: "14px", // Larger font size for buttons
                }}  
                >Cancel</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
};

export default FAQPage;
