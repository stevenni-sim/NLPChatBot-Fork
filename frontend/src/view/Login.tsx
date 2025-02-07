import React, { useState } from 'react';
import Header from '../component/header';
import { userController } from '../controller/userController';
import { useNavigate } from 'react-router-dom';
import { Authorise } from '../model/Authorise';  // Import Authorise model


const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [generalError, setGeneralError] = useState<string | null>(null);
    const navigate = useNavigate();

    
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
      
        const user: Authorise = { email, password };
      
        try {
          // Call the backend to authenticate the user
          const response = await userController.loginUser(user);
      
          // Extract userId and sessionId from the backend response
          const { user_id, session_id, role } = response.data;
      
          // Store userId and sessionId in sessionStorage
          sessionStorage.setItem("userId", user_id);
          sessionStorage.setItem("sessionId", session_id);
          sessionStorage.setItem("role", role);

          
          // Redirect based on user role
          if (role === "admin") {
            navigate("/admindashboard"); // Redirect to admin dashboard
          } else {
            navigate("/dashboard"); // Redirect to regular user dashboard
          }
        } catch (error: any) {
          setGeneralError(""); // Clear any previous error messages
          console.error("Login error:", error);
      
          // Display backend-provided error message if available
          if (error.response && error.response.data && error.response.data.detail) {
            setGeneralError(error.response.data.detail); // Use the error message from the backend
          } else {
            setGeneralError("Login Information Incorrect. Please try again."); // Fallback error message
          }
        }
      };
    

    return (
        <main>
            <Header />
            <div className="form-container">
                <form action="/login" method="POST" onSubmit={handleSubmit}>
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    
                    <button type="submit">Login</button>
                </form>
                <p>Don’t have an account? <a href="/register">Register here</a></p>
                <p>Forget Password? <a href="/forgetpassword">Reset here</a></p>
            </div>
            {/* General Error */}
            {generalError && <div style={{ color: 'red', marginLeft: '775px', marginTop: '-40px'}}>{generalError}</div>}

        </main>
    );
};

export default Login;
