import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation } from "react-router-dom";

import logo from "../../assets/images/logo.jpeg";
import profileIcon from "../../assets/icons/profile.png";
import userIcon from "../../assets/icons/user.png";
import logoutIcon from "../../assets/icons/logout.png";
import loginIcon from "../../assets/icons/sign-in.png";

import freeJournalIcon from "../../assets/images/freejournal.png";
import guidedJournalIcon from "../../assets/images/guidedjournal.png";

import "../../styles/navbar.css";

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [journalOpen, setJournalOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Fake user login for now
  const [loggedIn, setLoggedIn] = useState(false);

  const containerRef = useRef(null);
  const journalRef = useRef(null);
  const profileRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    setMenuOpen(false);
    setJournalOpen(false);
    setProfileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768);
    const onScroll = () => setScrolled(window.scrollY > 10);

    const onDocClick = (e) => {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target)) {
        setJournalOpen(false);
        setProfileOpen(false);
      }
    };

    const onKey = (e) => {
      if (e.key === "Escape") {
        setJournalOpen(false);
        setProfileOpen(false);
        setMenuOpen(false);
      }
    };

    window.addEventListener("resize", onResize);
    window.addEventListener("scroll", onScroll);
    document.addEventListener("click", onDocClick);
    document.addEventListener("keydown", onKey);

    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("click", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  const handleSignOut = () => setLoggedIn(false);
  const handleFakeGoogleSignIn = () => setLoggedIn(true);

  return (
    <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`} ref={containerRef}>
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={() => setJournalOpen(false)}>
          <img src={logo} alt="Pauz" />
        </Link>

        {/* Desktop */}
        {!isMobile && (
          <ul className="navbar-links">
            <li><Link to="/">Home</Link></li>

            {/* Journal Dropdown */}
            <li className="navbar-dropdown" ref={journalRef}>
              <button
                className={`dropdown-trigger ${journalOpen ? "open" : ""}`}
                onClick={() => setJournalOpen((v) => !v)}
              >
                Journal <span className="dropdown-arrow">▼</span>
              </button>
              {journalOpen && (
                <ul className="enhanced-dropdown">
                  <Link
                    to="/journal"
                    className="dropdown-item"
                    onClick={() => setJournalOpen(false)}
                  >
                    <img src={freeJournalIcon} alt="Free Journal" />
                    Free Journal
                  </Link>
                  <Link
                    to="/guided/journal"
                    className="dropdown-item"
                    onClick={() => setJournalOpen(false)}
                  >
                    <img src={guidedJournalIcon} alt="Guided Journal" />
                    Guided Journal
                  </Link>
                </ul>
              )}
            </li>

            <li><Link to="/garden">My Garden</Link></li>
          </ul>
        )}

        {/* Mobile Hamburger */}
        {isMobile && (
          <button
            className="navbar-hamburger"
            onClick={() => setMenuOpen((v) => !v)}
          >
            ☰
          </button>
        )}

        {/* Profile Dropdown */}
        <div className="navbar-profile" ref={profileRef}>
          <button className="profile-button" onClick={() => setProfileOpen((v) => !v)}>
            <img src={profileIcon} alt="Profile" className="profile-icon" />
          </button>

          {profileOpen && (
            <div className="enhanced-dropdown profile-pos">
              {!loggedIn ? (
                <button className="profile-option" onClick={handleFakeGoogleSignIn}>
                  <img src={loginIcon} alt="Login" />
                  Sign in with Google
                </button>
              ) : (
                <>
                  <Link className="profile-option" to="/profile">
                    <img src={userIcon} alt="Profile" />
                    Profile
                  </Link>
                  <button className="profile-option" onClick={handleSignOut}>
                    <img src={logoutIcon} alt="Logout" />
                    Log Out
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobile && menuOpen && (
        <div className="navbar-mobile-wrapper">
          <ul className="navbar-mobile-menu">
            <li><Link to="/">Home</Link></li>
            <li>
              <details className="mobile-accordion">
                <summary>Journal</summary>
                <ul className="mobile-submenu">
                  <li><Link to="/journal">Free Journal</Link></li>
                  <li><Link to="/guided/journal">Guided Journal</Link></li>
                </ul>
              </details>
            </li>
            <li><Link to="/garden">My Garden</Link></li>
            <li className="mobile-divider" />
            {!loggedIn ? (
              <li>
                <button className="profile-option" onClick={handleFakeGoogleSignIn}>
                  <img src={loginIcon} alt="Login" />
                  Sign in with Google
                </button>
              </li>
            ) : (
              <>
                <li><Link className="profile-option" to="/profile">
                  <img src={userIcon} alt="Profile" />
                  Profile
                </Link></li>
                <li><button className="profile-option" onClick={handleSignOut}>
                  <img src={logoutIcon} alt="Logout" />
                  Log Out
                </button></li>
              </>
            )}
          </ul>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
