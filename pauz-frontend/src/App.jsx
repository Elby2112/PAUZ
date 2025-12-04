import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";

import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import Home from "./pages/Home";
import Garden from "./pages/Garden";
import FreeJournal from "./Journals/freeJournal";
import GuidedJournaling from "./Journals/guidedJournal";
import SavedJournals from "./pages/SavedJournals"; // ⭐ ADD THIS IMPORT

// Profile page
import Profile from "./pages/authentication/Profile";
import GoogleCallback from "./pages/authentication/GoogleCallback";

// ⭐ Floating Help Button component
import FloatingHelpButton from "./utils/FloatingHelpButton"; // create this component as discussed

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
      {!hideLayout && <FloatingHelpButton />} {/* ⭐ Floating button added */}
    </>
  );
}

// Protected route component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem("pauz_token");
  return token ? children : <Navigate to="/" />;
}

function App() {
  return (
    <Router>
      <LayoutWrapper>
        <Routes>
          {/* Public Home */}
          <Route path="/" element={<Home />} />

          {/* Google Callback */}
          <Route path="/auth/callback" element={<GoogleCallback />} />

          {/* Protected Routes */}
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
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          {/* ⭐ ADD SAVED JOURNALS ROUTE */}
          <Route
            path="/saved-journals"
            element={
              <ProtectedRoute>
                <SavedJournals />
              </ProtectedRoute>
            }
          />

          {/* Catch-all redirect to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </LayoutWrapper>
    </Router>
  );
}

export default App;
