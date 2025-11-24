import React from "react";
import "../../styles/footer.css";
import logo from "../../assets/images/logo.jpeg";

const Footer = () => {
  return (
    <footer className="footer">
      {/* Left: Logo */}
      <div className="footer-left">
        <img src={logo} alt="PAUZ Logo" className="footer-logo" />
      </div>

      {/* Center: Tagline */}
      <div className="footer-center">
        Your AI journaling assistant helping you gain clarity.
      </div>

      {/* Right: Copyright */}
      <div className="footer-right">
        © {new Date().getFullYear()} PAUZ. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
