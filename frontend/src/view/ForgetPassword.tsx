import React, { useState } from "react";
import Header from "../component/header";
import { userController } from "../controller/userController";

const ForgetPassword: React.FC = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const onPasswordReset = async () => {
    const result = await userController.handlePasswordReset(email);
    setMessage(result.message);
    setError(result.error);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", backgroundColor: "#f7f9fc" }}>
      <Header />
      <div style={{ padding: "20px", maxWidth: "400px", textAlign: "center", backgroundColor: "#fff", borderRadius: "8px", boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)" }}>
        <h2 style={{ marginBottom: "20px", fontSize: "1.5rem", color: "#333" }}>Reset Your Password</h2>
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc", fontSize: "1rem" }}
        />
        <button
          onClick={onPasswordReset}
          style={{ width: "100%", padding: "10px", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer", fontSize: "1rem" }}
        >
          Send Reset Email
        </button>
        {message && <p style={{ color: "green", marginTop: "15px", fontSize: "0.9rem" }}>{message}</p>}
        {error && <p style={{ color: "red", marginTop: "15px", fontSize: "0.9rem" }}>{error}</p>}
      </div>
    </div>
  );
};

export default ForgetPassword;
