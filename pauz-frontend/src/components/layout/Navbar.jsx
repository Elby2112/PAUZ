import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";

import logo from "../../assets/images/logo.jpeg";
import profileIcon from "../../assets/icons/profile.png";
import userIcon from "../../assets/icons/user.png";
import logoutIcon from "../../assets/icons/logout.png";
import loginIcon from "../../assets/icons/sign-in.png";

import homeIcon from "../../assets/icons/home.png";
import freeJournalIcon from "../../assets/images/freejournal.png";
import guidedJournalIcon from "../../assets/images/guidedjournal.png";
import gardenIcon from "../../assets/icons/garden.png";
import videoIcon from "../../assets/icons/youtube.png";
import githubIcon from "../../assets/icons/github.png";

import "../../styles/navbar.css";

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [user, setUser] = useState(null);
  const [imageLoaded, setImageLoaded] = useState(false);

  const containerRef = useRef(null);
  const location = useLocation();

  // Load user from localStorage on component mount and route changes
  useEffect(() => {
    loadUserFromStorage();
  }, [location.pathname]); // Reload when route changes

  // Preload profile picture when user data changes
  useEffect(() => {
    if (user?.picture) {
      console.log("🖼️ Preloading profile picture:", user.picture);
      setImageLoaded(false);
      const img = new Image();
      img.src = user.picture;
      img.onload = () => {
        console.log("✅ Profile picture loaded successfully");
        setImageLoaded(true);
      };
      img.onerror = () => {
        console.log("❌ Failed to load profile picture");
        setImageLoaded(true);
      };
    } else {
      setImageLoaded(true);
    }
  }, [user?.picture]);

  // Load user data from localStorage
  const loadUserFromStorage = () => {
    const token = localStorage.getItem("pauz_token");
    const userData = localStorage.getItem("pauz_user");

    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        console.error("Error parsing user data:", error);
        setUser(null);
      }
    } else {
      setUser(null);
    }
  };

  // Listen for storage updates (from GoogleCallback) AND custom events
  useEffect(() => {
    const handleStorageUpdate = () => {
      console.log("Storage updated, reloading user data");
      loadUserFromStorage();
    };

    // Listen to all possible events
    window.addEventListener("storage", handleStorageUpdate);
    window.addEventListener("localStorageUpdate", handleStorageUpdate);
    
    // Add this for Safari
    const interval = setInterval(() => {
      loadUserFromStorage();
    }, 1000); // Check every second as backup

    return () => {
      window.removeEventListener("storage", handleStorageUpdate);
      window.removeEventListener("localStorageUpdate", handleStorageUpdate);
      clearInterval(interval);
    };
  }, []);

  // Close menu on route change
  useEffect(() => {
    setMenuOpen(false);
    setProfileOpen(false);
  }, [location.pathname]);

  // Close menus on scroll/click/Esc
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    const onDocClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setMenuOpen(false);
        setProfileOpen(false);
      }
    };
    const onKey = (e) => e.key === "Escape" && (setMenuOpen(false), setProfileOpen(false));

    window.addEventListener("scroll", onScroll);
    document.addEventListener("click", onDocClick);
    document.addEventListener("keydown", onKey);

    return () => {
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("click", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  // Google login
  const handleGoogleSignIn = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  // Logout
  const handleSignOut = () => {
    localStorage.removeItem("pauz_token");
    localStorage.removeItem("pauz_user");
    setUser(null);
    setImageLoaded(false);
    setProfileOpen(false);
    
    // Dispatch event to notify other components
    window.dispatchEvent(new Event("localStorageUpdate"));
    window.dispatchEvent(new Event("storage"));
  };

  const loggedIn = !!user;

  return (
    <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`} ref={containerRef}>
      <div className="navbar-container">

        {/* LEFT */}
        <div className="navbar-left">
          <button className="navbar-hamburger" onClick={() => setMenuOpen(v => !v)}>☰</button>

          {menuOpen && (
            <div className="enhanced-dropdown left-dropdown">
              <Link to="/" className="dropdown-item"><img src={homeIcon} /> Home</Link>
              <Link to="/journal" className="dropdown-item"><img src={freeJournalIcon} /> Free Journal</Link>
              <Link to="/guided/journal" className="dropdown-item"><img src={guidedJournalIcon} /> Guided Journal</Link>
              <Link to="/garden" className="dropdown-item"><img src={gardenIcon} /> My Garden</Link>
              <a href="https://youtu.be/..." target="_blank" className="dropdown-item"><img src={videoIcon} /> Introduction Video</a>
              <a href="https://github.com/..." target="_blank" className="dropdown-item"><img src={githubIcon} /> GitHub</a>
            </div>
          )}
        </div>

        {/* LOGO */}
        <Link to="/" className="navbar-logo" onClick={() => setMenuOpen(false)}>
          <img src={logo} alt="Pauz" />
        </Link>

        {/* RIGHT PROFILE */}
        <div className="navbar-profile">
          <button className="profile-button" onClick={() => setProfileOpen(v => !v)}>
            <img
              src={user?.picture || profileIcon}
              alt="Profile"
              className="profile-icon"
              crossOrigin="anonymous"
              onLoad={() => setImageLoaded(true)}
              onError={(e) => {
                console.log("Image failed, using fallback");
                e.target.src = profileIcon;
                setImageLoaded(true);
              }}
              style={{ 
                opacity: imageLoaded ? 1 : 0.7,
                transition: 'opacity 0.3s ease-in-out'
              }}
            />
          </button>

          {profileOpen && (
            <div className="enhanced-dropdown profile-pos">
              {!loggedIn ? (
                <button className="profile-option" onClick={handleGoogleSignIn}>
                  <img src={loginIcon} /> Sign in with Google
                </button>
              ) : (
                <>
                  <Link className="profile-option" to="/profile" onClick={() => setProfileOpen(false)}>
                    <img src={userIcon} /> Profile
                  </Link>
                  <button className="profile-option" onClick={handleSignOut}>
                    <img src={logoutIcon} /> Log Out
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;