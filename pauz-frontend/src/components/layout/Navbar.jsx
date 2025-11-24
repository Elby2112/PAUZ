import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import logo from "../../assets/images/logo.jpeg"// import your logo
import "../../styles/navbar.css";


const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [journalDropdown, setJournalDropdown] = useState(false);
  const [scrolled, setScrolled] = useState(false); // track scroll

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);

    const handleScroll = () => {
      setScrolled(window.scrollY > 10); // add shadow after 10px scroll
    };
    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`}>
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <img src={logo} alt="Pauz Logo" />
        </Link>

        {!isMobile && (
          <ul className="navbar-links">
            <li>
              <Link to="/">Home</Link>
            </li>

            <li
              className="navbar-dropdown"
              onMouseEnter={() => setJournalDropdown(true)}
              onMouseLeave={() => setJournalDropdown(false)}
            >
              <span className="dropdown-title">Journal ⌄</span>
              {journalDropdown && (
                <ul className="dropdown-menu">
                  <li>
                    <Link to="/journal">Free Journal</Link>
                  </li>
                  <li>
                    <Link to="/guided/${category}">Guided Journal</Link>
                  </li>
                </ul>
              )}
            </li>

            <li>
              <Link to="/garden">My Garden</Link>
            </li>
          </ul>
        )}

        {isMobile && (
          <button
            className="navbar-hamburger"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            ☰
          </button>
        )}
      </div>

      {isMobile && menuOpen && (
        <ul className="navbar-mobile-menu">
          <li>
            <Link to="/" onClick={() => setMenuOpen(false)}>Home</Link>
          </li>
          <li>
            <Link to="/journal" onClick={() => setMenuOpen(false)}>Free Journal</Link>
          </li>
          <li>
            <Link to="/guided-journal" onClick={() => setMenuOpen(false)}>Guided Journal</Link>
          </li>
          <li>
            <Link to="/garden" onClick={() => setMenuOpen(false)}>My Garden</Link>
          </li>
        </ul>
      )}
    </nav>
  );
};

export default Navbar;
