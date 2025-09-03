import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import ForgotPassword from './components/ForgotPassword';
import ResetPassword from './components/ResetPassword';
import ChatPage from './pages/ChatPage'; // Import the ChatPage
import './App.css';

// Simple authentication check placeholder
// In a real app, this would involve checking for a token, user context, etc.
const isAuthenticated = () => {
  // For demonstration, we'll assume the user is always authenticated.
  // You should replace this with your actual authentication logic.
  // For example, check if a token exists in localStorage.
  return true; 
};

// A wrapper for protected routes
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    // If not authenticated, redirect to the login page
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* Protected Chat Route */}
        <Route 
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          } 
        />

        {/* Default route */}
        <Route 
          path="/" 
          element={
            <Navigate to={isAuthenticated() ? "/chat" : "/login"} replace />
          } 
        />
      </Routes>
    </div>
  );
}

export default App;
