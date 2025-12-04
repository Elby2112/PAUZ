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

import journalIcon from "../../assets/icons/journals.png";
import "../../styles/navbar.css";
import CategoryModal from "../CategoryModal";  // ⭐ ADDED


const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [user, setUser] = useState(null);
  const [imageLoaded, setImageLoaded] = useState(false);

  const [showCategoryModal, setShowCategoryModal] = useState(false); // ⭐ ADDED

  const containerRef = useRef(null);
  const location = useLocation();

  // Load user from localStorage
  useEffect(() => {
    loadUserFromStorage();
  }, [location.pathname]);

  useEffect(() => {
    if (user?.picture) {
      setImageLoaded(false);
      const img = new Image();
      img.src = user.picture;
      img.onload = () => setImageLoaded(true);
      img.onerror = () => setImageLoaded(true);
    } else {
      setImageLoaded(true);
    }
  }, [user?.picture]);

  const loadUserFromStorage = () => {
    const token = localStorage.getItem("pauz_token");
    const userData = localStorage.getItem("pauz_user");

    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch {
        setUser(null);
      }
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    const handleStorageUpdate = () => loadUserFromStorage();

    window.addEventListener("storage", handleStorageUpdate);
    window.addEventListener("localStorageUpdate", handleStorageUpdate);

    const interval = setInterval(loadUserFromStorage, 1000);

    return () => {
      window.removeEventListener("storage", handleStorageUpdate);
      window.removeEventListener("localStorageUpdate", handleStorageUpdate);
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    setMenuOpen(false);
    setProfileOpen(false);
  }, [location.pathname]);

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

  const handleGoogleSignIn = () => {
    window.location.href = "http://localhost:8000/auth/login";
  };

  const handleSignOut = () => {
    localStorage.removeItem("pauz_token");
    localStorage.removeItem("pauz_user");
    setUser(null);
    setImageLoaded(false);
    setProfileOpen(false);

    window.dispatchEvent(new Event("localStorageUpdate"));
    window.dispatchEvent(new Event("storage"));
  };

  const loggedIn = !!user;

  return (
    <>
      <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`} ref={containerRef}>
        <div className="navbar-container">

          {/* LEFT */}
          <div className="navbar-left">
            <button className="navbar-hamburger" onClick={() => setMenuOpen(v => !v)}>☰</button>

            {menuOpen && (
              <div className="enhanced-dropdown left-dropdown">
                <Link to="/" className="dropdown-item"><img src={homeIcon} /> Home</Link>

                <Link to="/journal" className="dropdown-item">
                  <img src={freeJournalIcon} /> Free Journal
                </Link>

                {/* ⭐ REPLACED WITH BUTTON TO OPEN CATEGORY MODAL */}
                <button
                  className="dropdown-item"
                  onClick={() => setShowCategoryModal(true)}
                >
                  <img src={guidedJournalIcon} /> Guided Journal
                </button>

                <Link to="/saved-journals" className="dropdown-item">
                <img src={journalIcon} />
                 My Journals</Link>

                <Link to="/garden" className="dropdown-item"><img src={gardenIcon} /> My Garden</Link>

                <a href="https://youtu.be/..." target="_blank" className="dropdown-item">
                  <img src={videoIcon} /> Introduction Video
                </a>

                <a href="https://github.com/..." target="_blank" className="dropdown-item">
                  <img src={githubIcon} /> GitHub
                </a>
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
                className="profile-icon"
                alt="Profile"
                crossOrigin="anonymous"
                onLoad={() => setImageLoaded(true)}
                onError={(e) => {
                  e.target.src = profileIcon;
                  setImageLoaded(true);
                }}
                style={{
                  opacity: imageLoaded ? 1 : 0.7,
                  transition: "opacity 0.3s ease-in-out"
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

      {/* ⭐ CATEGORY MODAL */}
      {showCategoryModal && (
        <CategoryModal
  isOpen={showCategoryModal}
  onClose={() => setShowCategoryModal(false)}
  onSelect={(category) => {
    setShowCategoryModal(false);
    window.location.href = `/guided/${category}`;
  }}
/>

      )}
    </>
  );
};

export default Navbar;
