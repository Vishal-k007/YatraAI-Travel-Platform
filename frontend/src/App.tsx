import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Components
import Navbar from './components/Navbar';
// import Footer from './components/Footer';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import QuizPage from './pages/QuizPage';
import GenerateItineraryPage from './pages/GenerateItineraryPage';
import ItineraryDetailsPage from './pages/ItineraryDetailsPage';
import ExplorePage from './pages/ExplorePage';

// Protected Route Wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            <Route path="/dashboard" element={
              <ProtectedRoute><DashboardPage /></ProtectedRoute>
            } />
            <Route path="/quiz" element={
              <ProtectedRoute><QuizPage /></ProtectedRoute>
            } />
            <Route path="/plan" element={
              <ProtectedRoute><GenerateItineraryPage /></ProtectedRoute>
            } />
            <Route path="/itinerary/:id" element={
              <ProtectedRoute><ItineraryDetailsPage /></ProtectedRoute>
            } />
            <Route path="/explore" element={
              <ProtectedRoute><ExplorePage /></ProtectedRoute>
            } />
          </Routes>
        </main>
        {/* <Footer /> */}
      </div>
    </BrowserRouter>
  );
}

export default App;
