import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";

import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import Home from "./pages/Home";
import Garden from "./pages/Garden";
import FreeJournal from "./Journals/freeJournal";
import GuidedJournaling from "./Journals/guidedJournal";

// Auth pages
import Login from "./pages/authentication/Login"
import Signup from "./pages/authentication/Signup";

// Profile page
import Profile from "./pages/authentication/Profile"; // Import the Profile page

// Wrapper to hide Navbar/Footer on auth routes
function LayoutWrapper({ children }) {
  const location = useLocation();
  const authPages = ["/login", "/signup"];
  const hideLayout = authPages.includes(location.pathname);

  return (
    <>
      {!hideLayout && <Navbar />}
      {children}
      {!hideLayout && <Footer />}
    </>
  );
}

// Protected route
function ProtectedRoute({ children }) {
  const user = localStorage.getItem("pauz_user");
  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <LayoutWrapper>
        <Routes>
          {/* Auth */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Main App (protected) */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            }
          />

          <Route
            path="/garden"
            element={
              <ProtectedRoute>
                <Garden />
              </ProtectedRoute>
            }
          />

          <Route
            path="/journal"
            element={
              <ProtectedRoute>
                <FreeJournal />
              </ProtectedRoute>
            }
          />

          <Route
            path="/guided/:category"
            element={
              <ProtectedRoute>
                <GuidedJournaling />
              </ProtectedRoute>
            }
          />

          {/* Profile Route */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}

export default App;
